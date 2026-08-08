import json
import pandas as pd
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.paginator import Paginator

from .models import PredictionHistory, ReverseDesignHistory
from .forms import DynamicCircuitForm, UserRegistrationForm
from .circuit_engine import CIRCUIT_REGISTRY, get_circuit_config, get_circuits_by_category
from .circuit_diagrams import generate_circuit_svg
from .circuit_optimizer import optimize_circuit_components
from .ai_assistant import generate_bot_response
from .pdf_generator import generate_pdf_report, generate_reverse_pdf_report
from .reverse_engine import TARGET_SPECS_SCHEMA, run_reverse_circuit_design

def dashboard_home_view(request):
    """Home Dashboard listing all circuit categories and 15 individual circuit cards."""
    categories = get_circuits_by_category()
    total_predictions = PredictionHistory.objects.count()
    
    return render(request, 'home.html', {
        'categories': categories,
        'total_predictions': total_predictions,
        'total_circuits': len(CIRCUIT_REGISTRY)
    })

def category_view(request, category_slug):
    """Category page listing circuits belonging to a specific category."""
    categories = get_circuits_by_category()
    cat_info = categories.get(category_slug, None)
    
    if not cat_info:
        messages.error(request, "Category not found.")
        return redirect('home')
        
    return render(request, 'category_list.html', {
        'category': cat_info,
        'category_slug': category_slug
    })

def circuit_detail_view(request, slug):
    """Dedicated page for each of the 15 electronic circuits with Multi-Output Prediction & AI Optimization."""
    config = get_circuit_config(slug)
    if not config:
        messages.error(request, f"Circuit '{slug}' not found.")
        return redirect('home')
        
    diagram_svg = generate_circuit_svg(slug)
    result = None
    saved_record = None
    opt_result = None
    
    if request.method == 'POST':
        if 'action_type' in request.POST and request.POST['action_type'] == 'optimize':
            target_specs = {
                'target_fc': request.POST.get('target_fc', 1000.0),
                'target_gain': request.POST.get('target_gain', 20.0),
                'target_bw': request.POST.get('target_bw', 10000.0),
                'target_pm': request.POST.get('target_pm', 60.0),
                'target_vout': request.POST.get('target_vout', 12.0),
            }
            opt_result = optimize_circuit_components(slug, target_specs)
            if opt_result.get('success'):
                metrics = opt_result['achieved_metrics']
                score = opt_result['score']
                
                record = PredictionHistory(
                    user=request.user if request.user.is_authenticated else None,
                    circuit_slug=slug,
                    circuit_title=config['title'],
                    circuit_category=config['category'],
                    inputs_json=json.dumps(opt_result['recommended_components']),
                    outputs_json=json.dumps([{ 'name': m['name'], 'label': m['label'], 'value': m['value'], 'unit': m['unit'] } for m in metrics]),
                    performance_score=score
                )
                record.save()
                saved_record = record
                
                result = {
                    'outputs': metrics,
                    'score': score,
                    'record_id': record.id,
                    'inputs_used': opt_result['recommended_components']
                }
                messages.success(request, f"AI Optimization successfully applied for {config['title']}!")
            else:
                messages.error(request, f"Optimization error: {opt_result.get('error')}")
            
            form = DynamicCircuitForm(circuit_inputs=config['inputs'])

        else: # Standard Prediction
            form = DynamicCircuitForm(circuit_inputs=config['inputs'], data=request.POST)
            if form.is_valid():
                inputs_data = form.cleaned_data
                try:
                    calc_res = config['calc'](inputs_data)
                    metrics = calc_res['metrics']
                    score = calc_res['score']
                    
                    record = PredictionHistory(
                        user=request.user if request.user.is_authenticated else None,
                        circuit_slug=slug,
                        circuit_title=config['title'],
                        circuit_category=config['category'],
                        inputs_json=json.dumps(inputs_data),
                        outputs_json=json.dumps([{ 'name': m['name'], 'label': m['label'], 'value': m['value'], 'unit': m['unit'] } for m in metrics]),
                        performance_score=score
                    )
                    record.save()
                    saved_record = record
                    
                    result = {
                        'outputs': metrics,
                        'score': score,
                        'record_id': record.id,
                        'inputs_used': inputs_data
                    }
                    messages.success(request, f"Multi-output parameters for {config['title']} predicted successfully!")
                except Exception as e:
                    messages.error(request, f"Calculation error: {e}")
            else:
                messages.error(request, "Invalid component input parameters. Please check entries.")
    else:
        form = DynamicCircuitForm(circuit_inputs=config['inputs'])
        
    circuit_history = PredictionHistory.objects.filter(circuit_slug=slug)[:5]

    return render(request, 'circuit_detail.html', {
        'circuit': config,
        'diagram_svg': diagram_svg,
        'form': form,
        'result': result,
        'saved_record': saved_record,
        'opt_result': opt_result,
        'circuit_history': circuit_history
    })

# =========================================================
# NEW MODULE: AI REVERSE CIRCUIT DESIGN VIEWS
# =========================================================

def reverse_design_view(request):
    """
    Dedicated AI Reverse Circuit Design page.
    User specifies Target Circuit Performance -> GA/PSO Optimizer + ML Model -> Recommended Component Values.
    """
    all_circuits = list(CIRCUIT_REGISTRY.values())
    selected_slug = request.GET.get('circuit', 'rc-low-pass')
    if request.method == 'POST':
        selected_slug = request.POST.get('circuit_slug', 'rc-low-pass')

    config = get_circuit_config(selected_slug) or list(CIRCUIT_REGISTRY.values())[0]
    target_schema = TARGET_SPECS_SCHEMA.get(selected_slug, TARGET_SPECS_SCHEMA['rc-low-pass'])
    diagram_svg = generate_circuit_svg(selected_slug)
    
    rev_result = None
    saved_record = None

    if request.method == 'POST':
        # Extract target output values
        target_specs = {}
        weights = {}
        for item in target_schema:
            val_str = request.POST.get(f"target_{item['name']}", item['default'])
            weight_str = request.POST.get(f"weight_{item['name']}", '1.0')
            try:
                target_specs[item['name']] = float(val_str)
                weights[item['name']] = float(weight_str)
            except ValueError:
                target_specs[item['name']] = float(item['default'])
                weights[item['name']] = 1.0

        opt_settings = {
            'algorithm': request.POST.get('algorithm', 'Genetic Algorithm'),
            'comp_series': request.POST.get('comp_series', 'E24'),
            'pop_size': int(request.POST.get('pop_size', 40)),
            'max_iter': int(request.POST.get('max_iter', 60)),
            'weights': weights
        }

        rev_result = run_reverse_circuit_design(selected_slug, target_specs, opt_settings)

        if rev_result.get('success'):
            # Save into ReverseDesignHistory model
            record = ReverseDesignHistory(
                user=request.user if request.user.is_authenticated else None,
                circuit_slug=selected_slug,
                circuit_title=config['title'],
                algorithm_used=rev_result['algorithm_used'],
                comp_series=rev_result['comp_series'],
                target_params_json=json.dumps(target_specs),
                optimized_components_json=json.dumps(rev_result['recommended_components']),
                predicted_params_json=json.dumps([{ 'name': m['name'], 'label': m['label'], 'value': m['value'], 'unit': m['unit'] } for m in rev_result['predicted_metrics']]),
                performance_score=rev_result['score'],
                total_error=rev_result['total_error_pct'],
                iterations=rev_result['iterations'],
                optimization_time_ms=rev_result['optimization_time_ms']
            )
            record.save()
            saved_record = record
            rev_result['record_id'] = record.id

            if rev_result['is_feasible']:
                messages.success(request, f"AI Reverse Design completed successfully for {config['title']}! Score: {rev_result['score']}%")
            else:
                messages.warning(request, "No feasible design found within target constraints. Consider relaxing constraints.")
        else:
            messages.error(request, f"Reverse optimization error: {rev_result.get('error')}")

    target_schema_json = json.dumps({
        slug: [
            {'name': t['name'], 'label': t['label'], 'unit': t['unit'], 'default': t['default'], 'min': t['min'], 'max': t['max']}
            for t in schema
        ]
        for slug, schema in TARGET_SPECS_SCHEMA.items()
    })

    return render(request, 'reverse_design.html', {
        'all_circuits': all_circuits,
        'selected_circuit': config,
        'selected_slug': selected_slug,
        'target_schema': target_schema,
        'target_schema_json': target_schema_json,
        'diagram_svg': diagram_svg,
        'rev_result': rev_result,
        'saved_record': saved_record
    })

def reverse_history_view(request):
    """History log of AI Reverse Circuit Design sessions."""
    circuit_filter = request.GET.get('circuit', '')
    query = request.GET.get('q', '')
    
    records_list = ReverseDesignHistory.objects.all()
    if circuit_filter:
        records_list = records_list.filter(circuit_slug=circuit_filter)
    if query:
        records_list = records_list.filter(circuit_title__icontains=query)

    paginator = Paginator(records_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_circuits = CIRCUIT_REGISTRY.values()

    return render(request, 'reverse_history.html', {
        'page_obj': page_obj,
        'query': query,
        'circuit_filter': circuit_filter,
        'all_circuits': all_circuits
    })

def reverse_export_pdf_view(request, record_id):
    """Export Reverse Design session as ReportLab PDF report."""
    record = get_object_or_404(ReverseDesignHistory, id=record_id)
    config = get_circuit_config(record.circuit_slug)
    
    targets = record.get_targets_dict()
    comps = record.get_components_dict()
    
    # Run reverse calculation to fetch formatting
    rev_res = run_reverse_circuit_design(record.circuit_slug, targets, {
        'algorithm': record.algorithm_used,
        'comp_series': record.comp_series
    })
    
    pdf_bytes = generate_reverse_pdf_report(
        record.circuit_title,
        record.algorithm_used,
        record.comp_series,
        rev_res['target_comparison_table'],
        comps,
        rev_res['predicted_metrics'],
        record.performance_score,
        record.total_error,
        rev_res['xai_breakdown']
    )
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CircuitAI_ReverseDesign_{record.circuit_slug}_{record.id}.pdf"'
    return response

# Standard views
def optimizer_page_view(request):
    """Standalone AI Circuit Optimization interactive dashboard."""
    all_circuits = list(CIRCUIT_REGISTRY.values())
    selected_slug = request.GET.get('circuit', 'rc-low-pass')
    config = get_circuit_config(selected_slug)
    
    opt_result = None
    if request.method == 'POST':
        selected_slug = request.POST.get('circuit_slug', 'rc-low-pass')
        config = get_circuit_config(selected_slug)
        target_specs = {
            'target_fc': request.POST.get('target_fc', 1000.0),
            'target_gain': request.POST.get('target_gain', 20.0),
            'target_bw': request.POST.get('target_bw', 10000.0),
            'target_pm': request.POST.get('target_pm', 60.0),
            'target_vout': request.POST.get('target_vout', 12.0),
        }
        opt_result = optimize_circuit_components(selected_slug, target_specs)

    return render(request, 'optimizer.html', {
        'all_circuits': all_circuits,
        'selected_circuit': config,
        'opt_result': opt_result
    })

def api_chat_view(request):
    """API endpoint for AI Chatbot Assistant queries."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_query = data.get('query', '')
            circuit_slug = data.get('circuit_slug', None)
            prediction_data = data.get('prediction_data', None)
            
            response = generate_bot_response(user_query, circuit_slug, prediction_data)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'reply': f"Error processing query: {str(e)}"}, status=400)
            
    return JsonResponse({'reply': "Method not allowed"}, status=405)

def export_pdf_view(request, record_id):
    """Export prediction record as publication-ready ReportLab PDF."""
    record = get_object_or_404(PredictionHistory, id=record_id)
    config = get_circuit_config(record.circuit_slug)
    
    inputs_used = record.get_inputs_dict()
    calc_res = config['calc'](inputs_used)
    outputs_list = calc_res['metrics']
    
    pdf_bytes = generate_pdf_report(config, inputs_used, outputs_list, record.performance_score)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CircuitAI_Report_{record.circuit_slug}_{record.id}.pdf"'
    return response

def export_csv_view(request, record_id):
    """Export prediction record metrics to downloadable CSV file."""
    record = get_object_or_404(PredictionHistory, id=record_id)
    config = get_circuit_config(record.circuit_slug)
    
    inputs_used = record.get_inputs_dict()
    calc_res = config['calc'](inputs_used)
    outputs_list = calc_res['metrics']
    
    df_metrics = pd.DataFrame([
        {
            'Parameter Label': m['label'],
            'Predicted Value': m['value'],
            'Unit': m['unit'],
            'Normal Operating Range': m['normal_range'],
            'Prediction Confidence': m['confidence'],
            'Performance Rating': m['rating'],
            'Status': m['status'],
            'Engineering Explanation': m['explanation'],
            'Recommendation': m['recommendation']
        }
        for m in outputs_list
    ])
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="CircuitAI_Metrics_{record.circuit_slug}_{record.id}.csv"'
    df_metrics.to_csv(path_or_buf=response, index=False)
    return response

def export_excel_view(request, record_id):
    """Export prediction record metrics to downloadable Excel spreadsheet."""
    record = get_object_or_404(PredictionHistory, id=record_id)
    config = get_circuit_config(record.circuit_slug)
    
    inputs_used = record.get_inputs_dict()
    calc_res = config['calc'](inputs_used)
    outputs_list = calc_res['metrics']
    
    df_metrics = pd.DataFrame([
        {
            'Parameter Label': m['label'],
            'Predicted Value': m['value'],
            'Unit': m['unit'],
            'Normal Operating Range': m['normal_range'],
            'Prediction Confidence': m['confidence'],
            'Performance Rating': m['rating'],
            'Status': m['status'],
            'Engineering Explanation': m['explanation'],
            'Recommendation': m['recommendation']
        }
        for m in outputs_list
    ])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_metrics.to_excel(writer, sheet_name='Metrics', index=False)
        
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="CircuitAI_Metrics_{record.circuit_slug}_{record.id}.xlsx"'
    return response

def history_view(request):
    """Prediction History page with filters."""
    circuit_filter = request.GET.get('circuit', '')
    query = request.GET.get('q', '')
    
    records_list = PredictionHistory.objects.all()
    if circuit_filter:
        records_list = records_list.filter(circuit_slug=circuit_filter)
    if query:
        records_list = records_list.filter(circuit_title__icontains=query)

    paginator = Paginator(records_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_circuits = CIRCUIT_REGISTRY.values()

    return render(request, 'history.html', {
        'page_obj': page_obj,
        'query': query,
        'circuit_filter': circuit_filter,
        'all_circuits': all_circuits
    })

def analytics_view(request):
    """CAD Analytics Dashboard."""
    total_predictions = PredictionHistory.objects.count()
    avg_score = PredictionHistory.objects.aggregate(avg=Avg('performance_score'))['avg']
    avg_score = round(avg_score, 1) if avg_score else 95.0
    
    circuit_counts = PredictionHistory.objects.values('circuit_title').annotate(count=Count('id')).order_by('-count')[:6]
    recent_activity = PredictionHistory.objects.all()[:8]
    
    return render(request, 'analytics.html', {
        'total_predictions': total_predictions,
        'avg_score': avg_score,
        'circuit_counts': circuit_counts,
        'recent_activity': recent_activity
    })

def profile_view(request):
    """User profile view."""
    user_predictions = PredictionHistory.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'profile.html', {
        'user_predictions_count': len(user_predictions)
    })

def settings_view(request):
    """Settings page."""
    return render(request, 'settings.html')

def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CircuitAI, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed.")
    else:
        form = UserRegistrationForm()
        
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Signed in as {user.username}.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('home')

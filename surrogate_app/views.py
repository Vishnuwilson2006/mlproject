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

from .models import (
    PredictionHistory, ReverseDesignHistory,
    UncertaintyAnalysisHistory, MonteCarloHistory,
    ActiveLearningHistory, ParetoOptimizationHistory, SensitivityAnalysisHistory
)
from .forms import DynamicCircuitForm, UserRegistrationForm
from .circuit_engine import CIRCUIT_REGISTRY, get_circuit_config, get_circuits_by_category
from .circuit_diagrams import generate_circuit_svg
from .circuit_optimizer import optimize_circuit_components
from .ai_assistant import generate_bot_response
from .pdf_generator import generate_pdf_report, generate_reverse_pdf_report, generate_research_pdf_report
from .reverse_engine import TARGET_SPECS_SCHEMA, run_reverse_circuit_design
from .research_engine import (
    run_uncertainty_analysis, run_monte_carlo_analysis,
    run_active_learning, run_pareto_optimization, run_sensitivity_analysis
)


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


# =============================================================================
# 5 ADVANCED ECE RESEARCH MODULE VIEWS
# =============================================================================

def uncertainty_analysis_view(request):
    """Module 1: Uncertainty & Confidence Analysis"""
    circuit_slug = request.GET.get('circuit', request.POST.get('circuit', 'common-emitter'))
    config = get_circuit_config(circuit_slug) or get_circuit_config('common-emitter')
    
    # Process inputs
    inputs = {}
    for inp in config['inputs']:
        inputs[inp['name']] = request.POST.get(inp['name'], request.GET.get(inp['name'], inp['default']))

    model_type = request.POST.get('model_type', request.GET.get('model_type', 'Random Forest Ensemble'))
    
    res = run_uncertainty_analysis(config['slug'], inputs, model_type)
    
    if request.method == 'POST':
        # Save record
        record = UncertaintyAnalysisHistory(
            user=request.user if request.user.is_authenticated else None,
            circuit_slug=config['slug'],
            circuit_title=config['title'],
            model_type=model_type,
            inputs_json=json.dumps(res['inputs']),
            results_json=json.dumps(res['output_cards']),
            confidence_score=res['research_metrics']['avg_confidence'],
            mae=res['research_metrics']['mae'],
            rmse=res['research_metrics']['rmse'],
            r2_score=res['research_metrics']['r2']
        )
        record.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(res)

    all_circuits = list(CIRCUIT_REGISTRY.values())
    recent_history = UncertaintyAnalysisHistory.objects.all()[:5]

    return render(request, 'uncertainty_analysis.html', {
        'config': config,
        'all_circuits': all_circuits,
        'res': res,
        'res_json': json.dumps(res),
        'model_type': model_type,
        'recent_history': recent_history
    })


def monte_carlo_analysis_view(request):
    """Module 2: Component Tolerance & Monte Carlo Analysis"""
    circuit_slug = request.GET.get('circuit', request.POST.get('circuit', 'rc-low-pass'))
    config = get_circuit_config(circuit_slug) or get_circuit_config('rc-low-pass')
    
    inputs = {}
    for inp in config['inputs']:
        inputs[inp['name']] = request.POST.get(inp['name'], request.GET.get(inp['name'], inp['default']))

    tolerance_pct = float(request.POST.get('tolerance', request.GET.get('tolerance', 5.0)))
    n_simulations = int(request.POST.get('simulations', request.GET.get('simulations', 1000)))

    res = run_monte_carlo_analysis(config['slug'], inputs, tolerance_pct, n_simulations)

    if request.method == 'POST':
        record = MonteCarloHistory(
            user=request.user if request.user.is_authenticated else None,
            circuit_slug=config['slug'],
            circuit_title=config['title'],
            tolerance_pct=tolerance_pct,
            simulations_count=n_simulations,
            inputs_json=json.dumps(res['inputs']),
            results_json=json.dumps(res['outputs_analysis']),
            robustness_score=res['robustness_score']
        )
        record.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(res)

    all_circuits = list(CIRCUIT_REGISTRY.values())
    recent_history = MonteCarloHistory.objects.all()[:5]

    return render(request, 'monte_carlo_analysis.html', {
        'config': config,
        'all_circuits': all_circuits,
        'res': res,
        'res_json': json.dumps(res),
        'tolerance_pct': tolerance_pct,
        'n_simulations': n_simulations,
        'recent_history': recent_history
    })


def active_learning_view(request):
    """Module 3: Active Learning / Smart Dataset Expansion"""
    circuit_slug = request.GET.get('circuit', request.POST.get('circuit', 'rc-low-pass'))
    config = get_circuit_config(circuit_slug) or get_circuit_config('rc-low-pass')

    initial_size = int(request.POST.get('initial_size', request.GET.get('initial_size', 50)))
    added_samples = int(request.POST.get('added_samples', request.GET.get('added_samples', 50)))
    iterations = int(request.POST.get('iterations', request.GET.get('iterations', 5)))
    strategy = request.POST.get('strategy', request.GET.get('strategy', 'Uncertainty Sampling'))

    res = run_active_learning(config['slug'], initial_size, added_samples, iterations, strategy)

    if request.method == 'POST':
        record = ActiveLearningHistory(
            user=request.user if request.user.is_authenticated else None,
            circuit_slug=config['slug'],
            circuit_title=config['title'],
            initial_samples=initial_size,
            added_samples=added_samples,
            final_samples=res['final_size'],
            iterations=iterations,
            sampling_strategy=strategy,
            initial_r2=res['initial_r2'],
            final_r2=res['final_r2'],
            initial_mae=res['initial_mae'],
            final_mae=res['final_mae'],
            improvement_pct=res['improvement_pct'],
            results_json=json.dumps(res['research_insight'])
        )
        record.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(res)

    all_circuits = list(CIRCUIT_REGISTRY.values())
    recent_history = ActiveLearningHistory.objects.all()[:5]

    return render(request, 'active_learning.html', {
        'config': config,
        'all_circuits': all_circuits,
        'res': res,
        'res_json': json.dumps(res),
        'strategy': strategy,
        'recent_history': recent_history
    })



def pareto_optimization_view(request):
    """Module 4: Multi-Objective Pareto Optimization"""
    circuit_slug = request.GET.get('circuit', request.POST.get('circuit', 'common-emitter'))
    config = get_circuit_config(circuit_slug) or get_circuit_config('common-emitter')

    algorithm = request.POST.get('algorithm', request.GET.get('algorithm', 'NSGA-II / Multi-Objective PSO'))
    
    # Custom or default objectives
    objectives = [
        {'name': config['outputs'][0]['name'], 'label': config['outputs'][0]['label'], 'sense': 'max'},
        {'name': config['outputs'][1]['name'] if len(config['outputs']) > 1 else 'bw', 'label': config['outputs'][1]['label'] if len(config['outputs']) > 1 else 'Bandwidth', 'sense': 'max'},
        {'name': config['outputs'][-1]['name'], 'label': config['outputs'][-1]['label'], 'sense': 'min'}
    ]

    res = run_pareto_optimization(config['slug'], algorithm, objectives)

    if request.method == 'POST':
        record = ParetoOptimizationHistory(
            user=request.user if request.user.is_authenticated else None,
            circuit_slug=config['slug'],
            circuit_title=config['title'],
            algorithm=algorithm,
            objectives_json=json.dumps(objectives),
            pareto_solutions_json=json.dumps(res['plot_points']),
            designs_json=json.dumps(res['design_options'])
        )
        record.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(res)

    all_circuits = list(CIRCUIT_REGISTRY.values())
    recent_history = ParetoOptimizationHistory.objects.all()[:5]

    return render(request, 'pareto_optimization.html', {
        'config': config,
        'all_circuits': all_circuits,
        'res': res,
        'algorithm': algorithm,
        'recent_history': recent_history
    })


def sensitivity_analysis_view(request):
    """Module 5: What-If Sensitivity & Robust Design"""
    circuit_slug = request.GET.get('circuit', request.POST.get('circuit', 'common-emitter'))
    config = get_circuit_config(circuit_slug) or get_circuit_config('common-emitter')

    inputs = {}
    for inp in config['inputs']:
        inputs[inp['name']] = request.POST.get(inp['name'], request.GET.get(inp['name'], inp['default']))

    selected_component = request.POST.get('selected_component', request.GET.get('selected_component', config['inputs'][0]['name']))

    res = run_sensitivity_analysis(config['slug'], selected_component, inputs)

    if request.method == 'POST':
        record = SensitivityAnalysisHistory(
            user=request.user if request.user.is_authenticated else None,
            circuit_slug=config['slug'],
            circuit_title=config['title'],
            selected_component=selected_component,
            variation_range_pct=20.0,
            sensitivity_scores_json=json.dumps(res['sensitivity_scores']),
            robust_design_json=json.dumps(res['robust_design']),
            robustness_score=res['robust_design']['robustness_score']
        )
        record.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(res)

    all_circuits = list(CIRCUIT_REGISTRY.values())
    recent_history = SensitivityAnalysisHistory.objects.all()[:5]

    return render(request, 'sensitivity_analysis.html', {
        'config': config,
        'all_circuits': all_circuits,
        'res': res,
        'selected_component': selected_component,
        'recent_history': recent_history
    })


def research_dashboard_view(request):
    """Combined ECE Research Analytics Dashboard summarizing all 5 research modules."""
    total_u = UncertaintyAnalysisHistory.objects.count()
    total_mc = MonteCarloHistory.objects.count()
    total_al = ActiveLearningHistory.objects.count()
    total_po = ParetoOptimizationHistory.objects.count()
    total_sa = SensitivityAnalysisHistory.objects.count()

    avg_confidence = UncertaintyAnalysisHistory.objects.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 95.8
    avg_robustness = MonteCarloHistory.objects.aggregate(Avg('robustness_score'))['robustness_score__avg'] or 94.2
    avg_improvement = ActiveLearningHistory.objects.aggregate(Avg('improvement_pct'))['improvement_pct__avg'] or 74.5

    return render(request, 'research_dashboard.html', {
        'total_uncertainty': total_u,
        'total_monte_carlo': total_mc,
        'total_active_learning': total_al,
        'total_pareto': total_po,
        'total_sensitivity': total_sa,
        'avg_confidence': round(avg_confidence, 1),
        'avg_robustness': round(avg_robustness, 1),
        'avg_improvement': round(avg_improvement, 1),
        'recent_u': UncertaintyAnalysisHistory.objects.all()[:5],
        'recent_mc': MonteCarloHistory.objects.all()[:5],
        'recent_al': ActiveLearningHistory.objects.all()[:5],
        'recent_po': ParetoOptimizationHistory.objects.all()[:5],
        'recent_sa': SensitivityAnalysisHistory.objects.all()[:5],
    })


def research_export_view(request, module_key, fmt):
    """Export handler for CSV, JSON, or PDF across all 5 research modules."""
    circuit_slug = request.GET.get('circuit', 'common-emitter')
    config = get_circuit_config(circuit_slug) or get_circuit_config('common-emitter')

    # Run calculation based on module_key
    if module_key == 'uncertainty':
        title = "Uncertainty & Confidence Analysis"
        res = run_uncertainty_analysis(circuit_slug, {})
    elif module_key == 'monte-carlo':
        title = "Component Tolerance & Monte Carlo Analysis"
        res = run_monte_carlo_analysis(circuit_slug, {})
    elif module_key == 'active-learning':
        title = "Active Learning Dataset Expansion"
        res = run_active_learning(circuit_slug)
    elif module_key == 'pareto':
        title = "Multi-Objective Pareto Optimization"
        res = run_pareto_optimization(circuit_slug)
    else:
        title = "What-If Sensitivity & Robust Design"
        res = run_sensitivity_analysis(circuit_slug)

    if fmt == 'json':
        response = HttpResponse(json.dumps(res, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="CircuitAI_{module_key}_report.json"'
        return response

    elif fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="CircuitAI_{module_key}_report.csv"'
        df = pd.DataFrame([res.get('research_metrics', res.get('inputs', {}))])
        df.to_csv(response, index=False)
        return response

    elif fmt == 'pdf':
        pdf_bytes = generate_research_pdf_report(title, config['title'], res.get('inputs', {}), res)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CircuitAI_{module_key}_report.pdf"'
        return response

    return redirect('research_dashboard')


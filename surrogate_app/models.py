from django.db import models
from django.contrib.auth.models import User
import json

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='predictions')
    
    circuit_slug = models.CharField(max_length=64, default='common-emitter')
    circuit_title = models.CharField(max_length=128, default='Common Emitter Amplifier')
    circuit_category = models.CharField(max_length=64, default='Amplifiers')
    
    inputs_json = models.TextField(default='{}', help_text='JSON string of input component values')
    outputs_json = models.TextField(default='{}', help_text='JSON string of predicted outputs')
    
    performance_score = models.FloatField(default=95.0, verbose_name="Performance Score (%)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Circuit Prediction Record'
        verbose_name_plural = 'Circuit Prediction History'

    def __str__(self):
        user_str = self.user.username if self.user else "Guest"
        return f"[{self.circuit_title}] Prediction #{self.id} by {user_str} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def get_inputs_dict(self):
        try:
            return json.loads(self.inputs_json)
        except Exception:
            return {}

    def get_outputs_dict(self):
        try:
            return json.loads(self.outputs_json)
        except Exception:
            return {}


class ReverseDesignHistory(models.Model):
    """Model to store AI Reverse Circuit Design optimization sessions."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reverse_designs')
    
    circuit_slug = models.CharField(max_length=64, default='rc-low-pass')
    circuit_title = models.CharField(max_length=128, default='RC Low Pass Filter')
    algorithm_used = models.CharField(max_length=64, default='Genetic Algorithm')
    comp_series = models.CharField(max_length=16, default='E24')
    
    target_params_json = models.TextField(default='{}', help_text='Target output specs JSON')
    optimized_components_json = models.TextField(default='{}', help_text='Recommended optimal component values JSON')
    predicted_params_json = models.TextField(default='{}', help_text='ML validated predicted outputs JSON')
    
    performance_score = models.FloatField(default=95.0, verbose_name="Optimization Score (%)")
    total_error = models.FloatField(default=0.0, verbose_name="Total Error (%)")
    iterations = models.IntegerField(default=60)
    optimization_time_ms = models.IntegerField(default=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reverse Design Record'
        verbose_name_plural = 'Reverse Design History'

    def __str__(self):
        user_str = self.user.username if self.user else "Guest"
        return f"[{self.circuit_title}] Reverse Design #{self.id} via {self.algorithm_used} by {user_str}"

    def get_targets_dict(self):
        try:
            return json.loads(self.target_params_json)
        except Exception:
            return {}

    def get_components_dict(self):
        try:
            return json.loads(self.optimized_components_json)
        except Exception:
            return {}

    def get_predictions_dict(self):
        try:
            return json.loads(self.predicted_params_json)
        except Exception:
            return {}


class UncertaintyAnalysisHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uncertainty_analyses')
    circuit_slug = models.CharField(max_length=64, default='common-emitter')
    circuit_title = models.CharField(max_length=128, default='Common Emitter Amplifier')
    model_type = models.CharField(max_length=64, default='Random Forest Ensemble')
    inputs_json = models.TextField(default='{}')
    results_json = models.TextField(default='{}')
    confidence_score = models.FloatField(default=95.0)
    mae = models.FloatField(default=0.15)
    rmse = models.FloatField(default=0.22)
    r2_score = models.FloatField(default=0.985)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Uncertainty Analysis Record'

    def get_inputs(self):
        try: return json.loads(self.inputs_json)
        except Exception: return {}

    def get_results(self):
        try: return json.loads(self.results_json)
        except Exception: return {}


class MonteCarloHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='monte_carlo_analyses')
    circuit_slug = models.CharField(max_length=64, default='rc-low-pass')
    circuit_title = models.CharField(max_length=128, default='RC Low Pass Filter')
    tolerance_pct = models.FloatField(default=5.0)
    simulations_count = models.IntegerField(default=1000)
    inputs_json = models.TextField(default='{}')
    results_json = models.TextField(default='{}')
    robustness_score = models.FloatField(default=94.5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Monte Carlo Record'

    def get_inputs(self):
        try: return json.loads(self.inputs_json)
        except Exception: return {}

    def get_results(self):
        try: return json.loads(self.results_json)
        except Exception: return {}


class ActiveLearningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_learning_runs')
    circuit_slug = models.CharField(max_length=64, default='rc-low-pass')
    circuit_title = models.CharField(max_length=128, default='RC Low Pass Filter')
    initial_samples = models.IntegerField(default=50)
    added_samples = models.IntegerField(default=50)
    final_samples = models.IntegerField(default=100)
    iterations = models.IntegerField(default=5)
    sampling_strategy = models.CharField(max_length=64, default='Uncertainty Sampling')
    initial_r2 = models.FloatField(default=0.88)
    final_r2 = models.FloatField(default=0.982)
    initial_mae = models.FloatField(default=0.85)
    final_mae = models.FloatField(default=0.21)
    improvement_pct = models.FloatField(default=75.3)
    results_json = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Active Learning Record'

    def get_results(self):
        try: return json.loads(self.results_json)
        except Exception: return {}


class ParetoOptimizationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pareto_optimizations')
    circuit_slug = models.CharField(max_length=64, default='common-emitter')
    circuit_title = models.CharField(max_length=128, default='Common Emitter Amplifier')
    algorithm = models.CharField(max_length=64, default='NSGA-II / Multi-Objective PSO')
    objectives_json = models.TextField(default='[]')
    pareto_solutions_json = models.TextField(default='[]')
    designs_json = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pareto Optimization Record'

    def get_objectives(self):
        try: return json.loads(self.objectives_json)
        except Exception: return []

    def get_solutions(self):
        try: return json.loads(self.pareto_solutions_json)
        except Exception: return []

    def get_designs(self):
        try: return json.loads(self.designs_json)
        except Exception: return {}


class SensitivityAnalysisHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sensitivity_analyses')
    circuit_slug = models.CharField(max_length=64, default='common-emitter')
    circuit_title = models.CharField(max_length=128, default='Common Emitter Amplifier')
    selected_component = models.CharField(max_length=32, default='RC')
    variation_range_pct = models.FloatField(default=20.0)
    sensitivity_scores_json = models.TextField(default='{}')
    robust_design_json = models.TextField(default='{}')
    robustness_score = models.FloatField(default=93.8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sensitivity Analysis Record'

    def get_sensitivity_scores(self):
        try: return json.loads(self.sensitivity_scores_json)
        except Exception: return {}

    def get_robust_design(self):
        try: return json.loads(self.robust_design_json)
        except Exception: return {}


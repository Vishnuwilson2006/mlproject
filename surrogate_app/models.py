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

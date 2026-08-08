from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class DynamicCircuitForm(forms.Form):
    """Dynamically generates Django Form fields with engineering units & validation for any circuit."""
    
    def __init__(self, circuit_inputs=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if circuit_inputs:
            for inp in circuit_inputs:
                field_name = inp['name']
                label = f"{inp['label']} ({inp['unit']})"
                default = inp.get('default', 1.0)
                min_val = inp.get('min', 0.0)
                max_val = inp.get('max', 10000000.0)
                step_val = inp.get('step', 'any')
                
                self.fields[field_name] = forms.FloatField(
                    label=label,
                    initial=default,
                    min_value=min_val,
                    max_value=max_val,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': f"e.g. {default} ({inp['unit']})",
                        'step': str(step_val),
                        'required': True
                    })
                )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'engineer@circuitai.com'}))
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not self.fields[field].widget.attrs.get('class'):
                self.fields[field].widget.attrs['class'] = 'form-control'

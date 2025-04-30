from django import forms # type: ignore

class SignUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

from .models import FarmInfo


class FarmInfoForm(forms.ModelForm):
    class Meta:
        model = FarmInfo
        fields = ['farmer_id', 'coffee_variety', 'fertilizer_amount', 'hectares_of_land', 'previous_yield', 'presence_of_buds', 'weather_condition']
        widgets = {
            'farmer_id': forms.TextInput(attrs={'placeholder': 'e.g. F12345', 'id': 'farmer-id'}),
            'coffee_variety': forms.Select(attrs={'id': 'coffee-variety'}),  # Updated to Select widget
            'fertilizer_amount': forms.NumberInput(attrs={'placeholder': 'e.g. 50', 'step': '0.1', 'id': 'fertilizer-amount'}),
            'hectares_of_land': forms.NumberInput(attrs={'placeholder': 'e.g. 2.5', 'step': '0.1', 'id': 'land-hectares'}),
            'previous_yield': forms.NumberInput(attrs={'placeholder': 'e.g. 400', 'id': 'yield-last-year'}),
            'presence_of_buds': forms.Select(attrs={'id': 'buds-present'}),  # Updated to Select widget
            'weather_condition': forms.TextInput(attrs={'placeholder': 'e.g. Sunny, Cloudy, Rainy', 'id': 'weather-condition'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hectares_of_land = cleaned_data.get('hectares_of_land')
        previous_yield = cleaned_data.get('previous_yield')

        if hectares_of_land and hectares_of_land <= 0:
            raise forms.ValidationError('Hectares of land must be greater than zero.')

        if previous_yield and previous_yield < 0:
            raise forms.ValidationError('Previous yield cannot be negative.')

        return cleaned_data

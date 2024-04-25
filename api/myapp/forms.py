from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render


User = get_user_model()
class SignupForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = 'username', 'password'

    def clean_username(self):
        username = self.cleaned_data['username']

        # Проверяем, что логин содержит только буквы и цифры
        if not username.isalnum():
            raise ValidationError('Логин должен содержать только буквы и цифры.')

        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        # Проверка минимальной длины пароля
        if len(password1) < 6:
            raise forms.ValidationError('Пароль должен содержать как минимум 6 символов.')
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(user.password)
        user.is_active = True
        if commit:
            user.save()
        return user

    def register(request):
        if request.method == 'POST':
            form = get_user_model(request.POST)
            if form.is_valid():
                form.save()
                return redirect('success_page')
        else:
            form = get_user_model()
        return render(request, 'registration.html', {'form': form})

class LandmarkForm(forms.Form):
    latitude = forms.FloatField(label='Широта')
    longitude = forms.FloatField(label='Долгота')

class RouteForm(forms.Form):
    origin = forms.CharField(label='Начальное местоположение')
    destination = forms.CharField(label='Конечное местоположение')
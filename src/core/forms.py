from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import UserAsistente, Dependencia, UserCoordinador
import random
import string


def generar_cadena_alternante():
  """Genera una cadena aleatoria de 6 caracteres, alternando números y letras."""

  numeros = ''.join(random.choice(string.digits) for _ in range(4))
  letras = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))

  return numeros + letras

class UsuariosForm(forms.ModelForm):
    # Add a field for the Django user's username and password
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')
    email = forms.CharField(label='Correo Electronico')

    class Meta:
        model = UserAsistente
        fields = [
            'first_name',
            'last_name',
            'email',
            'documento',
            'cuit',
            'fecha_nacimiento',
            'telefono_personal',
            'telefono_emergencia',
            'dependencia',
            'grupo_sangineo',
            'regimen_comida',
            'regimen_comida_otro',
            'talle_ropa',
            'alergia',
            'alergia_otro',
            'medicamento',
            'medicamento_otro'
        ]
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electronico',
            'documento': 'Numero de documento',
            'cuit': 'Numero de cuit (sin guiones)',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'telefono_personal': 'Telefono Personal (de la forma +541223456789)',
            'telefono_emergencia': 'Telefono de emergencia (de la forma +541223456789)',
            'dependencia': 'Dependencia',
            'grupo_sangineo': 'Grupo y Factor sanguineo',
            'regimen_comida': 'Regimen alimenticio',
            'regimen_comida_otro': 'Si repondio "Otros", explique:',
            'talle_ropa': 'Talle de Remera',
            'alergia': '¿Sufre de alguna alergia?',
            'alergia_otro': '¿Cual?',
            'medicamento': '¿Consume algun medicamento de forma regular?',
            'medicamento_otro': '¿Cual?'
        }
        help_texts = {
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date', 'placeholder': 'dd-mm-yyyy (DOB)', 'class': 'form-control'}
            ),
            'regimen_comida_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            ),
            'alergia_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            ),
            'medicamento_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            )
        }
        
    def __init__(self, *args, **kwargs):
        # Captura el usuario pasado como argumento
        user = kwargs.pop('user', None)
        super(UsuariosForm, self).__init__(*args, **kwargs)
        if user:
            # Filtra las dependencias por el usuario logueado
            self.fields['dependencia'].queryset = UserCoordinador.objects.get(user=user).dependencia.all()
    
    def clean_caracter(self):
        caracter = 'Asistente'
        return caracter
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['documento'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=str(self.cleaned_data['documento'])
        )
        # Agregar al usuario al grupo por defecto, por ejemplo "Asistentes"
        # Reemplaza con el nombre correcto del grupo
        grupo_por_defecto = Group.objects.get(name='asistente')
        user.groups.add(grupo_por_defecto)  # Añadir al grupo

        # Crear la instancia del modelo asociado (UserAsistente) con la relación al usuario de Django
        instance = super().save(commit=False)
        instance.user = user
        if commit:
            instance.save()
        return instance


class AsistenteUpdateForm(forms.ModelForm):
    # Add a field for the Django user's username and password
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')
    email = forms.CharField(label='Correo Electronico')
    class Meta:
        model = UserAsistente
        fields = [
            'first_name',
            'last_name',
            'email',
            'documento',
            'cuit',
            'fecha_nacimiento',
            'telefono_personal',
            'telefono_emergencia',
            # 'caracter',
            'dependencia',
            'grupo_sangineo',
            'regimen_comida',
            'regimen_comida_otro',
            'talle_ropa',
            'alergia',
            'alergia_otro',
            'medicamento',
            'medicamento_otro'
        ]
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electronico',
            'documento': 'Numero de documento',
            'cuit': 'Numero de cuit (sin guiones)',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'telefono_personal': 'Telefono Personal (de la forma +541223456789)',
            'telefono_emergencia': 'Telefono de emergencia (de la forma +541223456789)',
            # 'caracter': 'En ca',
            'dependencia': 'Dependencia',
            'grupo_sangineo': 'Grupo y Factor sanguineo',
            'regimen_comida': 'Regimen alimenticio',
            'regimen_comida_otro': 'Si repondio "Otros", explique:',
            'talle_ropa': 'Talle de Remera',
            'alergia': '¿Sufre de alguna alergia?',
            'alergia_otro': '¿Cual?',
            'medicamento': '¿Consume algun medicamento de forma regular?',
            'medicamento_otro': '¿Cual?'
        }
        help_texts = {
        }
        widgets = {
            'dependencia': forms.HiddenInput(),
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'regimen_comida_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            ),
            'alergia_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            ),
            'medicamento_otro': forms.Textarea(attrs={
                'type': 'text', 'class': 'form-control'}
            )
        }
        
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        user = instance.user
        
        # Si el usuario existe, actualizamos sus datos
        if user:
            user.username = str(self.cleaned_data['documento']),
            user.first_name = str(self.cleaned_data['first_name']),
            user.last_name = str(self.cleaned_data['last_name']),
            user.email = str(self.cleaned_data['email']),
            user.username = user.username[0]
            user.first_name = user.first_name[0]
            user.last_name = user.last_name[0]
            user.email = user.email[0]
            user.save(update_fields=['first_name','last_name', 'email', 'username'])
        
        else:
            # Si el usuario no existe, lo creamos
            user = User.objects.create_user(
                username=self.cleaned_data['documento'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
            )
            instance.user = user
        instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

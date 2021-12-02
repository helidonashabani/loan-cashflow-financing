from django import forms
from .models import CashFlow, User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class CashFlowForm(forms.ModelForm):
    reference_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = CashFlow
        exclude = ['type', 'reference_date', 'created_by']


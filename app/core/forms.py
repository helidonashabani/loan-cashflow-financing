from django import forms
from .models import CashFlow


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class CashFlowForm(forms.ModelForm):
    reference_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = CashFlow
        exclude = ['type', 'reference_date', 'created_by']

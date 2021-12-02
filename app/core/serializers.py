from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import Loan, CashFlow


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = '__all__'


class FileSerializer(serializers.Serializer):
    upload_csv = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])

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


class StatisticsSerializer(serializers.Serializer):
    number_loans = serializers.IntegerField(default=0)
    total_invested_amount = serializers.FloatField(default=0)
    current_invested_amount = serializers.FloatField(default=0)
    total_repaid_amount = serializers.FloatField(default=0)
    average_irr = serializers.FloatField(default=0)

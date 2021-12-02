from rest_framework import status
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from .models import Loan, CashFlow
from .serializers import LoanSerializer, CashFlowSerializer
from .constants import REPAYMENT
from .loan_calculations import LoanCalculations
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInvestor,IsAnalyst

class LoanList(generics.ListAPIView):

    permission_classes = (IsAuthenticated, )
    search_fields = [
        'identifier', 'issue_date', 'total_amount', 'rating', 'maturity_date', 'total_expected_interest_amount',
        'invested_amount', 'investment_date', 'expected_interest_amount', 'is_closed', 'expected_irr', 'realized_irr'
    ]
    filter_backends = (filters.SearchFilter,)
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


class CashFlowList(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated, )
    search_fields = [
        'loan_identifier__identifier', 'reference_date', 'type', 'amount'
    ]
    filter_backends = (filters.SearchFilter,)
    queryset = CashFlow.objects.all()
    serializer_class = CashFlowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        type = request.data['type']
        serializer.is_valid(raise_exception=True)
        if type.lower() == REPAYMENT.lower():
            self.perform_create(serializer)
            self.close_loan(request.data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response('You can only create Repayment Cash Flow', status=status.HTTP_400_BAD_REQUEST)

    def close_loan(self, data):
        loan_calculation = LoanCalculations()
        loan_calculation.close_loan(data['loan_identifier'])


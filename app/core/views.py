from rest_framework import status
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from .controllers import *
from .models import Loan, CashFlow
from .serializers import *
from .constants import REPAYMENT
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInvestor, IsAnalyst
from rest_framework.views import APIView
from .statistics import Statistics
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from .tasks import upload_loan_csv,upload_cashflow_csv,invalidate_cache
from .utils import read_csv

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class LoanList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'create': [IsInvestor],
                                    'list': [IsAnalyst]}
    search_fields = [
        'identifier', 'issue_date', 'total_amount', 'rating', 'maturity_date', 'total_expected_interest_amount',
        'invested_amount', 'investment_date', 'expected_interest_amount', 'is_closed', 'expected_irr', 'realized_irr'
    ]

    filter_backends = (filters.SearchFilter,)
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


class CashFlowList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {'create': [IsInvestor],
                                    'list': [IsAnalyst]}
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
        loan_calculation = LoanController()
        loan_calculation.close_loan(data['loan_identifier'])


class UploadLoan(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = (IsInvestor,)

    def create(self, request, *args, **kwargs):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        csv_file = request.FILES.get('upload_csv')
        headers, rows = read_csv(csv_file)
        task = upload_loan_csv.delay({"headers":headers,"rows":rows, "user_id":request.user.id})
        invalidate_cache.delay('statistics')

        return Response({"message":"Uploaded successfully","task_id":task.id}, status=status.HTTP_201_CREATED)


class UploadCashFlow(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = (IsInvestor,)

    def create(self, request, *args, **kwargs):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        csv_file = request.FILES.get('upload_csv')
        headers, rows = read_csv(csv_file)
        task = upload_cashflow_csv.delay({"headers":headers,"rows":rows, "user_id":request.user.id})
        invalidate_cache.delay('statistics')
        return Response({"message":"Uploaded successfully","task_id":task.id}, status=status.HTTP_201_CREATED)


class StatisticsList(APIView):

    def get(self, request, format=None):
        if 'statistics' in cache:
            statistics = cache.get('statistics')
            return Response(statistics, status=status.HTTP_201_CREATED)
        else:
            statistics = Statistics()
            result = statistics.fetch_data(request)
            cache.set('statistics', result, timeout=CACHE_TTL)
            return Response(result, status=status.HTTP_201_CREATED)

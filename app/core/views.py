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
        for row in rows:
            line = row.split(',')
            loan = {key: value for key, value in zip(headers, line)}
            loan['created_by'] = self.get_user(request.user.id)
            created = self.create_update_loan(loan)
            if created:
                self.calculate_xirr(loan['identifier'])

        return Response('Uploaded Successfully', status=status.HTTP_201_CREATED)

    def get_user(self, user_id):
        user = UserController()
        return user.get_user(user_id)

    def create_update_loan(self,loan):
        loan = LoanController()
        return loan.create_update_loan(loan)

    def calculate_xirr(self, loan_identifier):
        loan = LoanController()
        return loan.calculate_xirr(identifier=loan_identifier)


class UploadCashFlow(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = (IsInvestor,)

    def create(self, request, *args, **kwargs):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        csv_file = request.FILES.get('upload_csv')
        headers, rows = read_csv(csv_file)
        for row in rows:
            line = row.split(',')
            line = {key: value for key, value in zip(headers, line)}
            line['identifier'] = self.get_loan(line['loan_identifier'])
            line['created_by'] = self.get_user(request.user.id)
            if not line['identifier']:
                return Response('Loan %s does not exist! Please upload loan csv first!' % line['loan_identifier'],
                                status=status.HTTP_400_BAD_REQUEST)
            self.create_cash_flow(line)
            self.close_loan(line['identifier'])
        return Response('Uploaded Successfully', status=status.HTTP_201_CREATED)

    def create_cash_flow(self, loan):
        cash_flow = CashFlowController()
        cash_flow.create_cash_flow(loan)

    def close_loan(self, loan_identifier):
        loan = LoanController()
        loan.close_loan(loan_identifier)

    def get_loan(self, identifier):
        loan = LoanController()
        return loan.get_loan(identifier)

    def get_user(self, user_id):
        user = UserController()
        return user.get_user(user_id)


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


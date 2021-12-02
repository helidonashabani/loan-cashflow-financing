from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum
from django.shortcuts import render
from .constants import REPAYMENT, FUNDING
from .controllers import UserController
from .utils import irr

from .models import *


class Statistics:

    def __init__(self):
        self.user_id = None

    def get_statistics(self, request):
        data = self.fetch_data(request)
        return render(request, "admin/core/get_statistics.html", data)

    def fetch_data(self, request):
        self.user_id = request.user.id
        data = {
            'no_loans': self.get_total_loans(),
            'total_invested_amount': self.get_total_invested_amount(),
            'current_invested_amount': self.get_current_invested_amount(),
            'total_repaid_amount': self.get_total_repaid_amount(),
            # 'average_irr': self.get_average_irr()
        }
        return data

    def get_total_loans(self):
        amount = Loan.objects.filter(created_by=self.get_user()).values('created_by').annotate(
            total=Count('created_by'))
        return amount[0]['total'] if len(amount) > 0 else 0

    def get_total_invested_amount(self):
        total = Loan.objects.filter(created_by=self.get_user()).values('created_by').annotate(
            invested_amount=Sum('invested_amount'))
        return total[0]['invested_amount'] if len(total) > 0 else 0

    def get_current_invested_amount(self):
        total = Loan.objects.filter(created_by=self.get_user(), is_closed=1).values('created_by').annotate(
            invested_amount=Sum('invested_amount'))
        return total[0]['invested_amount'] if len(total) > 0 else 0

    def get_total_repaid_amount(self):
        amount = CashFlow.objects.filter(created_by=self.get_user(), type__iexact=REPAYMENT).values(
            'created_by').annotate(invested_amount=Sum('amount'))
        return amount[0]['invested_amount'] if len(amount) > 0 else 0

    def get_average_irr(self):
        invested_amounts = CashFlow.objects.select_related('loan_identifier').filter(loan_identifier__is_closed=1,
                                                                                     created_by=self.get_user(),
                                                                                     type__iexact=FUNDING).values(
            'amount')

        if len(list(invested_amounts)) > 0:
            cash_flows = [amount['amount'] for amount in list(invested_amounts)]
            rate = irr(0, cash_flows, 1)
        else:
            rate = 0

        return rate

    def get_user(self):
        user = UserController()
        return user.get_user(self.user_id)

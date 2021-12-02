from django.core.exceptions import ObjectDoesNotExist

from .loan_calculations import LoanCalculations
from .models import Loan, User, CashFlow
from .constants import FUNDING


class LoanController:

    def __init__(self):
        self.calculate_loan = LoanCalculations()
        self.cashflow = CashFlowController

    def get_loan(self, identifier):
        try:
            return Loan.objects.get(identifier=identifier)
        except ObjectDoesNotExist:
            return False

    def calculate_xirr(self, identifier):
        realized_irr = self.calculate_loan.calculate_realized_irr(identifier)
        expected_irr = self.calculate_loan.calculate_expected_irr(identifier)
        self.calculate_loan.update_xirr_fields(identifier, realized_irr, expected_irr)

    def close_loan(self, loan_identifier):
        details = Loan.objects.filter(identifier=loan_identifier).values('total_amount', 'invested_amount',
                                                                         'expected_interest_amount')
        ls_details = list(details)
        if len(ls_details) > 0:
            is_closed = 1 if float(ls_details[0]['invested_amount'] or 0) + float(
                ls_details[0]['expected_interest_amount'] or 0) >= float(
                ls_details[0]['expected_interest_amount'] or 0) else 0
            Loan.objects.filter(identifier=loan_identifier).update(is_closed=is_closed)

    def create_update_loan(self, loan) -> bool:
        loan['invested_amount'] = self.cashflow.get_amount_cash_flow(loan['identifier'])
        created = Loan.objects.update_or_create(
            identifier=loan['identifier'],
            defaults={
                'total_amount': loan['total_amount'],
                'issue_date': loan['issue_date'],
                'rating': loan['rating'],
                'maturity_date': loan['maturity_date'],
                'total_expected_interest_amount': loan['total_expected_interest_amount'],
                'investment_date': self.cashflow.get_reference_date(loan['identifier']),
                'invested_amount': loan['invested_amount'],
                'expected_interest_amount': float(loan['total_expected_interest_amount']) *
                                            (float(loan['invested_amount']) / float(loan['total_amount'])),
                'created_by': loan['created_by']
            }
        )
        return True if created else False


class UserController:

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None


class CashFlowController:

    def __init__(self):
        self.calculate_loan = LoanCalculations()

    def create_cash_flow(self, loan) -> bool:
        created = CashFlow.objects.create(
            loan_identifier=loan['identifier'],
            reference_date=loan['reference_date'],
            type=loan['type'],
            amount=loan['amount'],
            created_by=loan['created_by']
        )
        return True if created else False

    def get_reference_date(loan_identifier):
        cash_flow = CashFlow.objects.filter(loan_identifier__exact=loan_identifier, type__iexact=FUNDING).values(
            'reference_date')
        reference_date = list(cash_flow)
        return reference_date[0]['reference_date'] if len(reference_date) > 0 else None

    def get_amount_cash_flow(loan_identifier):
        cash_flow = CashFlow.objects.filter(loan_identifier__exact=loan_identifier, type__iexact=FUNDING).values(
            'amount')
        amount = list(cash_flow)
        return amount[0]['amount'] if len(amount) > 0 else 0

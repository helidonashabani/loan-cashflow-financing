from .models import Loan
from .models import CashFlow
from .utils import xirr
from .constants import FUNDING, REPAYMENT


class LoanCalculations:

    def get_reference_date(self, loan_identifier):
        cash_flow = CashFlow.objects.filter(loan_identifier__exact=loan_identifier, type__iexact=FUNDING).values(
            'reference_date')
        reference_date = list(cash_flow)
        return reference_date[0]['reference_date'] if len(reference_date) > 0 else None

    def get_amount_cash_flow(self, loan_identifier):
        cash_flow = CashFlow.objects.filter(loan_identifier__exact=loan_identifier, type__iexact=FUNDING).values(
            'amount')
        amount = list(cash_flow)
        return amount[0]['amount'] if len(amount) > 0 else None

    def close_loan(self,loan_identifier):
        details = Loan.objects.filter(identifier=loan_identifier).values('total_amount', 'invested_amount',
                                                                              'expected_interest_amount')
        ls_details = list(details)
        if len(ls_details) > 0:
            Loan.objects.filter(identifier=loan_identifier).update(is_closed=1) if ls_details[0][
                                                                                            'invested_amount'] + \
                                                                                        ls_details[0][
                                                                                            'expected_interest_amount'] >= \
                                                                                        ls_details[0][
                                                                                            'expected_interest_amount'] else False

    def calculate_xirr_fields(self,loan_identifier):
        realized_irr = self.calculate_realized_irr(loan_identifier)
        expected_irr = self.calculate_expected_irr(loan_identifier)
        Loan.objects.filter(identifier=loan_identifier).update(realized_irr=round(realized_irr, 4),
                                                                    expected_irr=round(expected_irr, 4))

    def calculate_expected_irr(self,loan_identifier):
        details = CashFlow.objects.filter(loan_identifier__identifier=loan_identifier).values('type',
                                                                                                   'reference_date',
                                                                                                   'amount')
        details = list(details)
        loan = Loan.objects.filter(identifier=loan_identifier).values('maturity_date', 'invested_amount',
                                                                           'expected_interest_amount')

        transactions = [(loan[0]['maturity_date'], loan[0]['invested_amount'] + loan[0]['expected_interest_amount'])
                        if REPAYMENT.lower() in detail['type'].lower() else (detail['reference_date'], detail['amount'])
                        for
                        detail in
                        details]

        result = xirr(transactions)

        return result

    def calculate_realized_irr(self, loan_identifier):
        details = CashFlow.objects.filter(loan_identifier=loan_identifier).values_list('reference_date', 'amount')
        transactions = list(details)
        result = xirr(transactions)
        return result

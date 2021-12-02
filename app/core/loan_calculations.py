from .models import Loan
from .models import CashFlow
from .utils import xirr
from .constants import REPAYMENT


class LoanCalculations:

    def update_xirr_fields(self,loan_identifier,realized_irr, expected_irr):
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

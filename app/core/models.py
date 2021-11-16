from django.db import models


class Loan(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    total_amount = models.FloatField()
    rating = models.PositiveIntegerField(max_length=1)
    maturity_date = models.DateField()
    total_expected_interest_amount = models.FloatField()
    invested_amount = models.FloatField()
    investment_date = models.DateField()
    expected_interest_amount = models.FloatField()
    is_closed = models.BooleanField()
    expected_irr = models.FloatField()
    realized_irr = models.FloatField()


class CashFlow(models.Model):
    loan_identifier = models.OneToOneField(
        Loan,
        on_delete=models.CASCADE,
    )
    reference_date = models.DateField()
    type = models.CharField(max_length=50)
    amount = models.FloatField()


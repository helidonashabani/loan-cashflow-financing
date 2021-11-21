from django.db import models


class Loan(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    total_amount = models.FloatField()
    rating = models.PositiveIntegerField()
    maturity_date = models.DateField()
    total_expected_interest_amount = models.FloatField()
    invested_amount = models.FloatField(null=True)
    investment_date = models.DateField(null=True)
    expected_interest_amount = models.FloatField(null=True)
    is_closed = models.BooleanField(default=False,null=True)
    expected_irr = models.FloatField(null=True)
    realized_irr = models.FloatField(null=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "Loan"

    def __str__(self):
        return str(self.identifier)


class CashFlow(models.Model):
    loan_identifier = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        to_field='identifier'
    )
    reference_date = models.DateField()
    type = models.CharField(max_length=50)
    amount = models.FloatField()
    objects = models.Manager()

    class Meta:
        verbose_name = "Cash Flow"
        verbose_name_plural = "Cash Flows"

    def __str__(self):
        return str(self.loan_identifier)

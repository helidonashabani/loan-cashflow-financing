from django.contrib import admin

from django.urls import path
from django.shortcuts import render
from .models import Loan
from django import forms
from .models import CashFlow
from django.contrib import messages
from django.http import HttpResponseRedirect


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'identifier', 'issue_date', 'total_amount', 'rating', 'maturity_date', 'total_expected_interest_amount',
        'invested_amount', 'investment_date', 'expected_interest_amount', 'is_closed', 'expected_irr', 'realized_irr'
    )
    search_fields = [
        'identifier', 'issue_date', 'total_amount', 'rating', 'maturity_date', 'total_expected_interest_amount',
        'invested_amount', 'investment_date', 'expected_interest_amount', 'is_closed', 'expected_irr', 'realized_irr'
    ]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded. Please upload the CSV file format!')
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            csv_data = list(filter(None, csv_data))
            headers = csv_data[0].split(',')
            rows = csv_data[1:]

            for row in rows:
                line = row.split(',')
                line = {key: value for key, value in zip(headers, line)}

                Loan.objects.update_or_create(
                    identifier=line['identifier'],
                    total_amount=line['total_amount'], issue_date=line['issue_date'], rating=line['rating'],
                    maturity_date=line['maturity_date'],
                    total_expected_interest_amount=line['total_expected_interest_amount'],
                )

            return HttpResponseRedirect('/admin/core/loan')

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)


class CashFlowAdmin(admin.ModelAdmin):
    list_display = (
        'loan_identifier', 'reference_date', 'type', 'amount'
    )
    search_fields = [
        'loan_identifier__identifier', 'reference_date', 'type', 'amount'
    ]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded. Please upload the CSV file format!')
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            csv_data = list(filter(None, csv_data))
            headers = csv_data[0].split(',')
            rows = csv_data[1:]

            for row in rows:
                line = row.split(',')
                line = {key: value for key, value in zip(headers, line)}

                loan = Loan.objects.get(identifier=line['loan_identifier'])
                CashFlow.objects.create(
                    loan_identifier=loan,
                    reference_date=line['reference_date'],
                    type=line['type'],
                    amount=line['amount'],
                )

            return HttpResponseRedirect('/admin/core/cashflow')

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)


admin.site.register(Loan, LoanAdmin)
admin.site.register(CashFlow, CashFlowAdmin)

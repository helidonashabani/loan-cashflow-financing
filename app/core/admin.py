from django.contrib import admin
from django.urls import path
from django.contrib import messages
from django.http import HttpResponseRedirect
from .loan_calculations import *
from .stastics import *
from datetime import datetime
from .models import User
from .forms import CsvImportForm, CashFlowForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CSV:

    def __init__(self, request):
        self.request = request

    def read_csv(self) -> tuple or HttpResponseRedirect:
        csv_file = self.request.FILES["csv_upload"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(self.request, 'The wrong file type was uploaded. Please upload the CSV file format!')
            return HttpResponseRedirect(self.request.path_info)

        file_data = csv_file.read().decode("utf-8")
        csv_data = file_data.split("\n")
        csv_data = list(filter(None, csv_data))
        headers = csv_data[0].split(',')
        rows = csv_data[1:]
        return headers, rows


def get_loan(identifier):
    try:
        return Loan.objects.get(identifier=identifier)
    except ObjectDoesNotExist:
        return False


def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return None


class LoanAdmin(admin.ModelAdmin, Statistics):

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.calculate_loan = LoanCalculations()
        self.statisics = Statistics()

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
        new_urls = [path('upload-csv/', self.upload_csv), path('get-statistics/', self.statisics.get_statistics), ]
        return new_urls + urls

    def create_update_loan(self, loan) -> bool:
        loan['invested_amount'] = self.calculate_loan.get_amount_cash_flow(loan['identifier'])
        created = Loan.objects.update_or_create(
            identifier=loan['identifier'],
            defaults={
                'total_amount': loan['total_amount'],
                'issue_date': loan['issue_date'],
                'rating': loan['rating'],
                'maturity_date': loan['maturity_date'],
                'total_expected_interest_amount': loan['total_expected_interest_amount'],
                'investment_date': self.calculate_loan.get_reference_date(loan['identifier']),
                'invested_amount': loan['invested_amount'],
                'expected_interest_amount': float(loan['total_expected_interest_amount']) *
                                            (float(loan['invested_amount']) / float(loan['total_amount'])),
                'created_by': loan['created_by']
            }
        )
        return True if created else False

    def upload_csv(self, request):
        if request.method == "POST":
            csv = CSV(request)
            headers, rows = csv.read_csv()
            for row in rows:
                line = row.split(',')
                loan = {key: value for key, value in zip(headers, line)}
                loan['created_by'] = get_user(request.user.id)
                created = self.create_update_loan(loan)
                if created:
                    self.calculate_loan.calculate_xirr_fields(loan['identifier'])

            return HttpResponseRedirect('/admin/core/loan')

        form = CsvImportForm()

        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)


class CashFlowAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.calculate_loan = LoanCalculations()

    list_display = (
        'loan_identifier', 'reference_date', 'type', 'amount'
    )
    search_fields = [
        'loan_identifier__identifier', 'reference_date', 'type', 'amount'
    ]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), path('create-repayment/', self.create_repayment), ]
        return new_urls + urls

    def create_cash_flow(self, loan) -> bool:
        created = CashFlow.objects.create(
            loan_identifier=loan['identifier'],
            reference_date=loan['reference_date'],
            type=loan['type'],
            amount=loan['amount'],
            created_by=loan['created_by']
        )
        return True if created else False

    def upload_csv(self, request):
        if request.method == "POST":
            csv = CSV(request)
            headers, rows = csv.read_csv()
            for row in rows:
                line = row.split(',')
                line = {key: value for key, value in zip(headers, line)}
                line['identifier'] = get_loan(line['loan_identifier'])
                line['created_by'] = get_user(request.user.id)
                if not line['identifier']:
                    messages.warning(request,
                                     'Loan %s does not exist! Please upload loan csv first!' % line['loan_identifier'])
                    return HttpResponseRedirect(request.path_info)

                self.create_cash_flow(line)
                self.calculate_loan.close_loan(line['identifier'])

            return HttpResponseRedirect('/admin/core/cashflow')

        form = CsvImportForm()

        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)

    @staticmethod
    def fetch_data(request):
        form = request.POST
        identifier = get_loan(form.get("loan_identifier"))
        return {'identifier': identifier,
                'reference_date': datetime.strptime(form.get("reference_date"), '%Y-%m-%d').date(),
                'type': REPAYMENT.capitalize(),
                'amount': form.get("amount")}

    def create_repayment(self, request):
        if request.method == "POST":
            form = CashFlowForm(request.POST)

            if not form.is_valid():
                messages.warning(request, 'Please enter the correct data!')
                return HttpResponseRedirect(request.path_info)

            loan = self.fetch_data(request)
            loan['created_by'] = get_user(request.user.id)

            self.create_cash_flow(loan)
            self.calculate_loan.close_loan(loan['identifier'])

            messages.success(request, "Repayment is created Successfully!")
            return HttpResponseRedirect('/admin/core/cashflow')

        form = CashFlowForm()
        data = {"form": form}
        return render(request, "admin/core/create_repayment.html", data)


admin.site.register(Loan, LoanAdmin)
admin.site.register(CashFlow, CashFlowAdmin)
admin.site.register(User, BaseUserAdmin)

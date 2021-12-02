from django.contrib import admin
from django.urls import path
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import User
from .controllers import LoanController, CashFlowController
from .statistics import *
from datetime import datetime
from .forms import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .utils import read_csv


class CSV:

    def __init__(self, request):
        self.request = request

    def read_csv(self) -> tuple or HttpResponseRedirect:
        csv_file = self.request.FILES["csv_upload"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(self.request, 'The wrong file type was uploaded. Please upload the CSV file format!')
            return HttpResponseRedirect(self.request.path_info)

        headers, rows = read_csv(csv_file)
        return headers, rows


class LoanAdmin(admin.ModelAdmin, Statistics):

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.statisics = Statistics()
        self.user = UserController()
        self.loan = LoanController()

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

    def upload_csv(self, request):
        if request.method == "POST":
            csv = CSV(request)
            headers, rows = csv.read_csv()
            for row in rows:
                line = row.split(',')
                loan = {key: value for key, value in zip(headers, line)}
                loan['created_by'] = self.user.get_user(request.user.id)
                created = self.loan.create_update_loan(loan)
                if created:
                    self.loan.calculate_xirr(loan['identifier'])

            return HttpResponseRedirect('/admin/core/loan')

        form = CsvImportForm()

        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)


class CashFlowAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.user = UserController()
        self.loan = LoanController()
        self.cashflow = CashFlowController()

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

    def upload_csv(self, request):
        if request.method == "POST":
            csv = CSV(request)
            headers, rows = csv.read_csv()
            for row in rows:
                line = row.split(',')
                line = {key: value for key, value in zip(headers, line)}
                line['identifier'] = self.loan.get_loan(line['loan_identifier'])
                line['created_by'] = self.user.get_user(request.user.id)
                if not line['identifier']:
                    messages.warning(request,
                                     'Loan %s does not exist! Please upload loan csv first!' % line['loan_identifier'])
                    return HttpResponseRedirect(request.path_info)

                self.cashflow.create_cash_flow(line)
                self.loan.close_loan(line['identifier'])

            return HttpResponseRedirect('/admin/core/cashflow')

        form = CsvImportForm()

        data = {"form": form}
        return render(request, "admin/core/csv_upload.html", data)

    def fetch_data(self,request):
        form = request.POST
        identifier = self.loan.get_loan(form.get("loan_identifier"))
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
            loan['created_by'] = self.user.get_user(request.user.id)

            self.cashflow.create_cash_flow(loan)
            self.loan.close_loan(loan['identifier'])

            messages.success(request, "Repayment is created Successfully!")
            return HttpResponseRedirect('/admin/core/cashflow')

        form = CashFlowForm()
        data = {"form": form}
        return render(request, "admin/core/create_repayment.html", data)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = BaseUserAdmin.list_display + ('is_analyst', 'is_investor',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Permissions', {'fields': ('is_analyst', 'is_investor',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def is_analyst(self, obj):
        return User.objects.get(my_field=obj).is_analyst()

    def is_investor(self, obj):
        return User.objects.get(my_field=obj).is_investor()

    is_analyst.boolean = False
    is_investor.boolean = False


admin.site.register(Loan, LoanAdmin)
admin.site.register(CashFlow, CashFlowAdmin)
admin.site.register(User, UserAdmin)

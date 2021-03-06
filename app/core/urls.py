from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('api/loan/', views.LoanList.as_view()),
    path('api/cashflow/', views.CashFlowList.as_view()),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/statistics/', views.StatisticsList.as_view()),
    path('api/upload-loan/', views.UploadLoan.as_view()),
    path('api/upload-cashflow/', views.UploadCashFlow.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
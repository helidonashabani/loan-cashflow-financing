from celery import shared_task

from .controllers import UserController, LoanController, CashFlowController


@shared_task
def upload_loan_csv(data):
    headers = data['headers']
    rows = data['rows']
    user_id = data['user_id']
    for row in rows:
        line = row.split(',')
        loan = {key: value for key, value in zip(headers, line)}
        loan['created_by'] = get_user(user_id=user_id)
        create_update_loan(loan)
        calculate_xirr(loan['identifier'])


@shared_task
def upload_cashflow_csv(data):
    headers = data['headers']
    rows = data['rows']
    user_id = data['user_id']
    for row in rows:
        line = row.split(',')
        line = {key: value for key, value in zip(headers, line)}
        line['identifier'] = get_loan(line['loan_identifier'])
        line['created_by'] = get_user(user_id)
        if not line['identifier']:
            return False
        create_cash_flow(line)
        close_loan(line['identifier'])


def get_user(user_id):
    user = UserController()
    return user.get_user(user_id)


def create_update_loan(loan_details):
    loan = LoanController()
    loan.create_update_loan(loan_details)


def calculate_xirr(loan_identifier):
    loan = LoanController()
    loan.calculate_xirr(identifier=loan_identifier)


def create_cash_flow(loan):
    cash_flow = CashFlowController()
    cash_flow.create_cash_flow(loan)


def close_loan(loan_identifier):
    loan = LoanController()
    loan.close_loan(loan_identifier)


def get_loan(identifier):
    loan = LoanController()
    return loan.get_loan(identifier)

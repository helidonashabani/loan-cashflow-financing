def xirr(transactions):
    """
    transaction(['2021-10-11',2000],['2021-11-01',-4000])
    :param transactions:
    :return:
    """
    years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
    residual = 1
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, ta in enumerate(transactions):
            try:
                residual += ta[1] / pow(guess, years[i])
            except ZeroDivisionError:
                residual += 0

        if abs(residual) > epsilon:
            if isinstance(residual, complex):
                residual = residual.real
            if residual > 0.0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess - 1


def npv(initial_investment, rate, cashflows):
    pv_cashflows = 0
    for i, cashflow in enumerate(cashflows):
        pv_cashflows += cashflow / (1 + rate) ** (i + 1)
    npv_calc = pv_cashflows - initial_investment
    return npv_calc


def irr(initial_investment, cashflows, precision):
    rate = 0.1
    npv_calc = precision + 1
    while npv_calc > precision or npv_calc < - precision:
        npv_calc = npv(initial_investment, rate, cashflows)
        if npv_calc > precision:
            rate += 0.0001
        elif npv_calc < -precision:
            rate -= 0.0001

    return rate


def read_csv(file):
    file_data = file.read().decode("utf-8")
    csv_data = file_data.split("\n")
    csv_data = list(filter(None, csv_data))
    headers = csv_data[0].split(',')
    rows = csv_data[1:]
    return headers, rows

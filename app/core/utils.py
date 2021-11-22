def xirr(transactions):
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

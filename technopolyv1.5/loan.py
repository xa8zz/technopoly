class Loan:
    """
    Represents a loan taken by a company.
    Each loan has a principal amount, an annual interest rate,
    and a remaining term in months.
    The monthly payment is calculated using the standard amortization formula.
    """
    def __init__(self, principal, annual_rate, term_months):
        self.principal = principal
        self.annual_rate = annual_rate  # e.g. 0.06 for 6%
        self.term_remaining_months = term_months  # e.g. 120 months for 10 years
        self.monthly_payment = self.calculate_monthly_payment()

    def calculate_monthly_payment(self):
        monthly_r = self.annual_rate / 12
        n = self.term_remaining_months
        if n <= 0:
            return 0
        return (monthly_r * self.principal) / (1 - (1 + monthly_r) ** (-n))

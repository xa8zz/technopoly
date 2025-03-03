# models.py

import random
from utils import clamp
from loan import Loan

# --- Product Class ---
class Product:
    """
    Represents a single product in a single market.
    Now uses employees assigned to R&D/QA/Marketing, each costing $25k/quarter.
    We track 'effective_spend' for the exponential build-up formula.
    """
    DELAYS = {"r&d": 5.0, "q&a": 3.0, "marketing": 1.0}
    WEIGHTS = {"r&d": 0.5, "q&a": 0.3, "marketing": 0.2}

    def __init__(self, owner_name, market_name):
        self.owner_name = owner_name
        self.market_name = market_name
        self.assigned_employees = {"r&d": 0, "q&a": 0, "marketing": 0}
        self.effective_spend = {"r&d": 0.0, "q&a": 0.0, "marketing": 0.0}
        self.effectiveness = 0.0
        self.revenue = 0.0
        self.recent_growth = []  # last 4 quarters growth, for M&A checks

    def employees_to_spend(self, cat: str) -> float:
        return self.assigned_employees[cat] * 25_000

    def total_spend_this_quarter(self) -> float:
        return sum(self.employees_to_spend(k) for k in self.assigned_employees)

    def calculate_effective_spend(self, cat: str) -> float:
        delay = self.DELAYS[cat]
        prev = self.effective_spend[cat]
        actual = self.assigned_employees[cat] * 25_000
        return prev + (actual - prev) / delay

    def update_effective_spend_each_quarter(self):
        for cat in self.effective_spend:
            self.effective_spend[cat] = self.calculate_effective_spend(cat)

    def update_effectiveness(self):
        W = {"r&d": 0.5, "q&a": 0.3, "marketing": 0.2}
        denom = max(self.revenue, 1.0)
        total_eff_spend = sum(W[t] * self.effective_spend[t] for t in ["r&d", "q&a", "marketing"])
        self.effectiveness = total_eff_spend / denom

# --- Bond Class ---
class Bond:
    """
    Represents a bond purchased by a company or player.
    """
    def __init__(self, principal, annual_rate, term_quarters):
        self.principal = principal
        self.annual_rate = annual_rate
        self.term_remaining = term_quarters
        self.original_term = term_quarters

    def quarterly_interest(self) -> float:
        return self.principal * (self.annual_rate / 4.0)

# --- Company Class ---
class Company:
    """
    Represents either the player or an AI competitor.
    """
    def __init__(self, name, tier=None):
        self.name = name
        self.tier = tier
        self.cash = 0.0
        self.debt = 0.0
        self.debt_monthly_payment = 0.0
        self.debt_interest_rate = 0.06
        self.debt_remaining_months = 0
        self.loans = []  # List of Loan objects
        self.bonds = []  # List of Bond objects
        self.employees = 0
        self.market_cap = 0.0
        self.products = {}  # key: product name, value: Product
        self.past_quarter_profits = [0.0, 0.0, 0.0]
        self.campuses = []
        self._negative_cash_quarters = 0
        self.past_quarter_revenues = [0.0, 0.0, 0.0]  # store up to 3 prior quarter revenues
        self.last_acquisition_quarter = -100


    def employee_capacity(self) -> int:
        return sum(c[3] for c in self.campuses)

    def overhead_percent(self) -> float:
        if not self.campuses:
            return 0.0
        return max(c[2] for c in self.campuses)

    def total_revenue_this_quarter(self) -> float:
        return sum(p.revenue for p in self.products.values())

    def total_product_spend(self) -> float:
        total = 0.0
        for p in self.products.values():
            total += p.total_spend_this_quarter()
        return total

    def total_spending_this_quarter(self) -> float:
        employee_base = self.employees * 25_000
        overhead = employee_base * self.overhead_percent()
        debt_cost = self.debt_monthly_payment * 3
        return employee_base + overhead + debt_cost

    def quarterly_profit(self) -> float:
        return self.total_revenue_this_quarter() - self.total_spending_this_quarter()

    def update_negative_cash_quarters(self):
        if self.cash < 0:
            self._negative_cash_quarters += 1
        else:
            self._negative_cash_quarters = 0

    def is_bankrupt(self):
        return self._negative_cash_quarters >= 4


# --- Market Class ---
class Market:
    """
    Represents a market with size, growth rate, and other attributes.
    """
    def __init__(self, name):
        self.name = name
        self.size = random.randint(25_000_000, 50_000_000)
        self.base_growth_rate = random.uniform(0.05, 0.15)
        self.growth_rate = self.base_growth_rate 
        self.quarters_elapsed = 0
        self.is_in_global_recession = False
        self.recession_quarters_left = 0
        self.last_quarter_total_revenue = 0.0

    def apply_recession(self):
        if self.is_in_global_recession and self.recession_quarters_left > 0:
            self.size *= 0.95
            self.recession_quarters_left -= 1
            if self.recession_quarters_left <= 0:
                self.is_in_global_recession = False

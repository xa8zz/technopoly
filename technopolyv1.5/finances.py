"""
finances.py

Handles routines for:
 - Updating each company's finances
 - Paying out bond interest
 - New Market Cap formula:
   MarketCap = avg_profit_3q * (20 + (margin_last_q*0.1) + rnd(1..3)) + (net_assets).
"""

import random
from models import Company, Bond, Loan


def update_finances(companies):
    """
    Each quarter:
     - Pay out bond interest.
     - Compute profit and update cash.
     - Update market cap.
     - Process outstanding loans.
    
    We perform the updates in two main passes:
      1) Process bonds.
      2) Process profit and loans.
    """
    # 1) Pay bond interest
    for c in companies:
        total_bond_interest = 0.0
        remove_bonds = []
        for b in c.bonds:
            # Compute interest for this quarter.
            interest = b.quarterly_interest()
            total_bond_interest += interest

            # Reduce the bond's term.
            b.term_remaining -= 1
            if b.term_remaining <= 0:
                # When the bond expires, add back its principal.
                c.cash += b.principal
                remove_bonds.append(b)

        # Remove expired bonds.
        for bb in remove_bonds:
            c.bonds.remove(bb)

        # Add total bond interest to cash.
        c.cash += total_bond_interest

    # 2) Profit calculation and market cap update
    for c in companies:
        # Calculate this quarter's profit.
        q_profit = c.quarterly_profit()
        c.cash += q_profit  # Update cash with profit.
        c.past_quarter_profits.append(q_profit)
        if len(c.past_quarter_profits) > 3:
            c.past_quarter_profits.pop(0)
        rev_this_q = c.total_revenue_this_quarter()
        c.past_quarter_revenues.append(rev_this_q)
        if len(c.past_quarter_revenues) > 3:
            c.past_quarter_revenues.pop(0)

        # (a) Compute the average quarterly revenue from the past three quarters.
        if c.past_quarter_revenues:
            avg_revenue = sum(c.past_quarter_revenues) / len(c.past_quarter_revenues)
        else:
            avg_revenue = c.total_revenue_this_quarter()
        annualized_revenue = avg_revenue * 4

        # (b) Compute the total campus value.
        #    (Assuming each campus is stored as a tuple and that index 1 holds its value.)
        campus_value = sum(campus[1] for campus in c.campuses)

        # (c) Compute the total bonds value.
        bonds_value = sum(b.principal for b in c.bonds)

        # (d) Compute the total debt (sum of loan principals).
        debt = sum(loan.principal for loan in c.loans)

        # (e) Compute net assets: cash + campus_value + bonds_value - debt.
        net_assets = c.cash + campus_value + bonds_value - debt

        # (f) New market cap is the sum of net assets and annualized revenue.
        new_market_cap = net_assets + annualized_revenue

        # Ensure market cap does not fall below zero.
        c.market_cap = max(0, new_market_cap)

    # 3) Process loans for each company
    for c in companies:
        total_loan_payment = 0.0
        remove_loans = []
        for loan in c.loans:
            monthly_r = loan.annual_rate / 12
            # Calculate interest for one month.
            interest_payment = loan.principal * monthly_r
            # Calculate principal portion for one month.
            principal_portion = loan.monthly_payment - interest_payment
            if principal_portion < 0:
                principal_portion = 0
            # For the quarter (3 months):
            total_interest = interest_payment * 3
            principal_payment_total = principal_portion * 3
            # Reduce the loan principal.
            loan.principal = max(0, loan.principal - principal_payment_total)
            loan.term_remaining_months -= 3
            total_loan_payment += loan.monthly_payment * 3
            if loan.term_remaining_months <= 0 or loan.principal <= 0:
                remove_loans.append(loan)
        for loan in remove_loans:
            c.loans.remove(loan)
        # Subtract the total loan payment from cash.
        c.cash -= total_loan_payment

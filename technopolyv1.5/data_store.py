"""
data_store.py

Implements a DataStorage class that captures all changing values
each quarter: 
 - Company finances (cash, debt, market cap, profit)
 - Product data (employee assignments, effectiveness, revenue)
 - Market data (size, growth rate)
and so on.

We'll store them in a dictionary structure each turn.
"""

from typing import List
from models import Company, Market, Product, Loan, Bond


class DataStorage:
    """
    Maintains a list of snapshots, one per quarter, for historical analysis.
    """
    def __init__(self):
        self.history = []  # list of dict snapshots
        self.max_history_length = 10  # Limit history to 10 snapshots to avoid memory issues

    def record_state(self, turn_index: int, companies: List[Company], markets: List[Market]):
        """
        Create a big dictionary capturing everything. Then append to self.history.
        """
        snapshot = {
            "turn": turn_index,
            "companies": [],
            "markets": []
        }

        for c in companies:
            company_data = {
                "name": c.name,
                "tier": c.tier,
                "cash": c.cash,
                "debt": c.debt,
                "market_cap": c.market_cap,
                "employees": c.employees,
                "products": {},
                "bonds": []
            }
            for pname, prod in c.products.items():
                company_data["products"][pname] = {
                    "market_name": prod.market_name,
                    "r&d_employees": prod.assigned_employees["r&d"],
                    "qa_employees": prod.assigned_employees["q&a"],
                    "marketing_employees": prod.assigned_employees["marketing"],
                    "revenue": prod.revenue,
                    "effectiveness": prod.effectiveness
                }
            # bonds
            for b in c.bonds:
                company_data["bonds"].append({
                    "principal": b.principal,
                    "annual_rate": b.annual_rate,
                    "term_remaining": b.term_remaining
                })

            snapshot["companies"].append(company_data)

        for m in markets:
            market_data = {
                "name": m.name,
                "size": m.size,
                "growth_rate": m.growth_rate,
                "is_in_global_recession": m.is_in_global_recession,
                "last_quarter_revenue": m.last_quarter_total_revenue
            }
            snapshot["markets"].append(market_data)

        self.history.append(snapshot)
        
        # Limit history size to prevent memory issues
        if len(self.history) > self.max_history_length:
            self.history.pop(0)  # Remove the oldest snapshot

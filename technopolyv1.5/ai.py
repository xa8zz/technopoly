import random
from models import Company, Market, Product, Bond, Loan
from utils import random_product_name, format_money
from finances import update_finances
from configs import CAMPUS_TYPES

class AIController:
    def __init__(self, game_ref):
        self.game = game_ref  # reference to main game engine (BusinessGameEngine)

    def ai_take_actions(self, comp: Company):
        """
        Called each quarter by the game engine for each AI company.
        This method first checks bankruptcy, then delegates to tier-specific logic.
        """
        # 1) Update negative-cash logic and check bankruptcy.
        comp.update_negative_cash_quarters()
        if comp.is_bankrupt():
            self.handle_bankruptcy(comp)
            return

        # 2) Execute tier-specific strategy.
        if comp.tier == "Startup":
            self._logic_startup(comp)
        elif comp.tier == "Medium":
            self._logic_medium(comp)
        elif comp.tier == "Large":
            self._logic_large(comp)
        elif comp.tier == "Big Tech":
            self._logic_bigtech(comp)
        else:
            # Default / unknown tier: do nothing extra.
            pass

        # 3) Final update of negative cash quarters after actions.
        comp.update_negative_cash_quarters()
        # 4) Adjust employee assignments and push news.  This MUST happen after
        #    hiring/firing, as adjust_employee_assignments expects the correct
        #    total employee count.
        assignment_changes = self.adjust_employee_assignments(comp)
        for product_name, changes in assignment_changes.items():
            for dept, change in changes.items():
                if change > 0:
                    self.game._push_competitor_news(f"{comp.name} assigned {change} additional employees to {dept} for product '{product_name}'.")
                elif change < 0:
                    self.game._push_competitor_news(f"{comp.name} removed {-change} employees from {dept} for product '{product_name}'.")

    # =============================
    # Bankruptcy Handler
    # =============================
    def handle_bankruptcy(self, comp: Company):
        """
        If the company is bankrupt, give all assets to the biggest MC company (player or AI).
        Remove from the AI list and push news.
        """
        # Attempt to liquidate bonds as a last-ditch effort to recover cash
        if comp.cash < 0 and comp.bonds:
            self._liquidate_bonds_for_principal(comp)
            
        # Re-check if the company is still bankrupt after bond liquidation
        if comp.cash >= 0:
            # Successfully staved off bankruptcy
            self.game._push_competitor_news(f"{comp.name} avoided bankruptcy after liquidating bonds!")
            return


        largest = self.game.player
        largest_mc = largest.market_cap
        for ai in self.game.ai_companies:
            if ai != comp and ai.market_cap > largest_mc:
                largest_mc = ai.market_cap
                largest = ai

        self.game._merge_companies(largest, comp)
        if comp in self.game.ai_companies:
            self.game.ai_companies.remove(comp)
        self.game._push_competitor_news(f"{comp.name} has gone BANKRUPT! All assets given to {largest.name}.")

    # =============================
    # Helper Functions
    # =============================
    def _get_liquidity_ratio(self, comp: Company) -> float:
        """Return ratio of cash to quarterly revenue (avoid division by zero)."""
        rev = comp.total_revenue_this_quarter()
        return comp.cash / rev if rev > 0 else 10.0

    def _target_employee_count(self, comp: Company, target_cost_ratio: float) -> int:
        """
        Given a target employee cost ratio (employee cost as fraction of revenue),
        return the ideal number of employees.
        (Each employee costs $25K per quarter.)
        """
        revenue = comp.total_revenue_this_quarter()
        target_cost = target_cost_ratio * revenue
        return int(target_cost / 25000)

    def _liquidate_bonds_for_principal(self, comp: Company):
        """
        Sells all bonds for their principal amounts (no interest).
        """
        if not comp.bonds:
            return
        total_gained = sum(b.principal for b in comp.bonds)
        comp.cash += total_gained
        comp.bonds.clear()
        self.game._push_competitor_news(f"{comp.name} sold all bonds for {format_money(total_gained)} to raise emergency funds.")

    def fire_excess_employees(self, comp: Company, target_employees: int):
        """Fires employees down to the target, handling severance, and unassigning first."""
        to_fire = max(0, comp.employees - target_employees)
        if to_fire == 0:
            return  # Nothing to do

        # 1. Unassign from worst-performing products first.
        products_sorted = sorted(comp.products.items(), key=lambda item: item[1].effectiveness)
        for pname, product in products_sorted:
            if to_fire <= 0:
                break  # No more employees to fire

            # Calculate total assigned to this product.
            assigned_to_product = sum(product.assigned_employees.values())

            if assigned_to_product == 0: # if no employees in this product
                continue

            # Fire from the lowest rank of employees first
            if product.assigned_employees["marketing"] > 0:
                if product.assigned_employees["marketing"] >= to_fire:
                    product.assigned_employees["marketing"] -= to_fire
                    to_fire = 0
                else:
                    to_fire -= product.assigned_employees["marketing"]
                    product.assigned_employees["marketing"] = 0
            elif product.assigned_employees["q&a"] > 0:
                if product.assigned_employees["q&a"] >= to_fire:
                    product.assigned_employees["q&a"] -= to_fire
                    to_fire = 0
                else:
                    to_fire -= product.assigned_employees["q&a"]
                    product.assigned_employees["q&a"] = 0
            elif product.assigned_employees["r&d"] > 0:
                if product.assigned_employees["r&d"] >= to_fire:
                    product.assigned_employees["r&d"] -= to_fire
                    to_fire = 0
                else:
                    to_fire -= product.assigned_employees["r&d"]
                    product.assigned_employees["r&d"] = 0

        # 2. Now, actually reduce the employee count and handle severance.
        severance_cost = to_fire * 20000  # $20k per fired employee
        if comp.cash >= severance_cost:
            comp.cash -= severance_cost
            comp.employees -= to_fire
            self.game._push_competitor_news(f"{comp.name} fired {to_fire} employees, incurring {format_money(severance_cost)} in severance costs.")
        else:
            # Not enough cash to cover severance.  Fire as many as possible.
            affordable_to_fire = comp.cash // 20000
            if affordable_to_fire > 0:
                comp.cash -= affordable_to_fire * 20000
                comp.employees -= affordable_to_fire
                self.game._push_competitor_news(f"{comp.name} fired {affordable_to_fire} employees, incurring {format_money(affordable_to_fire * 20000)} in severance costs (limited by cash).")
            # Even if they can't afford *any*, they might still need to reduce staff if over capacity.
            over_capacity = max(0, comp.employees - comp.employee_capacity())
            if over_capacity > 0:
                comp.employees -= over_capacity  # No severance paid
                self.game._push_competitor_news(f"{comp.name} released {over_capacity} employees due to campus capacity limits.")


    # =============================
    # Tier-Specific Logic
    # =============================
    def _logic_startup(self, comp: Company):
            """
            Startup Strategy (Aggressive growth):
            - Prioritize raising product effectiveness.
            - Aim for a high employee spending ratio (~80% of revenue).
            - Take loans aggressively if liquidity is low.
            - Open new products when excess cash is available.
            - Invest a small fraction in bonds if surplus cash exists.
            """
            revenue = comp.total_revenue_this_quarter()
            profit = comp.quarterly_profit()
            liquidity = self._get_liquidity_ratio(comp)
            # Define target employee cost ratio (startup: ~80% of revenue)
            target_ratio = 0.8
            target_emp = self._target_employee_count(comp, target_ratio)

            # (B) HIRING / FIRING:
            if comp.employees < target_emp:
                # Hire only if campus capacity allows and if liquidity is reasonable.
                hires = min(target_emp - comp.employees, comp.employee_capacity() - comp.employees)
                # Ensure that hiring does not push liquidity below a safety margin.  Require 3x quarterly revenue.
                if comp.cash > revenue * 1:
                    comp.employees += hires
                    if hires > 0:  # Only push news if hires actually happened
                        self.game._push_competitor_news(f"{comp.name} hires {hires} new employees.")
            # Ensure firing happens if overstaffed AND losing money
            elif profit < 0 and comp.employees > int(target_emp * 1.2): # fires if employees are 20% greater than target employees AND comp is losing money
                self.fire_excess_employees(comp, target_emp)



            # (C) CAMPUS EXPANSION:
            remaining_capacity = comp.employee_capacity() - comp.employees
            if comp.employee_capacity() > 0 and remaining_capacity < 0.15 * comp.employee_capacity() and comp.cash > 250000:
                self.build_campus(comp, tier="startup")

            # (D) LIQUIDITY MANAGEMENT:
            if liquidity < 0.5:
                self.take_loan_if_needed(comp, emergency=True)

            # (E) NEW PRODUCT:
            # Use a threshold based on the market’s entry cost.
            # (For startups, require cash > 1.75× entry cost.)
            potential_markets = [m for m in self.game.markets if not self.game._company_has_product_in_market(comp, m.name)]
            if potential_markets:
                # Pick one market to evaluate (could be randomized).
                chosen_market = random.choice(potential_markets)
                entry_cost = chosen_market.size * 0.05 * 4
                if comp.cash > entry_cost * 1.75 and profit > 0:
                    self.open_new_product(comp, 0.25)

            # (F) BOND INVESTMENT:
            # If surplus cash exists (cash > 1.5× revenue), invest ~10% in short-term bonds.
            if comp.cash > revenue * 1.5 and comp.cash > 500000 and random.random() < 0.05:
                self.buy_bond(comp, term=2, annual_rate=0.06)

    def _logic_medium(self, comp: Company):
        """
        Medium Company Strategy (Balanced growth):
          - Moderately invest in product improvement (aim for ~35% employee cost ratio).
          - Hire/firing decisions are a bit more conservative.
          - New product expansion if cash exceeds 2× entry cost.
          - Consider acquisitions when underperforming products persist.
          - Invest in bonds if cash is in excess.
        """
        revenue = comp.total_revenue_this_quarter()
        profit = comp.quarterly_profit()
        liquidity = self._get_liquidity_ratio(comp)
        target_ratio = 0.6  # Target employee cost as a fraction of revenue
        target_emp = self._target_employee_count(comp, target_ratio)

        # (B) HIRING / FIRING:
        if comp.employees < target_emp:
            hires = min(target_emp - comp.employees, comp.employee_capacity() - comp.employees)
            # Medium companies require a bit more cash buffer.
            if comp.cash > revenue * 2:  # Increased cash buffer
                comp.employees += hires
                if hires > 0:
                    self.game._push_competitor_news(f"{comp.name} hires {hires} employees.")
        elif profit < 0 and comp.employees > int(target_emp * 1.15): # fires if employees are 15% greater than target and comp is losing cash
            self.fire_excess_employees(comp, target_emp)


        # (C) CAMPUS EXPANSION:
        remaining_capacity = comp.employee_capacity() - comp.employees
        if comp.employee_capacity() > 0 and remaining_capacity < 0.20 * comp.employee_capacity() and comp.cash > 1000000:
            self.build_campus(comp, tier="medium")

        # (D) LIQUIDITY MANAGEMENT:
        if liquidity < 0.6:  # Slightly tighter liquidity requirement
            self.take_loan_if_needed(comp, emergency=False)

        # (E) NEW PRODUCT:
        potential_markets = [m for m in self.game.markets if not self.game._company_has_product_in_market(comp, m.name)]
        if potential_markets:
            chosen_market = random.choice(potential_markets)
            entry_cost = chosen_market.size * 0.05 * 4
            if comp.cash > entry_cost * 2 and profit > 0:  # 2x entry cost buffer
                self.open_new_product(comp, 0.25)

        # (F) ACQUISITIONS:
        # If any product has been underperforming and game turn is mature, try to acquire a competitor.
        for pname, product in comp.products.items():
            rank = self.game._get_product_quality_rank(product)
            if rank in ["Very Bad", "Bad"] and self.game.turn_index >= 12 and self.game.turn_index - comp.last_acquisition_quarter >= 5:
                market_products = self.game._find_products_in_market(product.market_name)
                for other_product in market_products:
                    if other_product.owner_name != comp.name:
                        other_rank = self.game._get_product_quality_rank(other_product)
                        if other_rank in ["Very Good", "Good"]:  # Only acquire better-ranked products.
                            # Find target company
                            for potential_target in self.game.ai_companies:
                                if potential_target.name == other_product.owner_name:
                                    price = self.game._calculate_acquisition_price(potential_target)
                                    if comp.cash >= price:
                                        comp.last_acquisition_quarter = self.game.turn_index
                                        self.game.pending_acquisitions.append((comp, potential_target.name, price, self.game.turn_index))
                                        self.game._push_competitor_news(f"{comp.name} begins acquisition attempt of {potential_target.name}!")
                                        break  # Only one acquisition attempt per turn

        # (G) BOND INVESTMENT:
        if comp.cash > revenue * 1.5 and comp.cash > 1000000:
            if random.random() < 0.15:  # Reduced probability
                self.buy_bond(comp, term=4, annual_rate=0.07)


    def _logic_large(self, comp: Company):
        """
        Large Company Strategy (Profit-focused growth):
          - Aim for a lower employee cost ratio (~30% of revenue).
          - Be conservative with hiring and only expand staffing modestly.
          - Open new products only when strategically important.
          - Use loans primarily for acquisitions.
          - Invest in bonds if a significant cash surplus exists.
        """
        revenue = comp.total_revenue_this_quarter()
        profit = comp.quarterly_profit()
        liquidity = self._get_liquidity_ratio(comp)
        target_ratio = 0.5
        target_emp = self._target_employee_count(comp, target_ratio)

        # (B) HIRING / FIRING:
        if comp.employees < target_emp:
            hires = min(target_emp - comp.employees, comp.employee_capacity() - comp.employees)
            # Large companies are even more conservative.  Require 4x quarterly revenue.
            if comp.cash > revenue * 3:
                comp.employees += hires
                if hires > 0:
                     self.game._push_competitor_news(f"{comp.name} hires {hires} employees.")
        elif profit < 0 and comp.employees > int(target_emp * 1.10): # fires if employees are 10% greater than target
            self.fire_excess_employees(comp, target_emp)

        # (C) CAMPUS EXPANSION:
        remaining_capacity = comp.employee_capacity() - comp.employees
        if comp.employee_capacity() > 0 and remaining_capacity < 0.25 * comp.employee_capacity() and comp.cash > 5000000:
            self.build_campus(comp, tier="large")

        # (D) LIQUIDITY & LOAN MANAGEMENT:
        # Large companies use loans more strategically, mainly for acquisitions.
        if comp.cash < 0 or (liquidity < 0.7 and comp._negative_cash_quarters >= 2):
            self.take_loan_if_needed(comp, emergency=False)

        # (E) NEW PRODUCT:
        potential_markets = [m for m in self.game.markets if not self.game._company_has_product_in_market(comp, m.name)]
        if potential_markets:
            chosen_market = random.choice(potential_markets)
            entry_cost = chosen_market.size * 0.05 * 4
            if comp.cash > entry_cost * 3 and profit > 0:  # Higher cash buffer for large companies
                self.open_new_product(comp, 0.20)

        # (F) ACQUISITIONS:
        for pname, product in comp.products.items():
            rank = self.game._get_product_quality_rank(product)
            if rank in ["Very Bad", "Bad"] and self.game.turn_index >= 12 and self.game.turn_index - comp.last_acquisition_quarter >= 5:
                market_products = self.game._find_products_in_market(product.market_name)
                for other_product in market_products:
                    if other_product.owner_name != comp.name:
                        other_rank = self.game._get_product_quality_rank(other_product)
                        if other_rank in ["Very Good", "Good"] :
                            for potential_target in self.game.ai_companies:
                                if potential_target.name == other_product.owner_name:
                                    price = self.game._calculate_acquisition_price(potential_target)
                                    if comp.cash >= price:
                                        comp.last_acquisition_quarter = self.game.turn_index
                                        self.game.pending_acquisitions.append((comp, potential_target.name, price, self.game.turn_index))
                                        self.game._push_competitor_news(f"{comp.name} initiates acquisition of {potential_target.name}!")
                                        break

        # (G) BOND INVESTMENT:
        if comp.cash > revenue * 2 and comp.cash > 5000000:
            if random.random() < 0.20:  # Further Reduced probability
                self.buy_bond(comp, term=4, annual_rate=0.07)


    def _logic_bigtech(self, comp: Company):
        """
        Big Tech Strategy (Market dominance & strategic acquisitions):
          - Aim for a very low employee cost ratio (~25% of revenue).
          - Invest minimally in product improvements—just enough to maintain market position.
          - Hire only as needed to maintain a set ratio.
          - Open new products only when strategically important.
          - Use excess cash to buy bonds.
          - Aggressively attempt acquisitions when an opportunity arises.
        """
        revenue = comp.total_revenue_this_quarter()
        profit = comp.quarterly_profit()
        liquidity = self._get_liquidity_ratio(comp)
        target_ratio = 0.4
        target_emp = self._target_employee_count(comp, target_ratio)

        # (B) HIRING / FIRING:
        if comp.employees < target_emp:
            hires = min(target_emp - comp.employees, comp.employee_capacity() - comp.employees)
            # Big Tech hires sparingly; only hire if cash is very abundant.
            if comp.cash > revenue * 4:
                comp.employees += hires
                if hires > 0:
                     self.game._push_competitor_news(f"{comp.name} hires {hires} new employees.")
        elif profit < 0 and comp.employees > int(target_emp * 1.05): # very tight firing threshold, big tech almost never fires
            self.fire_excess_employees(comp, target_emp)

        # (C) CAMPUS EXPANSION:
        remaining_capacity = comp.employee_capacity() - comp.employees
        if comp.employee_capacity() > 0 and remaining_capacity < 0.30 * comp.employee_capacity() and comp.cash > 10000000:
            self.build_campus(comp, tier="big")

        # (D) LIQUIDITY & LOAN MANAGEMENT:
        # Big Tech rarely takes loans; only do so if cash is very low relative to market cap.
        if comp.cash < comp.market_cap * 0.1 and liquidity < 0.8: # much stricter condition for big tech
            self.take_loan_if_needed(comp, emergency=False)

        # (E) NEW PRODUCT:
        potential_markets = [m for m in self.game.markets if not self.game._company_has_product_in_market(comp, m.name)]
        if potential_markets:
            chosen_market = random.choice(potential_markets)
            entry_cost = chosen_market.size * 0.05 * 4
            if comp.cash > entry_cost * 4 and profit > 0:  # very high buffer for big tech
                self.open_new_product(comp, 0.30)

        # (F) ACQUISITIONS:
        # Big Tech aggressively acquires companies when they are smaller.
        for pname, product in comp.products.items():
            rank = self.game._get_product_quality_rank(product)
            if rank in ["Very Bad", "Bad", "Moderate"] and self.game.turn_index >= 12 and self.game.turn_index - comp.last_acquisition_quarter >= 5:  
                market_products = self.game._find_products_in_market(product.market_name)
                for other_product in market_products:
                    if other_product.owner_name != comp.name:
                        other_rank = self.game._get_product_quality_rank(other_product)
                        # Big tech will acquire companies with very good products.
                        if other_rank in ["Very Good", "Good"]:
                            for potential_target in self.game.ai_companies:
                                if potential_target.name == other_product.owner_name:
                                    price = self.game._calculate_acquisition_price(potential_target)
                                    if comp.cash >= price:
                                         comp.last_acquisition_quarter = self.game.turn_index
                                         self.game.pending_acquisitions.append((comp, potential_target.name, price, self.game.turn_index))
                                         self.game._push_competitor_news(f"{comp.name} initiates acquisition of {potential_target.name}!")
                                         break

        # (G) BOND INVESTMENT:
        # With surplus cash, invest a large portion (e.g., 50% of excess cash) in long-term bonds.
        if comp.cash > revenue * 2.5 and comp.cash > 10000000:
            if random.random() < 0.15: # reduced liklihood 0.5 -> 0.15
                self.buy_bond(comp, term=8, annual_rate=0.08)


    # =============================
    # Common AI Actions (Helpers)
    # These methods are largely unchanged from your original code.
    # =============================
    def build_campus(self, comp: Company, tier: str = "small"):
        """
        Attempt to build an appropriate campus.
        Chooses a campus that is affordable.
        """
        from configs import CAMPUS_TYPES
        affordable = [ctype for ctype in CAMPUS_TYPES if ctype[1] < comp.cash]
        if not affordable:
            return
        if tier == "startup":
            campus_to_build = sorted(affordable, key=lambda x: x[1])[min(len(affordable) - 1, 1)]
        elif tier == "medium":
            campus_to_build = sorted(affordable, key=lambda x: x[1])[min(len(affordable) - 1, 1)]
        elif tier == "large":
             campus_to_build = sorted(affordable, key=lambda x: x[1])[-2] if len(affordable) > 1 else affordable[-1]
        else: # big tech: choose the largest
            campus_to_build = sorted(affordable, key=lambda x: x[1])[-1]
        comp.cash -= campus_to_build[1]
        comp.campuses.append(campus_to_build)
        self.game._push_competitor_news(f"{comp.name} built a new campus: {campus_to_build[0]} for {format_money(campus_to_build[1])}.")


    def take_loan_if_needed(self, comp: Company, emergency: bool):
        """
        AI takes a loan.
        The credit limit is on revenue, same as the player.
        """
        if comp.past_quarter_revenues:
            avg_r = sum(comp.past_quarter_revenues) / len(comp.past_quarter_revenues)
        else:
            avg_r = comp.total_revenue_this_quarter()
        annual_revenue = avg_r * 4
        max_loan = annual_revenue * 0.40  # 40% of annualized revenue

        current_loans = sum(ln.principal for ln in comp.loans)
        available = max_loan - current_loans

        if available < 100_000:
            return  # Not enough room for a new loan

        if emergency:
            loan_amt = available  # Take the maximum available
        else:
            loan_amt = available * 0.5  # Take half in non-emergency situations

        # Increase base rate by 50% => 6% -> 9%
        base_rate = 0.06 * 1.5
        new_rate = base_rate + 0.01 * len(comp.loans)
        # Term is halved => 120 -> 60
        new_loan = Loan(loan_amt, new_rate, 60)
        comp.loans.append(new_loan)
        comp.cash += loan_amt
        self.game._push_competitor_news(f"{comp.name} took a loan of {format_money(loan_amt)} at {new_rate*100:.1f}% interest.")

    def open_new_product(self, comp: Company, cost_fraction: float):
        """
        AI creates a new product in a market it is not currently in.
        The product costs 5% of the market size.
        """
        mk_candidates = [m for m in self.game.markets if not self.game._company_has_product_in_market(comp, m.name)]
        if not mk_candidates:
            return
        chosen_m = random.choice(mk_candidates)
        cost = chosen_m.size * 0.05 * 4
        if cost < comp.cash * cost_fraction and comp.cash >= cost:
            comp.cash -= cost
            newp = Product(comp.name, chosen_m.name)
            prods = self.game._find_products_in_market(chosen_m.name)
            if prods:
                min_eff = min(pp.effectiveness for pp in prods)
                newp.effectiveness = max(0, min_eff - (min_eff * 0.4))
                biggest = max(prods, key=lambda x: x.revenue)
                if biggest.revenue > 10000:
                    biggest.revenue -= 10000
                    newp.revenue = 10000

            # Initial employee assignments for new products.  Start with a small team.
            newp.assigned_employees = {"r&d": 2, "q&a": 1, "marketing": 2}
            pname = random_product_name(self.game.used_product_names)
            comp.products[pname] = newp
            self.game._push_competitor_news(f"{comp.name} opened a new product in {chosen_m.name} for {format_money(cost)}.")

    def buy_bond(self, comp: Company, term: int, annual_rate: float):
        """
        AI invests a portion of cash into a bond.
        """
        invest = comp.cash * 0.25  # invest 25% of available cash, more reasonable.
        if invest < 100_000:
            return
        comp.cash -= invest
        b = Bond(invest, annual_rate, term)
        comp.bonds.append(b)
        self.game._push_competitor_news(f"{comp.name} purchased a {term}-quarter bond at {annual_rate*100:.1f}% for {format_money(invest)}.")

    def adjust_employee_assignments(self, comp: Company):
        """
        Adjusts employee assignments for all of a company's products based on their 
        effectiveness ranking in their respective markets.
        """
        total_employees = comp.employees
        num_products = len(comp.products)
        assignment_changes = {}

        if num_products == 0:
            return assignment_changes

        # Reset each product's assigned_employees dictionary.
        for product in comp.products.values():
            product.assigned_employees = {"r&d": 0, "q&a": 0, "marketing": 0}

        # --- Step 1. Determine per–product total employees using the 10% deviation formula ---
        # Sort the products by effectiveness (ascending order: best first).
        # (Note: In our game a “1st–ranked” product is the best; so the worst–performing
        #  product will appear last.)
        sorted_products = sorted(comp.products.items(), key=lambda item: item[1].effectiveness)
        
        # The even split (baseline) is:
        baseline = total_employees / num_products
        
        # We will assign a “factor” to each product based on its position in the sorted list.
        # For n > 1, we map the index i (0 = best, n-1 = worst) linearly to a number in [-1, 1]:
        #   - Best product: factor = -1  --> gets baseline - 10% of baseline
        #   - Worst product: factor =  1  --> gets baseline + 10% of baseline
        # (If there is only one product, it simply gets all the employees.)
        assigned_totals = {}   # product name -> target total (as float initially)
        factors = {}           # product name -> computed factor (for later rounding adjustment)
        if num_products == 1:
            pname, product = sorted_products[0]
            assigned_totals[pname] = total_employees
            factors[pname] = 0
        else:
            mid = (num_products - 1) / 2  # this is used for normalization
            for i, (pname, product) in enumerate(sorted_products):
                # Compute factor: best product (i=0) gets -1; worst (i=n-1) gets +1.
                factor = (i - mid) / mid
                factors[pname] = factor
                # Apply 10% deviation (10% of the baseline)
                assigned_totals[pname] = baseline + (factor * 0.1 * baseline)
        
            # Convert the float totals into integers while making sure the overall sum equals total_employees.
            assigned_int = {pname: int(round(val)) for pname, val in assigned_totals.items()}
            sum_assigned = sum(assigned_int.values())
            diff = total_employees - sum_assigned
            # If there is a discrepancy (due to rounding), adjust by adding extra employees 
            # to the worst–performing products (largest factor) when diff > 0, or by subtracting 
            # from the best–performing products when diff < 0.
            if diff > 0:
                sorted_names = sorted(assigned_int.keys(), key=lambda pname: factors[pname], reverse=True)
                idx = 0
                while diff > 0:
                    assigned_int[sorted_names[idx % num_products]] += 1
                    diff -= 1
                    idx += 1
            elif diff < 0:
                sorted_names = sorted(assigned_int.keys(), key=lambda pname: factors[pname])
                idx = 0
                while diff < 0:
                    if assigned_int[sorted_names[idx % num_products]] > 0:
                        assigned_int[sorted_names[idx % num_products]] -= 1
                        diff += 1
                    idx += 1
            assigned_totals = assigned_int

        # --- Step 2. For each product, distribute its target employees among departments ---
        # The departmental breakdown percentages remain the same as before,
        # differing slightly based on the product's quality rank.
        for pname, product in comp.products.items():
            # Record changes per product for news
            assignment_changes[pname] = {}
            # This is the target total for this product (as computed above)
            target_total = assigned_totals.get(pname, 0)
            
            # Determine quality rank (e.g., "Very Bad", "Bad", "Moderate", "Good", "Very Good")
            quality_rank = self.game._get_product_quality_rank(product)
            
            if quality_rank in ["Very Bad", "Bad"]:
                # For poor–quality products, put more into R&D and some into marketing.
                target_rd = int(round(0.6 * target_total))
                target_marketing = int(round(0.3 * target_total))
                target_q_a = target_total - (target_rd + target_marketing)
                product.assigned_employees["r&d"] = target_rd
                product.assigned_employees["marketing"] = target_marketing
                product.assigned_employees["q&a"] = target_q_a
                assignment_changes[pname]["r&d"] = target_rd
                assignment_changes[pname]["marketing"] = target_marketing
                assignment_changes[pname]["q&a"] = target_q_a
            elif quality_rank == "Moderate":
                # A balanced approach for moderate products.
                target_rd = int(round(0.4 * target_total))
                target_qa = int(round(0.3 * target_total))
                target_marketing = target_total - (target_rd + target_qa)
                product.assigned_employees["r&d"] = target_rd
                product.assigned_employees["q&a"] = target_qa
                product.assigned_employees["marketing"] = target_marketing
                assignment_changes[pname]["r&d"] = target_rd
                assignment_changes[pname]["q&a"] = target_qa
                assignment_changes[pname]["marketing"] = target_marketing
            else:
                # For good/very–good products, emphasize QA and marketing.
                target_qa = int(round(0.4 * target_total))
                target_marketing = int(round(0.5 * target_total))
                target_rd = target_total - (target_qa + target_marketing)
                product.assigned_employees["q&a"] = target_qa
                product.assigned_employees["marketing"] = target_marketing
                product.assigned_employees["r&d"] = target_rd
                assignment_changes[pname]["q&a"] = target_qa
                assignment_changes[pname]["marketing"] = target_marketing
                assignment_changes[pname]["r&d"] = target_rd

        # --- Sanity Check ---
        total_assigned = sum(sum(p.assigned_employees.values()) for p in comp.products.values())
        if total_assigned != total_employees:
            print("ERROR: Assigned employees do not match total employees for company", comp.name)

        return assignment_changes




    def fire_employees_with_underpreforming_products(self, comp: Company):
        """
        Fires employees from underperforming products, and fires additional employees if
        the company is unprofitable.
        """

        # First, re-distribute from underperforming products
        self.adjust_employee_assignments(comp)

        # Then, if still unprofitable, fire excess employees
        if comp.quarterly_profit() < 0:
            target_ratio = 0.7  # Example target: adjust based on tier
            if comp.tier == "Medium":
                target_ratio = 0.5
            elif comp.tier == "Large":
                target_ratio = 0.4
            elif comp.tier == "Big Tech":
                target_ratio = 0.3

            target_employees = self._target_employee_count(comp, target_ratio)
            self.fire_excess_employees(comp, target_employees)
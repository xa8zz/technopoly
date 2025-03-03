import sys
import random
from models import Company, Market, Loan, Product, Bond
from configs import CAMPUS_TYPES
from data_store import DataStorage
from events import EventManager
from finances import update_finances
from ai import AIController
from utils import format_money
from gui import TechnopolyGUI # import our gui


# ===================
#      GAME CLASS
# ===================

class BusinessGameEngine:
    """
    Coordinates everything:
      - Creates markets, AI companies, player
      - Each turn:
         1) AI actions
         2) Distribute revenue
         3) Events
         4) Acquisitions
         5) Finances
         6) Store data
         7) Output summary
    """
    def __init__(self):
        self.turn_index = 0
        self.start_year = 2000
        self.game_over=False

        self.player = None
        self.ai_companies=[]

        market_names = [
            "Artificial Intelligence", "Cloud Computing", "Cybersecurity", "Enterprise SaaS", 
            "E-Commerce", "Consumer Hardware", "FinTech", "Social Media",
        ]
        self.spawn_market_names = [
            "Semiconductors", "Autonomous Vehicles", "Blockchain", "Telecommunications",
            "VR Software", "Cloud Gaming", "Quantum Computing", "Smart Home",
            "Streaming Platforms", "GreenTech", "Wearables", "Video Games"
        ]
        self.markets=[Market(n) for n in market_names]

        self.data_store= DataStorage()
        self.event_manager= EventManager(self.markets)
        self.ai_controller= AIController(self)  # pass ref to ourselves

        self.used_company_names=set()
        self.used_product_names=set()

        self.pending_acquisitions=[]
        self.news_feed=[]
        self.competitor_news_feed = []  # For AI competitor moves
        
        self.spawned_ai_count = 0
        self.spawned_market_count = 0
        
        # --- ADDED THESE ---
        self.Loan = Loan # needed to avoid circular dependance and allow for gui to make loan objects with game engine loan parameters
        self.Bond = Bond # needed to avoid circular dependance and allow for gui to make bond objects with game engine bond parameters
        self.CAMPUS_TYPES = CAMPUS_TYPES # need to make campus types available

    def setup_game(self):
        # first, create AI
        self._create_ai_companies()
        # then create player
        self._initialize_player() # still creates a default player instance
        # NO initial state storage here; it happens AFTER player setup

    def _get_date(self):
        """
        Calculate the current year and quarter based on the turn index.
        """
        y_offset, q = divmod(self.turn_index, 4)
        return self.start_year + y_offset, q + 1


    def run_game(self):
        # REMOVED: while not self.game_over: and self.player_menu()
        # The GUI handles the main loop now.
        pass


    def _get_product_quality_rank(self, product):
        """
        Determines the product's effectiveness rank based on its position within the market.
        """
        products_in_market = self._find_products_in_market(product.market_name)
        products_in_market.sort(key=lambda x: x.effectiveness, reverse=True)

        # Get the index of the product in the sorted list
        position = products_in_market.index(product)
        total_products = len(products_in_market)

        if position == 0:
            return "Very Good"
        elif position == total_products - 1:
            return "Very Bad"
        elif position <= total_products // 4:
            return "Good"
        elif position >= 3 * (total_products // 4):
            return "Bad"
        else:
            return "Moderate"


    # ==================================
    #        SETUP / INITIALIZATION
    # ==================================
    def _create_ai_companies(self):
        """
        We'll create 20 AI with 4 tiers. 
        If you want to keep existing logic, do so. 
        We'll do a simpler approach for demonstration or keep your existing code.
        """
        from utils import random_company_name
        prefixes = [
            "Neuro", "Quantum", "Cyber", "Hyper", "Vertex", "Nexus", "Strato", "Omicron", "Zenith", "Titan",
            "Echo", "Horizon", "Aether", "Aurora", "Byte", "Nano", "Synth", "Vortex", "Lyric", "Sigma",
            "Meta", "Flux", "Pyro", "Velox", "Inferna", "Nova", "Zylo", "Sol", "Sky", "Celesti",
            "Arc", "Phantom", "Neon", "Axion", "Sentinel", "Helix", "Apollo", "Echelon", "Omni", "Synthetix"
]
        suffixes = [
            "Tech", "AI", "Soft", "Dynamics", "Labs", "Innovations", "Industries", "Solutions", "Cloud", "Systems",
            "Logic", "Cybernetics", "Synapse", "Robotics", "Intelligence", "Analytics", "Works", "Data", "Quantum",
            "Networks", "Ventures", "Enterprises", "Informatics", "Computation", "Ops", "Matrix", "Forge", "Frameworks",
            "Infotech", "Synergy", "Engage", "X", "Next", "Core", "Stream", "Node", "Sphere", "Hub"
]


        # The same distribution as your code
        # Startup=5(1mkt), Medium=7(2mkt), Large=5(4mkt), BigTech=3(5mkt)
        # We'll keep it minimal or replicate your logic exactly...
        # For brevity, keep simpler. 
        # Actually let's replicate your logic exactly if possible. 
        tiers=[("Startup",5,1),("Medium",7,2),("Large",5,4),("Big Tech",3,5)]
        for tier_name, count, mcount in tiers:
            for _ in range(count):
                cname= random_company_name(prefixes,suffixes,self.used_company_names)
                c= Company(cname, tier_name)
                # campus - large campus park
                # Example: Startup starts with "Garage", Medium with "Small Office", etc.
                if tier_name == "Startup":
                    c.campuses.append(("Garage", 0, 0.0, 10))
                elif tier_name == "Medium":
                    c.campuses.append(("Small Office", 250_000, 0.02, 50))
                elif tier_name == "Large":
                    c.campuses.append(("Large Office", 2_500_000, 0.04, 125))
                elif tier_name == "Big Tech":
                    c.campuses.append(("Large Building", 5_000_000, 0.08, 250))

                # set employees/cash
                if tier_name=="Startup":
                    c.employees=random.randint(10,20)
                    c.cash=random.uniform(500_000,2_000_000)
                elif tier_name=="Medium":
                    c.employees=random.randint(35, 70)
                    c.cash=random.uniform(3_000_000,6_000_000)
                elif tier_name=="Large":
                    c.employees=random.randint(80, 140)
                    c.cash=random.uniform(12_000_000,18_000_000)
                else:
                    c.employees=random.randint(180,300)
                    c.cash=random.uniform(25_000_000,40_000_000)
                # pick markets
                chosen_mkts= random.sample(self.markets,mcount)
                from models import Product
                from utils import random_product_name
                for mk in chosen_mkts:
                    p=Product(c.name,mk.name)
                    # random assignment
                    p.assigned_employees["r&d"] = random.randint(1, 3)
                    p.assigned_employees["q&a"] = random.randint(1, 3)
                    p.assigned_employees["marketing"] = random.randint(1, 3)
                    # random revenue
                    p.revenue=0.0
                    # store
                    prod_key= random_product_name(self.used_product_names)
                    c.products[prod_key]= p

                self.ai_companies.append(c)

        # do your ratio-based initial share distribution
        self._assign_initial_market_shares()

    def _initialize_player(self):
        # We still create the player, but with default values.  The GUI will get the name.
        self.player= Company("Player Co")  # Default name
        self.player.cash=1_000_000
        self.player.employees=5
        # campus => Garage
        self.player.campuses.append(("Garage",0,0.0,10))

    def _choose_initial_product(self):
        # NO LONGER NEEDED - GUI handles this.
        pass

    def _categorize_growth_rate(self, growth_rate):
        """
        Categorizes the growth rate into 'Low', 'Moderate', or 'High'.
        """
        if growth_rate <= 0.083:
            return "Low"
        elif growth_rate <= 0.1166:
            return "Moderate"
        else:
            return "High"


    def _assign_initial_market_shares(self):
        # Same logic as old code but with a check for player setup
        TIER_RATIO = {"Startup": 1, "Medium": 2, "Large": 4, "Big Tech": 8}

        for mk in self.markets:
            comps_in_mkt = {}

            # 1. AI Companies
            for c in self.ai_companies:
                prods = [p for p in c.products.values() if p.market_name == mk.name]
                if prods:
                    comps_in_mkt[c] = prods

            # Skip if no participants in the market
            if not comps_in_mkt:
                continue

            # 3. Distribute initial shares
            total_ratio = sum(TIER_RATIO.get(c.tier, 1) for c in comps_in_mkt)
            first_q = mk.size / 4.0



            for comp in comps_in_mkt:
                r = TIER_RATIO.get(comp.tier, 1)
                share = (r / total_ratio) * first_q
                prods = comps_in_mkt[comp]
                each = share / len(prods)

                for p in prods:
                    p.revenue += each


    def _count_products_in_market(self,mname) -> int:
        # all AI + player
        c=0
        for ai in self.ai_companies:
            for p in ai.products.values():
                if p.market_name==mname:
                    c+=1
        for p in self.player.products.values():
            if p.market_name==mname:
                c+=1
        return c

    # ===========================
    #      TURN STEPS
    # ===========================
    def _distribute_revenue_all_markets(self):
        is_initial_turn = (self.turn_index == 0)
        
        for mk in self.markets:
            # Apply recession effects if applicable.
            mk.apply_recession()
            participants = self._find_products_in_market(mk.name)
            if not participants:
                mk.last_quarter_total_revenue = 0
                continue

            # Initialize last_quarter_total_revenue if needed.
            if mk.last_quarter_total_revenue <= 0:
                mk.last_quarter_total_revenue = sum(p.revenue for p in participants)

            if mk.is_in_global_recession:
                growth_rev = 0
            else:
                growth_rev = (mk.size * mk.growth_rate) / 4.0

            churn_amount = 0.08 * mk.last_quarter_total_revenue

            # Store previous revenue for each product to calculate growth
            previous_revenues = {p: p.revenue for p in participants}

            for p in participants:
                if is_initial_turn and p.owner_name == self.player.name:
                    continue
                else:
                    p.update_effective_spend_each_quarter()
                    p.update_effectiveness()

            if is_initial_turn:
                total_eff = sum(p.effectiveness for p in participants if p.owner_name != self.player.name)
            else:
                total_eff = sum(p.effectiveness for p in participants)
            if total_eff <= 0:
                total_eff = 1.0

            for p in participants:
                if is_initial_turn and p.owner_name == self.player.name:
                    continue
                lost = p.revenue * 0.08
                p.revenue -= lost

            for p in participants:
                if is_initial_turn and p.owner_name == self.player.name:
                    continue
                share = p.effectiveness / total_eff
                p.revenue += share * churn_amount

            for p in participants:
                if is_initial_turn and p.owner_name == self.player.name:
                    continue
                share = p.effectiveness / total_eff
                p.revenue += share * growth_rev
                
                # Calculate and store growth percentage
                if previous_revenues[p] > 0 and not (is_initial_turn and p.owner_name == self.player.name):
                    growth_pct = ((p.revenue - previous_revenues[p]) / previous_revenues[p]) * 100
                    p.recent_growth.append(growth_pct)
                    # Limit the list to 4 quarters
                    if len(p.recent_growth) > 4:
                        p.recent_growth.pop(0)

            mk.last_quarter_total_revenue = sum(p.revenue for p in participants)

            # **** NEW: Update the market size each turn if not in recession ****
            if not mk.is_in_global_recession:
                # Increase market size by a compound rate.
                mk.size = mk.last_quarter_total_revenue # potentially change to mk.size = mk.last_quarter_total_revenue
            # potentially change to mk.size = mk.last_quarter_total_revenue


    def _handle_events(self):
            """
            Defer to event_manager. Done in process_turn, we skip here, or 
            you might want to do additional logic. 
            """
            pass

    def _resolve_pending_acquisitions(self):
        # same logic as your code
        to_remove=[]
        for (buyer, target_name, price, turn_submitted) in self.pending_acquisitions:
            if self.turn_index>= turn_submitted+1:
                # time to resolve
                t=None
                for ai in self.ai_companies:
                    if ai.name==target_name:
                        t= ai
                        break
                if not t:
                    self._push_competitor_news(f"Acquisition of {target_name} failed; no longer exists.")
                    to_remove.append((buyer,target_name,price,turn_submitted))
                    continue
                if buyer.cash< price:
                    self._push_competitor_news(f"Acquisition of {target_name} failed; insufficient funds.")
                    to_remove.append((buyer,target_name,price,turn_submitted))
                    continue
                # top2 growth check
                if self._is_target_in_top_2_growth(t):
                    self._push_competitor_news(f"Acquisition of {target_name} failed; top-2 growth.")
                    to_remove.append((buyer,target_name,price,turn_submitted))
                    continue
                # success
                buyer.cash-= price
                self._merge_companies(buyer, t)
                self._push_news(f"{buyer.name} acquired {target_name} for {format_money(price)}!")
                self.ai_companies.remove(t)
                to_remove.append((buyer,target_name,price,turn_submitted))

                self.pending_acquisitions = [acq for acq in self.pending_acquisitions if acq not in to_remove]


    def _is_target_in_top_2_growth(self, comp):
        # if any product's last growth>30 => top2
        for p in comp.products.values():
            if p.recent_growth and p.recent_growth[-1]>30:
                return True
        return False

    def _merge_companies(self, buyer: Company, target: Company):
        """
        Merge target company into buyer:
        - Cash, employees, and campuses are transferred.
        - Employee capacity and overhead are adjusted.
        - Products and bonds are absorbed.
        """
        if target.cash < 0:
            target.cash = 0

        buyer.cash += target.cash
        buyer.employees += target.employees
        buyer.campuses.extend(target.campuses)
        buyer.loans.extend(target.loans)
        buyer.bonds.extend(target.bonds)

        # Transfer and rename products if necessary
        for prod_name, prod in target.products.items():
            prod.owner_name = buyer.name
            if prod_name in buyer.products:
                buyer.products[f"{prod_name}_acq"] = prod
            else:
                buyer.products[prod_name] = prod

        # Clean up target after acquisition
        target.cash = 0
        target.employees = 0
        target.campuses.clear()
        target.products.clear()
        target.loans.clear()
        target.bonds.clear()


    def _update_finances(self):
        """
        Calls finances.update_finances
        """
        from finances import update_finances
        update_finances([self.player]+ self.ai_companies)

    def _log_turn_data(self):
        # done in process_turn via data_store.record_state
        pass

    def _print_turn_summary(self):
        # NO LONGER NEEDED - GUI handles this.
        pass

    def _check_endgame(self):
            
        # player losing
        if self.player.is_bankrupt():
            # print("\nYou lost! Your investors shut you down because your cash was negative 4 consecutive quarters.") # now handled by gui
            self._push_news("\nYou lost! Your investors shut you down because your cash was negative 4 consecutive quarters.")
            self._end_game()
            return
        # if no ai or if player MC>70
        total= self.player.market_cap
        for c in self.ai_companies:
            total+= c.market_cap
        if len(self.ai_companies)==0:
            # print("You acquired all of your competitors. Technopoly!") # now handled by gui
            self._push_news("You acquired all of your competitors. Technopoly!")
            self._end_game()
            return
        share= self.player.market_cap/ total if total>0 else 0
        if share>=0.7:
            # print("You got 70 percent of the market's total market capitalization. Technopoly!") # now handled by gui
            self._push_news("You got 70 percent of the market's total market capitalization. Technopoly!")
            self._end_game()

    def _end_game(self):
        self.game_over= True
        # print("\n=== GAME OVER ===") # now handled by gui
        # print("Historical Data:\n")
        # show some data
        #for snap in self.data_store.history:
            #t= snap["turn"]
            #print(f" Turn={t}, #Companies={len(snap['companies'])}")

    def _push_news(self, msg):
        """
        Add to news feed.
        """
        self.news_feed.append(msg)
        # Limit size to prevent memory issues
        if len(self.news_feed) > 100:  # Keep only the most recent 100 messages
            self.news_feed = self.news_feed[-100:]

    def _find_products_in_market(self, mname):
        results = []

        if self.player is not None:
            for p in self.player.products.values():
                if p.market_name == mname:
                    results.append(p)

        for c in self.ai_companies:
            for p in c.products.values():
                if p.market_name == mname:
                    results.append(p)

        # Include the imaginary product if the market has one
        for m in self.markets:
            if m.name == mname and hasattr(m, "imaginary_product"):
                results.append(m.imaginary_product)

        return results

    
    
    def _push_competitor_news(self, msg):
        """
        Add to competitor news, which is displayed separately.
        """
        self.competitor_news_feed.append(msg)
        # Limit size to prevent memory issues
        if len(self.competitor_news_feed) > 100:  # Keep only the most recent 100 messages
            self.competitor_news_feed = self.competitor_news_feed[-100:]


    def _company_has_product_in_market(self, comp, mname):
        for p in comp.products.values():
            if p.market_name==mname:
                return True
        return False

    def player_menu(self):
        # NO LONGER NEEDED - GUI handles player interaction.
        pass

    # ALL THE _menu_... METHODS ARE NO LONGER NEEDED.  The GUI handles this.

    ### acquisitions menu
    def _calculate_acquisition_price(self, target_company):
        """
        Minimum = (annualizedRevenue + max(netAssets, 0)) * 1.3
        Compare that to target's market_cap. Use whichever is higher.
        """
        # annualized revenue from last 3 quarters
        if target_company.past_quarter_revenues:
            avg_rev = sum(target_company.past_quarter_revenues)/len(target_company.past_quarter_revenues)
        else:
            avg_rev = target_company.total_revenue_this_quarter()
        annual_rev = avg_rev * 4

        
        net_assets = target_company.cash + sum(b.principal for b in target_company.bonds) - sum(ln.principal for ln in target_company.loans)
        if net_assets < 0:
            net_assets = 0

        min_cost = (annual_rev + net_assets) * 1.3
        # pick whichever is bigger: min_cost or the current market_cap
        base_price = max(min_cost, target_company.market_cap)
        return base_price
    
    
    def spawn_new_ai_companies(self):
        """
        Spawns 3 new AI companies (unless we already hit the 100-company limit).
        Each company selects its product markets at random, but only from the FIRST 8 initialized product markets.
        Each new product gets 3 employees automatically assigned (1 in marketing, R&D, and Q&A).
        """
        import random
        from utils import random_company_name, random_product_name
        from models import Company, Product

        # If we've already spawned 100 AI, do nothing
        if self.spawned_ai_count >= 100:
            return

        # Only allow new AI companies to select from the first 8 initialized markets
        available_markets = self.markets[:8]

        # Weighted tiers
        tiers = ["Startup", "Medium", "Large", "Big Tech"]
        weights = [0.50, 0.25, 0.15, 0.05]  # 50% Startup, 25% Medium, 15% Large, 5% Big Tech

        companies_to_spawn = 3
        for _ in range(companies_to_spawn):
            if self.spawned_ai_count >= 100:
                break  # never exceed 100 new spawns

            # Pick a tier based on weighted probabilities
            tier_choice = random.choices(tiers, weights, k=1)[0]
            new_name = random_company_name(
                prefixes=[
                    "Neuro", "Quantum", "Cyber", "Hyper", "Vertex", "Nexus", "Strato", "Omicron", "Zenith", "Titan",
                    "Echo", "Horizon", "Aether", "Aurora", "Byte", "Nano", "Synth", "Vortex", "Lyric", "Sigma",
                    "Celesti", "Axion", "Velox", "Sentinel", "Echelon", "Inferna", "Nova", "Sky", "Phantom", "Helix"
                ],
                suffixes=[
                    "Tech", "AI", "Soft", "Dynamics", "Labs", "Innovations", "Industries", "Solutions", "Cloud", "Systems",
                    "Logic", "Cybernetics", "Synapse", "Robotics", "Intelligence", "Analytics", "Works", "Data", "Quantum", "Networks",
                    "Engage", "Synergy", "Enterprises", "Computation", "Core", "Stream", "Matrix", "Node", "Forge", "Frameworks"
                ],
                used_names=self.used_company_names
            )

            # Create the new company object
            new_company = Company(new_name, tier_choice)

            # Choose campus, employees, cash, etc.
            if tier_choice == "Startup":
                new_company.campuses.append(("Garage", 0, 0.0, 10))
                new_company.employees = random.randint(5, 10)
                new_company.cash = random.uniform(500_000, 2_000_000)
                product_count = 1
            elif tier_choice == "Medium":
                new_company.campuses.append(("Small Office", 400_000, 0.02, 50))
                new_company.employees = random.randint(15, 35)
                new_company.cash = random.uniform(3_000_000, 5_000_000)
                product_count = 2
            elif tier_choice == "Large":
                new_company.campuses.append(("Large Office", 1_000_000, 0.04, 150))
                new_company.employees = random.randint(40, 70)
                new_company.cash = random.uniform(7_000_000, 15_000_000)
                product_count = 3
            else:
                # Big Tech
                new_company.campuses.append(("Large Building", 1_600_000, 0.08, 275))
                new_company.employees = random.randint(80, 140)
                new_company.cash = random.uniform(18_000_000, 28_000_000)
                product_count = 4

            # Create products for the new AI company (only from the first 8 initialized markets)
            chosen_markets = random.sample(available_markets, min(product_count, len(available_markets)))

            for market in chosen_markets:
                p = Product(new_company.name, market.name)

                # **Automatically assign 3 employees to each product (1 per type)**
                p.assigned_employees["r&d"] = 1
                p.assigned_employees["q&a"] = 1
                p.assigned_employees["marketing"] = 1

                # **Ensure these employees are counted in the company's finances**
                new_company.employees += 3

                # Start with $1k of revenue
                p.revenue = 1000.0

                # Deduct $1k from whichever competitor in that market has the highest revenue
                biggest_product = None
                biggest_revenue = 0.0
                for competitor in (self.ai_companies + [self.player]):
                    for prod_name, prod_obj in competitor.products.items():
                        if prod_obj.market_name == market.name and prod_obj.revenue > biggest_revenue:
                            biggest_revenue = prod_obj.revenue
                            biggest_product = prod_obj

                if biggest_product and biggest_product.revenue >= 1000.0:
                    biggest_product.revenue -= 1000.0
                elif biggest_product:
                    amount_to_deduct = min(biggest_product.revenue, 1000.0)
                    biggest_product.revenue -= amount_to_deduct

                # Store product in the new company under a unique product name
                product_name = random_product_name(self.used_product_names)
                new_company.products[product_name] = p

            # Add the new AI to our main list
            self.ai_companies.append(new_company)
            self.spawned_ai_count += 1

            # Push a competitor news announcement
            self._push_news(f"NEW COMPETITOR ALERT! {new_name} COMPANY SIZE: {tier_choice}")




    def spawn_new_product_market(self):
        """
        Spawns 1 new product market (unless 12 have already been spawned).
        Uses the following list of 12 market names in order:
            ["Semiconductors", "Autonomous Vehicles", "Blockchain", "Telecommunications",
            "VR Software", "Cloud Gaming", "Quantum Computing", "Smart Home",
            "Streaming Platforms", "GreenTech", "Wearables", "Video Games"]
        The new market has:
        - random initial revenue between $500k and $5m
        - random growth rate between 10% and 15%
        A news message is pushed with a rating of that growth rate
        (like 'Bad', 'Good', or 'Very Good' - purely cosmetic).
        """
        import random
        from models import Market, Product  # Ensure Product is imported

        spawn_market_names = [
            "Semiconductors", "Autonomous Vehicles", "Blockchain", "Telecommunications",
            "VR Software", "Cloud Gaming", "Quantum Computing", "Smart Home",
            "Streaming Platforms", "GreenTech", "Wearables", "Video Games"
        ]

        # If we already spawned 12 new markets, stop.
        if self.spawned_market_count >= 12:
            return

        # Use the next name in the list, based on how many we've spawned so far
        market_name = spawn_market_names[self.spawned_market_count]

        initial_revenue = random.uniform(500_000, 5_000_000)
        growth_rate = random.uniform(0.10, 0.15)

        new_market = Market(market_name)
        new_market.size = initial_revenue
        new_market.base_growth_rate = growth_rate
        new_market.growth_rate = growth_rate

        #imaginary product for proper rev distribution
        imaginary_product = Product("Initial Market Revenue", market_name)
        imaginary_product.effectiveness = 0.0
        imaginary_product.assigned_employees = {"r&d": 0, "q&a": 0, "marketing": 0}
        imaginary_product.revenue = initial_revenue  # Entire first quarter's revenue
        new_market.imaginary_product = imaginary_product  # Attach to market

        self.markets.append(new_market)
        self.spawned_market_count += 1

        # (Optional) Map the exact growth % to a descriptive label
        if growth_rate <= 0.11:
            rating = "Moderate"
        elif growth_rate <= 0.13:
            rating = "Good"
        else:
            rating = "Very Good"

        self._push_news(f"NEW PRODUCT MARKET! {market_name} SIZE: ~${initial_revenue:,.0f} GROWTH: {rating}")




def main():
    game = BusinessGameEngine()
    gui = TechnopolyGUI(game) 

if __name__=="__main__":
    main()

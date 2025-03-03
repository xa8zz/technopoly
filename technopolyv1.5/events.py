"""
events.py

Handles the new event system with:
 - 16 normal events (8 markets * ±5% growth)
 - 1 breaking event: Global Recession
One event is picked each quarter if not in a recession,
or if in a recession, we skip normal events for 3 quarters.

We store these in an 'EventManager' that is used by the game engine.
"""

import random
from typing import List
from models import Market

class GameEvent:
    """
    Represents a single event with:
     - name
     - description
     - effect function
     - is_breaking (True if global recession)
    """
    def __init__(self, name, description, is_breaking=False):
        self.name = name
        self.description = description
        self.is_breaking = is_breaking
        self.turn_happened = None

class EventManager:
    """
    Orchestrates the random event pick each quarter.
    - 16 normal events: each for a market (+5% or -5% growth).
    - 1 breaking event: global recession.
    If a global recession is in effect, we skip events for 3 quarters.
    """

    def __init__(self, markets: List[Market]):
        self.markets = markets
        self.last_5_events = []
        self.recession_active = False
        self.recession_quarters_left = 0

        # Pre-generate the normal events for each market ±5%
        self.normal_events = []
        for m in self.markets:
            # +5
            ename = f"Strong demand for {m.name}"
            edesc = f"+5% growth this quarter in {m.name}"
            self.normal_events.append(GameEvent(ename, edesc, is_breaking=False))

            # -5
            ename2 = f"Weak demand for {m.name}"
            edesc2 = f"-5% growth this quarter in {m.name}"
            self.normal_events.append(GameEvent(ename2, edesc2, is_breaking=False))

        # Breaking event: global recession
        self.recession_event = GameEvent(
            "Global Recession",
            "ALL markets freeze growth and shrink 5% each quarter for 3 quarters",
            is_breaking=True
        )

    def pick_random_event(self) -> GameEvent:
        """
        If not in a recession, 1/17 chance of the global recession,
        or pick from the normal events. Return the event chosen.
        """
        # If a global recession is active, we do not pick new events for 3 quarters
        if self.recession_active:
            return None  # means skip

        # 17 total events => 16 normal + 1 global
        # We'll do a 1/17 chance for global. If not chosen, pick from normal.
        r = random.randint(1, 17)
        if r == 17:
            return self.recession_event
        else:
            return random.choice(self.normal_events)

    # events.py: EventManager.apply_event

    def apply_event(self, event: GameEvent):
        """
        Actually implement the event's effect. Modify the relevant market or global.
        """
        if event is None:
            return  # skip if no event

        # Add to last_5_events
        if len(self.last_5_events) >= 5:
            self.last_5_events.pop(0)
        self.last_5_events.append(event)

        if event.is_breaking:
            # Global Recession: mark all markets for recession.
            self.recession_active = True
            self.recession_quarters_left = 3
            for m in self.markets:
                m.is_in_global_recession = True
                m.recession_quarters_left = 3
        else:
            # Before applying a new non-breaking event, reset each market's current growth rate to its base.
            for m in self.markets:
                m.growth_rate = m.base_growth_rate

            # Apply the temporary modifier.
            if "Strong demand for" in event.name:
                market_name = event.name.replace("Strong demand for ", "").strip()
                for mk in self.markets:
                    if mk.name == market_name:
                        # For a positive event, temporarily bump the growth rate.
                        mk.growth_rate += 0.05
            elif "Weak demand for" in event.name:
                market_name = event.name.replace("Weak demand for ", "").strip()
                for mk in self.markets:
                    if mk.name == market_name:
                        # For a negative event, temporarily lower the growth rate but not below zero.
                        mk.growth_rate = max(0, mk.growth_rate - 0.05)


    def format_news_feed(self, current_year, current_q):
        """
        Return a list of lines describing the last 5 events,
        but show the date they actually happened (from ev.turn_happened).
        """
        def compute_year_q_from_turn(turn_index):
            base_year = 2000  # match your start_year in main
            y_offset, q = divmod(turn_index, 4)
            return (base_year + y_offset, q + 1)

        lines = []
        for ev in reversed(self.last_5_events):
            if ev.turn_happened is not None:
                eyear, eq = compute_year_q_from_turn(ev.turn_happened)
            else:
                eyear, eq = (current_year, current_q)  # fallback if missing

            if ev.is_breaking:
                lines.append(f"{eyear}, Q{eq} - Global Recession (remaining {self.recession_quarters_left} quarters)")
            else:
                lines.append(f"{eyear}, Q{eq}: {ev.name}, {ev.description}")
        return lines

    
    def update_recession(self):
        """
        Update the global recession state by decrementing the recession counter.
        When the recession counter reaches 0, clear the recession flag.
        """
        if self.recession_active:
            self.recession_quarters_left -= 1
            if self.recession_quarters_left <= 0:
                self.recession_active = False
                # Also clear recession state on all markets.
                for m in self.markets:
                    m.is_in_global_recession = False
                    m.recession_quarters_left = 0


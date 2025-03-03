import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils import format_money
from models import Product
import os
import time
import threading
import concurrent.futures
import random
import math

class TechnopolyGUI:
    # Color Scheme
    COLORS = {
        "bg_primary": "#121212",        # Main background
        "bg_secondary": "#1E1E1E",      # Secondary background (cards, panels)
        "bg_tertiary": "#252525",       # Tertiary background (input fields)
        "accent_primary": "#3A86FF",    # Primary accent (buttons, highlights)
        "accent_secondary": "#8338EC",  # Secondary accent (selected items)
        "accent_success": "#06D6A0",    # Success indicators
        "accent_warning": "#FFD166",    # Warning indicators
        "accent_danger": "#EF476F",     # Danger/error indicators
        "text_primary": "#FFFFFF",      # Primary text
        "text_secondary": "#B0B0B0",    # Secondary text
        "text_tertiary": "#707070",     # Tertiary text (hints, disabled)
        "border": "#333333",            # Border color
        "tooltip": "#1A1A1A",           # Tooltip background
    }
    
    # Font Styles
    FONTS = {
        "heading1": ("Segoe UI", 32, "bold"),
        "heading2": ("Segoe UI", 24, "bold"),
        "heading3": ("Segoe UI", 18, "bold"),
        "subtitle": ("Segoe UI", 16, "normal"),
        "body": ("Segoe UI", 14, "normal"),
        "body_small": ("Segoe UI", 12, "normal"),
        "caption": ("Segoe UI", 10, "normal"),
        "button": ("Segoe UI", 14, "bold"),
    }

    def __init__(self, game_engine):
        self.game = game_engine
        self.competitor_moves = []
        
        # Configure CTk
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize root window
        self.root = ctk.CTk()
        self.root.title("Technopoly")
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        self.root.minsize(1024, 600)
        
        # Create splash screen
        self.show_splash_screen()
        
        self.root.mainloop()
    
    def show_splash_screen(self):
        """Show an animated splash screen before the main menu"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create splash screen container
        splash_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS["bg_primary"])
        splash_frame.pack(fill="both", expand=True)
        
        # Logo/title container with animation
        logo_frame = ctk.CTkFrame(splash_frame, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        # Title with animated reveal
        title_label = ctk.CTkLabel(
            logo_frame, 
            text="TECHNOPOLY", 
            font=("Impact", 80), 
            text_color=self.COLORS["bg_primary"]
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            logo_frame, 
            text="CORPORATE DOMINATION SIMULATOR", 
            font=self.FONTS["subtitle"],
            text_color=self.COLORS["bg_primary"]
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Progress bar
        loading_bar = ctk.CTkProgressBar(splash_frame, width=400)
        loading_bar.place(relx=0.5, rely=0.6, anchor="center")
        loading_bar.set(0)
        
        # Loading text
        loading_text = ctk.CTkLabel(
            splash_frame, 
            text="Loading...", 
            font=self.FONTS["body_small"],
            text_color=self.COLORS["text_tertiary"]
        )
        loading_text.place(relx=0.5, rely=0.65, anchor="center")
        
        # Animation function
        def animate_splash():
            # Fade in title
            for i in range(101):
                alpha = i / 100
                color = self.blend_colors(self.COLORS["bg_primary"], self.COLORS["text_primary"], alpha)
                title_label.configure(text_color=color)
                loading_bar.set(alpha * 0.3)  # First 30% of loading
                self.root.update()
                time.sleep(0.01)
            
            # Fade in subtitle
            for i in range(101):
                alpha = i / 100
                color = self.blend_colors(self.COLORS["bg_primary"], self.COLORS["text_secondary"], alpha)
                subtitle_label.configure(text_color=color)
                loading_bar.set(0.3 + (alpha * 0.3))  # Next 30%
                self.root.update()
                time.sleep(0.005)
            
            # Complete loading
            for i in range(41):
                loading_bar.set(0.6 + (i / 100))
                loading_texts = ["Initializing markets...", "Building companies...", "Analyzing competition...", "Setting up finances..."]
                if i % 10 == 0:
                    loading_text.configure(text=loading_texts[i // 10] if i // 10 < len(loading_texts) else "")
                self.root.update()
                time.sleep(0.05)
            
            loading_text.configure(text="Ready to launch")
            time.sleep(0.5)
            # Instead of directly calling self.main_menu() from the thread
            # Schedule it to run in the main thread
            self.root.after(0, self.main_menu)
        
        # Start animation in a separate thread
        threading.Thread(target=animate_splash, daemon=True).start()

    def main_menu(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.COLORS["bg_primary"])
        main_container.pack(fill="both", expand=True)
        
        # Left side - Image/Logo area (40% width)
        left_panel = ctk.CTkFrame(main_container, fg_color=self.COLORS["bg_secondary"], corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=0)
        
        # Title with glow effect
        title_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        title_container.place(relx=0.5, rely=0.35, anchor="center")
        
        # Main title
        title_label = ctk.CTkLabel(
            title_container, 
            text="TECHNOPOLY", 
            font=("Impact", 60),
            text_color=self.COLORS["text_primary"]
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_container, 
            text="CORPORATE DOMINATION SIMULATOR",
            font=self.FONTS["subtitle"],
            text_color=self.COLORS["text_secondary"]
        )
        subtitle_label.pack()
        
        # Credit
        credit_label = ctk.CTkLabel(
            left_panel, 
            text="Made by Om with love :)",
            font=self.FONTS["caption"],
            text_color=self.COLORS["text_tertiary"]
        )
        credit_label.place(relx=0.5, rely=0.9, anchor="center")
        
        # Right side - Menu buttons (60% width)
        right_panel = ctk.CTkFrame(main_container, fg_color=self.COLORS["bg_primary"], corner_radius=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Menu container
        menu_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        menu_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Menu buttons with hover effect
        button_width = 240
        button_height = 60
        button_spacing = 20
        
        # Button styling function
        def create_menu_button(parent, text, command, is_primary=True):
            if is_primary:
                btn = ctk.CTkButton(
                    parent,
                    text=text,
                    font=self.FONTS["button"],
                    width=button_width,
                    height=button_height,
                    corner_radius=8,
                    fg_color=self.COLORS["accent_primary"],
                    hover_color=self.blend_colors(self.COLORS["accent_primary"], "#FFFFFF", 0.2),
                    command=command
                )
            else:
                btn = ctk.CTkButton(
                    parent,
                    text=text,
                    font=self.FONTS["button"],
                    width=button_width,
                    height=button_height,
                    corner_radius=8,
                    fg_color="transparent",
                    text_color=self.COLORS["text_primary"],
                    hover_color=self.COLORS["bg_secondary"],
                    border_width=2,
                    border_color=self.COLORS["border"],
                    command=command
                )
            return btn
        
        # Play button
        play_button = create_menu_button(menu_container, "PLAY", self.start_game)
        play_button.pack(pady=(0, button_spacing))
        
        # Tutorial button
        tutorial_button = create_menu_button(menu_container, "TUTORIAL", self.show_tutorial, is_primary=False)
        tutorial_button.pack(pady=(0, button_spacing))
        
        # Exit button
        exit_button = create_menu_button(menu_container, "EXIT", self.root.quit, is_primary=False)
        exit_button.pack()
        
        # Version text
        version_label = ctk.CTkLabel(
            right_panel, 
            text="v1.0.0",
            font=self.FONTS["caption"],
            text_color=self.COLORS["text_tertiary"]
        )
        version_label.place(relx=0.95, rely=0.95, anchor="se")
        
        # Add animated background elements
        self.add_animated_background(main_container)
    
    def add_animated_background(self, parent):
        """Add subtle animated elements to the background"""
        canvas = tk.Canvas(parent, highlightthickness=0, bg=self.COLORS["bg_primary"])
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Fix: Use lift on other widgets instead of lower on canvas
        for child in parent.winfo_children():
            if child != canvas:
                child.lift()
        
        # Create grid lines
        grid_color = "#222222"
        grid_spacing = 40
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        if width <= 1 or height <= 1:  # Window not fully initialized
            width, height = 1280, 720
        
        # Draw horizontal and vertical grid lines
        for i in range(0, width + grid_spacing, grid_spacing):
            canvas.create_line(i, 0, i, height, fill=grid_color, width=1)
        
        for i in range(0, height + grid_spacing, grid_spacing):
            canvas.create_line(0, i, width, i, fill=grid_color, width=1)
        
        # Add floating particles
        particles = []
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 5)
            speed = random.uniform(0.2, 1.0)
            angle = random.uniform(0, 2 * math.pi)
            alpha = random.uniform(0.1, 0.3)
            
            # FIX: Use a lighter version of the color instead of alpha for Canvas
            # Canvas doesn't support RGBA hex colors
            color = self.blend_colors(self.COLORS["bg_primary"], self.COLORS["accent_primary"], alpha)
            
            particle = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
            particles.append({
                "id": particle,
                "x": x,
                "y": y,
                "size": size,
                "speed": speed,
                "angle": angle
            })
        
        # Add a flag to track if animation should continue
        self._animation_running = True
        
        def animate_particles():
            nonlocal width, height
            
            # Update width/height in case of window resize
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            if current_width > 1 and current_height > 1:
                width, height = current_width, current_height
            
            for p in particles:
                # Move particle
                p["x"] += math.cos(p["angle"]) * p["speed"]
                p["y"] += math.sin(p["angle"]) * p["speed"]
                
                # Wrap around edges
                if p["x"] < -p["size"]:
                    p["x"] = width + p["size"]
                elif p["x"] > width + p["size"]:
                    p["x"] = -p["size"]
                
                if p["y"] < -p["size"]:
                    p["y"] = height + p["size"]
                elif p["y"] > height + p["size"]:
                    p["y"] = -p["size"]
                
                # Update particle position
                canvas.coords(
                    p["id"], 
                    p["x"], p["y"], 
                    p["x"] + p["size"], p["y"] + p["size"]
                )
            
            # Schedule next animation frame only if still running
            if parent.winfo_exists() and self._animation_running:
                parent.after(50, animate_particles)
        
        # Start animation
        parent.after(50, animate_particles)
        
        # Store reference to parent to stop animation later
        self._animated_background_parent = parent

    def blend_colors(self, start_color: str, end_color: str, alpha: float) -> str:
        """
        Linearly blends between start_color and end_color by alpha.
        Both colors should be strings in "#RRGGBB" format.
        alpha is a float between 0.0 (start_color) and 1.0 (end_color).
        Returns a color string in "#RRGGBB" format.
        """
        # Remove '#' and convert hex to integers.
        start_color = start_color.lstrip('#')
        end_color = end_color.lstrip('#')
        sr, sg, sb = int(start_color[0:2], 16), int(start_color[2:4], 16), int(start_color[4:6], 16)
        er, eg, eb = int(end_color[0:2], 16), int(end_color[2:4], 16), int(end_color[4:6], 16)

        # Compute the blended color components.
        nr = int(sr + (er - sr) * alpha)
        ng = int(sg + (eg - sg) * alpha)
        nb = int(sb + (eb - sb) * alpha)

        return f'#{nr:02x}{ng:02x}{nb:02x}'

    def to_hex_with_alpha(self, color, alpha):
        """Convert a color to hex with an alpha value."""
        alpha_int = int(alpha * 255)
        
        # Handle hex color strings
        if isinstance(color, str) and color.startswith("#"):
            # Extract RGB values from hex
            color = color.lstrip('#')
            if len(color) == 6:
                r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
                return f'#{r:02x}{g:02x}{b:02x}{alpha_int:02x}'
        
        # Default fallback for other color formats
        try:
            # Try to use tkinter's color parsing
            rgb = self.root.winfo_rgb(color)
            r, g, b = rgb[0] // 256, rgb[1] // 256, rgb[2] // 256
            return f'#{r:02x}{g:02x}{b:02x}{alpha_int:02x}'
        except Exception:
            # Last resort fallback
            return f'#000000{alpha_int:02x}'

    def fade_in(self, widget, steps: int = 50, interval: int = 20, start_color: str = None, final_color: str = "white"):
        """
        Fades in the widget text from a starting color to a final color.
        """
        if start_color is None:
            start_color = self.COLORS["bg_primary"]

        # Ensure final_color is in "#RRGGBB" format.
        if final_color == "white":
            final_color = "#ffffff"

        def increase_alpha(i: int):
            try:
                if i <= steps:
                    blend_factor = i / steps
                    new_color = self.blend_colors(start_color, final_color, blend_factor)
                    widget.configure(text_color=new_color)
                    self.root.after(interval, increase_alpha, i + 1)
                else:
                    widget.configure(text_color=final_color)
            except tk.TclError:
                # The widget has been destroyed; exit the fade-in.
                return

        increase_alpha(0)

    def start_game(self):
        """Start the game with player setup"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Initialize player with default values
        self.game._initialize_player()
        
        # Show player setup panel
        self.show_player_setup_panel()

    def show_player_setup_panel(self):
        """Show the player setup screen with market selection"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Re-initialize the game: create AI companies and the player
        self.game._create_ai_companies()
        self.game._initialize_player()
        
        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.COLORS["bg_primary"])
        main_container.pack(fill="both", expand=True)
        
        # Left panel for company setup (40% width)
        left_panel = ctk.CTkFrame(main_container, fg_color=self.COLORS["bg_secondary"], corner_radius=0, width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 1), pady=0)
        left_panel.pack_propagate(False)  # Fixed width
        
        # Setup form container
        setup_form = ctk.CTkFrame(left_panel, fg_color="transparent")
        setup_form.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
        
        # Company setup header
        setup_header = ctk.CTkLabel(
            setup_form,
            text="COMPANY SETUP",
            font=self.FONTS["heading2"],
            text_color=self.COLORS["text_primary"]
        )
        setup_header.pack(pady=(0, 30), anchor="w")
        
        # Company name input
        name_label = ctk.CTkLabel(
            setup_form,
            text="COMPANY NAME",
            font=self.FONTS["body"],
            text_color=self.COLORS["text_secondary"]
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            setup_form,
            font=self.FONTS["body"],
            fg_color=self.COLORS["bg_tertiary"],
            border_color=self.COLORS["border"],
            text_color=self.COLORS["text_primary"],
            height=40,
            placeholder_text="Enter your company name"
        )
        name_entry.pack(fill="x", pady=(0, 20))
        name_entry.insert(0, "My Startup")
        
        # Market selection instructions
        market_label = ctk.CTkLabel(
            setup_form,
            text="SELECT STARTING MARKET",
            font=self.FONTS["body"],
            text_color=self.COLORS["text_secondary"]
        )
        market_label.pack(anchor="w", pady=(0, 5))
        
        market_desc = ctk.CTkLabel(
            setup_form,
            text="Choose a market to launch your first product. Consider competitiveness, growth potential, and overall market size.",
            font=self.FONTS["body_small"],
            text_color=self.COLORS["text_tertiary"],
            wraplength=320,
            justify="left"
        )
        market_desc.pack(anchor="w", pady=(0, 20))
        
        # Start button
        start_button = ctk.CTkButton(
            setup_form,
            text="START GAME",
            font=self.FONTS["button"],
            height=50,
            fg_color=self.COLORS["accent_primary"],
            hover_color=self.blend_colors(self.COLORS["accent_primary"], "#FFFFFF", 0.2),
            state="disabled"  # Initially disabled until market is selected
        )
        start_button.pack(fill="x", pady=(20, 0))
        
        # Right panel for market selection (60% width)
        right_panel = ctk.CTkFrame(main_container, fg_color=self.COLORS["bg_primary"], corner_radius=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Markets header
        markets_header = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        markets_header.pack(fill="x", padx=20, pady=(20, 10))
        
        markets_title = ctk.CTkLabel(
            markets_header,
            text="AVAILABLE MARKETS",
            font=self.FONTS["heading3"],
            text_color=self.COLORS["text_primary"],
            anchor="w"
        )
        markets_title.pack(side="left")
        
        # Scrollable markets list
        markets_scroll = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="transparent",
            corner_radius=0,
            border_width=0
        )
        markets_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Set up market selection behavior
        self.selected_market = None
        
        def on_market_select(market, card):
            # Clear previous selection
            for child in markets_scroll.winfo_children():
                child.configure(fg_color=self.COLORS["bg_secondary"])
            
            # Highlight selected card
            card.configure(fg_color=self.COLORS["accent_secondary"])
            
            # Update selected market
            self.selected_market = market
            
            # Enable start button
            start_button.configure(state="normal")
        
        # Create market cards
        for m in self.game.markets:
            competitor_count = self.game._count_products_in_market(m.name)
            quarterly_revenue = format_money(m.size / 4.0)
            growth_category = self.game._categorize_growth_rate(m.growth_rate)
            
            # Create card
            card = ctk.CTkFrame(
                markets_scroll,
                fg_color=self.COLORS["bg_secondary"],
                corner_radius=10,
                border_width=0
            )
            card.pack(fill="x", pady=5, padx=5)
            
            # Make card clickable
            card.bind("<Button-1>", lambda e, market=m, card=card: on_market_select(market, card))
            
            # Market name
            name_label = ctk.CTkLabel(
                card, 
                text=m.name,
                font=self.FONTS["heading3"],
                text_color=self.COLORS["text_primary"],
                anchor="w"
            )
            name_label.pack(anchor="w", padx=15, pady=(15, 5))
            name_label.bind("<Button-1>", lambda e, market=m, card=card: on_market_select(market, card))
            
            # Market metrics
            metrics_text = f"Revenue: {quarterly_revenue}/quarter • Growth: {growth_category} • Competitors: {competitor_count}"
            metrics_label = ctk.CTkLabel(
                card, 
                text=metrics_text,
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"],
                anchor="w"
            )
            metrics_label.pack(anchor="w", padx=15, pady=(0, 15))
            metrics_label.bind("<Button-1>", lambda e, market=m, card=card: on_market_select(market, card))
            
        # Configure start button command
        def confirm_setup():
            company_name = name_entry.get().strip()
            if not company_name:
                self.show_notification("Please enter a valid company name", "error")
                return
                
            if not self.selected_market:
                self.show_notification("Please select a market first", "error") 
                return
                
            # Set player name
            self.game.player.name = company_name
            chosen_m = self.selected_market
            
            # Create initial product
            from models import Product
            p = Product(self.game.player.name, chosen_m.name)
            p.assigned_employees["r&d"] = 0
            p.assigned_employees["q&a"] = 0
            p.assigned_employees["marketing"] = 0
            
            # Adjust product based on market competition
            prods = self.game._find_products_in_market(chosen_m.name)
            if prods:
                biggest = max(prods, key=lambda x: x.revenue)
                if biggest.revenue >= 10_000:
                    biggest.revenue -= 10_000
                    p.revenue = 10_000
                min_eff = min(prod.effectiveness for prod in prods)
                p.effectiveness = max(0, min_eff - (min_eff * 0.4))
                
            # Add product to player's portfolio
            self.game.player.products[chosen_m.name] = p
            
            # Record initial state
            self.game.data_store.record_state(
                self.game.turn_index,
                [self.game.player] + self.game.ai_companies,
                self.game.markets
            )
            
            # Create main game interface and process first turn
            self.create_main_game_interface()
            self.end_turn()
        
        start_button.configure(command=confirm_setup)
        
        # Add notification area at bottom of right panel
        self.notification_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=30)
        self.notification_frame.pack(fill="x", pady=(0, 10))
        
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=self.FONTS["body_small"],
            text_color=self.COLORS["accent_danger"]
        )
        self.notification_label.pack()

    def update_competitor_moves(self):
        """Update the competitor moves panel with latest news"""
        # Clear existing news
        for widget in self.competitor_news_frame.winfo_children():
            widget.destroy()
        
        # Get competitor news from the game engine
        competitor_moves = self.game.competitor_news_feed[:] 
        self.game.competitor_news_feed.clear()  # Clear after copying
        
        if not competitor_moves:
            no_news = ctk.CTkLabel(
                self.competitor_news_frame,
                text="No industry news this quarter",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_tertiary"]
            )
            no_news.pack(pady=20)
            return
        
        # Categorize messages
        def categorize_message(msg):
            msg_lower = msg.lower()
            if "hire" in msg_lower:
                return "Hiring"
            elif "fire" in msg_lower:
                return "Firing"
            elif "acquisition" in msg_lower or "acquired" in msg_lower:
                return "Acquisitions"
            elif "loan" in msg_lower:
                return "Loans"
            elif "bond" in msg_lower:
                return "Bonds"
            elif "campus" in msg_lower:
                return "Campus Expansion"
            elif "assigned" in msg_lower or "removed" in msg_lower:
                return "Employee Reassignments"
            else:
                return "Other"
                
        # Group messages by category
        categories = {}
        for msg in competitor_moves:
            cat = categorize_message(msg)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(msg)
        
        # Define the display order
        category_order = [
            "Hiring",
            "Firing",
            "Acquisitions",
            "Loans",
            "Bonds",
            "Campus Expansion",
            "Employee Reassignments",
            "Other"
        ]
        
        # Get the width of the competitor news frame
        panel_width = self.competitor_news_frame.winfo_width() - 30  # Leave margin for padding
        wrap_length = max(200, panel_width)  # Minimum 200px
        
        # Display categories in order
        for cat in category_order:
            if cat in categories:
                # Category header
                header = ctk.CTkLabel(
                    self.competitor_news_frame,
                    text=cat,
                    font=self.FONTS["body"],
                    text_color=self.COLORS["text_primary"],
                    anchor="w"
                )
                header.pack(fill="x", padx=10, pady=(10, 2))
                
                # Messages in this category
                for msg in categories[cat]:
                    msg_card = ctk.CTkFrame(
                        self.competitor_news_frame,
                        fg_color=self.COLORS["bg_tertiary"],
                        corner_radius=5
                    )
                    msg_card.pack(fill="x", padx=15, pady=1)
                    
                    msg_label = ctk.CTkLabel(
                        msg_card,
                        text=msg,
                        font=self.FONTS["body_small"],
                        text_color=self.COLORS["text_secondary"],
                        wraplength=wrap_length,
                        anchor="w",
                        justify="left"
                    )
                    msg_label.pack(fill="x", padx=10, pady=5)

    def update_news_feed(self, news):
        """Update the news feed with latest game events"""
        # Clear existing news
        for label in self.news_feed_labels:
            label.destroy()
        self.news_feed_labels = []
        
        if not news:
            no_news = ctk.CTkLabel(
                self.news_feed_scroll,
                text="No news this quarter",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_tertiary"]
            )
            no_news.pack(pady=20)
            self.news_feed_labels.append(no_news)
            return
        
        # Add news items in card format
        for item in news:
            news_card = ctk.CTkFrame(
                self.news_feed_scroll,
                fg_color=self.COLORS["bg_secondary"],
                corner_radius=5
            )
            news_card.pack(fill="x", pady=5)
            
            news_label = ctk.CTkLabel(
                news_card,
                text=item,
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_primary"],
                wraplength=380,
                justify="left"
            )
            news_label.pack(padx=10, pady=10, anchor="w")
            self.news_feed_labels.append(news_card)

    def update_product_summary(self):
        """Update the product summary section on the summary tab"""
        # Clear existing summary
        for widget in self.product_summary_scroll.winfo_children():
            widget.destroy()
        
        if not self.game.player.products:
            no_products = ctk.CTkLabel(
                self.product_summary_scroll,
                text="No products in portfolio",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_tertiary"]
            )
            no_products.pack(pady=20)
            return
        
        # Add product cards
        for name, product in self.game.player.products.items():
            prod_card = ctk.CTkFrame(
                self.product_summary_scroll,
                fg_color=self.COLORS["bg_secondary"],
                corner_radius=5
            )
            prod_card.pack(fill="x", pady=5)
            
            header_frame = ctk.CTkFrame(prod_card, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            name_label = ctk.CTkLabel(
                header_frame,
                text=name,
                font=self.FONTS["body"],
                text_color=self.COLORS["text_primary"],
                anchor="w"
            )
            name_label.pack(side="left")
            
            market_label = ctk.CTkLabel(
                header_frame,
                text=f"in {product.market_name}",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"],
                anchor="e"
            )
            market_label.pack(side="right")
            
            # Product metrics
            metrics_frame = ctk.CTkFrame(prod_card, fg_color="transparent")
            metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            revenue_frame = self.create_metric_row(
                metrics_frame,
                "Revenue",
                format_money(product.revenue)
            )
            revenue_frame.pack(fill="x", pady=2)
            
            effectiveness_frame = self.create_metric_row(
                metrics_frame,
                "Effectiveness",
                f"{product.effectiveness:.2f}"
            )
            effectiveness_frame.pack(fill="x", pady=2)
            
            employees_text = (
                f"R&D: {product.assigned_employees['r&d']} | "
                f"Q&A: {product.assigned_employees['q&a']} | "
                f"Marketing: {product.assigned_employees['marketing']}"
            )
            employees_frame = self.create_metric_row(
                metrics_frame,
                "Employees",
                employees_text
            )
            employees_frame.pack(fill="x", pady=2)

    def update_summary_tab(self):
        """Update all elements in the summary tab"""
        # Update quarterly metrics
        player = self.game.player
        revenue = player.total_revenue_this_quarter()
        profit = player.quarterly_profit()
        emp_cost = player.employees * 25000
        overhead = emp_cost * player.overhead_percent()
        total_costs = player.total_spending_this_quarter()
        total_debt = sum(ln.principal for ln in player.loans)
        debt_service = sum(ln.monthly_payment for ln in player.loans) * 4
        
        self.quarterly_metrics["Revenue"].configure(text=format_money(revenue))
        self.quarterly_metrics["Profit"].configure(text=format_money(profit))
        self.quarterly_metrics["Employee Cost"].configure(text=format_money(emp_cost))
        self.quarterly_metrics["Overhead Cost"].configure(text=format_money(overhead))
        self.quarterly_metrics["Total Costs"].configure(text=format_money(total_costs))
        self.quarterly_metrics["MarketCap"].configure(text=format_money(player.market_cap))
        self.quarterly_metrics["Debt"].configure(text=format_money(total_debt))
        self.quarterly_metrics["Debt Servicing"].configure(text=format_money(debt_service))
        
        # Update investments metrics
        total_bonds = sum(b.principal for b in player.bonds)
        bond_income = sum(b.principal*(b.annual_rate/4) for b in player.bonds)
        
        self.investments_metrics["Bonds (Principal)"].configure(text=format_money(total_bonds))
        self.investments_metrics["Bonds (Quarterly Income)"].configure(text=format_money(bond_income))
        self.investments_metrics["Campuses"].configure(text=str(len(player.campuses)))
        self.investments_metrics["Total Employees"].configure(text=str(player.employees))
        self.investments_metrics["Employee Capacity"].configure(text=str(player.employee_capacity()))
        
        # Update product summary
        self.update_product_summary()

    def update_live_info(self):
        """Update live info display in the top bar"""
        player = self.game.player
        
        # Update the company name (in case it was changed)
        self.company_name_label.configure(text=player.name)
        
        # Update date display
        year, quarter = self.game._get_date()
        self.date_label.configure(text=f"Year {year}, Q{quarter}")
        
        # Update metrics
        self.cash_label.configure(text=format_money(player.cash))
        
        total_debt = sum(ln.principal for ln in player.loans)
        self.debt_label.configure(text=f"Debt: {format_money(total_debt)}")
        
        self.employees_label.configure(text=f"Employees: {player.employees}/{player.employee_capacity()}")
        
        self.market_cap_label.configure(text=f"Market Cap: {format_money(player.market_cap)}")
        
        # Update dominance percentage in stock market tab
        total_market_cap = sum(comp.market_cap for comp in [player] + self.game.ai_companies if comp.market_cap > 0)
        if total_market_cap > 0:
            dominance = (player.market_cap / total_market_cap) * 100
            self.dominance_label.configure(text=f"Your Market Dominance: {dominance:.1f}%")
            
            # Change color based on dominance
            if dominance >= 50:
                self.dominance_label.configure(text_color=self.COLORS["accent_success"])
            elif dominance >= 25:
                self.dominance_label.configure(text_color=self.COLORS["accent_warning"])
            else:
                self.dominance_label.configure(text_color=self.COLORS["text_secondary"])

    def end_turn(self):
        """Process the end of turn and update the UI"""
        # Disable the end turn button during processing
        self.end_turn_button.configure(
            state="disabled",
            text="PROCESSING...",
            fg_color=self.COLORS["bg_tertiary"]
        )
        self.root.update()
        
        # Process turn in a separate thread to avoid UI freezing
        def process_turn():
            # Store the current turn's competitor moves
            self.competitor_moves = []
            
            # Re-randomize Market Growth Every 8 Turns
            if self.game.turn_index > 0 and (self.game.turn_index % 8) == 0:
                for mk in self.game.markets:
                    mk.base_growth_rate = random.uniform(0.05, 0.15)
                    mk.growth_rate = mk.base_growth_rate  # Reset growth rate

            # Resolve any pending acquisitions
            self.game._resolve_pending_acquisitions()

            # Run AI actions
            for comp in self.game.ai_companies:
                self.game.ai_controller.ai_take_actions(comp)
                
            # Spawn new companies and markets periodically
            if self.game.turn_index > 0 and (self.game.turn_index % 4) == 0:
                self.game.spawn_new_ai_companies()

            if self.game.turn_index > 0 and (self.game.turn_index % 3) == 0:
                self.game.spawn_new_product_market()

            # Distribute Revenue & Update Market Size
            self.game._distribute_revenue_all_markets()

            # Trigger Events
            ev = self.game.event_manager.pick_random_event()
            self.game.event_manager.apply_event(ev)
            if ev is not None:
                ev.turn_happened = self.game.turn_index
                self.game._push_news(f"{ev.name}: {ev.description}")
            
            self.game.event_manager.update_recession()

            # Update Finances
            self.game._update_finances()

            # Update bankruptcy status
            self.game.player.update_negative_cash_quarters()
            
            # Store data for the turn
            self.game.data_store.record_state(self.game.turn_index + 1, 
                                             [self.game.player] + self.game.ai_companies, 
                                             self.game.markets)
            
            # Check for game over conditions
            is_bankrupt = self.game.player.is_bankrupt()
            
            # Check for victory condition
            total_market_cap = sum(comp.market_cap for comp in [self.game.player] + self.game.ai_companies if comp.market_cap > 0)
            is_winner = False
            if total_market_cap > 0:
                player_dominance = (self.game.player.market_cap / total_market_cap)
                is_winner = player_dominance > 0.7 or len(self.game.ai_companies) == 0
            
            # Increment turn counter
            self.game.turn_index += 1
            
            # Prepare news for display
            year, quarter = self.game._get_date()
            news = self.game.event_manager.format_news_feed(year, quarter)
            news.extend(self.game.news_feed)
            self.game.news_feed.clear()
            
            # Handle game over conditions
            if is_bankrupt:
                self.root.after(0, lambda: self.show_game_over("BANKRUPTCY", "Your company has gone bankrupt!"))
                return
                
            if is_winner:
                self.root.after(0, lambda: self.show_game_over("VICTORY", "You've achieved market dominance and won the game!"))
                return
            
            # Update the UI with new game state
            self.root.after(0, lambda: self.update_all_tabs())
            self.root.after(0, lambda: self.update_news_feed(news))
            self.root.after(0, lambda: self.update_competitor_moves())
            
            # Re-enable the end turn button
            self.root.after(0, lambda: self.end_turn_button.configure(
                state="normal",
                text="END QUARTER",
                fg_color=self.COLORS["accent_primary"]
            ))
        
        # Start turn processing in a separate thread
        threading.Thread(target=process_turn, daemon=True).start()

    def show_game_over(self, status, message):
        """Show game over screen with modern design"""
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create game over container
        game_over_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS["bg_primary"])
        game_over_frame.pack(fill="both", expand=True)
        
        # Center content
        content_frame = ctk.CTkFrame(game_over_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Game over title
        title_text = "GAME OVER" if status == "BANKRUPTCY" else "CONGRATULATIONS"
        title_color = self.COLORS["accent_danger"] if status == "BANKRUPTCY" else self.COLORS["accent_success"]
        
        title_label = ctk.CTkLabel(
            content_frame,
            text=title_text,
            font=("Impact", 60),
            text_color=title_color
        )
        title_label.pack(pady=(0, 20))
        
        # Status
        status_label = ctk.CTkLabel(
            content_frame,
            text=status,
            font=self.FONTS["heading2"],
            text_color=self.COLORS["text_primary"]
        )
        status_label.pack(pady=(0, 30))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=self.FONTS["subtitle"],
            text_color=self.COLORS["text_secondary"]
        )
        message_label.pack(pady=(0, 40))
        
        # Final stats frame
        stats_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.COLORS["bg_tertiary"],
            corner_radius=10
        )
        stats_frame.pack(pady=(0, 40), padx=20, fill="x")
        
        # Company stats
        company_label = ctk.CTkLabel(
            stats_frame,
            text=f"COMPANY: {self.game.player.name}",
            font=self.FONTS["heading3"],
            text_color=self.COLORS["text_primary"]
        )
        company_label.pack(pady=(15, 10), padx=20, anchor="w")
        
        # Stats grid
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(padx=20, pady=(0, 15), fill="x")
        
        # Configure grid
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        # Duration
        year, quarter = self.game._get_date()
        duration_frame = self.create_metric_row(
            stats_grid,
            "Game Duration",
            f"{year} years, {quarter} quarters"
        )
        duration_frame.grid(row=0, column=0, sticky="ew", pady=2)
        
        # Final market cap
        market_cap_frame = self.create_metric_row(
            stats_grid,
            "Final Market Cap",
            format_money(self.game.player.market_cap)
        )
        market_cap_frame.grid(row=0, column=1, sticky="ew", pady=2)
        
        # Total revenue
        revenue = self.game.player.total_revenue_this_quarter()
        revenue_frame = self.create_metric_row(
            stats_grid,
            "Final Quarterly Revenue",
            format_money(revenue)
        )
        revenue_frame.grid(row=1, column=0, sticky="ew", pady=2)
        
        # Products
        products_frame = self.create_metric_row(
            stats_grid,
            "Products",
            str(len(self.game.player.products))
        )
        products_frame.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Configure grid
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # New game button
        new_game_button = ctk.CTkButton(
            button_frame,
            text="NEW GAME",
            font=self.FONTS["button"],
            height=50,
            fg_color=self.COLORS["accent_primary"],
            hover_color=self.blend_colors(self.COLORS["accent_primary"], "#FFFFFF", 0.2),
            command=self.start_game
        )
        new_game_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Main menu button
        main_menu_button = ctk.CTkButton(
            button_frame,
            text="MAIN MENU",
            font=self.FONTS["button"],
            height=50,
            fg_color=self.COLORS["bg_tertiary"],
            hover_color=self.COLORS["bg_secondary"],
            text_color=self.COLORS["text_primary"],
            command=self.main_menu
        )
        main_menu_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def update_all_tabs(self):
        """Update all tabs with current game data"""
        # Update live info in top bar
        self.update_live_info()
        
        # Update summary tab
        self.update_summary_tab()
        
        # Update products tab
        self.update_products_tab()
        
        # Update finances tab
        self.update_finances_tab()
        
        # Update stock market tab
        self.update_stock_market_tab()
        
        # Update acquisitions tab
        self.update_acquisitions_tab()
        
        # Update operations tab
        self.update_operations_tab()

    def stop_background_animation(self):
        """Stop the background animation if it's running"""
        self._animation_running = False

    # Add missing methods at the end of the class

    def view_market_rankings_dialog(self):
        """Show dialog with product rankings for each market"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Market Rankings")
        dialog.geometry("900x600")
        dialog.grab_set()
        
        # Main container
        main_frame = ctk.CTkFrame(dialog, fg_color=self.COLORS["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a tabbed interface for different markets
        market_tabs = ctk.CTkTabview(main_frame)
        market_tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs for each market
        for market in self.game.markets:
            market_name = market.name
            market_tabs.add(market_name)
            
            # Create a frame for this market's products
            market_frame = ctk.CTkFrame(
                market_tabs.tab(market_name), 
                fg_color="transparent"
            )
            market_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Find products in this market
            products = self.game._find_products_in_market(market_name)
            
            if not products:
                no_products = ctk.CTkLabel(
                    market_frame,
                    text=f"No products in the {market_name} market yet.",
                    font=self.FONTS["body"],
                    text_color=self.COLORS["text_tertiary"]
                )
                no_products.pack(pady=50)
                continue
                
            # Sort products by revenue (highest first)
            products.sort(key=lambda p: p.revenue, reverse=True)
            
            # Create header row
            header_frame = ctk.CTkFrame(
                market_frame,
                fg_color=self.COLORS["bg_secondary"],
                corner_radius=5
            )
            header_frame.pack(fill="x", pady=(0, 10))
            
            # Configure columns
            header_frame.columnconfigure(0, weight=1)  # Rank
            header_frame.columnconfigure(1, weight=3)  # Company
            header_frame.columnconfigure(2, weight=2)  # Revenue
            header_frame.columnconfigure(3, weight=2)  # Quality
            
            # Header labels
            rank_header = ctk.CTkLabel(
                header_frame,
                text="Rank",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"]
            )
            rank_header.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            company_header = ctk.CTkLabel(
                header_frame,
                text="Company",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"]
            )
            company_header.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            revenue_header = ctk.CTkLabel(
                header_frame,
                text="Revenue",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"]
            )
            revenue_header.grid(row=0, column=2, padx=10, pady=5, sticky="w")
            
            quality_header = ctk.CTkLabel(
                header_frame,
                text="Quality",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"]
            )
            quality_header.grid(row=0, column=3, padx=10, pady=5, sticky="w")
            
            # Product rows
            for i, product in enumerate(products):
                row_frame = ctk.CTkFrame(
                    market_frame,
                    fg_color=self.COLORS["bg_tertiary"] if i % 2 == 0 else "transparent",
                    corner_radius=5
                )
                row_frame.pack(fill="x", pady=2)
                
                # Configure columns (same as header)
                row_frame.columnconfigure(0, weight=1)
                row_frame.columnconfigure(1, weight=3)
                row_frame.columnconfigure(2, weight=2)
                row_frame.columnconfigure(3, weight=2)
                
                # Determine if this is the player's product
                is_player = product.owner_name == self.game.player.name
                text_color = self.COLORS["accent_primary"] if is_player else self.COLORS["text_primary"]
                
                # Rank
                rank_label = ctk.CTkLabel(
                    row_frame,
                    text=f"{i+1}",
                    font=self.FONTS["body"],
                    text_color=self.COLORS["text_primary"]
                )
                rank_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                
                # Company name
                company_text = f"{product.owner_name} {'(YOU)' if is_player else ''}"
                company_label = ctk.CTkLabel(
                    row_frame,
                    text=company_text,
                    font=self.FONTS["body"],
                    text_color=text_color
                )
                company_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
                
                # Revenue
                revenue_label = ctk.CTkLabel(
                    row_frame,
                    text=format_money(product.revenue),
                    font=self.FONTS["body"],
                    text_color=self.COLORS["text_primary"]
                )
                revenue_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
                
                # Quality
                quality_str = self.game._get_product_quality_rank(product)
                quality_label = ctk.CTkLabel(
                    row_frame,
                    text=quality_str,
                    font=self.FONTS["body"],
                    text_color=self.COLORS["text_primary"]
                )
                quality_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # Close button
        close_button = ctk.CTkButton(
            main_frame,
            text="CLOSE",
            font=self.FONTS["button"],
            height=40,
            fg_color=self.COLORS["accent_primary"],
            hover_color=self.blend_colors(self.COLORS["accent_primary"], "#FFFFFF", 0.2),
            command=dialog.destroy
        )
        close_button.pack(pady=10)

    def update_acquisitions_tab(self):
        """Update the acquisitions tab with current acquisition candidates"""
        # Clear current candidates
        for widget in self.candidates_scroll.winfo_children():
            widget.destroy()
        
        # Update pending acquisitions section
        if hasattr(self, 'pending_frame'):
            if self.game.pending_acquisitions:
                # Display pending acquisitions
                for i, (acquirer, target_name, price, turn) in enumerate(self.game.pending_acquisitions):
                    if acquirer == self.game.player:
                        self.pending_label.configure(
                            text=f"Pending acquisition of {target_name} for {format_money(price)} (finalizes next turn)",
                            text_color=self.COLORS["accent_warning"]
                        )
                        break
                else:
                    self.pending_label.configure(
                        text="No pending acquisitions",
                        text_color=self.COLORS["text_tertiary"]
                    )
            else:
                self.pending_label.configure(
                    text="No pending acquisitions",
                    text_color=self.COLORS["text_tertiary"]
                )
        
        # Find acquisition candidates
        candidates = []
        for ai_company in self.game.ai_companies:
            # Calculate acquisition price
            price = self.game._calculate_acquisition_price(ai_company)
            # Only include companies the player can afford
            if self.game.player.cash >= price:
                candidates.append((ai_company, price))
        
        # If no candidates are available
        if not candidates:
            no_candidates = ctk.CTkLabel(
                self.candidates_scroll,
                text="No acquisition candidates available. You either can't afford any acquisitions or there are no AI companies left.",
                font=self.FONTS["body"],
                text_color=self.COLORS["text_tertiary"],
                wraplength=600
            )
            no_candidates.pack(pady=20)
            return
        
        # Create cards for each candidate
        for i, (company, price) in enumerate(candidates):
            # Create candidate card
            card = ctk.CTkFrame(
                self.candidates_scroll,
                fg_color=self.COLORS["bg_tertiary"],
                corner_radius=10
            )
            card.pack(fill="x", pady=5, padx=10)
            
            # Card content
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=15)
            
            # Company name
            name_label = ctk.CTkLabel(
                content_frame,
                text=company.name,
                font=self.FONTS["heading3"],
                text_color=self.COLORS["text_primary"],
                anchor="w"
            )
            name_label.pack(side="left")
            
            # Market cap
            market_cap_label = ctk.CTkLabel(
                content_frame,
                text=f"Market Cap: {format_money(company.market_cap)}",
                font=self.FONTS["body"],
                text_color=self.COLORS["text_secondary"]
            )
            market_cap_label.pack(side="left", padx=20)
            
            # Acquisition price
            price_label = ctk.CTkLabel(
                content_frame,
                text=f"Price: {format_money(price)}",
                font=self.FONTS["body"],
                text_color=self.COLORS["text_primary"]
            )
            price_label.pack(side="left", padx=10)
            
            # Acquisition button
            acquire_button = ctk.CTkButton(
                content_frame,
                text="ACQUIRE",
                font=self.FONTS["body_small"],
                height=30,
                fg_color=self.COLORS["accent_primary"],
                hover_color=self.blend_colors(self.COLORS["accent_primary"], "#FFFFFF", 0.2),
                command=lambda c=company, p=price: self.confirm_acquisition_dialog(c, p)
            )
            acquire_button.pack(side="right")
            
            # Store widgets
            self.candidate_widgets[company.name] = (card, name_label, market_cap_label, price_label, acquire_button)
            
            # Additional company info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            # Product count
            product_count = len(company.products)
            products_label = ctk.CTkLabel(
                info_frame,
                text=f"Products: {product_count}",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"],
                anchor="w"
            )
            products_label.pack(side="left", padx=(0, 20))
            
            # Employee count
            employees_label = ctk.CTkLabel(
                info_frame,
                text=f"Employees: {company.employees}",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"],
                anchor="w"
            )
            employees_label.pack(side="left", padx=(0, 20))
            
            # Quarterly revenue
            revenue = company.total_revenue_this_quarter()
            revenue_label = ctk.CTkLabel(
                info_frame,
                text=f"Quarterly Revenue: {format_money(revenue)}",
                font=self.FONTS["body_small"],
                text_color=self.COLORS["text_secondary"],
                anchor="w"
            )
            revenue_label.pack(side="left")
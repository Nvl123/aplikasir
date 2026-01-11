"""
Profit/Loss Report Component - Calculate and display profit/loss from transactions
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from calendar import monthrange
from config import COLORS, FONTS
from db_manager import ProductDatabase, TransactionDatabase
from utils.helpers import format_currency

class ProfitLoss(tk.Frame):
    """Profit and Loss calculation report"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self.product_db = ProductDatabase()
        self.transaction_db = TransactionDatabase()
        
        # Default to current month
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        # Cache product buy prices
        self.product_prices = {}
        self._load_product_prices()
        
        self._create_widgets()
        self._load_data()
    
    def _load_product_prices(self):
        """Load all product buy prices into cache"""
        products = self.product_db.get_all()
        for p in products:
            try:
                self.product_prices[p['id']] = float(p.get('buy_price', 0) or 0)
            except (ValueError, TypeError):
                self.product_prices[p['id']] = 0
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Content
        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=0)
        content.grid_rowconfigure(1, weight=1)
        
        # Top - Stats cards
        self._create_stats_section(content)
        
        # Bottom left - Chart
        self._create_chart_section(content)
        
        # Bottom right - Detail table
        self._create_detail_section(content)
    
    def _create_header(self):
        """Create page header with month selector"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        # Title
        tk.Label(
            header,
            text="💹 Perhitungan Laba Rugi",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        ).pack(side='left')
        
        # Month selector
        selector = tk.Frame(header, bg=COLORS['background'])
        selector.pack(side='right')
        
        # Previous month
        tk.Button(
            selector,
            text="◀",
            font=FONTS['body_bold'],
            fg=COLORS['text'],
            bg=COLORS['card'],
            relief='flat',
            cursor='hand2',
            command=self._prev_month
        ).pack(side='left', padx=5)
        
        # Month label
        self.month_label = tk.Label(
            selector,
            text="",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            width=20
        )
        self.month_label.pack(side='left', padx=10)
        
        # Next month
        tk.Button(
            selector,
            text="▶",
            font=FONTS['body_bold'],
            fg=COLORS['text'],
            bg=COLORS['card'],
            relief='flat',
            cursor='hand2',
            command=self._next_month
        ).pack(side='left', padx=5)
    
    def _create_stats_section(self, parent):
        """Create statistics cards section"""
        stats_frame = tk.Frame(parent, bg=COLORS['background'])
        stats_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        stats_frame.grid_columnconfigure(0, weight=1, uniform='stat')
        stats_frame.grid_columnconfigure(1, weight=1, uniform='stat')
        stats_frame.grid_columnconfigure(2, weight=1, uniform='stat')
        stats_frame.grid_columnconfigure(3, weight=1, uniform='stat')
        
        # Stats cards data
        stats = [
            ("total_revenue", "💰 Total Pendapatan", COLORS['primary']),
            ("total_cost", "📦 Total Modal", COLORS['warning']),
            ("total_profit", "💹 Laba Bersih", COLORS['success']),
            ("profit_margin", "📊 Margin Laba", COLORS['secondary']),
        ]
        
        self.stat_cards = {}
        for i, (key, label, color) in enumerate(stats):
            card = self._create_stat_card(stats_frame, label, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            self.stat_cards[key] = card
    
    def _create_stat_card(self, parent, title, color):
        """Create a single stat card"""
        card = tk.Frame(parent, bg=COLORS['card'])
        card.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        
        inner = tk.Frame(card, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Color indicator
        indicator = tk.Frame(inner, bg=color, height=4)
        indicator.pack(fill='x', pady=(0, 10))
        
        # Title
        tk.Label(
            inner,
            text=title,
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        # Value
        value_label = tk.Label(
            inner,
            text="Rp 0",
            font=('Segoe UI', 18, 'bold'),
            fg=color,
            bg=COLORS['card']
        )
        value_label.pack(anchor='w', pady=(5, 0))
        
        # Store reference
        card.value_label = value_label
        
        return card
    
    def _create_chart_section(self, parent):
        """Create profit chart visualization"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=5)
        
        # Title
        tk.Label(
            section,
            text="📈 Grafik Laba Harian",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        # Chart canvas
        self.chart_canvas = tk.Canvas(
            section,
            bg=COLORS['white'],
            highlightthickness=0,
            height=280
        )
        self.chart_canvas.pack(fill='both', expand=True, padx=20, pady=(0, 15))
    
    def _create_detail_section(self, parent):
        """Create detail transactions table"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=1, column=1, sticky='nsew', padx=(5, 0), pady=5)
        
        # Title
        tk.Label(
            section,
            text="📋 Detail Transaksi",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        # Table
        table_frame = tk.Frame(section, bg=COLORS['card'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('date', 'revenue', 'cost', 'profit')
        self.detail_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.detail_tree.heading('date', text='Tanggal')
        self.detail_tree.heading('revenue', text='Pendapatan')
        self.detail_tree.heading('cost', text='Modal')
        self.detail_tree.heading('profit', text='Laba')
        
        self.detail_tree.column('date', width=100)
        self.detail_tree.column('revenue', width=100)
        self.detail_tree.column('cost', width=100)
        self.detail_tree.column('profit', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detail_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def _prev_month(self):
        """Go to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._load_data()
    
    def _next_month(self):
        """Go to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._load_data()
    
    def _calculate_transaction_profit(self, transaction):
        """Calculate profit for a single transaction"""
        revenue = float(transaction.get('total', 0) or 0)
        cost = 0
        
        items = transaction.get('items_list', [])
        for item in items:
            product_id = item.get('product_id', '')
            qty = int(item.get('qty', 1) or 1)
            buy_price = self.product_prices.get(product_id, 0)
            cost += buy_price * qty
        
        profit = revenue - cost
        return revenue, cost, profit
    
    def _load_data(self):
        """Load profit/loss data for current month"""
        # Update month label
        months = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        self.month_label.configure(text=f"{months[self.current_month]} {self.current_year}")
        
        # Reload product prices
        self._load_product_prices()
        
        # Get date range
        days_in_month = monthrange(self.current_year, self.current_month)[1]
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        end_date = f"{self.current_year}-{self.current_month:02d}-{days_in_month:02d}"
        
        # Get transactions
        transactions = self.transaction_db.get_by_date_range(start_date, end_date)
        
        # Calculate daily profits
        daily_data = {}  # day: {revenue, cost, profit}
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        
        for t in transactions:
            day = int(t['date'].split('-')[2])
            revenue, cost, profit = self._calculate_transaction_profit(t)
            
            if day not in daily_data:
                daily_data[day] = {'revenue': 0, 'cost': 0, 'profit': 0}
            
            daily_data[day]['revenue'] += revenue
            daily_data[day]['cost'] += cost
            daily_data[day]['profit'] += profit
            
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
        
        # Calculate margin
        margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Update stat cards
        self.stat_cards['total_revenue'].value_label.configure(text=format_currency(total_revenue))
        self.stat_cards['total_cost'].value_label.configure(text=format_currency(total_cost))
        
        # Color profit based on positive/negative
        profit_color = COLORS['success'] if total_profit >= 0 else COLORS['danger']
        self.stat_cards['total_profit'].value_label.configure(
            text=format_currency(total_profit),
            fg=profit_color
        )
        self.stat_cards['profit_margin'].value_label.configure(text=f"{margin:.1f}%")
        
        # Update detail table
        self._update_detail_table(daily_data, days_in_month)
        
        # Draw chart
        self._draw_chart(daily_data, days_in_month)
    
    def _update_detail_table(self, daily_data, days_in_month):
        """Update the detail transactions table"""
        # Clear existing
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        # Add rows for each day with transactions
        for day in sorted(daily_data.keys()):
            data = daily_data[day]
            date_str = f"{day:02d}/{self.current_month:02d}/{self.current_year}"
            
            self.detail_tree.insert('', 'end', values=(
                date_str,
                format_currency(data['revenue']),
                format_currency(data['cost']),
                format_currency(data['profit'])
            ))
    
    def _draw_chart(self, daily_data, days_in_month):
        """Draw profit bar chart"""
        self.chart_canvas.delete("all")
        
        # Get canvas dimensions
        self.chart_canvas.update_idletasks()
        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()
        
        if width < 10 or height < 10:
            width = 400
            height = 280
        
        # Margins
        left_margin = 60
        right_margin = 20
        top_margin = 20
        bottom_margin = 40
        
        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin
        
        # Calculate bar width
        bar_width = max(5, (chart_width / days_in_month) - 2)
        
        # Get profit values
        profits = {day: data['profit'] for day, data in daily_data.items()}
        
        # Find max/min values for scaling
        if profits:
            max_val = max(max(profits.values()), 0)
            min_val = min(min(profits.values()), 0)
        else:
            max_val = 100
            min_val = 0
        
        # Ensure we have range
        value_range = max_val - min_val
        if value_range == 0:
            value_range = 100
            max_val = 100
        
        # Calculate zero line position
        zero_y = top_margin + (max_val / value_range) * chart_height
        
        # Draw Y axis
        self.chart_canvas.create_line(
            left_margin, top_margin,
            left_margin, height - bottom_margin,
            fill=COLORS['border'], width=1
        )
        
        # Draw zero line (X axis)
        self.chart_canvas.create_line(
            left_margin, zero_y,
            width - right_margin, zero_y,
            fill=COLORS['text_light'], width=1
        )
        
        # Draw Y axis labels
        for i in range(5):
            y = top_margin + (chart_height * i / 4)
            value = max_val - (value_range * i / 4)
            
            # Grid line
            self.chart_canvas.create_line(
                left_margin, y,
                width - right_margin, y,
                fill=COLORS['background'], width=1, dash=(2, 2)
            )
            
            # Label
            if abs(value) >= 1000000:
                label = f"{value/1000000:.1f}M"
            elif abs(value) >= 1000:
                label = f"{value/1000:.0f}k"
            else:
                label = f"{value:.0f}"
            
            self.chart_canvas.create_text(
                left_margin - 10, y,
                text=label,
                anchor='e',
                font=('Segoe UI', 8),
                fill=COLORS['text_light']
            )
        
        # Draw bars
        for day in range(1, days_in_month + 1):
            x = left_margin + ((day - 0.5) * chart_width / days_in_month)
            value = profits.get(day, 0)
            
            if value != 0:
                bar_height = abs(value) / value_range * chart_height
                
                if value > 0:
                    # Positive bar (green, above zero line)
                    self.chart_canvas.create_rectangle(
                        x - bar_width/2, zero_y - bar_height,
                        x + bar_width/2, zero_y,
                        fill=COLORS['success'],
                        outline=COLORS['success']
                    )
                else:
                    # Negative bar (red, below zero line)
                    self.chart_canvas.create_rectangle(
                        x - bar_width/2, zero_y,
                        x + bar_width/2, zero_y + bar_height,
                        fill=COLORS['danger'],
                        outline=COLORS['danger']
                    )
            
            # X label (every 5 days)
            if day % 5 == 0 or day == 1:
                self.chart_canvas.create_text(
                    x, height - bottom_margin + 15,
                    text=str(day),
                    font=('Segoe UI', 8),
                    fill=COLORS['text_light']
                )
    
    def refresh(self):
        """Refresh report data"""
        self._load_product_prices()
        self._load_data()

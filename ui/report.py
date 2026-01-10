"""
Monthly Report Component - Sales recap with visualization
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from calendar import monthrange
from config import COLORS, FONTS
from db_manager import TransactionDatabase
from utils.helpers import format_currency

class Report(tk.Frame):
    """Monthly sales report with chart visualization"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self.transaction_db = TransactionDatabase()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Content
        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Left - Chart
        self._create_chart_section(content)
        
        # Right - Stats
        self._create_stats_section(content)
    
    def _create_header(self):
        """Create page header with month selector"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        # Title
        tk.Label(
            header,
            text="📈 Rekap Penjualan Bulanan",
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
    
    def _create_chart_section(self, parent):
        """Create bar chart visualization"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=10)
        
        # Title
        tk.Label(
            section,
            text="📊 Grafik Penjualan Harian",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', padx=20, pady=(20, 10))
        
        # Chart canvas
        self.chart_canvas = tk.Canvas(
            section,
            bg=COLORS['white'],
            highlightthickness=0,
            height=350
        )
        self.chart_canvas.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    def _create_stats_section(self, parent):
        """Create statistics section"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=10)
        
        inner = tk.Frame(section, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            inner,
            text="📋 Ringkasan Bulan Ini",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(0, 20))
        
        # Stats cards
        stats = [
            ("total_sales", "💰 Total Penjualan", COLORS['success']),
            ("total_transactions", "🧾 Total Transaksi", COLORS['primary']),
            ("avg_daily", "📊 Rata-rata/Hari", COLORS['warning']),
            ("highest_day", "🏆 Hari Tertinggi", COLORS['danger']),
        ]
        
        self.stat_labels = {}
        for key, label, color in stats:
            card = tk.Frame(inner, bg=COLORS['background'])
            card.pack(fill='x', pady=8)
            
            tk.Label(
                card,
                text=label,
                font=FONTS['body'],
                fg=COLORS['text_light'],
                bg=COLORS['background']
            ).pack(anchor='w', padx=15, pady=(10, 0))
            
            value_label = tk.Label(
                card,
                text="-",
                font=FONTS['heading'],
                fg=color,
                bg=COLORS['background']
            )
            value_label.pack(anchor='w', padx=15, pady=(0, 10))
            self.stat_labels[key] = value_label
    
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
    
    def _load_data(self):
        """Load sales data for current month"""
        # Update month label
        months = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        self.month_label.configure(text=f"{months[self.current_month]} {self.current_year}")
        
        # Get date range
        days_in_month = monthrange(self.current_year, self.current_month)[1]
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        end_date = f"{self.current_year}-{self.current_month:02d}-{days_in_month:02d}"
        
        # Get transactions
        transactions = self.transaction_db.get_by_date_range(start_date, end_date)
        
        # Calculate daily totals
        daily_totals = {}
        for t in transactions:
            day = int(t['date'].split('-')[2])
            total = float(t['total'])
            daily_totals[day] = daily_totals.get(day, 0) + total
        
        # Calculate stats
        total_sales = sum(daily_totals.values())
        total_transactions = len(transactions)
        avg_daily = total_sales / days_in_month if total_sales > 0 else 0
        highest_day = max(daily_totals.values()) if daily_totals else 0
        highest_day_num = max(daily_totals, key=daily_totals.get) if daily_totals else 0
        
        # Update stats
        self.stat_labels['total_sales'].configure(text=format_currency(total_sales))
        self.stat_labels['total_transactions'].configure(text=str(total_transactions))
        self.stat_labels['avg_daily'].configure(text=format_currency(avg_daily))
        if highest_day > 0:
            self.stat_labels['highest_day'].configure(
                text=f"Tgl {highest_day_num} ({format_currency(highest_day)})"
            )
        else:
            self.stat_labels['highest_day'].configure(text="-")
        
        # Draw chart
        self._draw_chart(daily_totals, days_in_month)
    
    def _draw_chart(self, daily_totals, days_in_month):
        """Draw bar chart"""
        self.chart_canvas.delete("all")
        
        # Get canvas dimensions
        self.chart_canvas.update_idletasks()
        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()
        
        if width < 10 or height < 10:
            width = 600
            height = 350
        
        # Margins
        left_margin = 60
        right_margin = 20
        top_margin = 20
        bottom_margin = 40
        
        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin
        
        # Calculate bar width
        bar_width = max(5, (chart_width / days_in_month) - 2)
        
        # Find max value
        max_value = max(daily_totals.values()) if daily_totals else 100
        if max_value == 0:
            max_value = 100
        
        # Draw Y axis
        self.chart_canvas.create_line(
            left_margin, top_margin,
            left_margin, height - bottom_margin,
            fill=COLORS['border'], width=1
        )
        
        # Draw X axis
        self.chart_canvas.create_line(
            left_margin, height - bottom_margin,
            width - right_margin, height - bottom_margin,
            fill=COLORS['border'], width=1
        )
        
        # Draw Y axis labels
        for i in range(5):
            y = top_margin + (chart_height * i / 4)
            value = max_value * (4 - i) / 4
            
            # Grid line
            self.chart_canvas.create_line(
                left_margin, y,
                width - right_margin, y,
                fill=COLORS['background'], width=1, dash=(2, 2)
            )
            
            # Label
            label = f"{value/1000:.0f}k" if value >= 1000 else f"{value:.0f}"
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
            value = daily_totals.get(day, 0)
            bar_height = (value / max_value) * chart_height if value > 0 else 0
            
            if bar_height > 0:
                # Bar
                self.chart_canvas.create_rectangle(
                    x - bar_width/2, height - bottom_margin - bar_height,
                    x + bar_width/2, height - bottom_margin,
                    fill=COLORS['primary'],
                    outline=COLORS['primary_dark']
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
        self._load_data()

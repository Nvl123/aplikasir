"""
Dashboard Component - Overview and statistics
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from db_manager import ProductDatabase, TransactionDatabase
from utils.helpers import format_currency, get_current_date, format_date
from datetime import datetime

class Dashboard(tk.Frame):
    """Dashboard with sales overview and statistics"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self.product_db = ProductDatabase()
        self.transaction_db = TransactionDatabase()
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Stats cards
        self._create_stats_cards()
        
        # Recent transactions
        self._create_recent_transactions()
    
    def _create_header(self):
        """Create page header"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        title = tk.Label(
            header,
            text="Dashboard",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        title.pack(side='left')
        
        date_label = tk.Label(
            header,
            text=f"📅 {format_date(get_current_date())}",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['background']
        )
        date_label.pack(side='right')
        
        # Clock
        self.clock_label = tk.Label(
            header,
            text="",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        self.clock_label.pack(side='right', padx=(0, 20))
        
        # Start clock update
        self._update_clock()
    
    def _create_stats_cards(self):
        """Create statistics cards"""
        cards_frame = tk.Frame(self, bg=COLORS['background'])
        cards_frame.pack(fill='x', padx=30, pady=10)
        
        # Configure grid
        cards_frame.grid_columnconfigure(0, weight=1, uniform='card')
        cards_frame.grid_columnconfigure(1, weight=1, uniform='card')
        cards_frame.grid_columnconfigure(2, weight=1, uniform='card')
        
        # Get data
        summary = self.transaction_db.get_today_summary()
        products = self.product_db.get_all()
        
        # Cards data
        cards_data = [
            ("Penjualan Hari Ini", format_currency(summary['total_sales']), COLORS['success'], "💰"),
            ("Transaksi Hari Ini", str(summary['total_transactions']), COLORS['primary'], "🧾"),
            ("Total Produk", str(len(products)), COLORS['warning'], "📦"),
        ]
        
        self.stat_cards = []
        for i, (title, value, color, icon) in enumerate(cards_data):
            card = self._create_stat_card(cards_frame, title, value, color, icon)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            self.stat_cards.append((card, title))
    
    def _create_stat_card(self, parent, title, value, color, icon):
        """Create a single stat card"""
        card = tk.Frame(parent, bg=COLORS['card'], relief='flat', bd=0)
        card.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        
        # Inner padding
        inner = tk.Frame(card, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top row with icon
        top = tk.Frame(inner, bg=COLORS['card'])
        top.pack(fill='x')
        
        icon_label = tk.Label(
            top,
            text=icon,
            font=('Segoe UI', 24),
            bg=COLORS['card']
        )
        icon_label.pack(side='left')
        
        # Color indicator
        indicator = tk.Frame(top, bg=color, width=4, height=40)
        indicator.pack(side='right')
        
        # Value
        value_label = tk.Label(
            inner,
            text=value,
            font=('Segoe UI', 24, 'bold'),
            fg=color,
            bg=COLORS['card']
        )
        value_label.pack(anchor='w', pady=(10, 5))
        
        # Title
        title_label = tk.Label(
            inner,
            text=title,
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        title_label.pack(anchor='w')
        
        # Store reference for updates
        card.value_label = value_label
        
        return card
    
    def _create_recent_transactions(self):
        """Create recent transactions section"""
        section = tk.Frame(self, bg=COLORS['background'])
        section.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Section header
        header = tk.Frame(section, bg=COLORS['background'])
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header,
            text="📋 Transaksi Terakhir",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        title.pack(side='left')
        
        # Card container
        card = tk.Frame(section, bg=COLORS['card'])
        card.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(fill='both', expand=True)
        
        # Create treeview
        columns = ('id', 'date', 'time', 'total', 'cashier')
        self.transactions_tree = ttk.Treeview(card, columns=columns, show='headings', height=6)
        
        # Configure columns
        self.transactions_tree.heading('id', text='ID Transaksi')
        self.transactions_tree.heading('date', text='Tanggal')
        self.transactions_tree.heading('time', text='Waktu')
        self.transactions_tree.heading('total', text='Total')
        self.transactions_tree.heading('cashier', text='Kasir')
        
        self.transactions_tree.column('id', width=150)
        self.transactions_tree.column('date', width=100)
        self.transactions_tree.column('time', width=80)
        self.transactions_tree.column('total', width=120)
        self.transactions_tree.column('cashier', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(card, orient='vertical', command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transactions_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Load data
        self._load_recent_transactions()
    
    def _load_recent_transactions(self):
        """Load recent transactions into treeview"""
        # Clear existing
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get recent transactions (last 10)
        transactions = self.transaction_db.get_all()
        transactions = sorted(transactions, key=lambda x: (x['date'], x['time']), reverse=True)[:10]
        
        for t in transactions:
            self.transactions_tree.insert('', 'end', values=(
                t['id'],
                format_date(t['date']),
                t['time'],
                format_currency(float(t['total'])),
                t['cashier']
            ))
    
    def _create_low_stock_alert(self):
        """Create low stock alert section"""
        low_stock = self.product_db.get_low_stock()
        
        if not low_stock:
            return
        
        section = tk.Frame(self, bg=COLORS['background'])
        section.pack(fill='x', padx=30, pady=(10, 20))
        
        # Alert card
        card = tk.Frame(section, bg='#FEF3C7')
        card.configure(highlightbackground=COLORS['warning'], highlightthickness=1)
        card.pack(fill='x')
        
        inner = tk.Frame(card, bg='#FEF3C7')
        inner.pack(fill='x', padx=15, pady=10)
        
        # Alert icon and text
        alert_text = tk.Label(
            inner,
            text=f"⚠️ {len(low_stock)} produk memiliki stok rendah (≤10)",
            font=FONTS['body_bold'],
            fg='#92400E',
            bg='#FEF3C7'
        )
        alert_text.pack(side='left')
        
        # Product names
        product_names = ", ".join([p['name'] for p in low_stock[:5]])
        if len(low_stock) > 5:
            product_names += f" dan {len(low_stock) - 5} lainnya"
        
        products_label = tk.Label(
            inner,
            text=product_names,
            font=FONTS['small'],
            fg='#92400E',
            bg='#FEF3C7'
        )
        products_label.pack(side='left', padx=(20, 0))
    
    def refresh(self):
        """Refresh dashboard data"""
        # Update stats
        summary = self.transaction_db.get_today_summary()
        products = self.product_db.get_all()
        
        values = [
            format_currency(summary['total_sales']),
            str(summary['total_transactions']),
            str(len(products))
        ]
        
        for i, (card, _) in enumerate(self.stat_cards):
            if i < len(values):
                card.value_label.configure(text=values[i])
        
        # Refresh transactions
        self._load_recent_transactions()
    
    def _update_clock(self):
        """Update clock display every second"""
        now = datetime.now()
        time_str = now.strftime("🕐 %H:%M:%S")
        self.clock_label.configure(text=time_str)
        # Schedule next update in 1 second
        self.after(1000, self._update_clock)

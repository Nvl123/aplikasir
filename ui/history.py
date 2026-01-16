"""
Transaction History Component
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from config import COLORS, FONTS
from db_manager import TransactionDatabase
from utils.helpers import format_currency, format_date, get_current_date

class History(tk.Frame):
    """Transaction history interface"""
    
    def __init__(self, parent, on_print_receipt=None):
        super().__init__(parent, bg=COLORS['background'])
        
        self.transaction_db = TransactionDatabase()
        self.on_print_receipt = on_print_receipt
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Filter section
        self._create_filter_section()
        
        # Transaction list
        self._create_transaction_list()
        
        # Detail panel
        self._create_detail_panel()
    
    def _create_header(self):
        """Create page header"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        title = tk.Label(
            header,
            text="📋 Riwayat Transaksi",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        title.pack(side='left')
        
        # Summary
        self.summary_label = tk.Label(
            header,
            text="",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['background']
        )
        self.summary_label.pack(side='right')
    
    def _create_filter_section(self):
        """Create date filter section"""
        filter_frame = tk.Frame(self, bg=COLORS['card'])
        filter_frame.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        filter_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        inner = tk.Frame(filter_frame, bg=COLORS['card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        # Date from
        tk.Label(inner, text="Dari:", font=FONTS['body'], bg=COLORS['card']).pack(side='left', padx=(0, 5))
        
        # Default: 7 days ago
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.date_from_var = tk.StringVar(value=week_ago)
        date_from_entry = tk.Entry(inner, textvariable=self.date_from_var, width=12, font=FONTS['body'])
        date_from_entry.pack(side='left', padx=5)
        
        # Date to
        tk.Label(inner, text="Sampai:", font=FONTS['body'], bg=COLORS['card']).pack(side='left', padx=(20, 5))
        
        self.date_to_var = tk.StringVar(value=get_current_date())
        date_to_entry = tk.Entry(inner, textvariable=self.date_to_var, width=12, font=FONTS['body'])
        date_to_entry.pack(side='left', padx=5)
        
        # Filter button
        filter_btn = tk.Button(
            inner,
            text="🔍 Filter",
            font=FONTS['body'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            relief='flat',
            cursor='hand2',
            command=self._apply_filter
        )
        filter_btn.pack(side='left', padx=20)
        
        # Quick filters
        today_btn = tk.Button(
            inner,
            text="Hari Ini",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._filter_today
        )
        today_btn.pack(side='left', padx=5)
        
        week_btn = tk.Button(
            inner,
            text="7 Hari",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._filter_week
        )
        week_btn.pack(side='left', padx=5)
        
        month_btn = tk.Button(
            inner,
            text="30 Hari",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._filter_month
        )
        month_btn.pack(side='left', padx=5)
    
    def _create_transaction_list(self):
        """Create transaction list"""
        list_frame = tk.Frame(self, bg=COLORS['card'])
        list_frame.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Treeview
        columns = ('id', 'date', 'time', 'items_count', 'total', 'payment', 'change', 'cashier')
        self.transaction_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.transaction_tree.heading('id', text='ID Transaksi')
        self.transaction_tree.heading('date', text='Tanggal')
        self.transaction_tree.heading('time', text='Waktu')
        self.transaction_tree.heading('items_count', text='Jumlah Item')
        self.transaction_tree.heading('total', text='Total')
        self.transaction_tree.heading('payment', text='Bayar')
        self.transaction_tree.heading('change', text='Kembali')
        self.transaction_tree.heading('cashier', text='Kasir')
        
        self.transaction_tree.column('id', width=150)
        self.transaction_tree.column('date', width=100)
        self.transaction_tree.column('time', width=80)
        self.transaction_tree.column('items_count', width=100)
        self.transaction_tree.column('total', width=100)
        self.transaction_tree.column('payment', width=100)
        self.transaction_tree.column('change', width=100)
        self.transaction_tree.column('cashier', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transaction_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Bind selection
        self.transaction_tree.bind('<<TreeviewSelect>>', self._on_select)
        self.transaction_tree.bind('<Double-1>', self._on_double_click)
        self.transaction_tree.bind('<Button-3>', self._show_context_menu)  # Right click
        self.transaction_tree.bind('<Delete>', lambda e: self._delete_transaction())
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cetak Struk", command=self._print_receipt)
        self.context_menu.add_command(label="Edit Transaksi", command=self._edit_transaction)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Hapus Transaksi", command=self._delete_transaction)
        
        # Load transactions
        self._apply_filter()
    
    def _create_detail_panel(self):
        """Create transaction detail panel"""
        detail_frame = tk.Frame(self, bg=COLORS['card'])
        detail_frame.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        detail_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        inner = tk.Frame(detail_frame, bg=COLORS['card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        # Action buttons (Pack first to ensure visibility)
        right = tk.Frame(inner, bg=COLORS['card'])
        right.pack(side='right', padx=(20, 0))
        
        self.print_btn = tk.Button(
            right,
            text="🖨️ Cetak Struk",
            font=FONTS['body_bold'],
            fg='#64748B',
            bg='#E2E8F0',
            relief='flat',
            cursor='arrow',
            width=18,
            command=self._print_receipt
        )
        self.print_btn.pack(pady=8, ipady=10, padx=10)
        
        self.edit_btn = tk.Button(
            right,
            text="✏️ Edit Transaksi",
            font=FONTS['body_bold'],
            fg='#64748B',
            bg='#E2E8F0',
            relief='flat',
            cursor='arrow',
            width=18,
            command=self._edit_transaction
        )
        self.edit_btn.pack(pady=8, ipady=10, padx=10)
        
        self.delete_btn = tk.Button(
            right,
            text="🗑️ Hapus Transaksi",
            font=FONTS['body_bold'],
            fg='#64748B',
            bg='#E2E8F0',
            relief='flat',
            cursor='arrow',
            width=18,
            command=self._delete_transaction
        )
        self.delete_btn.pack(pady=8, ipady=10, padx=10)
        
        # Detail left
        left = tk.Frame(inner, bg=COLORS['card'])
        left.pack(side='left', fill='both', expand=True)
        
        tk.Label(left, text="Detail Transaksi:", font=FONTS['body_bold'], bg=COLORS['card']).pack(anchor='w')
        
        self.detail_label = tk.Label(
            left,
            text="Pilih transaksi untuk melihat detail",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card'],
            justify='left'
        )
        self.detail_label.pack(anchor='w', pady=5)
        
        # Items list
        self.items_text = tk.Text(
            left,
            height=4,
            font=FONTS['small'],
            bg=COLORS['background'],
            relief='flat',
            state='disabled'
        )
        self.items_text.pack(fill='x', pady=5)
    
    def _apply_filter(self):
        """Apply date filter and load transactions"""
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()
        
        # Clear existing
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        transactions = self.transaction_db.get_by_date_range(date_from, date_to)
        transactions = sorted(transactions, key=lambda x: (x['date'], x['time']), reverse=True)
        
        total_sales = 0
        for t in transactions:
            # Fix: Sum quantity instead of count unique items
            items_count = sum(item['qty'] for item in t.get('items_list', []))
            total = float(t['total'])
            total_sales += total
            
            self.transaction_tree.insert('', 'end', iid=t['id'], values=(
                t['id'],
                format_date(t['date']),
                t['time'],
                items_count,
                format_currency(total),
                format_currency(float(t['payment'])),
                format_currency(float(t['change'])),
                t['cashier']
            ))
        
        self.summary_label.configure(
            text=f"{len(transactions)} transaksi | Total: {format_currency(total_sales)}"
        )
    
    def _filter_today(self):
        """Filter today's transactions"""
        today = get_current_date()
        self.date_from_var.set(today)
        self.date_to_var.set(today)
        self._apply_filter()
    
    def _filter_week(self):
        """Filter last 7 days"""
        today = get_current_date()
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.date_from_var.set(week_ago)
        self.date_to_var.set(today)
        self._apply_filter()
    
    def _filter_month(self):
        """Filter last 30 days"""
        today = get_current_date()
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.date_from_var.set(month_ago)
        self.date_to_var.set(today)
        self._apply_filter()
    
    def _on_select(self, event):
        """Handle transaction selection"""
        selection = self.transaction_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        transaction = self.transaction_db.get_by_id(transaction_id)
        
        if transaction:
            self.selected_transaction = transaction
            # Enable buttons with proper colors
            self.print_btn.configure(fg=COLORS['white'], bg=COLORS['primary'], cursor='hand2')
            self.edit_btn.configure(fg=COLORS['white'], bg=COLORS['warning'], cursor='hand2')
            self.delete_btn.configure(fg=COLORS['white'], bg=COLORS['danger'], cursor='hand2')
            
            # Update detail label
            detail_text = f"ID: {transaction['id']}\n"
            detail_text += f"Tanggal: {format_date(transaction['date'])} {transaction['time']}\n"
            detail_text += f"Total: {format_currency(float(transaction['total']))}"
            self.detail_label.configure(text=detail_text)
            
            # Update items list
            self.items_text.configure(state='normal')
            self.items_text.delete('1.0', 'end')
            
            items = transaction.get('items_list', [])
            for item in items:
                line = f"• {item['name']} x{item['qty']} = {format_currency(item['subtotal'])}\n"
                self.items_text.insert('end', line)
            
            self.items_text.configure(state='disabled')
    
    def _on_double_click(self, event):
        """Handle double-click to print receipt"""
        self._print_receipt()
    
    def _print_receipt(self):
        """Print receipt for selected transaction"""
        if hasattr(self, 'selected_transaction') and self.on_print_receipt:
            self.on_print_receipt(self.selected_transaction)
    
    def _delete_transaction(self):
        """Delete selected transaction"""
        if not hasattr(self, 'selected_transaction'):
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus transaksi {self.selected_transaction['id']}?"):
            try:
                self.transaction_db.delete(self.selected_transaction['id'])
                messagebox.showinfo("Sukses", "Transaksi berhasil dihapus!")
                self._apply_filter()
                self.selected_transaction = None
                # Reset buttons to inactive colors
                self.print_btn.configure(fg='#64748B', bg='#E2E8F0', cursor='arrow')
                self.edit_btn.configure(fg='#64748B', bg='#E2E8F0', cursor='arrow')
                self.delete_btn.configure(fg='#64748B', bg='#E2E8F0', cursor='arrow')
                self.detail_label.configure(text="Pilih transaksi untuk melihat detail")
                self.items_text.configure(state='normal')
                self.items_text.delete('1.0', 'end')
                self.items_text.configure(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")
    
    def _show_context_menu(self, event):
        """Show value context menu"""
        try:
            item = self.transaction_tree.identify_row(event.y)
            if item:
                self.transaction_tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        except:
            pass
            
    def _edit_transaction(self):
        """Edit selected transaction"""
        if not hasattr(self, 'selected_transaction') or not self.selected_transaction:
            return
            
        t = self.selected_transaction
        
        # Dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Transaksi")
        dialog.geometry("400x450")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center
        dialog.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 450) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Form
        p = tk.Frame(dialog, bg=COLORS['white'], padx=20, pady=20)
        p.pack(fill='both', expand=True)
        
        # Info (Read only)
        tk.Label(p, text=f"ID: {t['id']}", font=FONTS['body_bold'], bg=COLORS['white']).pack(anchor='w', pady=(0, 10))
        tk.Label(p, text=f"Total: {format_currency(float(t['total']))}", font=FONTS['body_bold'], bg=COLORS['white']).pack(anchor='w', pady=(0, 20))
        
        # Date
        tk.Label(p, text="Tanggal (YYYY-MM-DD):", font=FONTS['body'], bg=COLORS['white']).pack(anchor='w')
        date_var = tk.StringVar(value=t['date'])
        date_entry = tk.Entry(p, textvariable=date_var, font=FONTS['body'], width=30)
        date_entry.pack(fill='x', pady=(5, 15))
        
        # Time
        tk.Label(p, text="Waktu (HH:MM:SS):", font=FONTS['body'], bg=COLORS['white']).pack(anchor='w')
        time_var = tk.StringVar(value=t['time'])
        time_entry = tk.Entry(p, textvariable=time_var, font=FONTS['body'], width=30)
        time_entry.pack(fill='x', pady=(5, 15))
        
        # Payment
        tk.Label(p, text="Pembayaran:", font=FONTS['body'], bg=COLORS['white']).pack(anchor='w')
        payment_var = tk.StringVar(value=str(int(float(t['payment']))))
        payment_entry = tk.Entry(p, textvariable=payment_var, font=FONTS['body'], width=30)
        payment_entry.pack(fill='x', pady=(5, 5))
        
        # Change preview
        change_label = tk.Label(p, text=f"Kembali: {format_currency(float(t['change']))}", font=FONTS['body_bold'], bg=COLORS['white'], fg=COLORS['success'])
        change_label.pack(anchor='w', pady=(0, 20))
        
        def update_change(*args):
            try:
                pay = float(payment_var.get())
                tot = float(t['total'])
                chg = pay - tot
                change_label.configure(
                    text=f"Kembali: {format_currency(chg)}",
                    fg=COLORS['success'] if chg >= 0 else COLORS['danger']
                )
            except:
                pass
        
        payment_var.trace('w', update_change)
        
        def save():
            try:
                new_date = date_var.get()
                new_time = time_var.get()
                new_pay = float(payment_var.get())
                total = float(t['total'])
                
                if new_pay < total:
                    messagebox.showerror("Error", "Pembayaran kurang!", parent=dialog)
                    return
                
                new_change = new_pay - total
                
                # Update DB
                self.transaction_db.update(
                    t['id'],
                    date=new_date,
                    time=new_time,
                    payment=str(new_pay),
                    change=str(new_change)
                )
                
                messagebox.showinfo("Sukses", "Transaksi berhasil diperbarui!", parent=dialog)
                self._apply_filter()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan: {e}", parent=dialog)
        
        # Buttons
        btn_frame = tk.Frame(p, bg=COLORS['white'])
        btn_frame.pack(fill='x', side='bottom')
        
        tk.Button(btn_frame, text="Batal", command=dialog.destroy, font=FONTS['body'], bg='#E2E8F0', relief='flat').pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(btn_frame, text="Simpan", command=save, font=FONTS['body_bold'], bg=COLORS['primary'], fg='white', relief='flat').pack(side='left', fill='x', expand=True, padx=(5, 0))

    def refresh(self):
        """Refresh history view"""
        self._apply_filter()


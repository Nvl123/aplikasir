"""
Sales/POS Component - Main transaction interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS
from db_manager import ProductDatabase, TransactionDatabase
from utils.helpers import format_currency, parse_float, parse_int, format_currency_input, parse_currency_input

class Sales(tk.Frame):
    """Point of Sale interface for transactions"""
    
    def __init__(self, parent, on_print_receipt=None):
        super().__init__(parent, bg=COLORS['background'])
        
        self.product_db = ProductDatabase()
        self.transaction_db = TransactionDatabase()
        self.on_print_receipt = on_print_receipt
        
        # Cart items: list of {product_id, barcode, name, price, qty, subtotal}
        self.cart = []
        self.discount = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=2)  # Product search
        self.grid_columnconfigure(1, weight=3)  # Cart
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Product search
        self._create_product_panel()
        
        # Right panel - Cart and payment (scrollable)
        self._create_cart_panel()
    
    def _create_product_panel(self):
        """Create product search and selection panel"""
        panel = tk.Frame(self, bg=COLORS['card'])
        panel.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        panel.grid(row=0, column=0, sticky='nsew', padx=(30, 10), pady=30)
        
        # Header
        header = tk.Frame(panel, bg=COLORS['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        title = tk.Label(
            header,
            text="🔍 Cari Produk",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        )
        title.pack(side='left')
        
        # Search box
        search_frame = tk.Frame(panel, bg=COLORS['card'])
        search_frame.pack(fill='x', padx=20, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        search_entry.pack(fill='x', ipady=10, ipadx=10)
        search_entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        
        # Hint
        hint = tk.Label(
            panel,
            text="Ketik barcode atau nama produk, tekan Enter untuk tambah",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        hint.pack(anchor='w', padx=20)
        
        # Bind Enter key
        search_entry.bind('<Return>', self._on_search_enter)
        
        # Product list
        list_frame = tk.Frame(panel, bg=COLORS['card'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('barcode', 'name', 'price')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        self.product_tree.heading('barcode', text='Barcode')
        self.product_tree.heading('name', text='Nama Produk')
        self.product_tree.heading('price', text='Harga')
        
        self.product_tree.column('barcode', width=120)
        self.product_tree.column('name', width=180)
        self.product_tree.column('price', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Double-click to add
        self.product_tree.bind('<Double-1>', self._add_selected_product)
        
        # Load all products
        self._load_products()
    
    def _create_cart_panel(self):
        """Create cart and payment panel with scroll"""
        # Outer container for the entire right panel
        outer_panel = tk.Frame(self, bg=COLORS['card'])
        outer_panel.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        outer_panel.grid(row=0, column=1, sticky='nsew', padx=(10, 30), pady=30)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(outer_panel, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_panel, orient='vertical', command=canvas.yview)
        
        # Scrollable frame inside canvas
        self.cart_container = tk.Frame(canvas, bg=COLORS['card'])
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=self.cart_container, anchor='nw')
        
        # Configure scroll region and width
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        def configure_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.cart_container.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', configure_width)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        # Now create the cart content
        self._create_cart_content(self.cart_container)
    
    def _create_cart_content(self, panel):
        """Create cart content inside scrollable container"""
        # Header
        header = tk.Frame(panel, bg=COLORS['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        title = tk.Label(
            header,
            text="🛒 Keranjang Belanja",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        )
        title.pack(side='left')
        
        # Clear cart button
        clear_btn = tk.Button(
            header,
            text="🗑️ Kosongkan",
            font=FONTS['small'],
            fg=COLORS['danger'],
            bg=COLORS['card'],
            relief='flat',
            cursor='hand2',
            command=self._clear_cart
        )
        clear_btn.pack(side='right')
        
        # Cart table
        cart_frame = tk.Frame(panel, bg=COLORS['card'])
        cart_frame.pack(fill='x', padx=20, pady=10)
        
        columns = ('name', 'price', 'qty', 'subtotal', 'action')
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=6)
        
        self.cart_tree.heading('name', text='Produk')
        self.cart_tree.heading('price', text='Harga')
        self.cart_tree.heading('qty', text='Qty')
        self.cart_tree.heading('subtotal', text='Subtotal')
        self.cart_tree.heading('action', text='')
        
        self.cart_tree.column('name', width=150)
        self.cart_tree.column('price', width=100)
        self.cart_tree.column('qty', width=50)
        self.cart_tree.column('subtotal', width=100)
        self.cart_tree.column('action', width=40)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side='left', fill='x', expand=True)
        cart_scrollbar.pack(side='right', fill='y')
        
        # Bind delete key
        self.cart_tree.bind('<Delete>', self._remove_selected_item)
        self.cart_tree.bind('<Double-1>', self._edit_quantity)
        
        # Separator
        sep = tk.Frame(panel, bg=COLORS['border'], height=1)
        sep.pack(fill='x', padx=20, pady=10)
        
        # Totals section
        self._create_totals_section(panel)
        
        # Payment section
        self._create_payment_section(panel)
    
    def _create_totals_section(self, parent):
        """Create totals display"""
        totals_frame = tk.Frame(parent, bg=COLORS['card'])
        totals_frame.pack(fill='x', padx=20)
        
        # Subtotal
        row1 = tk.Frame(totals_frame, bg=COLORS['card'])
        row1.pack(fill='x', pady=2)
        tk.Label(row1, text="Subtotal:", font=FONTS['body'], fg=COLORS['text_light'], bg=COLORS['card']).pack(side='left')
        self.subtotal_label = tk.Label(row1, text="Rp 0", font=FONTS['body'], fg=COLORS['text'], bg=COLORS['card'])
        self.subtotal_label.pack(side='right')
        
        # Discount
        row2 = tk.Frame(totals_frame, bg=COLORS['card'])
        row2.pack(fill='x', pady=2)
        tk.Label(row2, text="Diskon:", font=FONTS['body'], fg=COLORS['text_light'], bg=COLORS['card']).pack(side='left')
        
        discount_input = tk.Frame(row2, bg=COLORS['card'])
        discount_input.pack(side='right')
        
        self.discount_var = tk.StringVar(value="0")
        self.discount_var.trace('w', self._update_totals)
        discount_entry = tk.Entry(
            discount_input,
            textvariable=self.discount_var,
            font=FONTS['body'],
            width=10,
            relief='flat',
            bg=COLORS['background'],
            justify='right'
        )
        discount_entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        discount_entry.pack(side='left', ipady=3)
        
        # Auto-format discount entry
        def format_discount(event):
            current_value = self.discount_var.get()
            formatted = format_currency_input(current_value)
            if formatted != current_value:
                self.discount_var.set(formatted)
                discount_entry.icursor(tk.END)
        
        discount_entry.bind('<KeyRelease>', format_discount)
        
        # Total
        row3 = tk.Frame(totals_frame, bg=COLORS['card'])
        row3.pack(fill='x', pady=(10, 5))
        tk.Label(row3, text="TOTAL:", font=FONTS['subheading'], fg=COLORS['text'], bg=COLORS['card']).pack(side='left')
        self.total_label = tk.Label(row3, text="Rp 0", font=('Segoe UI', 20, 'bold'), fg=COLORS['primary'], bg=COLORS['card'])
        self.total_label.pack(side='right')
    
    def _create_payment_section(self, parent):
        """Create payment input and buttons"""
        payment_frame = tk.Frame(parent, bg=COLORS['card'])
        payment_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Payment input
        pay_row = tk.Frame(payment_frame, bg=COLORS['card'])
        pay_row.pack(fill='x', pady=5)
        
        tk.Label(pay_row, text="Bayar:", font=FONTS['body_bold'], fg=COLORS['text'], bg=COLORS['card']).pack(side='left')
        
        self.payment_var = tk.StringVar(value="0")
        self.payment_var.trace('w', self._update_change)
        payment_entry = tk.Entry(
            pay_row,
            textvariable=self.payment_var,
            font=('Segoe UI', 14),
            width=15,
            relief='flat',
            bg=COLORS['background'],
            justify='right'
        )
        payment_entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        payment_entry.pack(side='right', ipady=5)
        
        # Auto-format payment entry
        def format_payment(event):
            current_value = self.payment_var.get()
            formatted = format_currency_input(current_value)
            if formatted != current_value:
                self.payment_var.set(formatted)
                payment_entry.icursor(tk.END)
        
        payment_entry.bind('<KeyRelease>', format_payment)
        
        # Change display
        change_row = tk.Frame(payment_frame, bg=COLORS['card'])
        change_row.pack(fill='x', pady=5)
        
        tk.Label(change_row, text="Kembalian:", font=FONTS['body_bold'], fg=COLORS['text'], bg=COLORS['card']).pack(side='left')
        self.change_label = tk.Label(change_row, text="Rp 0", font=('Segoe UI', 14, 'bold'), fg=COLORS['success'], bg=COLORS['card'])
        self.change_label.pack(side='right')
        
        # Quick payment buttons
        quick_frame = tk.Frame(payment_frame, bg=COLORS['card'])
        quick_frame.pack(fill='x', pady=10)
        
        quick_amounts = [10000, 20000, 50000, 100000]
        for amount in quick_amounts:
            btn = tk.Button(
                quick_frame,
                text=f"{amount//1000}K",
                font=FONTS['small'],
                fg=COLORS['text'],
                bg=COLORS['background'],
                relief='flat',
                cursor='hand2',
                command=lambda a=amount: self._set_payment(a)
            )
            btn.pack(side='left', padx=2, ipadx=8, ipady=3)
        
        # Exact payment button
        exact_btn = tk.Button(
            quick_frame,
            text="Uang Pas",
            font=FONTS['small'],
            fg=COLORS['white'],
            bg=COLORS['secondary'],
            relief='flat',
            cursor='hand2',
            command=self._set_exact_payment
        )
        exact_btn.pack(side='right', padx=2, ipadx=8, ipady=3)
        
        # Action buttons
        btn_frame = tk.Frame(payment_frame, bg=COLORS['card'])
        btn_frame.pack(fill='x', pady=(10, 10))
        
        # Process button
        self.process_btn = tk.Button(
            btn_frame,
            text="💳 Proses Pembayaran",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            activeforeground=COLORS['white'],
            activebackground=COLORS['primary_dark'],
            relief='flat',
            cursor='hand2',
            command=self._process_payment
        )
        self.process_btn.pack(fill='x', ipady=12)
    
    def _load_products(self, query=""):
        """Load products into treeview"""
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        if query:
            products = self.product_db.search(query)
        else:
            products = self.product_db.get_all()
        
        for p in products:
            self.product_tree.insert('', 'end', iid=p['id'], values=(
                p['barcode'],
                p['name'],
                format_currency(parse_float(p['sell_price']))
            ))
    
    def _on_search(self, *args):
        """Handle search input change"""
        query = self.search_var.get().strip()
        self._load_products(query)
    
    def _on_search_enter(self, event):
        """Handle Enter key in search - add first matching product"""
        query = self.search_var.get().strip()
        if not query:
            return
        
        # Try barcode first
        product = self.product_db.get_by_barcode(query)
        if product:
            self._add_to_cart(product)
            self.search_var.set("")
            return
        
        # Try search
        results = self.product_db.search(query)
        if results:
            self._add_to_cart(results[0])
            self.search_var.set("")
    
    def _add_selected_product(self, event):
        """Add selected product from treeview to cart"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        product_id = selection[0]
        product = self.product_db.get_by_id(product_id)
        if product:
            self._add_to_cart(product)
    
    def _add_to_cart(self, product):
        """Add product to cart"""
        # Check if already in cart
        for item in self.cart:
            if item['product_id'] == product['id']:
                item['qty'] += 1
                item['subtotal'] = item['price'] * item['qty']
                self._refresh_cart()
                return
        
        # Add new item
        price = parse_float(product['sell_price'])
        self.cart.append({
            'product_id': product['id'],
            'barcode': product['barcode'],
            'name': product['name'],
            'price': price,
            'qty': 1,
            'subtotal': price
        })
        self._refresh_cart()
    
    def _refresh_cart(self):
        """Refresh cart display"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        for i, item in enumerate(self.cart):
            self.cart_tree.insert('', 'end', iid=str(i), values=(
                item['name'],
                format_currency(item['price']),
                item['qty'],
                format_currency(item['subtotal']),
                '❌'
            ))
        
        self._update_totals()
    
    def _update_totals(self, *args):
        """Update totals display"""
        subtotal = sum(item['subtotal'] for item in self.cart)
        discount = parse_currency_input(self.discount_var.get())
        total = max(0, subtotal - discount)
        
        self.subtotal_label.configure(text=format_currency(subtotal))
        self.total_label.configure(text=format_currency(total))
        self._update_change()
    
    def _update_change(self, *args):
        """Update change display"""
        subtotal = sum(item['subtotal'] for item in self.cart)
        discount = parse_currency_input(self.discount_var.get())
        total = max(0, subtotal - discount)
        payment = parse_currency_input(self.payment_var.get())
        change = payment - total
        
        self.change_label.configure(
            text=format_currency(change),
            fg=COLORS['success'] if change >= 0 else COLORS['danger']
        )
    
    def _set_payment(self, amount):
        """Set payment amount"""
        current = parse_currency_input(self.payment_var.get())
        self.payment_var.set(format_currency_input(str(int(current + amount))))
    
    def _set_exact_payment(self):
        """Set exact payment amount"""
        subtotal = sum(item['subtotal'] for item in self.cart)
        discount = parse_currency_input(self.discount_var.get())
        total = max(0, subtotal - discount)
        self.payment_var.set(format_currency_input(str(int(total))))
    
    def _remove_selected_item(self, event=None):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        if 0 <= index < len(self.cart):
            del self.cart[index]
            self._refresh_cart()
    
    def _edit_quantity(self, event):
        """Edit quantity of selected item"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        if 0 <= index < len(self.cart):
            item = self.cart[index]
            
            # Simple quantity dialog
            dialog = tk.Toplevel(self)
            dialog.title("Ubah Jumlah")
            dialog.geometry("300x180")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            dialog.geometry(f"+{self.winfo_rootx() + 200}+{self.winfo_rooty() + 200}")
            
            tk.Label(dialog, text=f"Produk: {item['name']}", font=FONTS['body_bold']).pack(pady=(20, 10))
            
            qty_frame = tk.Frame(dialog)
            qty_frame.pack(pady=10)
            
            tk.Label(qty_frame, text="Jumlah:", font=FONTS['body']).pack(side='left', padx=5)
            qty_var = tk.StringVar(value=str(item['qty']))
            qty_entry = tk.Entry(qty_frame, textvariable=qty_var, width=10, font=FONTS['body'])
            qty_entry.pack(side='left')
            qty_entry.select_range(0, 'end')
            qty_entry.focus()
            
            def save_qty():
                new_qty = parse_int(qty_var.get())
                if new_qty <= 0:
                    del self.cart[index]
                else:
                    self.cart[index]['qty'] = new_qty
                    self.cart[index]['subtotal'] = self.cart[index]['price'] * new_qty
                self._refresh_cart()
                dialog.destroy()
            
            tk.Button(dialog, text="Simpan", command=save_qty, bg=COLORS['primary'], fg='white').pack(pady=10)
            qty_entry.bind('<Return>', lambda e: save_qty())
    
    def _clear_cart(self):
        """Clear all items from cart"""
        if self.cart and messagebox.askyesno("Konfirmasi", "Kosongkan keranjang?"):
            self.cart = []
            self.discount_var.set("0")
            self.payment_var.set("0")
            self._refresh_cart()
    
    def _process_payment(self):
        """Process the payment and save transaction"""
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang kosong!")
            return
        
        subtotal = sum(item['subtotal'] for item in self.cart)
        discount = parse_currency_input(self.discount_var.get())
        total = max(0, subtotal - discount)
        payment = parse_currency_input(self.payment_var.get())
        
        if payment < total:
            messagebox.showerror("Error", "Pembayaran kurang!")
            return
        
        change = payment - total
        
        # Prepare items for storage
        items_data = []
        for item in self.cart:
            items_data.append({
                'product_id': item['product_id'],
                'barcode': item['barcode'],
                'name': item['name'],
                'price': item['price'],
                'qty': item['qty'],
                'subtotal': item['subtotal']
            })
        
        # Save transaction
        transaction = self.transaction_db.add(
            items=items_data,
            subtotal=subtotal,
            discount=discount,
            total=total,
            payment=payment,
            change=change,
            cashier="Kasir"
        )
        
        messagebox.showinfo("Sukses", f"Transaksi berhasil!\n\nID: {transaction['id']}\nTotal: {format_currency(total)}\nKembalian: {format_currency(change)}")
        
        # Print receipt
        if self.on_print_receipt:
            self.on_print_receipt(transaction)
        
        # Clear cart
        self.cart = []
        self.discount_var.set("0")
        self.payment_var.set("0")
        self._refresh_cart()
        self._load_products()
    
    def refresh(self):
        """Refresh the sales view"""
        self._load_products()

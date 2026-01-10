"""
Products Management Component - CRUD for products
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from config import COLORS, FONTS
from db_manager import ProductDatabase
from utils.helpers import format_currency, parse_float, parse_int, format_currency_input, parse_currency_input

class Products(tk.Frame):
    """Product management interface"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self.product_db = ProductDatabase()
        self.selected_product = None
        self._initialized = False
        
        self._create_widgets()
        self._initialized = True
    
    def _create_widgets(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=2)  # Table
        self.grid_columnconfigure(1, weight=1)  # Form
        self.grid_rowconfigure(0, weight=1)
        
        # Create both panels
        self._create_list_panel()
        self._create_form_panel()
        
        # Now load data after all widgets are created
        self._load_products()
    
    def _create_list_panel(self):
        """Create product list panel"""
        panel = tk.Frame(self, bg=COLORS['card'])
        panel.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        panel.grid(row=0, column=0, sticky='nsew', padx=(30, 10), pady=30)
        
        # Header
        header = tk.Frame(panel, bg=COLORS['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        title = tk.Label(
            header,
            text="📦 Daftar Produk",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        )
        title.pack(side='left')
        
        # Button row
        btn_row = tk.Frame(header, bg=COLORS['card'])
        btn_row.pack(side='right')
        
        import_btn = tk.Button(
            btn_row,
            text="📥 Import CSV",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._import_csv
        )
        import_btn.pack(side='left', padx=5)
        
        export_btn = tk.Button(
            btn_row,
            text="📤 Export CSV",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._export_csv
        )
        export_btn.pack(side='left', padx=5)
        
        # Search box
        search_frame = tk.Frame(panel, bg=COLORS['card'])
        search_frame.pack(fill='x', padx=20, pady=10)
        
        self.search_var = tk.StringVar()
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        search_entry.pack(fill='x', ipady=8, ipadx=10)
        search_entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        search_entry.insert(0, "🔍 Cari produk...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, 'end') if search_entry.get().startswith("🔍") else None)
        search_entry.bind('<KeyRelease>', self._on_search_key)
        
        # Product table
        table_frame = tk.Frame(panel, bg=COLORS['card'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('product_number', 'barcode', 'name', 'category', 'buy_price', 'sell_price')
        self.product_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.product_tree.heading('product_number', text='No.')
        self.product_tree.heading('barcode', text='Barcode')
        self.product_tree.heading('name', text='Nama Produk')
        self.product_tree.heading('category', text='Kategori')
        self.product_tree.heading('buy_price', text='Harga Beli')
        self.product_tree.heading('sell_price', text='Harga Jual')
        
        self.product_tree.column('product_number', width=50)
        self.product_tree.column('barcode', width=120)
        self.product_tree.column('name', width=180)
        self.product_tree.column('category', width=100)
        self.product_tree.column('buy_price', width=100)
        self.product_tree.column('sell_price', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection
        self.product_tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Stats row
        stats_frame = tk.Frame(panel, bg=COLORS['card'])
        stats_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Total: 0 produk",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        self.stats_label.pack(side='left')
    
    def _create_form_panel(self):
        """Create product form panel"""
        panel = tk.Frame(self, bg=COLORS['card'])
        panel.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        panel.grid(row=0, column=1, sticky='nsew', padx=(10, 30), pady=30)
        
        # Header
        header = tk.Frame(panel, bg=COLORS['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        self.form_title = tk.Label(
            header,
            text="➕ Tambah Produk",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        )
        self.form_title.pack(side='left')
        
        # Form fields
        form_frame = tk.Frame(panel, bg=COLORS['card'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Barcode with auto-generate toggle switch
        barcode_frame = tk.Frame(form_frame, bg=COLORS['card'])
        barcode_frame.pack(fill='x', pady=8)
        
        barcode_label_frame = tk.Frame(barcode_frame, bg=COLORS['card'])
        barcode_label_frame.pack(fill='x')
        
        lbl = tk.Label(
            barcode_label_frame,
            text="Barcode",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        lbl.pack(side='left')
        
        # Toggle switch container
        switch_frame = tk.Frame(barcode_label_frame, bg=COLORS['card'])
        switch_frame.pack(side='right')
        
        tk.Label(
            switch_frame,
            text="Auto",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(side='left', padx=(0, 5))
        
        # Custom toggle switch
        self.auto_barcode_var = tk.BooleanVar(value=True)
        self.switch_canvas = tk.Canvas(
            switch_frame,
            width=50,
            height=26,
            bg=COLORS['card'],
            highlightthickness=0,
            cursor='hand2'
        )
        self.switch_canvas.pack(side='left')
        
        # Draw initial switch state (ON)
        self._draw_switch(True)
        
        # Bind click event
        self.switch_canvas.bind('<Button-1>', self._on_switch_click)
        
        self.barcode_var = tk.StringVar()
        self.barcode_entry = tk.Entry(
            barcode_frame,
            textvariable=self.barcode_var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background'],
            state='disabled'
        )
        self.barcode_entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        self.barcode_entry.pack(fill='x', ipady=8, ipadx=8)
        
        # Name
        self._create_form_field(form_frame, "Nama Produk", "name")
        
        # Category
        self._create_category_field(form_frame)
        
        # Buy price (with currency formatting)
        self._create_currency_field(form_frame, "Harga Beli (Rp)", "buy_price")
        
        # Sell price (with currency formatting)
        self._create_currency_field(form_frame, "Harga Jual (Rp)", "sell_price")
        
        # Buttons
        btn_frame = tk.Frame(panel, bg=COLORS['card'])
        btn_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Save button
        self.save_btn = tk.Button(
            btn_frame,
            text="💾 Simpan",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            relief='flat',
            cursor='hand2',
            command=self._save_product
        )
        self.save_btn.pack(fill='x', ipady=10)
        
        # Delete button (starts inactive with gray colors)
        self.delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Hapus Produk",
            font=FONTS['body_bold'],
            fg='#64748B',
            bg='#E2E8F0',
            relief='flat',
            cursor='arrow',
            command=self._delete_product
        )
        self.delete_btn.pack(fill='x', ipady=10, pady=(10, 0))
        
        # Clear button
        clear_btn = tk.Button(
            btn_frame,
            text="🔄 Batal / Baru",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._clear_form
        )
        clear_btn.pack(fill='x', ipady=8, pady=(10, 0))
    
    def _create_form_field(self, parent, label, field_name):
        """Create a form input field"""
        frame = tk.Frame(parent, bg=COLORS['card'])
        frame.pack(fill='x', pady=8)
        
        lbl = tk.Label(
            frame,
            text=label,
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        lbl.pack(anchor='w')
        
        var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background']
        )
        entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        entry.pack(fill='x', ipady=8, ipadx=8)
        
        setattr(self, f"{field_name}_var", var)
        setattr(self, f"{field_name}_entry", entry)
    
    def _create_currency_field(self, parent, label, field_name):
        """Create a currency input field with auto-formatting"""
        frame = tk.Frame(parent, bg=COLORS['card'])
        frame.pack(fill='x', pady=8)
        
        lbl = tk.Label(
            frame,
            text=label,
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        lbl.pack(anchor='w')
        
        var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background']
        )
        entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        entry.pack(fill='x', ipady=8, ipadx=8)
        
        # Bind key release for auto-formatting
        def on_key_release(event):
            # Get current cursor position
            current_value = var.get()
            formatted = format_currency_input(current_value)
            if formatted != current_value:
                var.set(formatted)
                # Move cursor to end
                entry.icursor(tk.END)
        
        entry.bind('<KeyRelease>', on_key_release)
        
        setattr(self, f"{field_name}_var", var)
        setattr(self, f"{field_name}_entry", entry)
    
    def _create_category_field(self, parent):
        """Create category combobox field"""
        frame = tk.Frame(parent, bg=COLORS['card'])
        frame.pack(fill='x', pady=8)
        
        lbl = tk.Label(
            frame,
            text="Kategori",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        lbl.pack(anchor='w')
        
        self.category_var = tk.StringVar()
        
        # Get existing categories
        categories = self.product_db.get_categories()
        
        self.category_combo = ttk.Combobox(
            frame,
            textvariable=self.category_var,
            values=categories,
            font=FONTS['body']
        )
        self.category_combo.pack(fill='x', ipady=5)
    
    def _draw_switch(self, is_on):
        """Draw the toggle switch"""
        self.switch_canvas.delete('all')
        
        # Background track
        if is_on:
            track_color = COLORS['primary']
        else:
            track_color = COLORS['border']
        
        # Draw rounded rectangle track
        self.switch_canvas.create_oval(0, 0, 26, 26, fill=track_color, outline='')
        self.switch_canvas.create_oval(24, 0, 50, 26, fill=track_color, outline='')
        self.switch_canvas.create_rectangle(13, 0, 37, 26, fill=track_color, outline='')
        
        # Draw circle knob
        if is_on:
            knob_x = 35
        else:
            knob_x = 13
        
        self.switch_canvas.create_oval(
            knob_x - 10, 3,
            knob_x + 10, 23,
            fill='white',
            outline=''
        )
    
    def _on_switch_click(self, event):
        """Handle switch click"""
        current = self.auto_barcode_var.get()
        new_value = not current
        self.auto_barcode_var.set(new_value)
        self._draw_switch(new_value)
        self._toggle_barcode_entry()
    
    def _toggle_barcode_entry(self):
        """Toggle barcode entry based on auto-generate switch"""
        if self.auto_barcode_var.get():
            self.barcode_entry.configure(state='disabled')
            self.barcode_var.set('')
        else:
            self.barcode_entry.configure(state='normal')
    
    def _load_products(self, query=""):
        """Load products into treeview"""
        if not hasattr(self, 'product_tree'):
            return
            
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        if query:
            products = self.product_db.search(query)
        else:
            products = self.product_db.get_all()
        
        for p in products:
            self.product_tree.insert('', 'end', iid=p['id'], values=(
                p.get('product_number', ''),
                p['barcode'],
                p['name'],
                p['category'],
                format_currency(parse_float(p['buy_price'])),
                format_currency(parse_float(p['sell_price']))
            ))
        
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(text=f"Total: {len(products)} produk")
        
        # Update category combo if exists
        if hasattr(self, 'category_combo'):
            categories = self.product_db.get_categories()
            self.category_combo['values'] = categories
    
    def _on_search_key(self, event):
        """Handle search key release"""
        if not self._initialized:
            return
        query = self.search_var.get().strip()
        if query.startswith("🔍"):
            query = ""
        self._load_products(query)
    
    def _on_select(self, event):
        """Handle product selection"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        product_id = selection[0]
        product = self.product_db.get_by_id(product_id)
        
        if product:
            self.selected_product = product
            self.form_title.configure(text="✏️ Edit Produk")
            # Enable delete button with danger colors
            self.delete_btn.configure(fg=COLORS['white'], bg=COLORS['danger'], cursor='hand2')
            
            self.barcode_var.set(product['barcode'])
            self.auto_barcode_var.set(False)
            self._draw_switch(False)
            self.barcode_entry.configure(state='normal')
            self.name_var.set(product['name'])
            self.category_var.set(product['category'])
            self.buy_price_var.set(format_currency_input(product['buy_price']))
            self.sell_price_var.set(format_currency_input(product['sell_price']))
    
    def _clear_form(self):
        """Clear form fields"""
        self.selected_product = None
        self.form_title.configure(text="➕ Tambah Produk")
        # Disable delete button with gray colors
        self.delete_btn.configure(fg='#64748B', bg='#E2E8F0', cursor='arrow')
        
        self.barcode_var.set("")
        self.auto_barcode_var.set(True)
        self._draw_switch(True)
        self.barcode_entry.configure(state='disabled')
        self.name_var.set("")
        self.category_var.set("")
        self.buy_price_var.set("")
        self.sell_price_var.set("")
        
        # Clear table selection
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)
    
    def _save_product(self):
        """Save product (add or update)"""
        barcode = self.barcode_var.get().strip()
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        buy_price = parse_currency_input(self.buy_price_var.get())
        sell_price = parse_currency_input(self.sell_price_var.get())
        
        # Validation
        if not name:
            messagebox.showerror("Error", "Nama Produk wajib diisi!")
            return
        
        # Check barcode requirement (only if not auto-generate and not editing)
        if not barcode and not self.auto_barcode_var.get() and not self.selected_product:
            messagebox.showerror("Error", "Barcode wajib diisi atau aktifkan auto-generate!")
            return
        
        if sell_price <= 0:
            messagebox.showerror("Error", "Harga jual harus lebih dari 0!")
            return
        
        try:
            if self.selected_product:
                # Update existing
                self.product_db.update(
                    self.selected_product['id'],
                    barcode=barcode,
                    name=name,
                    category=category,
                    buy_price=buy_price,
                    sell_price=sell_price
                )
                messagebox.showinfo("Sukses", "Produk berhasil diupdate!")
            else:
                # Check barcode duplicate only if barcode is provided
                if barcode:
                    existing = self.product_db.get_by_barcode(barcode)
                    if existing:
                        messagebox.showerror("Error", f"Barcode '{barcode}' sudah digunakan!")
                        return
                
                # Add new (barcode can be empty - will be auto-generated)
                self.product_db.add(barcode, name, category, buy_price, sell_price)
                messagebox.showinfo("Sukses", "Produk berhasil ditambahkan!")
            
            self._clear_form()
            self._load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")
    
    def _delete_product(self):
        """Delete selected product"""
        if not self.selected_product:
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus produk '{self.selected_product['name']}'?"):
            try:
                self.product_db.delete(self.selected_product['id'])
                messagebox.showinfo("Sukses", "Produk berhasil dihapus!")
                self._clear_form()
                self._load_products()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")
    
    def _import_csv(self):
        """Import products from CSV file"""
        filepath = filedialog.askopenfilename(
            title="Pilih file CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            imported = 0
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check required fields
                    if 'barcode' in row and 'name' in row and 'sell_price' in row:
                        existing = self.product_db.get_by_barcode(row['barcode'])
                        if not existing:
                            self.product_db.add(
                                barcode=row.get('barcode', ''),
                                name=row.get('name', ''),
                                category=row.get('category', ''),
                                buy_price=parse_float(row.get('buy_price', 0)),
                                sell_price=parse_float(row.get('sell_price', 0)),
                                stock=parse_int(row.get('stock', 0))
                            )
                            imported += 1
            
            messagebox.showinfo("Sukses", f"{imported} produk berhasil diimport!")
            self._load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal import: {e}")
    
    def _export_csv(self):
        """Export products to CSV file"""
        filepath = filedialog.asksaveasfilename(
            title="Simpan file CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            return
        
        try:
            products = self.product_db.get_all()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['barcode', 'name', 'category', 'buy_price', 'sell_price', 'stock'])
                writer.writeheader()
                for p in products:
                    writer.writerow({
                        'barcode': p['barcode'],
                        'name': p['name'],
                        'category': p['category'],
                        'buy_price': p['buy_price'],
                        'sell_price': p['sell_price'],
                        'stock': p['stock']
                    })
            
            messagebox.showinfo("Sukses", f"{len(products)} produk berhasil diexport!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {e}")
    
    def refresh(self):
        """Refresh the products view"""
        self._load_products()

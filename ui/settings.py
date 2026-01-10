"""
Settings Component - Application configuration
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
from config import COLORS, FONTS, STORE_CONFIG, DATABASE_DIR, APP_DIR, ASSETS_DIR, THEMES, apply_theme
from db_manager import ProductDatabase, TransactionDatabase

class Settings(tk.Frame):
    """Application settings interface"""
    
    CONFIG_FILE = os.path.join(APP_DIR, "store_config.json")
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self._load_config()
        self._create_widgets()
    
    def _load_config(self):
        """Load store configuration"""
        self.config = STORE_CONFIG.copy()
        
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except:
                pass
    
    def _save_config(self):
        """Save store configuration"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan konfigurasi: {e}")
            return False
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Content - scrollable
        self._create_content()
    
    def _create_header(self):
        """Create page header"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        title = tk.Label(
            header,
            text="⚙️ Pengaturan",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        title.pack(side='left')
    
    def _create_content(self):
        """Create settings content with scroll"""
        # Outer container
        outer = tk.Frame(self, bg=COLORS['background'])
        outer.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Canvas for scrolling
        canvas = tk.Canvas(outer, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        
        # Scrollable frame
        self.scroll_frame = tk.Frame(canvas, bg=COLORS['background'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        def configure_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.scroll_frame.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', configure_width)
        
        # Mouse wheel scroll
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        # Grid configuration for content
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        
        # Left column - Store info
        self._create_store_section(self.scroll_frame)
        
        # Right column - Database, Theme, and backup
        self._create_database_section(self.scroll_frame)
        
        # Theme section (below database, same column)
        self._create_theme_section(self.scroll_frame)
    
    def _create_store_section(self, parent):
        """Create store info section"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=10)
        
        inner = tk.Frame(section, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            inner,
            text="🏪 Informasi Toko",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(0, 15))
        
        # Store name
        self._create_setting_field(inner, "Nama Toko", "name")
        
        # Address
        self._create_setting_field(inner, "Alamat", "address")
        
        # Phone
        self._create_setting_field(inner, "Telepon", "phone")
        
        # Footer message
        self._create_setting_field(inner, "Pesan di Struk", "footer")
        
        save_btn = tk.Button(
            inner,
            text="💾 Simpan Pengaturan Toko",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            relief='flat',
            cursor='hand2',
            command=self._save_store_settings
        )
        save_btn.pack(fill='x', pady=(20, 0), ipady=10)
        
        # Printer settings section
        self._create_printer_section(inner)
        
        # Logo section
        self._create_logo_section(inner)
    
    def _create_setting_field(self, parent, label, key):
        """Create a setting input field"""
        frame = tk.Frame(parent, bg=COLORS['card'])
        frame.pack(fill='x', pady=8)
        
        tk.Label(
            frame,
            text=label,
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        var = tk.StringVar(value=self.config.get(key, ""))
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=FONTS['body'],
            relief='flat',
            bg=COLORS['background']
        )
        entry.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        entry.pack(fill='x', ipady=8, ipadx=8)
        
        setattr(self, f"{key}_var", var)
    
    def _create_printer_section(self, parent):
        """Create printer settings section"""
        sep = tk.Frame(parent, bg=COLORS['border'], height=1)
        sep.pack(fill='x', pady=20)
        
        tk.Label(
            parent,
            text="🖨️ Pengaturan Printer",
            font=FONTS['body_bold'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        tk.Label(
            parent,
            text="Pilih printer default untuk cetak struk otomatis",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        # Get list of printers
        printers = self._get_printers()
        
        printer_frame = tk.Frame(parent, bg=COLORS['card'])
        printer_frame.pack(fill='x', pady=10)
        
        tk.Label(
            printer_frame,
            text="Printer Default:",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        self.printer_var = tk.StringVar(value=self.config.get('default_printer', ''))
        
        printer_combo = ttk.Combobox(
            printer_frame,
            textvariable=self.printer_var,
            values=printers,
            font=FONTS['body'],
            state='readonly'
        )
        printer_combo.pack(fill='x', pady=5, ipady=5)
        
        # Buttons row
        btn_row = tk.Frame(parent, bg=COLORS['card'])
        btn_row.pack(fill='x', pady=5)
        
        refresh_btn = tk.Button(
            btn_row,
            text="🔄 Refresh",
            font=FONTS['small'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=lambda: self._refresh_printers(printer_combo)
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        save_printer_btn = tk.Button(
            btn_row,
            text="💾 Simpan Printer",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['success'],
            relief='flat',
            cursor='hand2',
            command=self._save_printer_settings
        )
        save_printer_btn.pack(side='right', ipadx=20, ipady=5)
        
        # Status
        self.printer_status = tk.Label(
            parent,
            text="",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        self.printer_status.pack(anchor='w')
        
        # Show current printer if set
        current = self.config.get('default_printer', '')
        if current:
            self.printer_status.configure(text=f"✅ Printer aktif: {current}", fg=COLORS['success'])
    
    def _get_printers(self):
        """Get list of installed printers"""
        printers = []
        try:
            import subprocess
            # Use wmic to get list of printers
            result = subprocess.run(
                ['wmic', 'printer', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=10
            )
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                printer = line.strip()
                if printer:
                    printers.append(printer)
        except Exception as e:
            print(f"Error getting printers: {e}")
            # Add some common printer names as fallback
            printers = ["Microsoft Print to PDF", "Microsoft XPS Document Writer"]
        return printers
    
    def _refresh_printers(self, combo):
        """Refresh printer list"""
        printers = self._get_printers()
        combo['values'] = printers
        messagebox.showinfo("Info", f"Ditemukan {len(printers)} printer")
    
    def _save_printer_settings(self):
        """Save printer settings"""
        printer = self.printer_var.get()
        if printer:
            self.config['default_printer'] = printer
            if self._save_config():
                self.printer_status.configure(text=f"✅ Printer aktif: {printer}", fg=COLORS['success'])
                messagebox.showinfo("Sukses", f"Printer default disimpan: {printer}")
        else:
            # Clear default printer
            self.config['default_printer'] = ''
            if self._save_config():
                self.printer_status.configure(text="Tidak ada printer default", fg=COLORS['text_light'])
                messagebox.showinfo("Info", "Printer default dihapus")
    
    def _create_logo_section(self, parent):
        """Create logo upload section"""
        sep = tk.Frame(parent, bg=COLORS['border'], height=1)
        sep.pack(fill='x', pady=20)
        
        tk.Label(
            parent,
            text="🖼️ Logo Toko",
            font=FONTS['body_bold'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        tk.Label(
            parent,
            text="Logo akan ditampilkan di sidebar aplikasi",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        logo_btn = tk.Button(
            parent,
            text="📁 Pilih Logo",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['background'],
            relief='flat',
            cursor='hand2',
            command=self._select_logo
        )
        logo_btn.pack(anchor='w', pady=10)
        
        self.logo_status = tk.Label(
            parent,
            text="",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        )
        self.logo_status.pack(anchor='w')
        
        # Check if logo exists
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            self.logo_status.configure(text="✅ Logo sudah ada", fg=COLORS['success'])
    
    def _create_database_section(self, parent):
        """Create database management section"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=10)
        
        inner = tk.Frame(section, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            inner,
            text="🗄️ Database",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(0, 15))
        
        # Database info
        product_db = ProductDatabase()
        transaction_db = TransactionDatabase()
        
        products = product_db.get_all()
        transactions = transaction_db.get_all()
        
        info_frame = tk.Frame(inner, bg=COLORS['background'])
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text=f"📦 Total Produk: {len(products)}",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['background']
        ).pack(anchor='w', padx=15, pady=5)
        
        tk.Label(
            info_frame,
            text=f"🧾 Total Transaksi: {len(transactions)}",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['background']
        ).pack(anchor='w', padx=15, pady=5)
        
        # Backup buttons
        tk.Label(
            inner,
            text="Backup & Restore",
            font=FONTS['body_bold'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(20, 10))
        
        backup_btn = tk.Button(
            inner,
            text="📥 Backup Database",
            font=FONTS['body'],
            fg=COLORS['white'],
            bg=COLORS['success'],
            relief='flat',
            cursor='hand2',
            command=self._backup_database
        )
        backup_btn.pack(fill='x', pady=5, ipady=8)
        
        restore_btn = tk.Button(
            inner,
            text="📤 Restore Database",
            font=FONTS['body'],
            fg=COLORS['white'],
            bg=COLORS['warning'],
            relief='flat',
            cursor='hand2',
            command=self._restore_database
        )
        restore_btn.pack(fill='x', pady=5, ipady=8)
        
        # Danger zone
        sep = tk.Frame(inner, bg=COLORS['border'], height=1)
        sep.pack(fill='x', pady=20)
        
        tk.Label(
            inner,
            text="⚠️ Zona Berbahaya",
            font=FONTS['body_bold'],
            fg=COLORS['danger'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(0, 10))
        
        clear_trans_btn = tk.Button(
            inner,
            text="🗑️ Hapus Semua Transaksi",
            font=FONTS['body'],
            fg=COLORS['white'],
            bg=COLORS['danger'],
            relief='flat',
            cursor='hand2',
            command=self._clear_transactions
        )
        clear_trans_btn.pack(fill='x', pady=5, ipady=8)
        
        clear_products_btn = tk.Button(
            inner,
            text="🗑️ Hapus Semua Produk",
            font=FONTS['body'],
            fg=COLORS['white'],
            bg=COLORS['danger'],
            relief='flat',
            cursor='hand2',
            command=self._clear_products
        )
        clear_products_btn.pack(fill='x', pady=5, ipady=8)
    
    def _save_store_settings(self):
        """Save store settings"""
        self.config['name'] = self.name_var.get()
        self.config['address'] = self.address_var.get()
        self.config['phone'] = self.phone_var.get()
        self.config['footer'] = self.footer_var.get()
        
        if self._save_config():
            messagebox.showinfo("Sukses", "Pengaturan berhasil disimpan!")
    
    def _select_logo(self):
        """Select logo file"""
        filepath = filedialog.askopenfilename(
            title="Pilih Logo",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            try:
                # Copy to assets folder
                dest = os.path.join(ASSETS_DIR, "logo.png")
                shutil.copy2(filepath, dest)
                self.logo_status.configure(text="✅ Logo berhasil diupload! Restart aplikasi.", fg=COLORS['success'])
            except Exception as e:
                messagebox.showerror("Error", f"Gagal upload logo: {e}")
    
    def _backup_database(self):
        """Backup database files"""
        folder = filedialog.askdirectory(title="Pilih folder backup")
        
        if folder:
            try:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_folder = os.path.join(folder, f"backup_{timestamp}")
                os.makedirs(backup_folder, exist_ok=True)
                
                # Copy database files
                for filename in os.listdir(DATABASE_DIR):
                    if filename.endswith('.csv'):
                        src = os.path.join(DATABASE_DIR, filename)
                        dst = os.path.join(backup_folder, filename)
                        shutil.copy2(src, dst)
                
                # Copy config
                if os.path.exists(self.CONFIG_FILE):
                    shutil.copy2(self.CONFIG_FILE, os.path.join(backup_folder, "store_config.json"))
                
                messagebox.showinfo("Sukses", f"Backup berhasil disimpan ke:\n{backup_folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup gagal: {e}")
    
    def _restore_database(self):
        """Restore database from backup"""
        folder = filedialog.askdirectory(title="Pilih folder backup")
        
        if folder:
            if not messagebox.askyesno("Konfirmasi", "Data yang ada sekarang akan diganti dengan data backup. Lanjutkan?"):
                return
            
            try:
                # Copy database files
                for filename in os.listdir(folder):
                    if filename.endswith('.csv'):
                        src = os.path.join(folder, filename)
                        dst = os.path.join(DATABASE_DIR, filename)
                        shutil.copy2(src, dst)
                
                # Copy config
                config_src = os.path.join(folder, "store_config.json")
                if os.path.exists(config_src):
                    shutil.copy2(config_src, self.CONFIG_FILE)
                    self._load_config()
                
                messagebox.showinfo("Sukses", "Database berhasil direstore! Restart aplikasi.")
            except Exception as e:
                messagebox.showerror("Error", f"Restore gagal: {e}")
    
    def _clear_transactions(self):
        """Clear all transactions"""
        if messagebox.askyesno("Konfirmasi", "⚠️ PERINGATAN: Semua data transaksi akan dihapus permanen!\n\nLanjutkan?"):
            try:
                trans_file = os.path.join(DATABASE_DIR, "transactions.csv")
                if os.path.exists(trans_file):
                    os.remove(trans_file)
                    # Recreate empty file
                    TransactionDatabase()
                messagebox.showinfo("Sukses", "Semua transaksi berhasil dihapus!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")
    
    def _clear_products(self):
        """Clear all products"""
        if messagebox.askyesno("Konfirmasi", "⚠️ PERINGATAN: Semua data produk akan dihapus permanen!\n\nLanjutkan?"):
            try:
                prod_file = os.path.join(DATABASE_DIR, "products.csv")
                if os.path.exists(prod_file):
                    os.remove(prod_file)
                    # Recreate empty file
                    ProductDatabase()
                messagebox.showinfo("Sukses", "Semua produk berhasil dihapus!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")
    
    def refresh(self):
        """Refresh settings view"""
        self._load_config()
    
    def _create_theme_section(self, parent):
        """Create theme settings section"""
        section = tk.Frame(parent, bg=COLORS['card'])
        section.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        section.grid(row=1, column=1, sticky='nsew', padx=(10, 0), pady=10)
        
        inner = tk.Frame(section, bg=COLORS['card'])
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            inner,
            text="🎨 Tema Warna",
            font=FONTS['subheading'],
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            inner,
            text="Pilih tema warna untuk tampilan aplikasi",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        # Theme dropdown
        theme_frame = tk.Frame(inner, bg=COLORS['card'])
        theme_frame.pack(fill='x', pady=10)
        
        # Get current theme
        current_theme = self.config.get('theme', 'blue')
        
        # Create theme options
        theme_options = [(key, THEMES[key]['name']) for key in THEMES.keys()]
        theme_names = [name for _, name in theme_options]
        theme_keys = [key for key, _ in theme_options]
        
        # Find current theme index
        current_index = 0
        for i, key in enumerate(theme_keys):
            if key == current_theme:
                current_index = i
                break
        
        self.theme_var = tk.StringVar(value=theme_names[current_index])
        self.theme_keys = theme_keys
        self.theme_names = theme_names
        
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=theme_names,
            font=FONTS['body'],
            state='readonly',
            width=30
        )
        theme_combo.pack(fill='x', pady=5, ipady=5)
        
        # Theme preview colors
        preview_frame = tk.Frame(inner, bg=COLORS['card'])
        preview_frame.pack(fill='x', pady=10)
        
        tk.Label(
            preview_frame,
            text="Preview warna:",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(anchor='w')
        
        self.preview_colors_frame = tk.Frame(preview_frame, bg=COLORS['card'])
        self.preview_colors_frame.pack(fill='x', pady=5)
        
        # Initial preview
        self._update_theme_preview(current_theme)
        
        # Bind change event
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)
        
        # Save button
        save_theme_btn = tk.Button(
            inner,
            text="💾 Simpan Tema",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            relief='flat',
            cursor='hand2',
            command=self._save_theme_settings
        )
        save_theme_btn.pack(fill='x', pady=(10, 0), ipady=10)
        
        # Note
        tk.Label(
            inner,
            text="⚠️ Perubahan tema memerlukan restart aplikasi",
            font=FONTS['small'],
            fg=COLORS['warning'],
            bg=COLORS['card']
        ).pack(anchor='w', pady=(10, 0))
    
    def _update_theme_preview(self, theme_key):
        """Update theme color preview"""
        # Clear existing preview
        for widget in self.preview_colors_frame.winfo_children():
            widget.destroy()
        
        if theme_key in THEMES:
            theme = THEMES[theme_key]
            colors_to_show = ['primary', 'primary_dark', 'sidebar', 'sidebar_hover']
            
            for color_key in colors_to_show:
                if color_key in theme:
                    color_box = tk.Frame(
                        self.preview_colors_frame,
                        bg=theme[color_key],
                        width=40,
                        height=30
                    )
                    color_box.pack(side='left', padx=2)
                    color_box.pack_propagate(False)
    
    def _on_theme_change(self, event):
        """Handle theme selection change"""
        selected_name = self.theme_var.get()
        for i, name in enumerate(self.theme_names):
            if name == selected_name:
                self._update_theme_preview(self.theme_keys[i])
                break
    
    def _save_theme_settings(self):
        """Save theme settings"""
        selected_name = self.theme_var.get()
        theme_key = 'blue'  # default
        
        for i, name in enumerate(self.theme_names):
            if name == selected_name:
                theme_key = self.theme_keys[i]
                break
        
        self.config['theme'] = theme_key
        if self._save_config():
            messagebox.showinfo(
                "Sukses", 
                f"Tema '{selected_name}' berhasil disimpan!\n\nRestart aplikasi untuk menerapkan perubahan."
            )

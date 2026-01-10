"""
Sidebar Navigation Component with Logo
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from config import COLORS, FONTS, SIDEBAR_WIDTH, ASSETS_DIR

class Sidebar(tk.Frame):
    """Sidebar navigation with logo and menu items"""
    
    def __init__(self, parent, on_menu_click):
        super().__init__(parent, bg=COLORS['sidebar'], width=SIDEBAR_WIDTH)
        self.pack_propagate(False)
        
        self.on_menu_click = on_menu_click
        self.active_menu = "dashboard"
        self.menu_buttons = {}
        self.logo_image = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Logo section
        self._create_logo_section()
        
        # Separator
        sep = tk.Frame(self, bg=COLORS['sidebar_hover'], height=1)
        sep.pack(fill='x', padx=15, pady=10)
        
        # Menu items
        self._create_menu_items()
        
        # Bottom section - version info
        self._create_bottom_section()
    
    def _create_logo_section(self):
        """Create logo area at top of sidebar"""
        logo_frame = tk.Frame(self, bg=COLORS['sidebar'])
        logo_frame.pack(fill='x', pady=(20, 10))
        
        # Try to load logo image
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                # Resize to fit sidebar
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                
                logo_label = tk.Label(logo_frame, image=self.logo_image, bg=COLORS['sidebar'])
                logo_label.pack()
            except Exception as e:
                self._create_text_logo(logo_frame)
        else:
            self._create_text_logo(logo_frame)
        
        # App name
        app_name = tk.Label(
            logo_frame,
            text="APLIKASI KASIR",
            font=FONTS['logo'],
            fg=COLORS['white'],
            bg=COLORS['sidebar']
        )
        app_name.pack(pady=(10, 0))
        
        # Tagline
        tagline = tk.Label(
            logo_frame,
            text="Point of Sale System",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['sidebar']
        )
        tagline.pack()
    
    def _create_text_logo(self, parent):
        """Create text-based logo if no image available"""
        logo_container = tk.Frame(parent, bg=COLORS['primary'], width=60, height=60)
        logo_container.pack()
        logo_container.pack_propagate(False)
        
        logo_text = tk.Label(
            logo_container,
            text="POS",
            font=('Segoe UI', 20, 'bold'),
            fg=COLORS['white'],
            bg=COLORS['primary']
        )
        logo_text.place(relx=0.5, rely=0.5, anchor='center')
    
    def _create_menu_items(self):
        """Create menu buttons"""
        menu_frame = tk.Frame(self, bg=COLORS['sidebar'])
        menu_frame.pack(fill='both', expand=True, padx=10)
        
        menus = [
            ("dashboard", "📊", "Dashboard"),
            ("sales", "🛒", "Penjualan"),
            ("products", "📦", "Produk"),
            ("history", "📋", "Riwayat"),
            ("report", "📈", "Rekap Bulanan"),
            ("settings", "⚙️", "Pengaturan"),
            ("developer", "👨‍💻", "Developer"),
        ]
        
        for menu_id, icon, text in menus:
            btn = self._create_menu_button(menu_frame, menu_id, icon, text)
            self.menu_buttons[menu_id] = btn
        
        # Set initial active state
        self._set_active("dashboard")
    
    def _create_menu_button(self, parent, menu_id, icon, text):
        """Create a single menu button"""
        btn = tk.Frame(parent, bg=COLORS['sidebar'], cursor='hand2')
        btn.pack(fill='x', pady=2)
        
        # Inner container for padding
        inner = tk.Frame(btn, bg=COLORS['sidebar'])
        inner.pack(fill='x', padx=5, pady=8)
        
        # Icon
        icon_label = tk.Label(
            inner,
            text=icon,
            font=('Segoe UI', 14),
            fg=COLORS['white'],
            bg=COLORS['sidebar']
        )
        icon_label.pack(side='left', padx=(10, 10))
        
        # Text
        text_label = tk.Label(
            inner,
            text=text,
            font=FONTS['menu'],
            fg=COLORS['white'],
            bg=COLORS['sidebar'],
            anchor='w'
        )
        text_label.pack(side='left', fill='x', expand=True)
        
        # Store references
        btn.inner = inner
        btn.icon_label = icon_label
        btn.text_label = text_label
        btn.menu_id = menu_id
        
        # Bind events
        for widget in [btn, inner, icon_label, text_label]:
            widget.bind('<Enter>', lambda e, b=btn: self._on_hover(b, True))
            widget.bind('<Leave>', lambda e, b=btn: self._on_hover(b, False))
            widget.bind('<Button-1>', lambda e, mid=menu_id: self._on_click(mid))
        
        return btn
    
    def _on_hover(self, btn, entering):
        """Handle hover effect"""
        if btn.menu_id == self.active_menu:
            return
        
        color = COLORS['sidebar_hover'] if entering else COLORS['sidebar']
        btn.configure(bg=color)
        btn.inner.configure(bg=color)
        btn.icon_label.configure(bg=color)
        btn.text_label.configure(bg=color)
    
    def _on_click(self, menu_id):
        """Handle menu click"""
        self._set_active(menu_id)
        if self.on_menu_click:
            self.on_menu_click(menu_id)
    
    def _set_active(self, menu_id):
        """Set active menu item"""
        # Reset previous active
        if self.active_menu in self.menu_buttons:
            btn = self.menu_buttons[self.active_menu]
            btn.configure(bg=COLORS['sidebar'])
            btn.inner.configure(bg=COLORS['sidebar'])
            btn.icon_label.configure(bg=COLORS['sidebar'])
            btn.text_label.configure(bg=COLORS['sidebar'], font=FONTS['menu'])
        
        # Set new active
        self.active_menu = menu_id
        if menu_id in self.menu_buttons:
            btn = self.menu_buttons[menu_id]
            btn.configure(bg=COLORS['sidebar_active'])
            btn.inner.configure(bg=COLORS['sidebar_active'])
            btn.icon_label.configure(bg=COLORS['sidebar_active'])
            btn.text_label.configure(bg=COLORS['sidebar_active'], font=FONTS['menu_bold'])
    
    def _create_bottom_section(self):
        """Create bottom section with version info"""
        bottom = tk.Frame(self, bg=COLORS['sidebar'])
        bottom.pack(fill='x', side='bottom', pady=15)
        
        version = tk.Label(
            bottom,
            text="v1.0.0",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['sidebar']
        )
        version.pack()

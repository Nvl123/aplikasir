"""
Developer Component - Developer information page
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser
from config import COLORS, FONTS, ASSETS_DIR

class Developer(tk.Frame):
    """Developer information page"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['background'])
        
        self.dev_image = None
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        self._create_header()
        
        # Content
        self._create_content()
    
    def _create_header(self):
        """Create page header"""
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        tk.Label(
            header,
            text="👨‍💻 Developer",
            font=FONTS['heading'],
            fg=COLORS['text'],
            bg=COLORS['background']
        ).pack(side='left')
    
    def _create_content(self):
        """Create main content"""
        # Center container
        container = tk.Frame(self, bg=COLORS['background'])
        container.pack(expand=True)
        
        # Card
        card = tk.Frame(container, bg=COLORS['card'])
        card.configure(highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(padx=50, pady=30)
        
        inner = tk.Frame(card, bg=COLORS['card'])
        inner.pack(padx=50, pady=40)
        
        # Developer photo
        self._create_photo(inner)
        
        # Developer name
        tk.Label(
            inner,
            text="Novil M",
            font=('Segoe UI', 28, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['card']
        ).pack(pady=(20, 5))
        
        # Title
        tk.Label(
            inner,
            text="Software Developer",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(pady=(0, 20))
        
        # Separator
        sep = tk.Frame(inner, bg=COLORS['border'], height=1, width=200)
        sep.pack(pady=15)
        
        # Contact info
        contacts = [
            ("📧", "Email", "mohnovilm@gmail.com", "mailto:mohnovilm@gmail.com"),
            ("📷", "Instagram", "@me_ezpzy", "https://instagram.com/me_ezpzy"),
        ]
        
        for icon, label, value, link in contacts:
            self._create_contact_row(inner, icon, label, value, link)
        
        # Footer message
        tk.Label(
            inner,
            text="Terima kasih telah menggunakan Aplikasi Kasir ini!",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(pady=(30, 10))
        
        # App info
        tk.Label(
            inner,
            text="Aplikasi Kasir v1.0.0",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack()
        
        tk.Label(
            inner,
            text="Built with Python & Tkinter ❤️",
            font=FONTS['small'],
            fg=COLORS['text_light'],
            bg=COLORS['card']
        ).pack(pady=(2, 0))
    
    def _create_photo(self, parent):
        """Create developer photo"""
        photo_frame = tk.Frame(parent, bg=COLORS['primary'], width=130, height=130)
        photo_frame.pack()
        photo_frame.pack_propagate(False)
        
        # Try to load developer image
        photo_path = os.path.join(ASSETS_DIR, "developer.jpg")
        if os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                # Resize and make circular crop
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                self.dev_image = ImageTk.PhotoImage(img)
                
                photo_label = tk.Label(photo_frame, image=self.dev_image, bg=COLORS['primary'])
                photo_label.place(relx=0.5, rely=0.5, anchor='center')
            except Exception as e:
                self._create_placeholder_photo(photo_frame)
        else:
            self._create_placeholder_photo(photo_frame)
    
    def _create_placeholder_photo(self, parent):
        """Create placeholder photo"""
        tk.Label(
            parent,
            text="👤",
            font=('Segoe UI', 50),
            fg=COLORS['white'],
            bg=COLORS['primary']
        ).place(relx=0.5, rely=0.5, anchor='center')
    
    def _create_contact_row(self, parent, icon, label, value, link):
        """Create contact info row"""
        row = tk.Frame(parent, bg=COLORS['card'])
        row.pack(fill='x', pady=8)
        
        # Icon and label
        left = tk.Frame(row, bg=COLORS['card'])
        left.pack(side='left')
        
        tk.Label(
            left,
            text=f"{icon} {label}:",
            font=FONTS['body'],
            fg=COLORS['text_light'],
            bg=COLORS['card'],
            width=12,
            anchor='w'
        ).pack(side='left')
        
        # Value (clickable)
        value_label = tk.Label(
            row,
            text=value,
            font=FONTS['body_bold'],
            fg=COLORS['primary'],
            bg=COLORS['card'],
            cursor='hand2'
        )
        value_label.pack(side='left', padx=(10, 0))
        
        # Bind click
        value_label.bind('<Button-1>', lambda e, url=link: self._open_link(url))
        value_label.bind('<Enter>', lambda e, lbl=value_label: lbl.configure(fg=COLORS['primary_dark']))
        value_label.bind('<Leave>', lambda e, lbl=value_label: lbl.configure(fg=COLORS['primary']))
    
    def _open_link(self, url):
        """Open link in browser"""
        try:
            webbrowser.open(url)
        except:
            pass
    
    def refresh(self):
        """Refresh page"""
        pass

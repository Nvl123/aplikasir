"""
Aplikasi Kasir - Main Entry Point
Point of Sale System dengan Python Tkinter
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add app directory to path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from config import COLORS, FONTS, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, SIDEBAR_WIDTH
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.sales import Sales
from ui.products import Products
from ui.history import History
from ui.settings import Settings
from ui.report import Report
from ui.developer import Developer
from ui.receipt import show_receipt


class KasirApp(tk.Tk):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Aplikasi Kasir")
        self.geometry("1200x700")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(bg=COLORS['background'])
        
        # Configure styles
        self._setup_styles()
        
        # Create main layout
        self._create_layout()
        
        # Initialize pages
        self._init_pages()
        
        # Show dashboard by default
        self._show_page("dashboard")
        
        # Center window
        self._center_window()
    
    def _setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview style
        style.configure(
            "Treeview",
            background=COLORS['white'],
            foreground=COLORS['text'],
            fieldbackground=COLORS['white'],
            font=FONTS['body'],
            rowheight=35
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS['background'],
            foreground=COLORS['text'],
            font=FONTS['body_bold']
        )
        style.map(
            "Treeview",
            background=[('selected', COLORS['primary_light'])],
            foreground=[('selected', COLORS['white'])]
        )
        
        # Scrollbar style
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS['border'],
            troughcolor=COLORS['background']
        )
        
        # Combobox style
        style.configure(
            "TCombobox",
            fieldbackground=COLORS['background'],
            background=COLORS['white']
        )
    
    def _create_layout(self):
        """Create main layout with sidebar and content area"""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar - fixed
        self.grid_columnconfigure(1, weight=1)  # Content - expandable
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = Sidebar(self, self._on_menu_click)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        
        # Content area
        self.content_frame = tk.Frame(self, bg=COLORS['background'])
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def _init_pages(self):
        """Initialize all page frames"""
        self.pages = {}
        
        # Dashboard
        self.pages['dashboard'] = Dashboard(self.content_frame)
        
        # Sales
        self.pages['sales'] = Sales(self.content_frame, on_print_receipt=self._show_receipt)
        
        # Products
        self.pages['products'] = Products(self.content_frame)
        
        # History
        self.pages['history'] = History(self.content_frame, on_print_receipt=self._show_receipt)
        
        # Settings
        self.pages['settings'] = Settings(self.content_frame)
        
        # Report
        self.pages['report'] = Report(self.content_frame)
        
        # Developer
        self.pages['developer'] = Developer(self.content_frame)
        
        # Grid all pages (hidden initially)
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky='nsew')
            page.grid_remove()
    
    def _on_menu_click(self, menu_id):
        """Handle sidebar menu click"""
        self._show_page(menu_id)
    
    def _show_page(self, page_id):
        """Show specified page"""
        # Hide all pages
        for page in self.pages.values():
            page.grid_remove()
        
        # Show selected page
        if page_id in self.pages:
            self.pages[page_id].grid()
            
            # Refresh page data
            if hasattr(self.pages[page_id], 'refresh'):
                self.pages[page_id].refresh()
    
    def _show_receipt(self, transaction):
        """Show receipt dialog"""
        show_receipt(self, transaction)
    
    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Main entry point"""
    try:
        # Check for PIL (optional, for logo)
        try:
            from PIL import Image, ImageTk
        except ImportError:
            print("Note: PIL not installed. Logo display will use text fallback.")
            print("Install with: pip install Pillow")
        
        app = KasirApp()
        app.mainloop()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

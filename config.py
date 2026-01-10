"""
Konfigurasi Aplikasi Kasir
"""
import os
import sys
import json

# Detect if running as PyInstaller bundle
def get_base_path():
    """Get the base path for the application"""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE - use the directory containing the EXE
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_assets_path():
    """Get the assets path - bundled in EXE or in app directory"""
    if getattr(sys, 'frozen', False):
        # When frozen, assets are bundled - check both locations
        # First try next to EXE (for user-added files like logo)
        exe_assets = os.path.join(os.path.dirname(sys.executable), "assets")
        if os.path.exists(exe_assets):
            return exe_assets
        # Fallback to bundled assets in temp
        return os.path.join(sys._MEIPASS, "assets")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Path aplikasi - persistent location for data
APP_DIR = get_base_path()
DATABASE_DIR = os.path.join(APP_DIR, "database")
ASSETS_DIR = get_assets_path()

# Pastikan folder ada (untuk data yang perlu ditulis)
os.makedirs(DATABASE_DIR, exist_ok=True)
# Create assets folder next to EXE if frozen
if getattr(sys, 'frozen', False):
    os.makedirs(os.path.join(os.path.dirname(sys.executable), "assets"), exist_ok=True)
else:
    os.makedirs(ASSETS_DIR, exist_ok=True)

# Database files
PRODUCTS_FILE = os.path.join(DATABASE_DIR, "products.csv")
TRANSACTIONS_FILE = os.path.join(DATABASE_DIR, "transactions.csv")

# Informasi Toko (bisa diubah di settings)
STORE_CONFIG = {
    "name": "TOKO SEJAHTERA",
    "address": "Jl. Contoh No. 123",
    "phone": "08123456789",
    "footer": "Terima kasih telah berbelanja!"
}

# Available color themes
THEMES = {
    'blue': {
        'name': 'Biru (Default)',
        'primary': '#2563EB',
        'primary_dark': '#1D4ED8',
        'primary_light': '#3B82F6',
        'sidebar': '#1E293B',
        'sidebar_hover': '#334155',
        'sidebar_active': '#2563EB',
    },
    'green': {
        'name': 'Hijau',
        'primary': '#059669',
        'primary_dark': '#047857',
        'primary_light': '#10B981',
        'sidebar': '#064E3B',
        'sidebar_hover': '#065F46',
        'sidebar_active': '#059669',
    },
    'purple': {
        'name': 'Ungu',
        'primary': '#7C3AED',
        'primary_dark': '#6D28D9',
        'primary_light': '#8B5CF6',
        'sidebar': '#2E1065',
        'sidebar_hover': '#3B0764',
        'sidebar_active': '#7C3AED',
    },
    'orange': {
        'name': 'Oranye',
        'primary': '#EA580C',
        'primary_dark': '#C2410C',
        'primary_light': '#F97316',
        'sidebar': '#431407',
        'sidebar_hover': '#7C2D12',
        'sidebar_active': '#EA580C',
    },
    'dark': {
        'name': 'Gelap',
        'primary': '#6366F1',
        'primary_dark': '#4F46E5',
        'primary_light': '#818CF8',
        'sidebar': '#0F172A',
        'sidebar_hover': '#1E293B',
        'sidebar_active': '#6366F1',
        'background': '#1E293B',
        'card': '#334155',
        'text': '#F1F5F9',
        'text_light': '#94A3B8',
        'border': '#475569',
    },
}

# Default colors (will be updated by theme)
COLORS = {
    'primary': '#2563EB',
    'primary_dark': '#1D4ED8',
    'primary_light': '#3B82F6',
    'secondary': '#64748B',
    'success': '#10B981',
    'success_dark': '#059669',
    'danger': '#EF4444',
    'danger_dark': '#DC2626',
    'warning': '#F59E0B',
    'background': '#F1F5F9',
    'sidebar': '#1E293B',
    'sidebar_hover': '#334155',
    'sidebar_active': '#2563EB',
    'white': '#FFFFFF',
    'text': '#1E293B',
    'text_light': '#64748B',
    'border': '#E2E8F0',
    'card': '#FFFFFF'
}

def load_theme():
    """Load saved theme from config file"""
    config_file = os.path.join(APP_DIR, "store_config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('theme', 'blue')
        except:
            pass
    return 'blue'

def apply_theme(theme_name='blue'):
    """Apply a color theme to the COLORS dictionary"""
    global COLORS
    
    if theme_name not in THEMES:
        theme_name = 'blue'
    
    theme = THEMES[theme_name]
    
    # Reset to default light colors first
    COLORS.update({
        'background': '#F1F5F9',
        'card': '#FFFFFF',
        'text': '#1E293B',
        'text_light': '#64748B',
        'border': '#E2E8F0',
        'white': '#FFFFFF',
    })
    
    # Apply theme colors
    for key, value in theme.items():
        if key != 'name' and key in COLORS:
            COLORS[key] = value

# Load and apply theme on startup
_current_theme = load_theme()
apply_theme(_current_theme)

# Font
FONTS = {
    'heading': ('Segoe UI', 18, 'bold'),
    'subheading': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 11),
    'body_bold': ('Segoe UI', 11, 'bold'),
    'small': ('Segoe UI', 10),
    'menu': ('Segoe UI', 12),
    'menu_bold': ('Segoe UI', 12, 'bold'),
    'receipt': ('Consolas', 10),
    'receipt_bold': ('Consolas', 10, 'bold'),
    'logo': ('Segoe UI', 20, 'bold')
}

# Window settings
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 600
SIDEBAR_WIDTH = 220


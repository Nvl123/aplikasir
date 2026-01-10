"""
Utility helper functions
"""
import uuid
from datetime import datetime

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())[:8].upper()

def generate_transaction_id():
    """Generate transaction ID with date prefix"""
    date_prefix = datetime.now().strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:6].upper()
    return f"TRX-{date_prefix}-{unique}"

def format_currency(amount):
    """Format number as Indonesian Rupiah"""
    try:
        amount = float(amount)
        return f"Rp {amount:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

def format_date(date_str):
    """Format date string to readable format"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

def format_datetime(dt_str):
    """Format datetime string"""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return dt_str

def get_current_date():
    """Get current date as string"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    """Get current time as string"""
    return datetime.now().strftime("%H:%M:%S")

def get_current_datetime():
    """Get current datetime as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_float(value, default=0.0):
    """Safely parse float value"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def parse_int(value, default=0):
    """Safely parse integer value"""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def generate_barcode(product_number):
    """Generate barcode from product number with prefix"""
    # Format: PRD + product_number (padded to 6 digits)
    return f"PRD{int(product_number):06d}"

def format_currency_input(value):
    """Format number with thousand separator (Indonesian format: dot)
    
    Args:
        value: String input from entry field
    
    Returns:
        Formatted string with dots as thousand separators
    """
    # Remove all non-digit characters
    digits = ''.join(c for c in str(value) if c.isdigit())
    
    if not digits:
        return ''
    
    # Convert to integer and format with dots
    num = int(digits)
    # Format with commas first, then replace with dots
    formatted = f"{num:,}".replace(",", ".")
    return formatted

def parse_currency_input(value):
    """Parse formatted currency string back to float
    
    Args:
        value: Formatted string like "1.000.000"
    
    Returns:
        Float value
    """
    # Remove all dots (thousand separator)
    clean = str(value).replace(".", "")
    try:
        return float(clean)
    except (ValueError, TypeError):
        return 0.0

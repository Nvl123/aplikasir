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
    
    Handles two cases:
    1. Database values like "25000.0" -> "25.000"
    2. User typing with existing format "1.000" -> keeps working correctly
    
    Args:
        value: String input from entry field or float/database value
    
    Returns:
        Formatted string with dots as thousand separators
    """
    str_value = str(value).strip()
    
    if not str_value:
        return ''
    
    # Check if this looks like a database float value
    # Database floats have format like "25000.0" or "1500.5" (one decimal place typically)
    # Thousand-separated values look like "1.000" or "25.000" (dots every 3 digits)
    # Key difference: database float has dot NOT at position that would be thousand separator
    import re
    
    # Match pattern: digits, dot, 1-2 digits at end (typical float from database)
    # But NOT if it looks like thousand separator (dot followed by exactly 3 digits before end or another dot)
    if re.match(r'^\d+\.\d{1,2}$', str_value):
        # This is likely a float from database (e.g., "25000.0" or "1500.50")
        try:
            num = int(float(str_value))
            if num == 0:
                return ''
            return f"{num:,}".replace(",", ".")
        except (ValueError, TypeError):
            pass
    
    # For user input or already formatted values:
    # Remove all dots (thousand separators) and extract digits
    clean_value = str_value.replace(".", "")
    digits = ''.join(c for c in clean_value if c.isdigit())
    
    if not digits:
        return ''
    
    num = int(digits)
    
    if num == 0:
        return ''
    
    # Format with dots as thousand separator
    return f"{num:,}".replace(",", ".")

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

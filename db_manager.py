"""
Database Manager - CSV operations for products and transactions
"""
import csv
import os
import json
from datetime import datetime
from config import PRODUCTS_FILE, TRANSACTIONS_FILE
from utils.helpers import generate_id, generate_transaction_id, get_current_datetime, generate_barcode

class ProductDatabase:
    """Manage products CSV database"""
    
    HEADERS = ['id', 'product_number', 'barcode', 'name', 'category', 'buy_price', 'sell_price', 'created_at', 'updated_at']
    
    def __init__(self):
        self.file_path = PRODUCTS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if not exists"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADERS)
    
    def get_all(self):
        """Get all products"""
        products = []
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    products.append(row)
        except Exception as e:
            print(f"Error reading products: {e}")
        return products
    
    def get_by_id(self, product_id):
        """Get product by ID"""
        products = self.get_all()
        for p in products:
            if p['id'] == product_id:
                return p
        return None
    
    def get_by_barcode(self, barcode):
        """Get product by barcode"""
        products = self.get_all()
        for p in products:
            if p['barcode'] == barcode:
                return p
        return None
    
    def get_by_product_number(self, product_number):
        """Get product by product number"""
        products = self.get_all()
        for p in products:
            if p.get('product_number') == str(product_number):
                return p
        return None
    
    def generate_product_number(self):
        """Generate next product number (auto-increment)"""
        products = self.get_all()
        if not products:
            return 1
        max_num = 0
        for p in products:
            try:
                num = int(p.get('product_number', 0))
                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                pass
        return max_num + 1
    
    def search(self, query):
        """Search products by name, barcode, or product_number"""
        products = self.get_all()
        query = query.lower()
        results = []
        for p in products:
            if (query in p['name'].lower() or 
                query in p['barcode'].lower() or
                query == p.get('product_number', '').lower()):
                results.append(p)
        return results
    
    def add(self, barcode, name, category, buy_price, sell_price):
        """Add new product"""
        product_number = self.generate_product_number()
        
        # Auto-generate barcode if empty
        if not barcode:
            barcode = generate_barcode(product_number)
        
        product = {
            'id': generate_id(),
            'product_number': str(product_number),
            'barcode': barcode,
            'name': name,
            'category': category,
            'buy_price': str(buy_price),
            'sell_price': str(sell_price),
            'created_at': get_current_datetime(),
            'updated_at': get_current_datetime()
        }
        
        with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(product)
        
        return product
    
    def update(self, product_id, **kwargs):
        """Update product by ID"""
        products = self.get_all()
        updated = False
        
        for i, p in enumerate(products):
            if p['id'] == product_id:
                for key, value in kwargs.items():
                    if key in self.HEADERS:
                        products[i][key] = str(value)
                products[i]['updated_at'] = get_current_datetime()
                updated = True
                break
        
        if updated:
            self._write_all(products)
        
        return updated
    
    def delete(self, product_id):
        """Delete product by ID"""
        products = self.get_all()
        new_products = [p for p in products if p['id'] != product_id]
        
        if len(new_products) < len(products):
            self._write_all(new_products)
            return True
        return False
    
    def _write_all(self, products):
        """Write all products to CSV"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(products)
    
    def get_categories(self):
        """Get all unique categories"""
        products = self.get_all()
        categories = set()
        for p in products:
            if p['category']:
                categories.add(p['category'])
        return sorted(list(categories))


class TransactionDatabase:
    """Manage transactions CSV database"""
    
    HEADERS = ['id', 'date', 'time', 'items', 'subtotal', 'discount', 'total', 'payment', 'change', 'cashier']
    
    def __init__(self):
        self.file_path = TRANSACTIONS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if not exists"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADERS)
    
    def get_all(self):
        """Get all transactions"""
        transactions = []
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse items JSON
                    try:
                        row['items_list'] = json.loads(row['items'])
                    except:
                        row['items_list'] = []
                    transactions.append(row)
        except Exception as e:
            print(f"Error reading transactions: {e}")
        return transactions
    
    def get_by_id(self, transaction_id):
        """Get transaction by ID"""
        transactions = self.get_all()
        for t in transactions:
            if t['id'] == transaction_id:
                return t
        return None
    
    def get_by_date(self, date_str):
        """Get transactions by date (YYYY-MM-DD)"""
        transactions = self.get_all()
        return [t for t in transactions if t['date'] == date_str]
    
    def get_by_date_range(self, start_date, end_date):
        """Get transactions within date range"""
        transactions = self.get_all()
        results = []
        for t in transactions:
            if start_date <= t['date'] <= end_date:
                results.append(t)
        return results
    
    def add(self, items, subtotal, discount, total, payment, change, cashier="Kasir"):
        """Add new transaction"""
        now = datetime.now()
        transaction = {
            'id': generate_transaction_id(),
            'date': now.strftime("%Y-%m-%d"),
            'time': now.strftime("%H:%M:%S"),
            'items': json.dumps(items, ensure_ascii=False),
            'subtotal': str(subtotal),
            'discount': str(discount),
            'total': str(total),
            'payment': str(payment),
            'change': str(change),
            'cashier': cashier
        }
        
        with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(transaction)
        
        return transaction
    
    def get_today_summary(self):
        """Get today's sales summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        transactions = self.get_by_date(today)
        
        total_sales = sum(float(t['total']) for t in transactions)
        total_transactions = len(transactions)
        
        return {
            'date': today,
            'total_sales': total_sales,
            'total_transactions': total_transactions
        }
    
    def delete(self, transaction_id):
        """Delete transaction by ID"""
        transactions = self.get_all()
        new_transactions = [t for t in transactions if t['id'] != transaction_id]
        
        if len(new_transactions) < len(transactions):
            self._write_all(new_transactions)
            return True
        return False
    
    def _write_all(self, transactions):
        """Write all transactions to CSV"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            for t in transactions:
                # Remove parsed items_list before writing
                row = {k: v for k, v in t.items() if k in self.HEADERS}
                writer.writerow(row)

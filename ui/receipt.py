"""
Receipt Component - Preview and print receipts using Windows printer
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
import json
from config import COLORS, FONTS, STORE_CONFIG, APP_DIR
from utils.helpers import format_currency, format_date

class Receipt(tk.Toplevel):
    """Receipt preview and print dialog"""
    
    CONFIG_FILE = os.path.join(APP_DIR, "store_config.json")
    
    def __init__(self, parent, transaction):
        super().__init__(parent)
        
        self.transaction = transaction
        self._load_store_config()
        
        self.title("Struk Pembayaran")
        self.geometry("400x600")
        self.resizable(False, True)
        self.transient(parent)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # Show print confirmation after window is displayed
        self.after(300, self._ask_print_confirmation)
    
    def _load_store_config(self):
        """Load store configuration"""
        self.store_config = STORE_CONFIG.copy()
        
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.store_config.update(saved_config)
            except:
                pass
    
    def _create_widgets(self):
        # Main container
        main = tk.Frame(self, bg=COLORS['white'])
        main.pack(fill='both', expand=True)
        
        # Receipt preview
        self._create_receipt_preview(main)
        
        # Action buttons
        self._create_buttons(main)
    
    def _create_receipt_preview(self, parent):
        """Create receipt preview"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=COLORS['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        
        self.receipt_frame = tk.Frame(canvas, bg=COLORS['white'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True, pady=10)
        
        canvas_frame = canvas.create_window((0, 0), window=self.receipt_frame, anchor='nw')
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.receipt_frame.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Build receipt content
        self._build_receipt_content()
    
    def _build_receipt_content(self):
        """Build receipt content"""
        frame = self.receipt_frame
        t = self.transaction
        
        # Store header
        tk.Label(
            frame,
            text=self.store_config.get('name', 'TOKO'),
            font=FONTS['receipt_bold'],
            bg=COLORS['white']
        ).pack(pady=(20, 2))
        
        tk.Label(
            frame,
            text=self.store_config.get('address', ''),
            font=FONTS['receipt'],
            fg=COLORS['text_light'],
            bg=COLORS['white']
        ).pack()
        
        tk.Label(
            frame,
            text=self.store_config.get('phone', ''),
            font=FONTS['receipt'],
            fg=COLORS['text_light'],
            bg=COLORS['white']
        ).pack()
        
        # Separator
        self._add_separator(frame)
        
        # Transaction info
        info_frame = tk.Frame(frame, bg=COLORS['white'])
        info_frame.pack(fill='x', padx=30)
        
        self._add_info_row(info_frame, "No", t['id'])
        self._add_info_row(info_frame, "Tanggal", format_date(t['date']))
        self._add_info_row(info_frame, "Waktu", t['time'])
        self._add_info_row(info_frame, "Kasir", t.get('cashier', 'Kasir'))
        
        # Separator
        self._add_separator(frame)
        
        # Items
        items_frame = tk.Frame(frame, bg=COLORS['white'])
        items_frame.pack(fill='x', padx=30)
        
        items = t.get('items_list', [])
        if not items and 'items' in t:
            try:
                items = json.loads(t['items'])
            except:
                items = []
        
        for item in items:
            self._add_item_row(items_frame, item)
        
        # Separator
        self._add_separator(frame)
        
        # Totals
        totals_frame = tk.Frame(frame, bg=COLORS['white'])
        totals_frame.pack(fill='x', padx=30)
        
        subtotal = float(t.get('subtotal', 0))
        discount = float(t.get('discount', 0))
        total = float(t.get('total', 0))
        payment = float(t.get('payment', 0))
        change = float(t.get('change', 0))
        
        self._add_total_row(totals_frame, "Subtotal", format_currency(subtotal))
        if discount > 0:
            self._add_total_row(totals_frame, "Diskon", f"-{format_currency(discount)}")
        self._add_total_row(totals_frame, "TOTAL", format_currency(total), bold=True)
        self._add_total_row(totals_frame, "Bayar", format_currency(payment))
        self._add_total_row(totals_frame, "Kembali", format_currency(change))
        
        # Separator
        self._add_separator(frame)
        
        # Footer
        tk.Label(
            frame,
            text=self.store_config.get('footer', 'Terima kasih!'),
            font=FONTS['receipt'],
            fg=COLORS['text_light'],
            bg=COLORS['white']
        ).pack(pady=15)
    
    def _add_separator(self, parent, char="-"):
        """Add separator line"""
        sep = tk.Label(
            parent,
            text=char * 45,
            font=FONTS['receipt'],
            fg=COLORS['text_light'],
            bg=COLORS['white']
        )
        sep.pack(pady=5)
    
    def _add_info_row(self, parent, label, value):
        """Add info row"""
        row = tk.Frame(parent, bg=COLORS['white'])
        row.pack(fill='x')
        
        tk.Label(
            row,
            text=f"{label}:",
            font=FONTS['receipt'],
            bg=COLORS['white'],
            width=10,
            anchor='w'
        ).pack(side='left')
        
        tk.Label(
            row,
            text=value,
            font=FONTS['receipt'],
            bg=COLORS['white'],
            anchor='e'
        ).pack(side='right')
    
    def _add_item_row(self, parent, item):
        """Add item row"""
        # Item name
        tk.Label(
            parent,
            text=item['name'],
            font=FONTS['receipt'],
            bg=COLORS['white'],
            anchor='w'
        ).pack(fill='x')
        
        # Qty x price = subtotal
        detail = tk.Frame(parent, bg=COLORS['white'])
        detail.pack(fill='x', pady=(0, 5))
        
        tk.Label(
            detail,
            text=f"  {item['qty']} x {format_currency(item['price'])}",
            font=FONTS['receipt'],
            fg=COLORS['text_light'],
            bg=COLORS['white']
        ).pack(side='left')
        
        tk.Label(
            detail,
            text=format_currency(item['subtotal']),
            font=FONTS['receipt'],
            bg=COLORS['white']
        ).pack(side='right')
    
    def _add_total_row(self, parent, label, value, bold=False):
        """Add total row"""
        row = tk.Frame(parent, bg=COLORS['white'])
        row.pack(fill='x', pady=2)
        
        font = FONTS['receipt_bold'] if bold else FONTS['receipt']
        
        tk.Label(
            row,
            text=label,
            font=font,
            bg=COLORS['white'],
            anchor='w'
        ).pack(side='left')
        
        tk.Label(
            row,
            text=value,
            font=font,
            bg=COLORS['white'],
            anchor='e'
        ).pack(side='right')
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        btn_frame = tk.Frame(parent, bg=COLORS['background'])
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=15)
        
        # Print button
        print_btn = tk.Button(
            btn_frame,
            text="🖨️ Cetak ke Printer",
            font=FONTS['body_bold'],
            fg=COLORS['white'],
            bg=COLORS['primary'],
            relief='flat',
            cursor='hand2',
            command=self._print_to_printer
        )
        print_btn.pack(fill='x', ipady=10, pady=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            btn_frame,
            text="Tutup",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['white'],
            relief='flat',
            cursor='hand2',
            command=self.destroy
        )
        close_btn.pack(fill='x', ipady=8)
    
    def _generate_receipt_text(self):
        """Generate plain text receipt for 48mm thermal printer with ESC/POS formatting"""
        import textwrap
        
        t = self.transaction
        width = 32  # Characters width for 48mm thermal printer
        
        lines = []
        
        # ESC/POS Commands
        ESC = "\x1b"
        GS = "\x1d"
        INIT = ESC + "@"           # Initialize printer
        BOLD_ON = ESC + "E\x01"    # Bold on
        BOLD_OFF = ESC + "E\x00"   # Bold off
        DOUBLE_ON = GS + "!\x11"   # Double width+height
        DOUBLE_OFF = GS + "!\x00"  # Normal size
        CENTER_ON = ESC + "a\x01"  # Center align
        LEFT_ON = ESC + "a\x00"    # Left align
        
        # Helper: format number with thousand separator (Indonesian style: 1.000)
        def fmt_num(n):
            return "{:,.0f}".format(float(n)).replace(",", ".")
        
        # Helper: center text with wrapping
        def center(text):
            text = str(text)
            wrapped = textwrap.wrap(text, width)
            return "\n".join(line.center(width) for line in wrapped)
        
        def line(char="-"):
            return char * width
        
        def left_right(left, right):
            # If combining them fits
            if len(left) + len(right) + 1 <= width:
                space = width - len(left) - len(right)
                return f"{left}{' ' * space}{right}"
            
            # If left is too long, wrap it
            wrapped = textwrap.wrap(left, width)
            # If the last line of wrapped text + right fits
            if len(wrapped[-1]) + len(right) + 1 <= width:
                result = wrapped[:-1]
                last_line = wrapped[-1]
                space = width - len(last_line) - len(right)
                result.append(f"{last_line}{' ' * space}{right}")
                return "\n".join(result)
            else:
                # Print wrapped text then right aligned on next line
                result = wrapped
                result.append(right.rjust(width))
                return "\n".join(result)
        
        # Initialize printer
        lines.append(INIT)
        
        # Header - Bold and Double size, centered
        # Double width = half characters per line (16)
        header_name = self.store_config.get('name', 'TOKO').upper()
        
        # Custom wrapping for header (max 16 chars due to double width)
        wrapped_header = textwrap.wrap(header_name, 16)
        centered_header = "\n".join(line.center(16) for line in wrapped_header)
        
        # ESC ! n = Master Print Mode Select
        # n = 0x38 (56) = Emphasized (8) + Double Height (16) + Double Width (32)
        HEADER_STYLE = ESC + "!\x38"
        NORMAL_STYLE = ESC + "!\x00"
        
        lines.append(CENTER_ON + HEADER_STYLE)
        lines.append(centered_header)
        lines.append(NORMAL_STYLE)
        
        # Address and phone - normal, centered
        addr = self.store_config.get('address', '')
        if addr:
            lines.append(center(addr))
        phone = self.store_config.get('phone', '')
        if phone:
            lines.append(center(phone))
        lines.append(LEFT_ON)
        lines.append(line("="))
        
        # Transaction info
        lines.append(left_right("No:", t['id'][-12:]))
        lines.append(left_right("Tgl:", format_date(t['date'])))
        lines.append(left_right("Jam:", t['time']))
        lines.append(line("-"))
        
        # Items header
        lines.append(BOLD_ON)
        lines.append(left_right("Item", "Harga"))
        lines.append(BOLD_OFF)
        lines.append(line("-"))
        
        # Items
        items = t.get('items_list', [])
        if not items and 'items' in t:
            try:
                items = json.loads(t['items'])
            except:
                items = []
        
        for item in items:
            name = item['name']
            lines.append(name)
            
            qty_price = f" {item['qty']} x {fmt_num(item['price'])}"
            subtotal_str = fmt_num(item['subtotal'])
            
            # Indent qty_price slightly to visually separate from name
            lines.append(left_right(qty_price, subtotal_str))
        
        lines.append(line("-"))
        
        # Totals
        subtotal = float(t.get('subtotal', 0))
        discount = float(t.get('discount', 0))
        total = float(t.get('total', 0))
        payment = float(t.get('payment', 0))
        change = float(t.get('change', 0))
        
        lines.append(left_right("Subtotal", fmt_num(subtotal)))
        if discount > 0:
            lines.append(left_right("Diskon", f"-{fmt_num(discount)}"))
        
        # Total in bold
        lines.append(BOLD_ON)
        lines.append(left_right("TOTAL", fmt_num(total)))
        lines.append(BOLD_OFF)
        
        lines.append(left_right("Bayar", fmt_num(payment)))
        lines.append(left_right("Kembali", fmt_num(change)))
        lines.append(line("="))
        
        # Footer - centered
        lines.append(CENTER_ON)
        footer = self.store_config.get('footer', 'Terima kasih!')
        lines.append(center(footer))
        lines.append(LEFT_ON)
        # Feed lines for manual tear-off if cutter command fails/not present
        lines.append("\n\n")
        
        return "\n".join(lines)
    
    def _ask_print_confirmation(self):
        """Ask user if they want to print the receipt"""
        default_printer = self.store_config.get('default_printer', '')
        
        if default_printer:
            # If default printer is set, ask for confirmation
            result = messagebox.askyesno(
                "Cetak Struk",
                f"Cetak struk ke printer '{default_printer}'?",
                parent=self
            )
            if result:
                self._print_to_printer_direct(default_printer)
        else:
            # No default printer, ask if user wants to print
            result = messagebox.askyesno(
                "Cetak Struk",
                "Cetak struk sekarang?\n\n(Atur printer default di menu Pengaturan untuk otomatis cetak)",
                parent=self
            )
            if result:
                self._print_to_printer()
    
    def _print_to_printer_direct(self, printer_name):
        """Print receipt directly to thermal printer"""
        try:
            receipt_text = self._generate_receipt_text()
            
            # Add ESC/POS command for paper cut (works on most thermal printers)
            # ESC d n = print and feed n lines
            # GS V m = cut paper (m=0 full cut, m=1 partial cut)
            cut_command = "\n\n\n\x1d\x56\x00"  # Feed 3 lines then full cut
            receipt_with_cut = receipt_text + cut_command
            
            # Try using win32print first
            printed = False
            try:
                import win32print
                import win32api
                
                # Open printer
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    # Start raw document
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                    try:
                        win32print.StartPagePrinter(hPrinter)
                        # Write raw data
                        win32print.WritePrinter(hPrinter, receipt_with_cut.encode('cp437', errors='replace'))
                        win32print.EndPagePrinter(hPrinter)
                        printed = True
                    finally:
                        win32print.EndDocPrinter(hPrinter)
                finally:
                    win32print.ClosePrinter(hPrinter)
                
                if printed:
                    messagebox.showinfo("Sukses", f"Struk berhasil dicetak ke {printer_name}!", parent=self)
                    return
                    
            except ImportError:
                # win32print not installed, try alternative method
                pass
            except Exception as e:
                print(f"win32print error: {e}")
            
            # Alternative: Use copy command to print to LPT or USB printer
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
                f.write(receipt_with_cut.encode('cp437', errors='replace'))
                temp_file = f.name
            
            try:
                import subprocess
                # Try copy to printer share name
                # Format: copy /b filename \\computername\printername
                result = subprocess.run(
                    ['cmd', '/c', f'copy /b "{temp_file}" "{printer_name}"'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 or 'copied' in result.stdout.lower():
                    messagebox.showinfo("Sukses", f"Struk berhasil dicetak!", parent=self)
                else:
                    # Fallback to print dialog
                    os.startfile(temp_file, "print")
                    messagebox.showinfo("Info", "Silakan pilih printer dan klik Print", parent=self)
                    
            except Exception as e:
                os.startfile(temp_file, "print")
                messagebox.showinfo("Info", "Silakan pilih printer dan klik Print", parent=self)
            
            # Clean up
            self.after(10000, lambda: self._cleanup_temp(temp_file))
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencetak: {e}", parent=self)
    
    def _print_to_printer(self):
        """Print receipt using Windows print dialog"""
        try:
            receipt_text = self._generate_receipt_text()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(receipt_text)
                temp_file = f.name
            
            # Open Windows print dialog
            try:
                os.startfile(temp_file, "print")
                messagebox.showinfo("Info", "Dialog cetak dibuka. Pilih printer dan klik Print.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka dialog cetak: {e}", parent=self)
            
            # Clean up temp file after a delay
            self.after(10000, lambda: self._cleanup_temp(temp_file))
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencetak: {e}", parent=self)
    
    def _cleanup_temp(self, filepath):
        """Clean up temporary file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass


def show_receipt(parent, transaction):
    """Show receipt dialog"""
    Receipt(parent, transaction)


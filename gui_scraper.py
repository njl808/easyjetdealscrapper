#!/usr/bin/env python3
"""
GUI for EasyJet Holiday Deal Scraper
User-friendly interface for configuring and running the scraper
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import pandas as pd
from datetime import datetime
import queue
import sys

from easyjet_scraper import EasyJetScraper
from config import DEFAULT_CONFIG, AIRPORT_CODES

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyJet Holiday Deal Scraper")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        
        # Variables
        self.scraper_thread = None
        self.is_running = False
        
        self.setup_ui()
        self.load_defaults()
        
        # Start log queue checker
        self.check_log_queue()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="EasyJet Holiday Deal Scraper", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Airport Selection
        ttk.Label(main_frame, text="Departure Airports:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.airport_frame = ttk.Frame(main_frame)
        self.airport_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.airport_vars = {}
        self.setup_airport_checkboxes()
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="Search Configuration", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        # Duration settings
        ttk.Label(config_frame, text="Min Duration (days):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.min_duration_var = tk.StringVar(value="7")
        ttk.Entry(config_frame, textvariable=self.min_duration_var, width=10).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(config_frame, text="Max Duration (days):").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.max_duration_var = tk.StringVar(value="14")
        ttk.Entry(config_frame, textvariable=self.max_duration_var, width=10).grid(row=0, column=3, sticky=tk.W)
        
        # Price settings
        ttk.Label(config_frame, text="Min Price (£):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.min_price_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.min_price_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(config_frame, text="Max Price (£):").grid(row=1, column=2, sticky=tk.W, padx=(20, 10), pady=(10, 0))
        self.max_price_var = tk.StringVar(value="2000")
        ttk.Entry(config_frame, textvariable=self.max_price_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # Advanced settings
        ttk.Label(config_frame, text="Max Deals per Search:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.max_deals_var = tk.StringVar(value="50")
        ttk.Entry(config_frame, textvariable=self.max_deals_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(config_frame, text="Months Ahead:").grid(row=2, column=2, sticky=tk.W, padx=(20, 10), pady=(10, 0))
        self.months_ahead_var = tk.StringVar(value="6")
        ttk.Entry(config_frame, textvariable=self.months_ahead_var, width=10).grid(row=2, column=3, sticky=tk.W, pady=(10, 0))
        
        # Sort by price checkbox
        self.sort_price_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Sort by lowest price first", 
                       variable=self.sort_price_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Output settings
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_file_var = tk.StringVar(value="easyjet_deals.csv")
        ttk.Entry(output_frame, textvariable=self.output_file_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).grid(row=0, column=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 15))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Open Results", command=self.open_results).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=6, column=0, columnspan=3, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 15))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_airport_checkboxes(self):
        """Setup airport selection checkboxes"""
        # Create checkboxes in a grid layout
        airports = list(AIRPORT_CODES.keys())
        cols = 3
        
        for i, airport in enumerate(airports):
            row = i // cols
            col = i % cols
            
            var = tk.BooleanVar()
            if airport == "Bristol":  # Default selection
                var.set(True)
            
            self.airport_vars[airport] = var
            
            cb = ttk.Checkbutton(self.airport_frame, text=f"{airport} ({AIRPORT_CODES[airport]})", 
                               variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=(0, 20), pady=2)
    
    def load_defaults(self):
        """Load default configuration"""
        self.log_message("GUI initialized with default settings")
        
    def browse_output_file(self):
        """Browse for output file location"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save results as..."
        )
        if filename:
            self.output_file_var.set(filename)
    
    def get_selected_airports(self):
        """Get list of selected airports"""
        selected = []
        for airport, var in self.airport_vars.items():
            if var.get():
                selected.append(airport)
        return selected
    
    def validate_inputs(self):
        """Validate user inputs"""
        try:
            # Check airports
            airports = self.get_selected_airports()
            if not airports:
                raise ValueError("Please select at least one departure airport")
            
            # Check numeric inputs
            min_duration = int(self.min_duration_var.get())
            max_duration = int(self.max_duration_var.get())
            min_price = int(self.min_price_var.get())
            max_price = int(self.max_price_var.get())
            max_deals = int(self.max_deals_var.get())
            months_ahead = int(self.months_ahead_var.get())
            
            # Validate ranges
            if min_duration >= max_duration:
                raise ValueError("Maximum duration must be greater than minimum duration")
            
            if min_price >= max_price:
                raise ValueError("Maximum price must be greater than minimum price")
            
            if max_deals < 1 or max_deals > 200:
                raise ValueError("Max deals must be between 1 and 200")
            
            if months_ahead < 1 or months_ahead > 12:
                raise ValueError("Months ahead must be between 1 and 12")
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False
    
    def create_config(self):
        """Create configuration from GUI inputs"""
        config = DEFAULT_CONFIG.copy()
        config.update({
            'departure_airports': self.get_selected_airports(),
            'min_duration': int(self.min_duration_var.get()),
            'max_duration': int(self.max_duration_var.get()),
            'min_price': int(self.min_price_var.get()),
            'price_threshold': int(self.max_price_var.get()),
            'max_deals_per_search': int(self.max_deals_var.get()),
            'search_months_ahead': int(self.months_ahead_var.get()),
            'sort_by_price': self.sort_price_var.get(),
            'output_file': self.output_file_var.get()
        })
        return config
    
    def start_scraping(self):
        """Start the scraping process"""
        if not self.validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("Already Running", "Scraper is already running!")
            return
        
        # Update UI state
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Starting scraper...")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Create config
        config = self.create_config()
        
        # Log configuration
        self.log_message("=== Starting EasyJet Deal Scraper ===")
        self.log_message(f"Airports: {', '.join(config['departure_airports'])}")
        self.log_message(f"Duration: {config['min_duration']}-{config['max_duration']} days")
        self.log_message(f"Price range: £{config['min_price']}-£{config['price_threshold']}")
        self.log_message(f"Max deals: {config['max_deals_per_search']}")
        self.log_message(f"Sort by price: {config['sort_by_price']}")
        self.log_message(f"Output: {config['output_file']}")
        self.log_message("")
        
        # Start scraper in separate thread
        self.scraper_thread = threading.Thread(target=self.run_scraper, args=(config,))
        self.scraper_thread.daemon = True
        self.scraper_thread.start()
    
    def run_scraper(self, config):
        """Run the scraper in a separate thread"""
        try:
            # Create custom scraper with GUI logging
            scraper = EasyJetScraper(config)
            
            # Override logger to send messages to GUI
            original_info = scraper.logger.info
            original_error = scraper.logger.error
            original_warning = scraper.logger.warning
            
            def gui_info(msg):
                self.log_queue.put(('INFO', msg))
                original_info(msg)
            
            def gui_error(msg):
                self.log_queue.put(('ERROR', msg))
                original_error(msg)
                
            def gui_warning(msg):
                self.log_queue.put(('WARNING', msg))
                original_warning(msg)
            
            scraper.logger.info = gui_info
            scraper.logger.error = gui_error
            scraper.logger.warning = gui_warning
            
            # Run scraper
            scraper.run()
            
            self.log_queue.put(('SUCCESS', f"Scraping completed! Results saved to: {config['output_file']}"))
            
        except Exception as e:
            self.log_queue.put(('ERROR', f"Scraping failed: {str(e)}"))
        
        finally:
            self.log_queue.put(('FINISHED', ''))
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.progress_bar.stop()
        self.progress_var.set("Stopping...")
        self.log_message("Stop requested by user")
        
        # Reset UI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set("Stopped")
    
    def check_log_queue(self):
        """Check for log messages from scraper thread"""
        try:
            while True:
                level, message = self.log_queue.get_nowait()
                
                if level == 'FINISHED':
                    self.is_running = False
                    self.progress_bar.stop()
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.progress_var.set("Completed")
                elif level == 'SUCCESS':
                    self.log_message(message, 'success')
                    self.progress_var.set("Completed successfully!")
                elif level == 'ERROR':
                    self.log_message(f"ERROR: {message}", 'error')
                elif level == 'WARNING':
                    self.log_message(f"WARNING: {message}", 'warning')
                else:
                    self.log_message(message)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_log_queue)
    
    def log_message(self, message, level='info'):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        
        # Color coding
        if level == 'error':
            start_line = self.log_text.index(tk.END + "-2l")
            end_line = self.log_text.index(tk.END + "-1l")
            self.log_text.tag_add("error", start_line, end_line)
            self.log_text.tag_config("error", foreground="red")
        elif level == 'success':
            start_line = self.log_text.index(tk.END + "-2l")
            end_line = self.log_text.index(tk.END + "-1l")
            self.log_text.tag_add("success", start_line, end_line)
            self.log_text.tag_config("success", foreground="green")
        elif level == 'warning':
            start_line = self.log_text.index(tk.END + "-2l")
            end_line = self.log_text.index(tk.END + "-1l")
            self.log_text.tag_add("warning", start_line, end_line)
            self.log_text.tag_config("warning", foreground="orange")
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def open_results(self):
        """Open the results CSV file"""
        output_file = self.output_file_var.get()
        
        if not os.path.exists(output_file):
            messagebox.showwarning("File Not Found", f"Results file not found: {output_file}")
            return
        
        try:
            # Try to open with default application
            if sys.platform.startswith('darwin'):  # macOS
                os.system(f'open "{output_file}"')
            elif sys.platform.startswith('win'):  # Windows
                os.system(f'start "" "{output_file}"')
            else:  # Linux
                os.system(f'xdg-open "{output_file}"')
                
            self.log_message(f"Opened results file: {output_file}")
            
        except Exception as e:
            # Fallback: show file info
            try:
                df = pd.read_csv(output_file)
                info = f"Results file: {output_file}\n"
                info += f"Total deals: {len(df)}\n"
                info += f"Price range: £{df['total_price'].str.replace('£', '').str.replace(',', '').astype(float).min():.0f} - £{df['total_price'].str.replace('£', '').str.replace(',', '').astype(float).max():.0f}\n"
                info += f"Destinations: {', '.join(df['destination'].unique()[:5])}"
                if len(df['destination'].unique()) > 5:
                    info += f" and {len(df['destination'].unique()) - 5} more"
                
                messagebox.showinfo("Results Summary", info)
                
            except Exception as e2:
                messagebox.showerror("Error", f"Could not open results file: {str(e2)}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = ScraperGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()

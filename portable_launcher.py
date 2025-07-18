#!/usr/bin/env python3
"""
Portable Launcher for EasyJet Deal Scraper
This script can be converted to .exe and run without installation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import webbrowser
from pathlib import Path

class PortableLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyJet Deal Scraper - Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the launcher interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🛫 EasyJet Deal Scraper", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """Find the lowest price EasyJet holiday deals!
        
✈️ Search from Bristol and other UK airports
💰 Filter by price range (lowest prices first)
📊 Export results to CSV
🖥️ Choose your preferred interface"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, 
                              font=('Arial', 10), justify=tk.CENTER)
        desc_label.pack(pady=(0, 30))
        
        # Launch options frame
        options_frame = ttk.LabelFrame(main_frame, text="Choose Interface", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Desktop GUI button
        desktop_btn = ttk.Button(options_frame, text="🖥️ Desktop GUI (Recommended)", 
                                command=self.launch_desktop_gui, width=30)
        desktop_btn.pack(pady=5)
        
        ttk.Label(options_frame, text="Full-featured desktop interface with all options", 
                 font=('Arial', 9), foreground='gray').pack()
        
        # Web GUI button
        web_btn = ttk.Button(options_frame, text="🌐 Web Interface", 
                            command=self.launch_web_gui, width=30)
        web_btn.pack(pady=(15, 5))
        
        ttk.Label(options_frame, text="Modern web interface - opens in your browser", 
                 font=('Arial', 9), foreground='gray').pack()
        
        # Command line button
        cmd_btn = ttk.Button(options_frame, text="⌨️ Command Line", 
                            command=self.show_command_help, width=30)
        cmd_btn.pack(pady=(15, 5))
        
        ttk.Label(options_frame, text="For advanced users - direct command line access", 
                 font=('Arial', 9), foreground='gray').pack()
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready to launch", 
                                     font=('Arial', 9))
        self.status_label.pack()
        
        # Help and info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(info_frame, text="📖 Help", command=self.show_help).pack(side=tk.LEFT)
        ttk.Button(info_frame, text="ℹ️ About", command=self.show_about).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(info_frame, text="🌐 GitHub", command=self.open_github).pack(side=tk.RIGHT)
        
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            'gui_scraper.py',
            'web_gui.py', 
            'easyjet_scraper.py',
            'config.py'
        ]
        
        missing = []
        for file in required_files:
            if not os.path.exists(file):
                missing.append(file)
        
        if missing:
            messagebox.showerror("Missing Files", 
                               f"Required files not found:\n{', '.join(missing)}\n\n"
                               "Please ensure all files are in the same directory.")
            return False
        return True
    
    def launch_desktop_gui(self):
        """Launch the desktop GUI"""
        if not self.check_dependencies():
            return
            
        self.status_label.config(text="Launching desktop GUI...")
        self.root.update()
        
        try:
            # Try to launch the GUI
            subprocess.Popen([sys.executable, 'gui_scraper.py'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            self.status_label.config(text="Desktop GUI launched successfully!")
            
            # Ask if user wants to close launcher
            if messagebox.askyesno("GUI Launched", 
                                 "Desktop GUI has been launched!\n\nClose this launcher?"):
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch desktop GUI:\n{str(e)}")
            self.status_label.config(text="Failed to launch desktop GUI")
    
    def launch_web_gui(self):
        """Launch the web GUI"""
        if not self.check_dependencies():
            return
            
        self.status_label.config(text="Starting web server...")
        self.root.update()
        
        try:
            # Start web server in background
            def start_web_server():
                subprocess.run([sys.executable, 'web_gui.py'])
            
            thread = threading.Thread(target=start_web_server, daemon=True)
            thread.start()
            
            # Give server time to start
            self.root.after(3000, self.open_web_browser)
            self.status_label.config(text="Web server starting... Browser will open shortly")
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to start web server:\n{str(e)}")
            self.status_label.config(text="Failed to start web server")
    
    def open_web_browser(self):
        """Open web browser to the application"""
        try:
            webbrowser.open('http://localhost:8000')
            self.status_label.config(text="Web interface opened in browser (http://localhost:8000)")
            
            if messagebox.askyesno("Web Interface", 
                                 "Web interface opened in your browser!\n\n"
                                 "Keep this launcher open to maintain the web server?"):
                self.status_label.config(text="Web server running - keep this window open")
            else:
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Browser Error", f"Failed to open browser:\n{str(e)}")
    
    def show_command_help(self):
        """Show command line help"""
        help_text = """Command Line Usage:

Basic usage:
python run_scraper.py --airports "Bristol"

Advanced options:
python run_scraper.py --airports "Bristol" "Manchester" \\
    --min-duration 7 --max-duration 14 \\
    --min-price 300 --max-price 1000 \\
    --output my_deals.csv

List available airports:
python run_scraper.py --list-airports

Examples:
# Find cheapest deals from Bristol
python run_scraper.py --airports "Bristol" --max-price 600

# Search multiple airports with price range
python run_scraper.py --airports "Bristol" "Birmingham" \\
    --min-price 400 --max-price 1200
"""
        
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Command Line Help")
        help_window.geometry("600x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
    
    def show_help(self):
        """Show general help"""
        help_text = """EasyJet Deal Scraper Help

🎯 Purpose:
Find the lowest price EasyJet holiday deals from UK airports

✈️ Features:
• Search from Bristol, Manchester, Birmingham and other UK airports
• Filter by price range (£100-£2000+)
• Sort results by lowest price first
• Export results to CSV format
• Multiple interface options

🖥️ Desktop GUI:
Full-featured interface with all options and real-time progress

🌐 Web Interface:
Modern browser-based interface with interactive tables

⌨️ Command Line:
Direct command line access for advanced users

💡 Tips:
• Install Google Chrome for live web scraping
• Results are automatically sorted by lowest price
• CSV files can be opened in Excel or Google Sheets
• Demo data is shown if web scraping fails

🔧 Troubleshooting:
• Ensure all files are in the same directory
• Install Google Chrome browser
• Check internet connection for live scraping
"""
        
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """EasyJet Deal Scraper v1.0

🛫 Find the lowest price EasyJet holiday deals

Created with:
• Python & tkinter (Desktop GUI)
• Flask & Bootstrap (Web Interface)  
• Selenium (Web Scraping)
• Pandas (Data Processing)

Features:
✅ Price-focused search (lowest first)
✅ Multiple UK departure airports
✅ Advanced filtering options
✅ Professional CSV export
✅ Real-time progress tracking
✅ Multiple interface options

License: GPL-3.0 (Open Source)
GitHub: github.com/njl808/easyjetdealscrapper

Happy deal hunting! ✈️🏖️"""
        
        messagebox.showinfo("About", about_text)
    
    def open_github(self):
        """Open GitHub repository"""
        webbrowser.open('https://github.com/njl808/easyjetdealscrapper')

def main():
    """Main function"""
    root = tk.Tk()
    app = PortableLauncher(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()

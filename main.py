import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Messagebox
import awesometkinter as atk
import sqlite3
import os
import requests
import threading
import openpyxl
import re
import csv
import json
from tkhtmlview import HTMLLabel

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrape & Validate Emails")
        self.root.geometry("750x430")
        style = Style(theme='morph')
        try:
            self.root.iconbitmap('main.ico')
        except Exception as e:
            pass

        style.configure('.', font=('Helvetica', 11))
        self.root.resizable(False, False)

        # Top-Left: Multiline input field
        top_left_frame = tk.Frame(root)
        top_left_frame.grid(row=0, column=0, pady=10, padx=10, sticky=tk.NSEW)

        self.label_input = tk.Label(top_left_frame, text="Enter emails or websites:", font=('Helvetica', 11))
        self.label_input.grid(row=0, column=0, pady=10, padx=10, sticky=tk.W)
        

        self.text_input = tk.Text(top_left_frame, height=5, width=93)
        self.text_input.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W + tk.E)

        # Bottom-Left: Treeview
        bottom_left_frame = tk.Frame(root)
        bottom_left_frame.grid(row=1, column=0, pady=10, padx=10, sticky=tk.NSEW)

        self.tree_profile = ttk.Treeview(bottom_left_frame, columns=("ID", "Website", "Email", "Valid"), show="headings")
        self.tree_profile.heading("ID", text="ID")
        self.tree_profile.heading("Website", text="Website")
        self.tree_profile.heading("Email", text="Email")
        self.tree_profile.heading("Valid", text="Valid")

        # Set the width of the columns
        for col in ("ID", "Website", "Email", "Valid"):
            self.tree_profile.column(col, width=60, anchor=tk.CENTER)

        y_scrollbar = ttk.Scrollbar(bottom_left_frame, orient='vertical', command=self.tree_profile.yview)
        y_scrollbar.pack(side='right', fill='y')
        self.tree_profile.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(bottom_left_frame, orient='horizontal', command=self.tree_profile.xview)
        x_scrollbar.pack(side='bottom', fill='x')
        self.tree_profile.configure(xscroll=x_scrollbar.set)

        self.tree_profile.pack(pady=10, fill='both', expand=True)

        # Right side: Buttons in a frame
        right_frame = tk.Frame(root)
        right_frame.grid(row=0, column=1, rowspan=2, pady=10, padx=10, sticky=tk.NSEW)

        self.btn_open_file = atk.Button3d(right_frame, text="Open File", command=self.open_file_action)
        self.btn_open_file.grid(row=0, column=0, pady=5, padx=5, sticky=tk.EW)

        self.btn_scrape = atk.Button3d(right_frame, text="Scrape", command=self.scrape_action)
        self.btn_scrape.grid(row=1, column=0, pady=5, padx=5, sticky=tk.EW)

        self.btn_validate = atk.Button3d(right_frame, text="Validate", command=self.validate_action)
        self.btn_validate.grid(row=2, column=0, pady=5, padx=5, sticky=tk.EW)


        self.btn_save = atk.Button3d(right_frame, text="Save All", command=self.save_action)
        self.btn_save.grid(row=3, column=0, pady=5, padx=5, sticky=tk.EW)

        self.btn_save = atk.Button3d(right_frame, text="Save only Valid", command=self.save_valid_action)
        self.btn_save.grid(row=4, column=0, pady=5, padx=5, sticky=tk.EW)

        self.btn_clean = atk.Button3d(right_frame, text="Clean Table", command=self.clean_action, bg='red')
        self.btn_clean.grid(row=5, column=0, pady=5, padx=5, sticky=tk.EW)

        self.progress = ttk.Progressbar(right_frame, orient="horizontal", length=30, mode="determinate")
        self.progress.grid(row=6, column=0, pady=5, padx=5, sticky=tk.EW)

        # Configure column weights
        root.columnconfigure(0, weight=2)
        root.columnconfigure(1, weight=1)

        # Configure row weights
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        # Configure top-left frame row weights
        top_left_frame.rowconfigure(0, weight=1)
        top_left_frame.rowconfigure(1, weight=3)

        # Configure bottom-left frame row weights
        bottom_left_frame.rowconfigure(0, weight=1)

        # Configure right frame row weights
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.rowconfigure(2, weight=1)
        right_frame.rowconfigure(3, weight=1)
        right_frame.rowconfigure(4, weight=1)
        right_frame.rowconfigure(5, weight=1)
        right_frame.rowconfigure(6, weight=1)


        self.database_reload()
        self.donut()

    def donut(self):
        message = """
    <div style="font-family: Arial, sans-serif; color: #333;">
        <p>We are a team of developers who are passionate about creating useful and informative apps. We believe that everyone should have access to quality information, regardless of their financial situation. That's why we make our apps free to download and use.</p>
        <p>Maintaining apps costs money, and we rely on generous users like you to keep things running and develop new features.</p>
        <p>If you find our apps helpful, consider donating!</p>
        <h4>How to Donate:</h4>
        <p>Every bit counts! Consider donating through one of these options:</p>

            <ol>
<li><strong>Bitcoin Cash (BCH):</strong><br />qzwkzt9vdf8sr5masj4fr97rw7w3w08evu25vjs97u</li>
<li><strong>Litecoin (LTC):</strong><br />ltc1qhsjgqv6auz53nlkm8u7h5jpjlq393ut4zh8tp2</li>
<li><strong>Polygon (MATIC):</strong><br />0x4E5D08f745e0c81877f6FA102E7a2a7de8E1A276</li>
<li><strong>Dogecoin (DOGE):</strong><br />DDxiWQwEF6T5kLUXhb5JyjHJ9pdp997QR6</li>
</ol>
<p></p>

        <p>Thank you for your support!</p>
        <h4>What You Get in Return</h4>
        <p>As a thank you for your donation, if you donate $10 or more, we will also give you the opportunity to request a new feature for one of our apps. Simply send us an email at <a href="mailto:jouasa86@gmail.com" style="color: #007BFF;">jouasa86@gmail.com</a> with your request, the donation amount and date, and we will do our best to implement it.</p>
        <p>Thank you again for your support!</p>
    </div>
"""

        dialog = tk.Toplevel()
        dialog.grab_set()
        try:
            dialog.iconbitmap('main.ico')
        except Exception as e:
            pass
        dialog.attributes('-topmost', True)
        dialog.title("Donate for Donut")

        html_label = HTMLLabel(dialog, html=message)
        html_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)
        

    def open_file_action(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                if content:
                    # Если поле ввода не пустое, добавляем новую строку перед добавлением содержимого файла
                    if self.text_input.get("1.0", "end-1c"):
                        content = '\n' + content
                    self.text_input.insert(tk.END, content)

    def database_reload(self):
        file_path = 'emails.db'
        try:
            os.remove(file_path)
        except Exception as e:
            pass

        conn = sqlite3.connect(file_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT,
                email TEXT,
                valid INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

    def scrape_action(self):
        threading.Thread(target=self._scrape_action_thread, daemon=True).start()

    def _scrape_action_thread(self):

        input_text = self.text_input.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Error", "No data to scrape.")
            return

        websites = input_text.splitlines()
        found_emails = set()
        self.progress["maximum"] = len(websites)
        self.progress["value"] = 0


        for website in websites:
            self.root.after(0, lambda: self.progress.step(1))
            try:
                # Check if the website starts with http:// or https://
                if not website.startswith("http://") and not website.startswith("https://"):
                    # If not, add http:// by default
                    website = "http://" + website

                response = requests.get(website)
                if response.status_code == 200:
                    # Use regex to find email addresses in the webpage content
                    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
                    emails = re.findall(pattern, response.text)

                    for email in emails:
                        found_emails.add((website, email))
                else:
                    print(f"Error requesting {website}: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")

        try:
            conn = sqlite3.connect('emails.db')
            c = conn.cursor()

            # Insert found email addresses into the database if not exist
            for website, email in found_emails:
                c.execute('SELECT * FROM emails WHERE website=? AND email=?', (website, email))
                result = c.fetchone()
                if not result:
                    c.execute('INSERT INTO emails (website, email) VALUES (?, ?)', (website, email))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()
            self.load_data()
            self.root.after(0, lambda: self.progress.stop())

            messagebox.showinfo("Scrape Result", f"Found emails scraped and saved to the database!")
        except Exception as e:
            print(f"Error saving emails to the database: {e}")

    def clean_action(self):
        self.database_reload()
        self.load_data()

    def validate_action(self):
        threading.Thread(target=self._validate_action_thread, daemon=True).start()

    def _validate_action_thread(self):
        input_text = self.text_input.get("1.0", tk.END).strip()
        input_lines = input_text.splitlines()

        found_emails = set()
        for line in input_lines:
            match = re.match(r'\S+@\S+', line)
            if match:
                email_parts = line.split('@')
                local_email = email_parts[0] if len(email_parts) == 2 else email
                domain = email_parts[-1] if len(email_parts) == 2 else ""
                website = f"http://{domain}"
                found_emails.add((website, line))
        if found_emails:
            conn = sqlite3.connect('emails.db')
            c = conn.cursor()

            for website, email in found_emails:
                c.execute('SELECT * FROM emails WHERE website=? AND email=?', (website, email))
                result = c.fetchone()
                if not result:
                    c.execute('INSERT INTO emails (website, email) VALUES (?, ?)', (website, email))
            conn.commit()
            conn.close()
        

        # Connect to the database
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()

        c.execute('SELECT email FROM emails')
        emails = [row[0] for row in c.fetchall()]
        # Close the database connection
        conn.close()

        # If still no emails, show a message and return
        if not emails:
            messagebox.showinfo("Validation Result", "No valid emails found for validation.")
            return
        self.progress["maximum"] = len(emails)
        self.progress["value"] = 0

        try:

            # Validate the found email addresses through the API
            for email in emails:
                self.root.after(0, lambda: self.progress.step(1))
                validation_url = f"https://api.mailcheck.ai/email/{email}"
                response = requests.get(validation_url)

                if response.status_code == 200:
                    validation_data = response.json()

                    disposable = validation_data.get("disposable", False)

                    if not disposable:
                        # Update the valid field in the database to 1
                        conn = sqlite3.connect('emails.db')
                        c = conn.cursor()
                        c.execute('UPDATE emails SET valid = 1 WHERE email = ?', (email,))
                        conn.commit()
                        conn.close()
                        self.load_data()
                    else:
                        self.load_data()
            
            self.root.after(0, lambda: self.progress.stop())
            messagebox.showinfo("Validation Result", "Email validation completed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_action(self):
        # Define the file types for the save dialog
        file_types = [
            ('CSV files', '*.csv'),
            ('Text files', '*.txt'),
            ('Excel files', '*.xlsx'),
            ('JSON files', '*.json')
        ]

        # Open the save file dialog
        filepath = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=file_types)

        if not filepath:
            return  # The user cancelled the save operation

        # Choose the saving method based on the file extension
        if filepath.endswith('.csv'):
            self.save_as_csv(filepath)
        elif filepath.endswith('.txt'):
            self.save_as_txt(filepath)
        elif filepath.endswith('.xlsx'):
            self.save_as_xlsx(filepath)
        elif filepath.endswith('.json'):
            self.save_as_json(filepath)

    def fetch_data_from_db(self):
        """Fetches data from the database and returns it as a list of dictionaries."""
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute('SELECT id, website, email, valid FROM emails')
        data = [{'id': row[0], 'website': row[1], 'email': row[2], 'valid': row[3]} for row in c.fetchall()]
        conn.close()
        return data

    def save_as_csv(self, filepath):
        data = self.fetch_data_from_db()
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'website', 'email', 'valid'])
            writer.writeheader()
            writer.writerows(data)

    def save_as_txt(self, filepath):
        data = self.fetch_data_from_db()
        with open(filepath, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item['id']}, {item['website']}, {item['email']}, {item['valid']}\n")

    def save_as_xlsx(self, filepath):
        data = self.fetch_data_from_db()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['ID', 'Website', 'Email', 'Valid'])
        for item in data:
            ws.append([item['id'], item['website'], item['email'], item['valid']])
        wb.save(filepath)

    def save_as_json(self, filepath):
        data = self.fetch_data_from_db()
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def save_valid_action(self):
        file_types = [
            ('CSV files', '*.csv'),
            ('Text files', '*.txt'),
            ('Excel files', '*.xlsx'),
            ('JSON files', '*.json')
        ]

        filepath = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=file_types)

        if not filepath:
            return  
        
        if filepath.endswith('.csv'):
            self.save_valid_as_csv(filepath)
        elif filepath.endswith('.txt'):
            self.save_valid_as_txt(filepath)
        elif filepath.endswith('.xlsx'):
            self.save_valid_as_xlsx(filepath)
        elif filepath.endswith('.json'):
            self.save_valid_as_json(filepath)

    def fetch_valid_data_from_db(self):
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute('SELECT id, website, email, valid FROM emails WHERE valid = 1')
        data = [{'id': row[0], 'website': row[1], 'email': row[2], 'valid': row[3]} for row in c.fetchall()]
        conn.close()
        return data

    def save_valid_as_csv(self, filepath):
        data = self.fetch_valid_data_from_db()
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'website', 'email', 'valid'])
            writer.writeheader()
            writer.writerows(data)

    def save_valid_as_txt(self, filepath):
        data = self.fetch_valid_data_from_db()
        with open(filepath, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item['id']}, {item['website']}, {item['email']}, {item['valid']}\n")

    def save_valid_as_xlsx(self, filepath):
        data = self.fetch_valid_data_from_db()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['ID', 'Website', 'Email', 'Valid'])
        for item in data:
            ws.append([item['id'], item['website'], item['email'], item['valid']])
        wb.save(filepath)

    def save_valid_as_json(self, filepath):
        data = self.fetch_valid_data_from_db()
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_data(self):
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute('SELECT * FROM emails')
        data = c.fetchall()
        conn.close()

        # Clear the table before updating
        for row in self.tree_profile.get_children():
            self.tree_profile.delete(row)

        # Update the table with data from the database
        for row in data:
            self.tree_profile.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

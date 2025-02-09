import re
import requests
import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_js_files(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        js_files = [urljoin(url, script['src']) for script in soup.find_all('script') if script.get('src')]
        return js_files
    except requests.RequestException:
        return []

def find_secrets(js_url):
    try:
        response = requests.get(js_url, timeout=5)
        content = response.text
        
        patterns = {
            'API Key': r'(?i)(?:apikey|api_key|access_token|secret)\s*[:=]\s*["\']([A-Za-z0-9_\-]+)["\']',
            'AWS Key': r'AKIA[0-9A-Z]{16}',
            'JWT Token': r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
        }
        
        found_secrets = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                found_secrets[key] = matches
        
        return found_secrets
    except requests.RequestException:
        return {}

def take_screenshot(url, output_path):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    driver.save_screenshot(output_path)
    driver.quit()

def save_results(data, filename):
    with open(filename, "w") as file:
        file.write(data)

def scan_url():
    url = entry_url.get()
    js_files = get_js_files(url)
    
    results = "Discovered JS Files:\n" + "\n".join(js_files) + "\n\n"
    
    for js_file in js_files:
        secrets = find_secrets(js_file)
        if secrets:
            results += f"Secrets found in {js_file}:\n"
            for key, values in secrets.items():
                for value in values:
                    results += f"    {key}: {value}\n"
    
    output_area.insert(tk.END, results + "\n")
    save_results(results, "scan_results.txt")
    take_screenshot(url, "screenshot.png")

def create_gui():
    global entry_url, output_area
    
    root = tk.Tk()
    root.title("Bug Bounty Tool")
    
    tk.Label(root, text="Enter Target URL:").pack()
    entry_url = tk.Entry(root, width=50)
    entry_url.pack()
    
    tk.Button(root, text="Scan", command=scan_url).pack()
    
    output_area = scrolledtext.ScrolledText(root, width=80, height=20)
    output_area.pack()
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()

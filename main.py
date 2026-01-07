"""
Yahoo Finance Options Straddle Table Scraper
Extracts the Calls & Puts table from Yahoo Finance options straddle view and saves to CSV.

This script uses pydoll for browser automation and BeautifulSoup for HTML parsing.
It captures the page source after the table is rendered and extracts the data.

Usage:
    python main.py AAPL
    python main.py TSLA
    python main.py https://ca.finance.yahoo.com/quote/AAPL/options/?straddle=true
    python main.py saved_page.html  # Parse from saved HTML file
"""

import asyncio
import csv
import sys
import re
import base64
import json
from bs4 import BeautifulSoup
from pydoll.browser import Chrome


def parse_straddle_table(html_content, output_file="yahoo_straddle.csv"):
    """
    Parse the straddle table from HTML content and save to CSV.
    Returns True on success, False on failure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the straddle table section
    section = soup.find('section', {'data-testid': 'options-straddle-table'})
    if not section:
        print("❌ Error: Could not find 'options-straddle-table' section.")
        return False
    
    table = section.find('table')
    if not table:
        print("❌ Error: No table found in section.")
        return False
    
    print("Table found! Extracting data...")
    
    # Extract headers
    thead = table.find('thead')
    headers = []
    if thead:
        ths = thead.find_all('th')
        raw_headers = [th.get_text(strip=True) for th in ths]
        # Format headers: first 5 are Calls, then Strike, then 5 Puts
        for i, h in enumerate(raw_headers):
            if i < 5:
                headers.append(f"Call {h}")
            elif i == 5:
                headers.append("Strike")
            else:
                headers.append(f"Put {h}")
    
    # Extract rows
    tbody = table.find('tbody')
    rows_data = []
    if tbody:
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                rows_data.append(row_data)
    
    if not rows_data:
        print("❌ Error: No data rows found in table.")
        return False
    
    print(f"Extracted {len(rows_data)} rows with {len(headers)} columns.")
    
    # Save to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows_data)
        print(f"✅ Successfully saved to '{output_file}'")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


async def scrape_yahoo_straddle(url, output_file):
    """
    Scrape Yahoo Finance options straddle table using pydoll.
    Uses network event interception to wait for page load completion.
    """
    page_loaded = asyncio.Event()
    html_source = {"content": None}
    
    async def on_load_event(event):
        """Called when page finishes loading."""
        page_loaded.set()
    
    print("--- Starting Browser ---")
    print(f"Target URL: {url}")
    
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Enable page events to detect load completion
        await tab.enable_page_events()
        await tab.on("Page.loadEventFired", on_load_event)
        
        print("Navigating to page...")
        try:
            # Don't await go_to directly - it can hang
            asyncio.create_task(tab.go_to(url))
            
            # Wait for page load event with timeout
            try:
                await asyncio.wait_for(page_loaded.wait(), timeout=30)
                print("Page load event received.")
            except asyncio.TimeoutError:
                print("Timeout waiting for page load, proceeding anyway...")
            
        except Exception as e:
            print(f"Navigation error: {e}")

        # Extra wait for dynamic content
        print("Waiting for dynamic content...")
        await asyncio.sleep(5)
        
        # Get page source
        print("Getting page source...")
        try:
            source = await tab.page_source
            if callable(source):
                source = await source()
            html_source["content"] = source
        except Exception as e:
            print(f"Error getting page source: {e}")
            return False
        
        if not html_source["content"]:
            print("❌ Error: Could not get page source.")
            return False
            
        print(f"Page source: {len(html_source['content'])} characters")
    
    # Parse and save
    return parse_straddle_table(html_source["content"], output_file)


def parse_ticker_from_url(url):
    """Extract ticker symbol from Yahoo Finance URL."""
    match = re.search(r'/quote/([A-Z0-9.-]+)/', url, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def main():
    print("=" * 50)
    print("Yahoo Finance Straddle Table Scraper")
    print("=" * 50)
    print()
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Example: https://ca.finance.yahoo.com/quote/AAPL/options/?straddle=true")
        print()
        url = input("Enter Yahoo Finance Options URL: ").strip()
    
    if not url:
        print("❌ Error: No URL provided.")
        sys.exit(1)
    
    if not url.startswith("http"):
        print("❌ Error: Please enter a valid URL starting with http:// or https://")
        sys.exit(1)
    
    # Extract ticker from URL for filename
    ticker = parse_ticker_from_url(url) or "data"
    output_filename = f"yahoo_{ticker}_straddle.csv"
    
    print()
    print(f"URL: {url}")
    print(f"Output: {output_filename}")
    print()
    
    # Run the async scraper
    success = asyncio.run(scrape_yahoo_straddle(url, output_filename))
    
    if not success:
        print()
        print("⚠️ Scraping failed. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

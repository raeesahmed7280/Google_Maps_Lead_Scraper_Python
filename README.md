Google Maps Scraper (Selenium)

A reliable Python-based Google Maps business scraper built with Selenium. It extracts detailed business information — including contact details and social media links — and exports everything to Excel. The project is tested, easy to use, and ideal for showcasing technical skills or generating business leads.

Features

Extracts the following:

Title

Rating

Reviews count

Phone

Email (best-effort from business website)

Address

Website

Facebook

Instagram

LinkedIn

Twitter

Google Maps Link

Exports results to Excel (.xlsx)

Automatically saves files as filename_01.xlsx, filename_02.xlsx, etc., to prevent overwriting

Supports headless mode (runs Chrome invisibly)

Uses webdriver-manager to auto-install ChromeDriver

Handles multiple Google Maps layouts with fallback logic

Requirements

Python 3.8 or higher

Google Chrome installed

Install dependencies:

pip install -r requirements.txt

How to Use Option 1: Double-click to run

Double-click Google_Maps_Lead_Scraper.py. You’ll be prompted to enter:

Search query (e.g. dentist in Lahore)

Output file name

Max results

Page load delay (in seconds)

Option 2: Run from Command Line python Google_Maps_Lead_Scraper.py --query "plumbers in Chicago" --output plumbers.xlsx --max-results 300 --slow 3

Optional flags:

--headless → Run without showing the browser window

--max-results → Limit total listings

--slow → Increase wait time for slow connections

Example Output

The exported Excel file includes the following columns:

Title | Rating | Reviews | Phone | Email | Address | Website | Facebook | Instagram | LinkedIn | Twitter | GoogleMapsLink

Example output file: examples/dentist_in_saskatoon.xlsx

Folder Structure

Google_Maps_Lead_Scraper.py — main scraper script

requirements.txt — dependencies

examples/dentist_in_saskatoon.xlsx — example output

docs/screenshots.png — replace with your own screenshots

LICENSE — MIT License

README.md — documentation

Notes

Results may vary due to Google’s dynamic listings.

Google frequently changes its page layout, which may require small updates.

Email extraction depends on whether a business lists an email publicly.

webdriver-manager automatically downloads the correct ChromeDriver version.

Use responsibly and follow Google’s Terms of Service.

License

MIT License — see LICENSE for details.

Author

Created by Raees Ahmed Fazal

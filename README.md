# Google Maps Scraper (Selenium)

A reliable **Python-based Google Maps business scraper** built with **Selenium**.  
It extracts detailed business information — including contact details and social media links — and exports everything to **Excel**.  
Perfect for showcasing automation skills or generating real business leads.

---

## 🚀 Features

- Extracts:
  - **Title**
  - **Rating**
  - **Reviews count**
  - **Phone**
  - **Email** (best-effort from the business website)
  - **Address**
  - **Website**
  - **Facebook, Instagram, LinkedIn, Twitter**
  - **Google Maps Link**
- Exports results to **Excel (.xlsx)**
- Prevents overwriting: saves as `filename_01.xlsx`, `filename_02.xlsx`, etc.
- Supports **headless mode** (runs Chrome invisibly)
- Uses **webdriver-manager** to auto-install ChromeDriver
- Handles multiple Google Maps layouts with smart fallbacks

---

## 🧩 Requirements

- Python **3.8+**
- **Google Chrome** installed

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🖥️ How to Use
Option 1: Double-click (easy mode)

Run Google_Maps_Lead_Scraper.py directly.

You’ll be asked for:

Search query (e.g. dentist in Lahore)

Output file name

Max results

Page load delay (in seconds)

Option 2: Command Line (advanced)

python Google_Maps_Lead_Scraper.py --query "plumbers in Chicago" --output plumbers.xlsx --max-results 300 --slow 3

Optional flags:

--headless → Run Chrome without opening a window

--max-results → Limit total listings

--slow → Increase wait time for slow networks

📊 Example Output

Excel columns:
Title | Rating | Reviews | Phone | Email | Address | Website | Facebook | Instagram | LinkedIn | Twitter | GoogleMapsLink

Example file:
examples/dentist_in_saskatoon.xlsx

📁 Folder Structure
Google_Maps_Lead_Scraper.py   → main scraper script
requirements.txt               → dependencies
examples/dentist_in_saskatoon.xlsx → sample output
docs/                          → screenshots folder
LICENSE                        → MIT License
README.md                      → documentation

⚠️ Notes

Google’s layout changes frequently; small updates may be needed.

Some listings may lack emails or full info.

webdriver-manager automatically installs the correct ChromeDriver.

Use responsibly and comply with Google’s Terms of Service.

🧾 License

Licensed under the MIT License.
See the LICENSE
 file for details.

👨‍💻 Author

Created by Raees Ahmed Fazal
Email: raeesahmed7280@gmail.com


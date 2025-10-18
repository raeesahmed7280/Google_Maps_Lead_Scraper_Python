# Google Maps Lead Scraper (Selenium)

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

`Option 1:` Double-click (easy mode)

Run Google_Maps_Lead_Scraper.py directly.

You’ll be asked for:

Search query (e.g. dentist in Lahore)

Output file name

Max results

Page load delay (in seconds)

`Option 2:` Command Line (advanced)

```
python Google_Maps_Lead_Scraper.py --query "dentist in saskatoon sk canada" --output dentists.xlsx --max-results 200 --slow 3
```

Optional flags:

- `--headless` to run Chrome without opening a window.
- `--max-results` to limit total listings processed.
- `--slow` to increase base wait time if pages load slowly on your network.

📊 Example Output

Excel columns:
Title | Rating | Reviews | Phone | Email | Address | Website | Facebook | Instagram | LinkedIn | Twitter | GoogleMapsLink

Example file:
examples/dentist_in_saskatoon.xlsx

📁 Folder Structure
- `Google_Maps_Lead_Scraper.py`   → main scraper script
- `requirements.txt`               → dependencies
- `examples/dentist_in_saskatoon.xlsx` → sample output
- `docs/`                          → screenshots folder
- `LICENSE`                        → MIT License
- `README.md`                      → documentation

⚠️Notes, Limitations, and Tips

- Result counts can vary. Google Maps does not guarantee a fixed number of listings for a query; duplicates or hidden listings can reduce totals.
- Google frequently changes page structure. This scraper uses multiple fallbacks, but updates may be required over time.
- Email extraction is best-effort by scanning the listed website; not all businesses list an email.
- If Chrome or ChromeDriver versions change, webdriver-manager will fetch a compatible driver automatically.
- If you see intermittent timeouts, increase `--slow` (e.g., 3 → 5 or 7).
- Use responsibly and comply with the terms of the services you access.

🧾 License

Licensed under the MIT License.
See the LICENSE
 file for details.

👨‍💻 Author

Created by Raees Ahmed Fazal
Email: raeesahmed7280@gmail.com


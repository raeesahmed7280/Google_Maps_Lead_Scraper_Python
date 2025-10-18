#!/usr/bin/env python3
"""
Google_Maps_Lead_Scraper.py
Single-file Google Maps scraper (best-effort).

Usage example:
Google_Maps_Lead_Scraper.py --query "dentist in saskatoon sk canada" --output dentists.xlsx --max-results 200 --slow 3

Requirements:
pip install selenium pandas requests openpyxl webdriver-manager
"""
import os
import re
import time
import argparse
import random
from urllib.parse import urlparse

import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# webdriver_manager will auto-download the right ChromeDriver for your installed Chrome
from webdriver_manager.chrome import ChromeDriverManager


def safe_text(driver, by, selector, default=""):
    try:
        el = driver.find_element(by, selector)
        txt = el.text.strip()
        return txt
    except Exception:
        return default


def find_results_panel(driver):
    # Try a few likely selectors for the left results container
    xpaths = [
        "//div[@id='pane']",
        "//div[@role='region']",
        "//div[@role='feed']",
        "//div[contains(@aria-label,'Results') or contains(@aria-label,'results')]",
    ]
    for xp in xpaths:
        try:
            el = driver.find_element(By.XPATH, xp)
            return el
        except Exception:
            continue
    return None


def scroll_results(driver, pause_time=2, max_scrolls=100):
    """Scrolls the left sidebar to load more results (up to max_scrolls)."""
    try:
        results_panel = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        scrolls = 0
        seen_links = set()

        while scrolls < max_scrolls:
            # Scroll down
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
            time.sleep(pause_time)

            # Collect current links
            elems = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            for e in elems:
                href = e.get_attribute("href")
                if href and "/maps/place/" in href:
                    seen_links.add(href.split("?")[0])

            print(f"[INFO] Scroll {scrolls+1}/{max_scrolls} → collected {len(seen_links)} links")

            scrolls += 1

            # Stop early if results stop growing
            if scrolls > 5 and len(seen_links) < 5:
                print("[INFO] No more new results.")
                break

        return list(seen_links)

    except Exception as e:
        print(f"[WARN] Could not scroll results: {e}")
        return []


def scroll_results_until_done(driver, pause=2, max_iterations=100):
    """Continuously scrolls until no new results appear or max_iterations reached."""
    try:
        results_panel = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
    except Exception:
        rp = find_results_panel(driver)
        if rp is None:
            print("[WARN] Cannot locate results panel to scroll.")
            return []
        results_panel = rp

    seen = set()
    last_count = 0
    same_rounds = 0
    max_same_rounds = 3

    for i in range(max_iterations):
        try:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
        except Exception:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except Exception:
                pass

        time.sleep(pause + random.uniform(0.3, 1.0))

        elems = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
        for e in elems:
            href = e.get_attribute("href")
            if href and "/maps/place/" in href:
                seen.add(href.split("?")[0])

        print(f"[INFO] Scroll {i+1}/{max_iterations} → {len(seen)} links")

        # Stop if reached desired number
        if len(seen) >= args_max_results:
            print(f"[INFO] Reached target of {args_max_results} links. Stopping scroll.")
            break

        # Stop if results stop growing
        if len(seen) == last_count:
            same_rounds += 1
        else:
            same_rounds = 0

        last_count = len(seen)

        if same_rounds >= max_same_rounds:
            print("[INFO] No new results after several rounds. Stopping scroll.")
            break

    return list(seen)

def collect_listing_links(driver, max_results=500):
    anchors = driver.find_elements(By.XPATH, "//a[contains(@href,'/place/')]")
    seen = set()
    out = []
    for a in anchors:
        href = a.get_attribute("href")
        if not href:
            continue
        href_clean = href.split('?')[0]
        if href_clean in seen:
            continue
        seen.add(href_clean)
        out.append(href_clean)
        if len(out) >= max_results:
            break
    return out


def get_website_details(url):
    if not url:
        return "", "", "", "", ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, timeout=10, headers=headers)
        txt = r.text

        # Emails
        found_emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", txt)
        cleaned_emails = []
        for e in found_emails:
            e = e.lower()
            if any(bad in e for bad in [
                "sentry", "wixpress", "cloudflare", "example.com", "no-reply",
                "noreply", "support@", "admin@", "test@", "donotreply",
                "github", "wordpress", "amazonaws", "shopifyemail",
                "smart.journey.prober", "business.google.com", "google.com"
            ]):

                continue
            if re.search(r'\.(jpg|jpeg|png|gif|webp|svg)', e):
                continue
            if re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', e):
                cleaned_emails.append(e)
        email = ",".join(sorted(set(cleaned_emails)))

        # Social links
        fb = re.search(r'https?://(www\.)?facebook\.com/[^\s"\']+', txt)
        insta = re.search(r'https?://(www\.)?instagram\.com/[^\s"\']+', txt)
        linkedin = re.search(r'https?://(www\.)?linkedin\.com/[^\s"\']+', txt)
        twitter = re.search(r'https?://(www\.)?(x|twitter)\.com/[^\s"\']+', txt)

        return email, fb.group(0) if fb else "", insta.group(0) if insta else "", linkedin.group(0) if linkedin else "", twitter.group(0) if twitter else ""

    except Exception:
        return "", "", "", "", ""




def _clean_address(addr: str) -> str:
    if not addr:
        return ""
    # remove weird glyphs/icons and normalize whitespace
    addr = re.sub(r'[\u2000-\uFFFF]+', ' ', addr)  # drop unusual unicode icons
    addr = addr.replace("\n", " ").strip()
    addr = re.sub(r'\s+', ' ', addr)
    return addr


def parse_maps_listing(driver, link, slow=3, max_retries=3):
    """
    Load a single maps place page and extract fields. This function is intentionally
    robust with multiple fallbacks and retries because Google Maps DOM varies.
    """
    row = {
        "Title": "",
        "Rating": "",
        "Reviews": "",
        "Phone": "",
        "Email": "",
        "Address": "",
        "Website": "",
        "Facebook": "",
        "Instagram": "",
        "LinkedIn": "",
        "Twitter": "",
        "GoogleMapsLink": link,
    }


    # Load page with a few retries
    for attempt in range(max_retries):
        try:
            driver.get(link)
            # wait for title to appear if possible
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            # small jitter to give Maps time to render dynamic parts
            time.sleep(slow + random.uniform(0.3, 1.0))
            break
        except Exception as e:
            print(f"[WARN] Loading attempt {attempt+1} failed for {link}: {e}")
            time.sleep(1 + attempt * 2)
            # try again; on last attempt continue with whatever we have
    try:
        html = driver.page_source or ""
    except Exception:
        html = ""

    # ---------- Title ----------
    title = ""
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except Exception:
        # fallback to HTML regex
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
        if m:
            title = re.sub(r'\s+', ' ', m.group(1)).strip()
    row["Title"] = title
    if not title:
        return None

    # ---------- Rating & Reviews ----------
    rating = ""
    reviews = ""

    # 1) Try JSON-LD aggregateRating block
    try:
        m = re.search(r'"aggregateRating"\s*:\s*\{([^}]+)\}', html)
        if m:
            block = m.group(1)
            m_r = re.search(r'"ratingValue"\s*:\s*([0-9.]+)', block)
            m_c = re.search(r'"reviewCount"\s*:\s*([0-9,]+)', block)
            if m_r:
                rating = m_r.group(1)
            if m_c:
                reviews = m_c.group(1).replace(",", "")
    except Exception:
        pass

    # 2) Try other known JSON keys
    if not rating:
        m = re.search(r'"rating"\s*:\s*([0-9.]+)', html)
        if m:
            rating = m.group(1)
    if not reviews:
        for key in ['"reviewCount"', '"userRatingCount"', '"user_ratings_total"', '"review_count"',
                    '"ratingCount"', '"totalReviews"', '"rating_count"']:
            try:
                m = re.search(key + r'\s*:\s*([0-9,]+)', html)
                if m:
                    reviews = m.group(1).replace(",", "")
                    break
            except Exception:
                continue

    # 3) HTML textual fallback: '123 reviews' pattern
    if not reviews:
        m = re.search(r'([0-9][0-9,]*)\s+reviews?', html, re.I)
        if m:
            reviews = m.group(1).replace(",", "")

    # 4) Selenium-level fallback: scan a limited number of candidate elements for aria-label/text
    if not reviews:
        try:
            # scan buttons/spans/divs near top, but limit to first ~250 elements for speed
            candidates = driver.find_elements(By.XPATH, "//button|//span|//div")
            scanned = 0
            for el in candidates:
                scanned += 1
                txt = (el.get_attribute("aria-label") or el.text or "").strip()
                if not txt:
                    if scanned > 250:
                        break
                    continue
                m = re.search(r'\b([0-9][0-9,]*)\b\s+reviews?', txt, re.I)
                if m:
                    reviews = m.group(1).replace(",", "")
                    break
                if scanned > 250:
                    break
        except Exception:
            pass

    # rating fallback via aria-label/text scan if not found
    if not rating:
        try:
            candidates = driver.find_elements(By.XPATH, "//span|//div")
            scanned = 0
            for el in candidates:
                scanned += 1
                txt = (el.get_attribute("aria-label") or el.text or "").strip()
                if txt:
                    m = re.search(r'([0-9]\.[0-9])', txt)
                    if m:
                        rating = m.group(1)
                        break
                if scanned > 200:
                    break
        except Exception:
            pass

    row["Rating"] = rating
    row["Reviews"] = reviews

    # ---------- Address ----------
    address = ""
    try:
        address = safe_text(driver, By.XPATH, "//button[@data-item-id='address']//div")
        if not address:
            address = safe_text(driver, By.CLASS_NAME, "Io6YTe")
    except Exception:
        address = ""
    address = _clean_address(address)
    row["Address"] = address

# ---------- Phone ----------
    phone = ""
    try:
        # 1) tel: link
        tel_links = driver.find_elements(By.XPATH, "//a[starts-with(@href,'tel:')]")
        if tel_links:
            phone = tel_links[0].get_attribute("href").split(":", 1)[1]
        else:
            # 2) explicit button with data-item-id 'phone'
            try:
                b = driver.find_element(By.XPATH, "//button[@data-item-id='phone']")
                phone = (b.text or b.get_attribute("aria-label") or "").strip()
            except Exception:
                # 3) other buttons with aria-label mentioning Call/Phone (skip "Send to phone")
                candidates = driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Phone') or contains(@aria-label,'Call') or contains(.,'Call')]")
                for c in candidates:
                    txt = (c.get_attribute("aria-label") or c.text or "").strip()
                    if not txt:
                        continue
                    if "send to phone" in txt.lower():
                        continue
                    # discard non-numeric noisy labels
                    phone = txt
                    break
    except Exception:
        phone = ""
    row["Phone"] = phone

    # Skip entries without both title and phone
    if not row["Title"] and not phone:
        return None
    
    # ---------- Website ----------
    website = ""
    try:
        anchors = driver.find_elements(By.XPATH, "//a[contains(@href,'http')]")
        for a in anchors:
            href = a.get_attribute("href") or ""
            if not href:
                continue
            # ignore google internal links
            if "maps.google" in href or "google.com/maps" in href or "search?api=1" in href:
                continue
            # ignore image files or static assets
            if re.search(r'\.(png|jpg|jpeg|svg|gif|webp)(\?|$)', href, re.I):
                continue
            # ignore javascript pseudo links
            if href.startswith("http"):
                # Ignore useless Google business links
                if "business.google.com/create" in href or "google.com/local" in href or "add.place" in href:
                    continue
                website = href
                break

        # Skip irrelevant Google or support links
        if website and any(x in website for x in [
            "google.com",
            "support.google",
            "about/products",
            "policies.google",
            "contributionpolicy",
            "accounts.google",
            "maps.google"
        ]):
            website = ""

    except Exception:
        website = ""
    row["Website"] = website


    # ---------- Email + Social links ----------
    email = fb = insta = linkedin = twitter = ""
    if website:
        email, fb, insta, linkedin, twitter = get_website_details(website)

    row["Email"] = email
    row["Facebook"] = fb
    row["Instagram"] = insta
    row["LinkedIn"] = linkedin
    row["Twitter"] = twitter
    return row



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", "-q", required=True, help='e.g. "barbers near me" or "dentist in saskatoon sk canada"')
    parser.add_argument("--output", "-o", default="maps_results.xlsx", help="Excel (.xlsx) output filename")
    parser.add_argument("--max-results", "-m", type=int, default=500, help="Maximum places to collect")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--slow", type=float, default=3.0, help="Base wait (increase if pages load slowly)")
    args = parser.parse_args()
    
    global args_max_results
    args_max_results = args.max_results


    chrome_opts = Options()
    if args.headless:
        # new headless for modern Chrome
        try:
            chrome_opts.add_argument("--headless=new")
        except Exception:
            chrome_opts.add_argument("--headless")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_argument("--window-size=1200,900")

    # install chrome driver automatically
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.set_page_load_timeout(60)

    try:
        driver.get("https://www.google.com/maps")
        time.sleep(args.slow + 1)

        # perform search
        try:
            search_box = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            search_box.clear()
            search_box.send_keys(args.query)
            time.sleep(0.8)
            try:
                btn = driver.find_element(By.ID, "searchbox-searchbutton")
                btn.click()
            except Exception:
                search_box.send_keys("\n")
        except Exception:
            # fallback: navigate to maps search url
            driver.get(f"https://www.google.com/maps/search/{args.query.replace(' ', '+')}")
        time.sleep(args.slow + 2)

        # scroll results to load many entries (use return value)
        links = scroll_results_until_done(driver, pause=args.slow, max_iterations=100)
        if not links:
            # fallback to simpler collection if scroll failed
            links = collect_listing_links(driver, max_results=args.max_results)
        print(f"Found {len(links)} candidate links; will process up to {args.max_results} entries.")
        links = links[: args.max_results]

        results = []
        for i, link in enumerate(links, start=1):
            from urllib.parse import unquote
            name = unquote(link.split("/place/")[-1].split("/data=")[0].replace("+", " "))

            print(f"[{i}/{len(links)}] {name}")

            try:
                row = parse_maps_listing(driver, link, slow=args.slow)
                results.append(row)
            except Exception as e:
                print("Error processing:", e)
            # polite pause between place pages
            time.sleep(0.8 + random.uniform(0.2, 0.8))

        import os

        if results:
            df = pd.DataFrame(results)
            # Ensure filename ends with .xlsx
            base_name = args.output if args.output.lower().endswith(".xlsx") else args.output + ".xlsx"

            # If file exists, auto-increment name
            if os.path.exists(base_name):
                name, ext = os.path.splitext(base_name)
                counter = 1
                new_name = f"{name}_{counter:02d}{ext}"
                while os.path.exists(new_name):
                    counter += 1
                    new_name = f"{name}_{counter:02d}{ext}"
                base_name = new_name

            df.to_excel(base_name, index=False)
            print("Saved:", base_name)
        else:
            print("No results scraped.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":

    print("=== Google Maps Scraper ===")
    query = input("Enter your search query (e.g. 'dentist in saskatoon sk canada'): ").strip()
    if not query:
        print("No query entered. Exiting.")
        exit()

    output = input("Enter output file name (default: results.xlsx): ").strip()
    if not output:
        output = "results.xlsx"

    try:
        max_results = int(input("Max results to scrape (default 200): ").strip() or 200)
    except ValueError:
        max_results = 200

    try:
        slow = float(input("Page load delay seconds (default 3): ").strip() or 3)
    except ValueError:
        slow = 3

    # Build fake CLI args dynamically
    import sys
    sys.argv = [
        sys.argv[0],
        "--query", query,
        "--output", output,
        "--max-results", str(max_results),
        "--slow", str(slow)
    ]

    main()

    print("\n=== Done! Check your Excel file in the same folder. ===")
    input("Press Enter to exit...")


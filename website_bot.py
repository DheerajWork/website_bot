print("🚀 Script started")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re, json, time, tldextract

# ---------------- Utility functions ---------------- #

def clean(text):
    return re.sub(r'\s+', ' ', text).strip() if text else "N/A"

def extract_domain_name(url):
    ext = tldextract.extract(url)
    return ext.domain.capitalize() if ext.domain else "N/A"

def find_business_name(soup, url):
    meta_name = soup.find("meta", property="og:site_name")
    if meta_name and meta_name.get("content"):
        return clean(meta_name["content"])
    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
        name = meta_title["content"]
    elif soup.title and soup.title.text:
        name = soup.title.text
    else:
        name = extract_domain_name(url)
    name = re.sub(r'(?i)(welcome|home|about|services|contact|official site|private limited|pvt ltd|ltd)', '', name)
    name = re.sub(r'[\-|•|–|:|,].*', '', name)
    name = clean(name)
    return name if len(name) > 2 else extract_domain_name(url)

def find_email_phone(text):
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))
    phones = list(set(re.findall(r"\+?\d[\d\s\-]{8,}\d", text)))
    phone = next((p for p in phones if re.search(r"(\+91|[0-9]{10,13})", p)), phones[0] if phones else "N/A")
    return emails[0] if emails else "N/A", phone

def find_address_jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "address" in item:
                        addr = item["address"]
                        if isinstance(addr, dict):
                            return clean(", ".join(str(v) for v in addr.values() if v))
            elif isinstance(data, dict) and "address" in data:
                addr = data["address"]
                if isinstance(addr, dict):
                    return clean(", ".join(str(v) for v in addr.values() if v))
        except Exception:
            continue
    return None

def find_full_address(soup, text):
    addr = find_address_jsonld(soup)
    if addr:
        return addr
    keywords = ["address", "location", "office", "contact us", "head office"]
    blocks = []
    for tag in soup.find_all(text=re.compile("|".join(keywords), re.I)):
        block = clean(tag.parent.get_text(" ", strip=True))
        if any(k in block.lower() for k in ["india", "road", "street", "nagar", "sector", "floor", "tower", "city", "district"]):
            blocks.append(block)
    for tag in soup.find_all(["address", "footer", "p", "div"]):
        txt = clean(tag.get_text(" ", strip=True))
        if re.search(r"\d{6}|India|Road|Street|Nagar|Sector|Building", txt, re.I):
            blocks.append(txt)
    if blocks:
        return max(blocks, key=len)[:250]
    addr = re.search(r"([A-Za-z0-9\s,./#-]{15,200}(Road|Street|Nagar|Sector|India)[A-Za-z0-9\s,./#-]{0,150})", text, re.I)
    if addr:
        return clean(addr.group(0))
    return "N/A"

def detect_business_line(text):
    t = text.lower()
    if any(k in t for k in ["it", "software", "digital", "web", "seo"]): return "IT Company"
    if "construction" in t: return "Construction Company"
    if "hospital" in t or "clinic" in t: return "Healthcare"
    if "school" in t or "education" in t: return "Educational"
    if "marketing" in t: return "Marketing Agency"
    return "Business / Service Provider"

# ---------------- Scraping function ---------------- #

def scrape_site(url, headless=True):
    opt = Options()
    if headless:
        opt.add_argument("--headless")  # Run without GUI
    
    # ✅ Linux / Render friendly
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--log-level=3")
    
    # Use environment variable if Docker set it
    import os
    chrome_path = os.environ.get("CHROME_BIN", None)
    if chrome_path:
        opt.binary_location = chrome_path
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    business_name = find_business_name(soup, url)

    # About Us
    about_link = next((a['href'] for a in soup.find_all('a', href=True) if "about" in a['href'].lower()), "")
    about_text = ""
    if about_link:
        full_about_link = about_link if "http" in about_link else url.rstrip("/") + "/" + about_link.lstrip("/")
        driver.get(full_about_link); time.sleep(2)
        about_text = clean(BeautifulSoup(driver.page_source, "html.parser").get_text(" ")[:1000])
    else:
        about_text = clean(" ".join([p.get_text() for p in soup.find_all("p")[:5]]))

    # Contact
    contact_link = next((a['href'] for a in soup.find_all('a', href=True) if "contact" in a['href'].lower()), "")
    contact_text, contact_soup = "", soup
    if contact_link:
        full_contact_link = contact_link if "http" in contact_link else url.rstrip("/") + "/" + contact_link.lstrip("/")
        driver.get(full_contact_link); time.sleep(2)
        contact_html = driver.page_source
        contact_soup = BeautifulSoup(contact_html, "html.parser")
        contact_text = contact_soup.get_text(" ")
    else:
        contact_text = soup.get_text(" ")

    email, phone = find_email_phone(contact_text)
    address = find_full_address(contact_soup, contact_text)

    socials = {"Facebook": "N/A", "Instagram": "N/A", "LinkedIn": "N/A", "Twitter": "N/A"}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "facebook.com" in href: socials["Facebook"] = href
        elif "instagram.com" in href: socials["Instagram"] = href
        elif "linkedin.com" in href: socials["LinkedIn"] = href
        elif "twitter.com" in href or "x.com" in href: socials["Twitter"] = href

    services = [clean(s.get_text()) for s in soup.find_all(["h3", "h4", "li"]) if 5 < len(s.get_text()) < 80]
    main_services = ", ".join(list(dict.fromkeys(services[:10]))) if services else "N/A"
    biz_line = detect_business_line(about_text + main_services)
    driver.quit()

    data = {
        "Business Name": business_name,
        "Business Line": biz_line,
        "About Us": about_text[:400] + "...",
        "Main Products / Services": main_services,
        "Email": email,
        "Phone": phone,
        "Address": address,
        "Facebook": socials["Facebook"],
        "Instagram": socials["Instagram"],
        "LinkedIn": socials["LinkedIn"],
        "Twitter / X": socials["Twitter"],
    }
    return data

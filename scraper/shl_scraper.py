import requests
from bs4 import BeautifulSoup
import time, json
from urllib.parse import urljoin
from tqdm import tqdm

BASE = "https://www.shl.com"
CATALOG = "https://www.shl.com/solutions/products/product-catalog/"

def parse_product_page(url):
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""
    description_tag = soup.find("meta", {"name":"description"})
    description = description_tag.get("content","").strip() if description_tag else ""
    skills = []
    for h in soup.find_all(["h2","h3"]):
        if "skill" in h.get_text(strip=True).lower():
            nxt = h.find_next_sibling("ul")
            if nxt:
                skills = [li.get_text(strip=True) for li in nxt.find_all("li")]
    return {"name": title, "url": url, "description": description, "skills": skills, "category": "", "test_type": ""}

def crawl_catalog(start_url=CATALOG, max_products=None):
    r = requests.get(start_url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    product_links = set()
    for a in soup.select("a"):
        href = a.get("href")
        if not href:
            continue
        if ("/products/" in href or "/solutions/products/" in href) and "product-catalog" not in href:
            full = urljoin(BASE, href)
            product_links.add(full)
    products = []
    for link in tqdm(sorted(product_links)):
        try:
            data = parse_product_page(link)
            if "package" in data['name'].lower() or "job" in data['name'].lower():
                continue
            products.append(data)
            if max_products and len(products) >= max_products:
                break
            time.sleep(0.6)
        except Exception as e:
            print("error parsing", link, e)
    return products

if __name__ == "__main__":
    products = crawl_catalog()
    print("Scraped", len(products))
    with open("../data/shl_catalog.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print("Saved to data/shl_catalog.json")

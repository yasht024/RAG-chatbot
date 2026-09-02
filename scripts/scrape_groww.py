import json
import re
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def scrape_funds():
    root_dir = Path(__file__).parents[1]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    facts_path = root_dir / "data" / "catalog" / "scheme_facts.json"
    
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    with open(facts_path, "r", encoding="utf-8") as f:
        facts = json.load(f)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        page = await context.new_page()
        
        for scheme in schemes:
            sid = scheme["scheme_id"]
            url = scheme["groww_url"]
            print(f"Scraping {sid} -> {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # wait for a bit to let react render
                await page.wait_for_timeout(3000)
                
                text = await page.locator("body").inner_text()
                
                # We update the `facts[sid]` if we find matches
                if sid not in facts:
                    facts[sid] = {}
                    
                er_match = re.search(r"Expense ratio[^\d]*([\d.]+%)", text, re.IGNORECASE)
                if er_match:
                    facts[sid]["expense_ratio"] = er_match.group(1)
                    
                el_match = re.search(r"Exit load[\s\n]*([^\n]+)", text, re.IGNORECASE)
                if el_match:
                    # Clean up if it captures too much
                    load_text = el_match.group(1).strip()
                    if len(load_text) > 5 and len(load_text) < 100:
                        facts[sid]["exit_load"] = load_text
                        
                inc_match = re.search(r"Inception date[\s\n]*([\d]{1,2} [A-Za-z]+ [\d]{4})", text, re.IGNORECASE)
                if inc_match:
                    facts[sid]["inception_date"] = inc_match.group(1)
                    
                sip_match = re.search(r"Min SIP amount[\s\n]*[₹\s]*([\d,]+)", text, re.IGNORECASE)
                if sip_match:
                    facts[sid]["min_sip"] = f"₹ {sip_match.group(1)}"
                    
            except Exception as e:
                print(f"  Error scraping {sid}: {e}")
                
        await browser.close()
        
    # Write back
    with open(facts_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=4)
        
    print(f"Scraping completed. Updated {facts_path}.")

if __name__ == "__main__":
    asyncio.run(scrape_funds())

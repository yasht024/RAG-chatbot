import json
from pathlib import Path

# Extract from user's pasted text
new_urls = {
    "HDFC Mid Cap Fund": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "HDFC Flexi Cap Fund": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "HDFC Small Cap Fund": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "HDFC Large and Mid Cap Fund": "https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth",
    "HDFC Large Cap Fund": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "HDFC Multi Cap Fund": "https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth",
    "HDFC Focused Fund": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "HDFC Value Fund": "https://groww.in/mutual-funds/hdfc-value-fund-direct-plan-growth",
    "HDFC ELSS Tax Saver Fund": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "HDFC MNC Fund": "https://groww.in/mutual-funds/hdfc-mnc-fund-direct-growth",
    "HDFC Business Cycle Fund": "https://groww.in/mutual-funds/hdfc-business-cycle-fund-direct-growth",
    "HDFC Defence Fund": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "HDFC Consumption Fund": "https://groww.in/mutual-funds/hdfc-consumption-fund-direct-growth",
    "HDFC Transportation and Logistics Fund": "https://groww.in/mutual-funds/hdfc-transportation-and-logistics-fund-direct-growth",
    "HDFC Technology Fund": "https://groww.in/mutual-funds/hdfc-technology-fund-direct-growth",
    "HDFC Pharma and Healthcare Fund": "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
    "HDFC Manufacturing Fund": "https://groww.in/mutual-funds/hdfc-manufacturing-fund-direct-growth",
    "HDFC Infrastructure Fund": "https://groww.in/mutual-funds/hdfc-infrastructure-fund-direct-growth",
    "HDFC Innovation Fund": "https://groww.in/mutual-funds/hdfc-innovation-fund-direct-growth",
    "HDFC Children's Fund": "https://groww.in/mutual-funds/hdfc-children%27s-fund-direct-plan",
    "HDFC NIFTY 50 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
    "HDFC NIFTY Next 50 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-next-50-index-fund-direct-growth",
    "HDFC NIFTY 100 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-100-index-fund-direct-growth",
    "HDFC NIFTY 100 Equal Weight Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-100-equal-weight-index-fund-direct-growth",
    "HDFC NIFTY50 Equal Weight Index Fund": "https://groww.in/mutual-funds/hdfc-nifty50-equal-weight-index-fund-direct-growth",
    "HDFC NIFTY Midcap 150 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-midcap-150-index-fund-direct-growth",
    "HDFC Nifty Smallcap 250 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-smallcap-250-index-fund-direct-growth",
    "HDFC Nifty LargeMidcap 250 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-largemidcap-250-index-fund-direct-growth",
    "HDFC NIFTY200 Momentum 30 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty200-momentum-30-index-fund-direct-growth",
    "HDFC NIFTY100 Low Volatility 30 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty100-low-volatility-30-index-fund-direct-growth",
    "HDFC Nifty100 Quality 30 Index Fund": "https://groww.in/mutual-funds/hdfc-nifty100-quality-30-index-fund-direct-growth",
    "HDFC Nifty Top 20 Equal Weight Index Fund": "https://groww.in/mutual-funds/hdfc-nifty-top-20-equal-weight-index-fund-direct-growth",
    "HDFC Balanced Advantage Fund": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
    "HDFC Multi Asset Allocation Fund": "https://groww.in/mutual-funds/hdfc-multi-asset-allocation-fund-direct-growth",
    "HDFC Gold ETF Fund of Fund": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth"
}

def update_urls():
    root_dir = Path(__file__).parents[1]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    updated = 0
    for scheme in schemes:
        # Match by prefix since canonical_name has " - Direct Growth" or " - Direct Plan Growth"
        for fund_key, url in new_urls.items():
            if scheme["canonical_name"].startswith(fund_key):
                if scheme["groww_url"] != url:
                    print(f"Updating URL for {scheme['canonical_name']}")
                    print(f"  Old: {scheme['groww_url']}")
                    print(f"  New: {url}")
                    scheme["groww_url"] = url
                    updated += 1
                break
                
    with open(schemes_path, "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2)
        
    print(f"Updated {updated} URLs in schemes.json")

if __name__ == "__main__":
    update_urls()

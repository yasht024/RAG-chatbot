import json

aliases = {
  "hdfc_mid_cap": [
    "HDFC Mid Cap",
    "HDFC MidCap",
    "HDFC Mid Cap Fund",
    "HDFC Mid-Cap Opportunities Fund",
    "HDFC Mid Cap Direct Growth"
  ],
  "hdfc_flexi_cap": [
    "HDFC Flexi Cap",
    "HDFC Flexicap",
    "HDFC Equity Fund",
    "HDFC Flexi Cap Fund",
    "HDFC Flexi Cap Direct Growth"
  ],
  "hdfc_small_cap": [
    "HDFC Small Cap",
    "HDFC SmallCap",
    "HDFC Small Cap Fund",
    "HDFC Small Cap Direct Growth"
  ],
  "hdfc_large_and_mid_cap": [
    "HDFC Large and Mid Cap",
    "HDFC Large & Mid Cap",
    "HDFC Large & Mid Cap Fund",
    "HDFC Large and Mid Cap Direct Growth"
  ],
  "hdfc_large_cap": [
    "HDFC Large Cap",
    "HDFC Top 100",
    "HDFC Top 100 Fund",
    "HDFC Large Cap Fund",
    "HDFC Large Cap Direct Growth"
  ],
  "hdfc_multi_cap": [
    "HDFC Multi Cap",
    "HDFC Multicap",
    "HDFC Multi Cap Fund"
  ],
  "hdfc_focused": [
    "HDFC Focused",
    "HDFC Focused 30",
    "HDFC Focused Fund"
  ],
  "hdfc_value": [
    "HDFC Value",
    "HDFC Capital Builder",
    "HDFC Value Fund"
  ],
  "hdfc_elss_tax_saver": [
    "HDFC ELSS",
    "HDFC Tax Saver",
    "HDFC ELSS Tax Saver",
    "HDFC ELSS Tax Saver Fund"
  ],
  "hdfc_mnc": [
    "HDFC MNC",
    "HDFC MNC Fund"
  ],
  "hdfc_business_cycle": [
    "HDFC Business Cycle",
    "HDFC Business Cycle Fund"
  ],
  "hdfc_defence": [
    "HDFC Defence",
    "HDFC Defense",
    "HDFC Defence Fund"
  ],
  "hdfc_consumption": [
    "HDFC Consumption",
    "HDFC Consumption Fund"
  ],
  "hdfc_transportation_and_logistics": [
    "HDFC Transportation",
    "HDFC Logistics",
    "HDFC Transportation and Logistics Fund"
  ],
  "hdfc_technology": [
    "HDFC Tech",
    "HDFC Technology",
    "HDFC Technology Fund"
  ],
  "hdfc_pharma_and_healthcare": [
    "HDFC Pharma",
    "HDFC Healthcare",
    "HDFC Pharma and Healthcare Fund"
  ],
  "hdfc_manufacturing": [
    "HDFC Manufacturing",
    "HDFC Manufacturing Fund"
  ],
  "hdfc_infrastructure": [
    "HDFC Infra",
    "HDFC Infrastructure",
    "HDFC Infrastructure Fund"
  ],
  "hdfc_innovation": [
    "HDFC Innovation",
    "HDFC Innovation Fund"
  ],
  "hdfc_childrens": [
    "HDFC Childrens",
    "HDFC Children's Gift",
    "HDFC Children's Fund"
  ],
  "hdfc_nifty_50_index": [
    "HDFC NIFTY 50",
    "HDFC Nifty 50 Index",
    "HDFC NIFTY 50 Index Fund"
  ],
  "hdfc_nifty_next_50_index": [
    "HDFC NIFTY Next 50",
    "HDFC Nifty Next 50 Index Fund"
  ],
  "hdfc_nifty_100_index": [
    "HDFC NIFTY 100",
    "HDFC Nifty 100 Index Fund"
  ],
  "hdfc_nifty_100_equal_weight_index": [
    "HDFC Nifty 100 Equal Weight",
    "HDFC NIFTY 100 Equal Weight Index Fund"
  ],
  "hdfc_nifty50_equal_weight_index": [
    "HDFC Nifty 50 Equal Weight",
    "HDFC NIFTY50 Equal Weight Index Fund"
  ],
  "hdfc_nifty_midcap_150_index": [
    "HDFC Nifty Midcap 150",
    "HDFC NIFTY Midcap 150 Index Fund"
  ],
  "hdfc_nifty_smallcap_250_index": [
    "HDFC Nifty Smallcap 250",
    "HDFC Nifty Smallcap 250 Index Fund"
  ],
  "hdfc_nifty_largemidcap_250_index": [
    "HDFC Nifty LargeMidcap 250",
    "HDFC Nifty LargeMidcap 250 Index Fund"
  ],
  "hdfc_nifty200_momentum_30_index": [
    "HDFC Momentum 30",
    "HDFC NIFTY200 Momentum 30 Index Fund"
  ],
  "hdfc_nifty100_low_volatility_30_index": [
    "HDFC Low Volatility 30",
    "HDFC NIFTY100 Low Volatility 30 Index Fund"
  ],
  "hdfc_nifty100_quality_30_index": [
    "HDFC Quality 30",
    "HDFC Nifty100 Quality 30 Index Fund"
  ],
  "hdfc_nifty_top_20_equal_weight_index": [
    "HDFC Top 20 Equal Weight",
    "HDFC Nifty Top 20 Equal Weight Index Fund"
  ],
  "hdfc_balanced_advantage": [
    "HDFC BAF",
    "HDFC Balanced Advantage",
    "HDFC Balanced Advantage Fund",
    "HDFC Prudence"
  ],
  "hdfc_multi_asset_allocation": [
    "HDFC Multi Asset",
    "HDFC Multi Asset Allocation Fund"
  ],
  "hdfc_gold_etf_fof": [
    "HDFC Gold FOF",
    "HDFC Gold Fund",
    "HDFC Gold ETF Fund of Fund"
  ],
  "sbi_small_cap": [
    "SBI Small Cap",
    "SBI Small Cap Fund"
  ],
  "sbi_equity_hybrid": [
    "SBI Hybrid",
    "SBI Equity Hybrid",
    "SBI Equity Hybrid Fund",
    "SBI Magnum Balanced"
  ],
  "sbi_bluechip": [
    "SBI Bluechip",
    "SBI Bluechip Fund"
  ]
}

def resolve_scheme(query: str) -> str:
    q = query.lower()
    for scheme_id, alias_list in aliases.items():
        for alias in alias_list:
            if alias.lower() in q:
                return scheme_id
    return None

print(resolve_scheme("Who is the current fund manager?"))
print(resolve_scheme("What is the riskometer classification?"))

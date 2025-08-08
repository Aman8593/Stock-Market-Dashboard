import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

def parse_financial_table(soup, section_title):
    try:
        section = soup.find("h2", string=section_title)
        if not section:
            return []

        table = section.find_next("table")
        if not table:
            return []

        headers = [th.text.strip() for th in table.find_all("th")]
        rows = table.find_all("tr")[1:]

        result = []
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue
            label = cols[0].text.strip()
            values = [col.text.strip() for col in cols[1:]]
            row_dict = {headers[i + 1]: values[i] for i in range(len(values))}
            row_dict["label"] = label
            result.append(row_dict)

        return result

    except Exception as e:
        print(f"❌ Failed to parse section '{section_title}': {e}")
        return []



def extract_shareholding_from_screener(soup):
    try:
        pattern_section = soup.find("section", {"id": "shareholding"})
        if not pattern_section:
            return []

        table = pattern_section.find("table")
        rows = table.find_all("tr")[1:]  # Skip header row

        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                data.append({
                    "Category": cols[0].text.strip(),
                    "Holding": cols[1].text.strip()
                })

        return data
    except Exception as e:
        print(f"Shareholding scraping failed: {e}")
        return []

# def get_cashflow_from_screener(symbol):
#     try:
#         url = f"https://www.screener.in/company/{symbol}/cash-flow/"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")

#         section = soup.find("h2", string="Cash Flow Statement")
#         if not section:
#             return []

#         table = section.find_next("table")
#         if not table:
#             return []

#         headers = [th.text.strip() for th in table.find_all("th")]
#         rows = table.find_all("tr")[1:]

#         result = []
#         for row in rows:
#             cols = row.find_all("td")
#             if not cols:
#                 continue
#             label = cols[0].text.strip()
#             values = [col.text.strip() for col in cols[1:]]
#             row_dict = {headers[i + 1]: values[i] for i in range(len(values))}
#             row_dict["label"] = label
#             result.append(row_dict)

#         return result
#     except Exception as e:
#         print(f"Error fetching cash flow: {e}")
#         return []


def get_company_overview_data(symbol):
    """
    Extract company overview data including sector, market cap, PE, ROCE, ROE from screener.in
    """
    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Get all text content for pattern matching
        page_text = soup.get_text()
        
        # Extract data using multiple approaches
        sector = extract_sector_from_page(soup, page_text)
        market_cap = extract_market_cap_from_page(soup, page_text)
        pe_ratio = extract_pe_ratio(soup, page_text)
        roce = extract_roce(soup, page_text)
        roe = extract_roe(soup, page_text)
        
        return {
            "sector": sector,
            "market_cap": market_cap,
            "pe": pe_ratio,
            "roce": roce,
            "roe": roe
        }
        
    except Exception as e:
        print(f"Error fetching company overview data: {e}")
        return {
            "sector": "N/A",
            "market_cap": "N/A", 
            "pe": "N/A",
            "roce": "N/A",
            "roe": "N/A"
        }

def extract_sector_from_page(soup, page_text):
    """Extract sector information using multiple methods"""
    try:
        import re
        
        # Method 1: Look for business description or about section
        # This usually contains the actual business sector info
        about_section = soup.find("div", class_="company-about") or soup.find("div", class_="description")
        if about_section:
            about_text = about_section.get_text()
            # Look for sector/industry keywords in description
            sector_keywords = ['software', 'IT services', 'consulting', 'technology', 'banking', 'pharmaceutical', 'automobile', 'steel', 'oil', 'gas', 'telecom']
            for keyword in sector_keywords:
                if keyword.lower() in about_text.lower():
                    if 'software' in about_text.lower() or 'IT' in about_text or 'information technology' in about_text.lower():
                        return "IT Services & Consulting"
                    elif 'bank' in about_text.lower():
                        return "Banking"
                    elif 'pharma' in about_text.lower():
                        return "Pharmaceuticals"
        
        # Method 2: Look for sector in peer comparison or similar companies section
        peers_section = soup.find("section", id="peers") or soup.find("div", class_="peers")
        if peers_section:
            sector_element = peers_section.find("h3") or peers_section.find("h2")
            if sector_element:
                sector_text = sector_element.get_text().strip()
                if sector_text and not any(word in sector_text.lower() for word in ['peer', 'comparison', 'companies', 'nifty']):
                    return sector_text
        
        # Method 3: Look in the company profile table/section
        profile_elements = soup.find_all(["td", "th", "div", "span"])
        for element in profile_elements:
            text = element.get_text().strip()
            if text.lower() == 'sector' or text.lower() == 'industry':
                # Find the next sibling or parent element that contains the sector value
                next_element = element.find_next_sibling() or element.parent.find_next_sibling()
                if next_element:
                    sector_value = next_element.get_text().strip()
                    # Filter out index names and invalid sectors
                    if (sector_value and len(sector_value) > 2 and 
                        not any(word in sector_value.lower() for word in ['nifty', 'sensex', 'index', 'bse', 'nse', 'show', 'more'])):
                        return sector_value
        
        # Method 4: Look for meta tags with industry/sector info
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            content = meta.get("content", "")
            if "sector" in content.lower() or "industry" in content.lower():
                # Extract sector from meta content
                sector_match = re.search(r'(?:sector|industry)[:\s]*([^,\.\n]+)', content, re.IGNORECASE)
                if sector_match:
                    sector = sector_match.group(1).strip()
                    if not any(word in sector.lower() for word in ['nifty', 'index', 'stock']):
                        return sector
        
        # Method 5: Fallback - look for specific company patterns
        company_name = soup.find("h1")
        if company_name:
            name = company_name.get_text().lower()
            if 'infosys' in name or 'tcs' in name or 'wipro' in name or 'tech' in name:
                return "IT Services & Consulting"
            elif 'bank' in name:
                return "Banking"
            elif 'pharma' in name:
                return "Pharmaceuticals"
        
        return "N/A"
    except:
        return "N/A"

def extract_market_cap_from_page(soup, page_text):
    """Extract market cap and clean formatting"""
    try:
        import re
        
        # Look for market cap patterns in the page text
        market_cap_patterns = [
            r'Mkt Cap[:\s]*₹?\s*([0-9,]+(?:\.[0-9]+)?)\s*([TCL]?cr|Crore?|Lakh)?',
            r'Market Cap[:\s]*₹?\s*([0-9,]+(?:\.[0-9]+)?)\s*([TCL]?cr|Crore?|Lakh)?',
            r'MarketCap[:\s]*₹?\s*([0-9,]+(?:\.[0-9]+)?)\s*([TCL]?cr|Crore?|Lakh)?'
        ]
        
        for pattern in market_cap_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                number = match.group(1).strip()
                unit = match.group(2).strip() if match.group(2) else ""
                
                # Clean the number - remove extra whitespace and newlines
                number = re.sub(r'\s+', '', number)
                
                # Format with unit
                if unit:
                    unit = unit.replace('Crore', 'Cr').replace('crore', 'Cr')
                    return f"{number} {unit}"
                else:
                    return number
        
        # Alternative: Look in specific elements that might contain market cap
        elements = soup.find_all(["span", "div", "td", "li", "p"])
        for element in elements:
            text = element.get_text()
            if "mkt cap" in text.lower() or "market cap" in text.lower():
                # Clean text - remove newlines and extra spaces
                cleaned_text = re.sub(r'\s+', ' ', text.strip())
                
                # Extract market cap value
                cap_match = re.search(r'([0-9,]+(?:\.[0-9]+)?)\s*([TCL]?cr|Crore?|Lakh)?', cleaned_text, re.IGNORECASE)
                if cap_match:
                    number = cap_match.group(1)
                    unit = cap_match.group(2) if cap_match.group(2) else "Cr"
                    unit = unit.replace('Crore', 'Cr').replace('crore', 'Cr')
                    return f"{number} {unit}"
        
        # Try to find market cap in ratios table
        ratios_table = soup.find("table") 
        if ratios_table:
            rows = ratios_table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    first_cell = cells[0].get_text().strip().lower()
                    if "market cap" in first_cell or "mkt cap" in first_cell:
                        second_cell = cells[1].get_text().strip()
                        # Clean the value
                        cleaned_value = re.sub(r'\s+', ' ', second_cell)
                        # Extract number and unit
                        value_match = re.search(r'([0-9,]+(?:\.[0-9]+)?)\s*([TCL]?cr|Crore?|Lakh)?', cleaned_value, re.IGNORECASE)
                        if value_match:
                            number = value_match.group(1)
                            unit = value_match.group(2) if value_match.group(2) else "Cr"
                            unit = unit.replace('Crore', 'Cr').replace('crore', 'Cr')
                            return f"{number} {unit}"
        
        return "N/A"
    except Exception as e:
        print(f"Error extracting market cap: {e}")
        return "N/A"

def extract_pe_ratio(soup, page_text):
    """Extract PE ratio from the page"""
    try:
        import re
        
        # Look for PE ratio patterns
        pe_patterns = [
            r'PE[:\s]*([0-9]+(?:\.[0-9]+)?)',
            r'P/E[:\s]*([0-9]+(?:\.[0-9]+)?)',
            r'Price to Earnings[:\s]*([0-9]+(?:\.[0-9]+)?)'
        ]
        
        for pattern in pe_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                pe_value = float(match.group(1))
                # Basic validation - PE should be reasonable
                if 0 < pe_value < 1000:
                    return pe_value
        
        # Look in ratios table specifically
        ratios_section = soup.find("section", id="ratios") or soup.find("div", class_="ratios")
        if ratios_section:
            pe_element = ratios_section.find(string=re.compile(r'PE|P/E', re.IGNORECASE))
            if pe_element:
                parent = pe_element.parent
                # Look for number in the same row
                row = parent.find_parent("tr") or parent.find_parent("div")
                if row:
                    numbers = re.findall(r'([0-9]+(?:\.[0-9]+)?)', row.get_text())
                    for num in numbers:
                        pe_val = float(num)
                        if 0 < pe_val < 1000:
                            return pe_val
        
        return "N/A"
    except:
        return "N/A"

def extract_roce(soup, page_text):
    """Extract ROCE (Return on Capital Employed) from the page"""
    try:
        import re
        
        # Look for ROCE patterns
        roce_patterns = [
            r'ROCE[:\s]*([0-9]+(?:\.[0-9]+)?)%?',
            r'Return on Capital Employed[:\s]*([0-9]+(?:\.[0-9]+)?)%?',
            r'RoCE[:\s]*([0-9]+(?:\.[0-9]+)?)%?'
        ]
        
        for pattern in roce_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                roce_value = float(match.group(1))
                # Basic validation - ROCE should be reasonable percentage
                if -100 < roce_value < 200:
                    return roce_value
        
        # Look in ratios table specifically
        ratios_section = soup.find("section", id="ratios") or soup.find("div", class_="ratios")
        if ratios_section:
            roce_element = ratios_section.find(string=re.compile(r'ROCE|Return on Capital', re.IGNORECASE))
            if roce_element:
                parent = roce_element.parent
                row = parent.find_parent("tr") or parent.find_parent("div")
                if row:
                    numbers = re.findall(r'([0-9]+(?:\.[0-9]+)?)%?', row.get_text())
                    for num in numbers:
                        roce_val = float(num.replace('%', ''))
                        if -100 < roce_val < 200:
                            return roce_val
        
        return "N/A"
    except:
        return "N/A"

def extract_roe(soup, page_text):
    """Extract ROE (Return on Equity) from the page"""
    try:
        import re
        
        # Look for ROE patterns
        roe_patterns = [
            r'ROE[:\s]*([0-9]+(?:\.[0-9]+)?)%?',
            r'Return on Equity[:\s]*([0-9]+(?:\.[0-9]+)?)%?',
            r'RoE[:\s]*([0-9]+(?:\.[0-9]+)?)%?'
        ]
        
        for pattern in roe_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                roe_value = float(match.group(1))
                # Basic validation - ROE should be reasonable percentage
                if -100 < roe_value < 200:
                    return roe_value
        
        # Look in ratios table specifically
        ratios_section = soup.find("section", id="ratios") or soup.find("div", class_="ratios")
        if ratios_section:
            roe_element = ratios_section.find(string=re.compile(r'ROE|Return on Equity', re.IGNORECASE))
            if roe_element:
                parent = roe_element.parent
                row = parent.find_parent("tr") or parent.find_parent("div")
                if row:
                    numbers = re.findall(r'([0-9]+(?:\.[0-9]+)?)%?', row.get_text())
                    for num in numbers:
                        roe_val = float(num.replace('%', ''))
                        if -100 < roe_val < 200:
                            return roe_val
        
        return "N/A"
    except:
        return "N/A"

def get_indian_fundamentals(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        overview = soup.find("h1").text.strip()

        income_stmt = parse_financial_table(soup, "Profit & Loss")
        balance_sheet = parse_financial_table(soup, "Balance Sheet")
        cash_flow = parse_financial_table(soup, "Cash Flow")

        shareholding = extract_shareholding_from_screener(soup)
        valuation_data = get_company_overview_data(symbol)

        return {
            "symbol": symbol,
            "market": "India",
            "company": overview,
            "income_statement": income_stmt,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
            "shareholding_pattern": shareholding,
            **valuation_data  # injects sector, market_cap, etc.
        }

    except Exception as e:
        return {
            "symbol": symbol,
            "market": "India",
            "error": f"Could not fetch Indian fundamentals: {str(e)}"
        }


# def get_indian_fundamentals(symbol):
#     try:
#         url = f"https://www.screener.in/company/{symbol}/consolidated/"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")

#         overview = soup.find("h1").text.strip()

#         income_stmt = parse_financial_table(soup, "Profit & Loss")
#         balance_sheet = parse_financial_table(soup, "Balance Sheet")

#         # Attempt cash flow via original method, fallback to scrape
#         # cashflow_stmt = get_cashflow_from_screener(symbol)
#         # if not cashflow_stmt:
#         #     cashflow_stmt = get_cashflow_from_screener_fallback(soup)

#         # Get shareholding pattern
#         shareholding = extract_shareholding_from_screener(soup)

#         return {
#             "symbol": symbol,
#             "market": "India",
#             "company": overview,
#             "income_statement": income_stmt,
#             "balance_sheet": balance_sheet,
#             # "cash_flow": cashflow_stmt,
#             "shareholding_pattern": shareholding
#         }

#     except Exception as e:
#         return {
#             "symbol": symbol,
#             "market": "India",
#             "error": str(e)
#         }

# def get_indian_fundamentals(symbol):
#     try:
#         url = f"https://www.screener.in/company/{symbol}/consolidated/"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")

#         income_stmt = parse_financial_table(soup, "Profit & Loss")
#         balance_sheet = parse_financial_table(soup, "Balance Sheet")
#         # cashflow_stmt = parse_financial_table(soup, "Key Financial Ratios") or []
#         # cashflow_stmt = parse_financial_table(soup, "Cash Flow") or []
#         cashflow_stmt = get_cashflow_from_screener(symbol)

#         overview = soup.find("h1").text.strip()

#         return {
#             "symbol": symbol,
#             "market": "India",
#             "company": overview,
#             "income_statement": income_stmt,
#             "balance_sheet": balance_sheet,
#             "cash flow": cashflow_stmt,
#             # "shareholding_pattern": extract_shareholding_breakup(symbol),
#             "shareholding_pattern": extract_shareholding_from_screener(soup)
#         }

#     except Exception as e:
#         return {
#             "symbol": symbol,
#             "market": "India",
#             "error": str(e)
#         }

def get_us_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)

        def df_to_dict(df: pd.DataFrame):
            return df.fillna(0).astype(float).T.to_dict() if not df.empty else {}

        info = ticker.info
        pe_ratio = info.get("trailingPE") or info.get("forwardPE") or "N/A"
        roe = info.get("returnOnEquity") or "N/A"
        roa = info.get("returnOnAssets") or "N/A"

        return {
            "symbol": symbol,
            "market": "US",
            "company": info.get("shortName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe": pe_ratio,
            "roe": roe,
            "roa": roa,
            "income_statement": df_to_dict(ticker.financials),
            "balance_sheet": df_to_dict(ticker.balance_sheet),
            "cash_flow": df_to_dict(ticker.cashflow),
            "investors": ticker.institutional_holders.to_dict(orient='records') if ticker.institutional_holders is not None else [],
        }

    except Exception as e:
        return {
            "symbol": symbol,
            "market": "US",
            "error": f"Could not fetch US fundamentals: {str(e)}"
        }


# def get_us_fundamentals(symbol):
#     try:
#         ticker = yf.Ticker(symbol)

#         def df_to_dict(df: pd.DataFrame):
#             return df.fillna(0).astype(float).T.to_dict() if not df.empty else {}

#         return {
#             "symbol": symbol,
#             "market": "US",
#             "company": ticker.info.get("shortName", "N/A"),
#             "sector": ticker.info.get("sector", "N/A"),
#             "marketCap": ticker.info.get("marketCap", "N/A"),
#             "income_statement": df_to_dict(ticker.financials),
#             "balance_sheet": df_to_dict(ticker.balance_sheet),
#             "cash_flow": df_to_dict(ticker.cashflow),
#             "investors": ticker.institutional_holders.to_dict(orient='records')
#                 if ticker.institutional_holders is not None else [],
#         }

#     except Exception as e:
#         return {
#             "symbol": symbol,   
#             "market": "US",
#             "error": f"Could not fetch US fundamentals: {str(e)}"
#         }


def get_fundamentals(symbol: str):
    if symbol.upper().endswith(".NS"):
        return get_indian_fundamentals(symbol.upper().replace(".NS", ""))
    else:
        return get_us_fundamentals(symbol.upper())
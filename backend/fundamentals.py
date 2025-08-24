import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

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
        
        # If we couldn't get sector or ROCE from screener, try yfinance as fallback
        if sector == "N/A" or roce == "N/A":
            try:
                yf_data = get_yfinance_fallback_data(symbol)
                if sector == "N/A" and yf_data.get("sector") != "N/A":
                    sector = yf_data["sector"]
                if roce == "N/A" and yf_data.get("roce") != "N/A":
                    roce = yf_data["roce"]
            except:
                pass
        
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

def get_yfinance_fallback_data(symbol):
    """
    Get sector and calculate ROCE using yfinance as fallback for Indian stocks
    """
    try:
        # Try with .NS suffix for Indian stocks
        ticker_symbol = f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        sector = info.get("sector", "N/A")
        
        # Calculate ROCE from financial statements if available
        roce = "N/A"
        try:
            # Get financial data
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            if not financials.empty and not balance_sheet.empty:
                # Get the most recent year data
                latest_year = financials.columns[0]
                
                # Calculate EBIT (Operating Income)
                ebit = None
                if 'Operating Income' in financials.index:
                    ebit = financials.loc['Operating Income', latest_year]
                elif 'EBIT' in financials.index:
                    ebit = financials.loc['EBIT', latest_year]
                
                # Calculate Capital Employed (Total Assets - Current Liabilities)
                total_assets = None
                current_liabilities = None
                
                if 'Total Assets' in balance_sheet.index:
                    total_assets = balance_sheet.loc['Total Assets', latest_year]
                if 'Current Liabilities' in balance_sheet.index:
                    current_liabilities = balance_sheet.loc['Current Liabilities', latest_year]
                
                if ebit and total_assets and current_liabilities:
                    capital_employed = total_assets - current_liabilities
                    if capital_employed != 0:
                        roce = (ebit / capital_employed) * 100
                        roce = round(roce, 2)
        except:
            pass
        
        return {
            "sector": sector,
            "roce": roce
        }
        
    except Exception as e:
        print(f"Error in yfinance fallback: {e}")
        return {
            "sector": "N/A",
            "roce": "N/A"
        }

def extract_sector_from_page(soup, page_text):
    """Extract sector information using multiple methods"""
    try:
        import re
        
        # Method 1: Look for sector in the top info section (most reliable)
        top_info = soup.find("div", class_="top") or soup.find("div", class_="company-info")
        if top_info:
            # Look for sector in small text or sub-headings
            small_elements = top_info.find_all(["small", "span", "p", "div"])
            for element in small_elements:
                text = element.get_text().strip()
                # Check if this looks like a sector (not a number, not too short, not an index)
                if (len(text) > 5 and len(text) < 50 and 
                    not re.match(r'^[\d\.,\s%₹$]+$', text) and
                    not any(word in text.lower() for word in ['nifty', 'sensex', 'index', 'bse', 'nse', 'show', 'more', 'market cap', 'pe', 'price'])):
                    # This might be the sector
                    if any(sector_word in text.lower() for sector_word in ['services', 'technology', 'banking', 'pharma', 'auto', 'steel', 'oil', 'telecom', 'fmcg', 'textile', 'cement', 'power', 'finance', 'insurance', 'retail', 'media', 'real estate']):
                        return text
        
        # Method 2: Look for breadcrumb or navigation that shows sector
        breadcrumb = soup.find("nav", class_="breadcrumb") or soup.find("ol", class_="breadcrumb")
        if breadcrumb:
            links = breadcrumb.find_all("a")
            for link in links:
                text = link.get_text().strip()
                if (len(text) > 5 and 
                    not any(word in text.lower() for word in ['home', 'companies', 'screener', 'nifty', 'sensex'])):
                    return text
        
        # Method 3: Look in the company description/about section
        about_section = soup.find("div", class_="company-about") or soup.find("div", class_="description") or soup.find("section", id="about")
        if about_section:
            about_text = about_section.get_text()
            # Look for sector/industry keywords in description
            sector_patterns = [
                r'(?:operates in|engaged in|business of|sector of|industry of)\s+([^.]+)',
                r'(?:is a|leading)\s+([^.]*(?:services|technology|banking|pharma|auto|steel|oil|telecom|fmcg|textile|cement|power|finance|insurance|retail|media)[^.]*)',
            ]
            for pattern in sector_patterns:
                match = re.search(pattern, about_text, re.IGNORECASE)
                if match:
                    sector_text = match.group(1).strip()
                    if len(sector_text) < 100:  # Reasonable length
                        return sector_text
        
        # Method 4: Look for sector in peer comparison section header
        peers_section = soup.find("section", id="peers") or soup.find("div", class_="peers")
        if peers_section:
            # Look for heading that mentions sector
            headings = peers_section.find_all(["h1", "h2", "h3", "h4"])
            for heading in headings:
                text = heading.get_text().strip()
                if ('peer' in text.lower() or 'similar' in text.lower()) and len(text) > 10:
                    # Extract sector from text like "Peers in IT Services sector"
                    sector_match = re.search(r'(?:in|of)\s+([^.]+?)(?:\s+sector|\s+industry|$)', text, re.IGNORECASE)
                    if sector_match:
                        sector = sector_match.group(1).strip()
                        if not any(word in sector.lower() for word in ['peer', 'comparison', 'companies', 'nifty']):
                            return sector
        
        # Method 5: Look in ratios or key metrics table for sector info
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    first_cell = cells[0].get_text().strip().lower()
                    if 'sector' in first_cell or 'industry' in first_cell:
                        sector_value = cells[1].get_text().strip()
                        if (sector_value and len(sector_value) > 2 and 
                            not any(word in sector_value.lower() for word in ['nifty', 'sensex', 'index', 'bse', 'nse'])):
                            return sector_value
        
        # Method 6: Look for meta tags with industry/sector info
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            content = meta.get("content", "")
            if "sector" in content.lower() or "industry" in content.lower():
                sector_match = re.search(r'(?:sector|industry)[:\s]*([^,\.\n]+)', content, re.IGNORECASE)
                if sector_match:
                    sector = sector_match.group(1).strip()
                    if not any(word in sector.lower() for word in ['nifty', 'index', 'stock']):
                        return sector
        
        # Method 7: Fallback - look for specific company patterns and known sectors
        company_name = soup.find("h1")
        if company_name:
            name = company_name.get_text().lower()
            if any(word in name for word in ['infosys', 'tcs', 'wipro', 'tech mahindra', 'hcl tech']):
                return "IT Services & Consulting"
            elif any(word in name for word in ['hdfc', 'icici', 'sbi', 'axis', 'kotak', 'bank']):
                return "Banking & Financial Services"
            elif any(word in name for word in ['sun pharma', 'dr reddy', 'cipla', 'lupin', 'pharma']):
                return "Pharmaceuticals"
            elif any(word in name for word in ['tata motors', 'mahindra', 'maruti', 'bajaj auto', 'hero motocorp']):
                return "Automobile"
            elif any(word in name for word in ['reliance', 'ongc', 'oil', 'gas']):
                return "Oil & Gas"
            elif any(word in name for word in ['tata steel', 'jsw steel', 'steel']):
                return "Steel"
        
        return "N/A"
    except Exception as e:
        print(f"Error extracting sector: {e}")
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
        
        # Method 1: Look for ROCE in ratios table (most reliable)
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    first_cell = cells[0].get_text().strip().lower()
                    if 'roce' in first_cell or 'return on capital' in first_cell:
                        # Found ROCE row, extract value from second cell
                        value_cell = cells[1].get_text().strip()
                        # Look for percentage or number
                        roce_match = re.search(r'([+-]?[0-9]+(?:\.[0-9]+)?)%?', value_cell)
                        if roce_match:
                            roce_value = float(roce_match.group(1))
                            if -100 < roce_value < 500:  # Reasonable range
                                return roce_value
        
        # Method 2: Look for ROCE patterns in page text
        roce_patterns = [
            r'ROCE[:\s]*([+-]?[0-9]+(?:\.[0-9]+)?)%?',
            r'Return on Capital Employed[:\s]*([+-]?[0-9]+(?:\.[0-9]+)?)%?',
            r'RoCE[:\s]*([+-]?[0-9]+(?:\.[0-9]+)?)%?',
            r'Return on Capital[:\s]*([+-]?[0-9]+(?:\.[0-9]+)?)%?'
        ]
        
        for pattern in roce_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                roce_value = float(match.group(1))
                # Basic validation - ROCE should be reasonable percentage
                if -100 < roce_value < 500:
                    return roce_value
        
        # Method 3: Calculate ROCE from financial data if available
        # ROCE = EBIT / Capital Employed
        # Capital Employed = Total Assets - Current Liabilities
        try:
            # Look for financial data in tables
            financial_data = {}
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        label = cells[0].get_text().strip().lower()
                        value_text = cells[1].get_text().strip()
                        
                        # Extract numeric value
                        value_match = re.search(r'([+-]?[0-9,]+(?:\.[0-9]+)?)', value_text.replace(',', ''))
                        if value_match:
                            try:
                                value = float(value_match.group(1).replace(',', ''))
                                
                                # Map common financial terms
                                if any(term in label for term in ['ebit', 'operating profit', 'operating income']):
                                    financial_data['ebit'] = value
                                elif any(term in label for term in ['total assets', 'total asset']):
                                    financial_data['total_assets'] = value
                                elif any(term in label for term in ['current liabilities', 'current liability']):
                                    financial_data['current_liabilities'] = value
                                elif any(term in label for term in ['capital employed']):
                                    financial_data['capital_employed'] = value
                            except:
                                continue
            
            # Calculate ROCE if we have the data
            if 'ebit' in financial_data:
                if 'capital_employed' in financial_data and financial_data['capital_employed'] != 0:
                    roce = (financial_data['ebit'] / financial_data['capital_employed']) * 100
                    if -100 < roce < 500:
                        return round(roce, 2)
                elif ('total_assets' in financial_data and 'current_liabilities' in financial_data):
                    capital_employed = financial_data['total_assets'] - financial_data['current_liabilities']
                    if capital_employed != 0:
                        roce = (financial_data['ebit'] / capital_employed) * 100
                        if -100 < roce < 500:
                            return round(roce, 2)
        except:
            pass
        
        # Method 4: Look in specific ratios section
        ratios_section = soup.find("section", id="ratios") or soup.find("div", class_="ratios")
        if ratios_section:
            roce_element = ratios_section.find(string=re.compile(r'ROCE|Return on Capital', re.IGNORECASE))
            if roce_element:
                parent = roce_element.parent
                row = parent.find_parent("tr") or parent.find_parent("div")
                if row:
                    numbers = re.findall(r'([+-]?[0-9]+(?:\.[0-9]+)?)%?', row.get_text())
                    for num in numbers:
                        try:
                            roce_val = float(num.replace('%', ''))
                            if -100 < roce_val < 500:
                                return roce_val
                        except:
                            continue
        
        return "N/A"
    except Exception as e:
        print(f"Error extracting ROCE: {e}")
        return "N/A"

def calculate_roce_from_statements(income_stmt, balance_sheet):
    """
    Calculate ROCE from financial statements when not directly available
    ROCE = EBIT / Capital Employed
    Capital Employed = Total Assets - Current Liabilities OR Shareholders' Equity + Long-term Debt
    """
    try:
        if not income_stmt or not balance_sheet:
            return "N/A"
        
        # Get the most recent year data (first column usually)
        latest_year = None
        ebit = None
        capital_employed = None
        
        # Find EBIT from income statement
        for item in income_stmt:
            if latest_year is None and item.get('label'):
                # Get the first year column (excluding label)
                years = [k for k in item.keys() if k != 'label']
                if years:
                    latest_year = years[0]
            
            if item.get('label'):
                label = item['label'].lower()
                if any(term in label for term in ['operating profit', 'ebit', 'operating income', 'profit before interest']):
                    if latest_year and latest_year in item:
                        value_str = item[latest_year].replace(',', '').replace('₹', '').strip()
                        try:
                            ebit = float(value_str)
                            break
                        except:
                            continue
        
        # Find Capital Employed from balance sheet
        total_assets = None
        current_liabilities = None
        shareholders_equity = None
        long_term_debt = None
        
        for item in balance_sheet:
            if item.get('label'):
                label = item['label'].lower()
                if latest_year and latest_year in item:
                    value_str = item[latest_year].replace(',', '').replace('₹', '').strip()
                    try:
                        value = float(value_str)
                        
                        if any(term in label for term in ['total assets', 'total asset']):
                            total_assets = value
                        elif any(term in label for term in ['current liabilities', 'current liability']):
                            current_liabilities = value
                        elif any(term in label for term in ['shareholders equity', 'shareholder equity', 'equity']):
                            shareholders_equity = value
                        elif any(term in label for term in ['long term debt', 'long-term debt', 'non-current liabilities']):
                            long_term_debt = value
                    except:
                        continue
        
        # Calculate Capital Employed using available data
        if total_assets and current_liabilities:
            capital_employed = total_assets - current_liabilities
        elif shareholders_equity and long_term_debt:
            capital_employed = shareholders_equity + long_term_debt
        elif shareholders_equity:  # Fallback to just equity
            capital_employed = shareholders_equity
        
        # Calculate ROCE
        if ebit and capital_employed and capital_employed != 0:
            roce = (ebit / capital_employed) * 100
            if -100 < roce < 500:  # Reasonable range
                return round(roce, 2)
        
        return "N/A"
    except Exception as e:
        print(f"Error calculating ROCE from statements: {e}")
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

def get_alternative_sector_data(symbol):
    """
    Try to get sector data from alternative sources like NSE
    """
    try:
        # Try NSE website for sector information
        nse_url = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(nse_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for sector information in NSE page
            sector_elements = soup.find_all(string=re.compile(r'sector|industry', re.IGNORECASE))
            for element in sector_elements:
                parent = element.parent
                if parent:
                    # Look for sector value near the sector label
                    siblings = parent.find_next_siblings()
                    for sibling in siblings[:3]:  # Check next 3 siblings
                        text = sibling.get_text().strip()
                        if (len(text) > 5 and len(text) < 50 and 
                            not any(word in text.lower() for word in ['nifty', 'sensex', 'index'])):
                            return text
        
        return "N/A"
    except Exception as e:
        print(f"Error fetching alternative sector data: {e}")
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
        
        # If sector is still N/A, try alternative sources
        if valuation_data.get("sector") == "N/A":
            alt_sector = get_alternative_sector_data(symbol)
            if alt_sector != "N/A":
                valuation_data["sector"] = alt_sector
        
        # If ROCE is still N/A, try to calculate from financial statements
        if valuation_data.get("roce") == "N/A":
            calculated_roce = calculate_roce_from_statements(income_stmt, balance_sheet)
            if calculated_roce != "N/A":
                valuation_data["roce"] = calculated_roce

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
            if not df.empty:
                return df.fillna(0).infer_objects(copy=False).astype(float).T.to_dict()
            return {}

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
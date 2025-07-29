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


def get_shareholding_from_investing_com(symbol):
    """
    Alternative 4: Investing.com - International financial data
    """
    try:
        clean_symbol = symbol.replace('.NS', '')
        
        # Search for the stock first
        search_url = f"https://api.investing.com/api/financialdata/search/{clean_symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Domain-Id': '1'  # Required by Investing.com API
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            search_results = response.json()
            if search_results and len(search_results) > 0:
                stock_id = search_results[0].get('pairId')
                
                # Get detailed data including shareholding
                detail_url = f"https://api.investing.com/api/financialdata/{stock_id}/shareholding"
                detail_response = requests.get(detail_url, headers=headers, timeout=10)
                
                if detail_response.status_code == 200:
                    return detail_response.json()
        
        return None
        
    except Exception as e:
        print(f"Investing.com API failed: {e}")
        return None

def extract_shareholding_breakup(symbol):
    """
    Extracts shareholding data using Investing.com API (annual for last 5 years).
    """
    try:
        data = get_shareholding_from_investing_com(symbol)
        if not data or "data" not in data:
            return []

        records = data["data"]
        annual_records = []

        for record in records:
            # Filter only yearly data (e.g., "Dec 2023")
            if "periodType" in record and record["periodType"] == "Annual":
                entry = {
                    "Year": record.get("date", "N/A")[:4],  # Extract year from date
                    "Promoters": record.get("promoters", "N/A"),
                    "Public": record.get("public", "N/A"),
                    "Government": record.get("government", "N/A"),
                    "FII": record.get("foreignInstitutionalInvestors", "N/A"),
                    "DII": record.get("domesticInstitutionalInvestors", "N/A"),
                    "MF": record.get("mutualFunds", "N/A"),
                }
                annual_records.append(entry)

        # Return only the last 5 years (sorted from oldest to latest)
        return annual_records[-5:] if len(annual_records) > 0 else []

    except Exception as e:
        print(f"Shareholding extraction failed: {e}")
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

def get_cashflow_from_screener(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/cash-flow/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        section = soup.find("h2", string="Cash Flow Statement")
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
        print(f"Error fetching cash flow: {e}")
        return []


def get_indian_fundamentals(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        income_stmt = parse_financial_table(soup, "Profit & Loss")
        balance_sheet = parse_financial_table(soup, "Balance Sheet")
        # cashflow_stmt = parse_financial_table(soup, "Key Financial Ratios") or []
        # cashflow_stmt = parse_financial_table(soup, "Cash Flow") or []
        cashflow_stmt = get_cashflow_from_screener(symbol)

        overview = soup.find("h1").text.strip()

        return {
            "symbol": symbol,
            "market": "India",
            "company": overview,
            "income_statement": income_stmt,
            "balance_sheet": balance_sheet,
            "cash flow": cashflow_stmt,
            # "shareholding_pattern": extract_shareholding_breakup(symbol),
            "shareholding_pattern": extract_shareholding_from_screener(soup)
        }

    except Exception as e:
        return {
            "symbol": symbol,
            "market": "India",
            "error": str(e)
        }


def get_us_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)

        def df_to_dict(df: pd.DataFrame):
            return df.fillna(0).astype(float).T.to_dict() if not df.empty else {}

        return {
            "symbol": symbol,
            "market": "US",
            "company": ticker.info.get("shortName", "N/A"),
            "sector": ticker.info.get("sector", "N/A"),
            "marketCap": ticker.info.get("marketCap", "N/A"),
            "income_statement": df_to_dict(ticker.financials),
            "balance_sheet": df_to_dict(ticker.balance_sheet),
            "cash_flow": df_to_dict(ticker.cashflow),
            "investors": ticker.institutional_holders.to_dict(orient='records')
                if ticker.institutional_holders is not None else [],
        }

    except Exception as e:
        return {
            "symbol": symbol,   
            "market": "US",
            "error": f"Could not fetch US fundamentals: {str(e)}"
        }



def get_fundamentals(symbol: str):
    if symbol.upper().endswith(".NS"):
        return get_indian_fundamentals(symbol.upper().replace(".NS", ""))
    else:
        return get_us_fundamentals(symbol.upper())
import os
import logger
import time
import pytz
import json
import shutil
import shelve
import requests
import numpy as np
from parser import Parser
from datetime import datetime, timedelta
from sec_edgar_downloader import Downloader as SECDownloader
from llm import generate_llm_response
from logger import get_logger
logger = get_logger(__name__)

class Downloader:
    def __init__(self, ticker = 'AAPL'):
        self.apiKey = os.environ.get('FMP_API_KEY')
        self.cache_dir = 'cache'
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_file = os.path.join(self.cache_dir, 'cache.db')
        self.cache_expiry = timedelta(minutes=300)  # Cache expires after 300 minutes

    def get_earnings_transcript(self, ticker):
        """
        Get the latest earnings transcript for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: The latest earnings transcript content.
        """
        # get latest earnings date
        url = f"https://financialmodelingprep.com/api/v4/earning_call_transcript?symbol={ticker}&apikey={self.apiKey}"
        latest_date = requests.get(url)
        latest_date = latest_date.json()
        if len(latest_date) == 0:
            logger.warning(f"[Warning] No earnings transcript found for {ticker}")
            return ""

        quarter, year = latest_date[0][0], latest_date[0][1]

        # get transcript
        url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{ticker}?year={year}&quarter={quarter}&apikey={self.apiKey}"   
        transcript = requests.get(url)
        transcript = transcript.json()
        transcript = transcript[0]
        if "content" not in transcript:
            logger.warning(f"[Warning] No transcript found for {ticker}")
            return ""

        transcript = transcript["content"]
        return transcript

    def get_company_information(self, ticker):
        """
        Retrieve company information for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            dict: A dictionary containing company information.
        """
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={self.apiKey}"
        company_information = requests.get(url)
        company_information = company_information.json()
        if len(company_information) == 0:
            logger.warning(f"[Warning] No company information found for {ticker}")
            return {}
        
        return company_information[0]

    def get_sec_filing(self, report_type, ticker):
        """
        Fetch and parse SEC filing for a given report type and ticker.
        Args:
            report_type (str): The type of SEC report (e.g., '10-K', '10-Q').
            ticker (str): The stock ticker symbol.
        Returns:
            dict: Parsed content of the SEC filing.
        """
        cache_key = f"{ticker}_{report_type}"
        
        # Try to get from cache first
        with shelve.open(self.cache_file) as cache:
            if cache_key in cache:
                cached_data = cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < self.cache_expiry:
                    return Parser().parse_sec_filing(cached_data['content'])
            
        # If not in cache or expired, fetch new data
        logger.info(f"[Task] Fetching new {report_type} filing")
        dl = SECDownloader("Blotter", "info@blotter.fyi")
        dl.get(report_type, ticker, limit=1, download_details=True)
        
        # Get current directory full path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the 10-K filing
        filing_path = os.path.join(current_dir, "sec-edgar-filings", ticker, report_type)
        
        # Get the most recent filing folder
        filing_folders = [f for f in os.listdir(filing_path) if os.path.isdir(os.path.join(filing_path, f))]
        if not filing_folders:
            return f"No {report_type} filing found"
        latest_filing = max(filing_folders)
        latest_filing_path = os.path.join(filing_path, latest_filing)
        
        # Find the HTML file
        html_files = [f for f in os.listdir(latest_filing_path) if f.endswith('.html')]
        if not html_files:
            return f"No HTML file found in the {report_type} filing"
        html_file = html_files[0]
        html_file_path = os.path.join(latest_filing_path, html_file)
        
        # Read the contents of the HTML file
        content = ""
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove the directory and its contents
        shutil.rmtree("sec-edgar-filings", ignore_errors=True)
        
        # Store in cache
        with shelve.open(self.cache_file) as cache:
            cache[cache_key] = {
                'content': content,
                'timestamp': datetime.now()
            }
        
        return Parser().parse_sec_filing(content)

    def get_financial_statements_10q(self, ticker):
        """
        Get financial statements from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Financial statements content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "financial_statements" in data:
            return data["financial_statements"]
        elif "financial_statements_(unaudited)" in data:
            return data["financial_statements_(unaudited)"]
        else:
            logger.warning(f"[Warning] No financial statements found for {ticker} in 10-Q filing")
            return ""

    def get_managements_discussion_and_analysis_10q(self, ticker):
        """
        Get management's discussion and analysis from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Management's discussion and analysis content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "managements_discussion_and_analysis" in data:
            return data["managements_discussion_and_analysis"]
        else:
            logger.warning(f"[Warning] No managements discussion and analysis found for {ticker} in 10-Q filing")
            return ""

    def get_quantitative_and_qualitative_disclosures_10q(self, ticker):
        """
        Get quantitative and qualitative disclosures from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Quantitative and qualitative disclosures content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "quantitative_and_qualitative_disclosures" in data:
            return data["quantitative_and_qualitative_disclosures"]
        else:
            logger.warning(f"[Warning] No quantitative and qualitative disclosures found for {ticker} in 10-Q filing")
            return ""

    def get_controls_and_procedures_10q(self, ticker):
        """
        Get controls and procedures information from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Controls and procedures content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "controls_and_procedures" in data:
            return data["controls_and_procedures"]
        else:
            logger.warning(f"[Warning] No controls and procedures found for {ticker} in 10-Q filing")
            return ""

    def get_legal_proceedings_10q(self, ticker):
        """
        Get legal proceedings information from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Legal proceedings content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "legal_proceedings" in data:
            return data["legal_proceedings"]
        else:
            logger.warning(f"[Warning] No legal proceedings found for {ticker} in 10-Q filing")
            return ""

    def get_risk_factors_10q(self, ticker):
        """
        Get risk factors from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Risk factors content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "risk_factors" in data:
            return data["risk_factors"]
        else:
            logger.warning(f"[Warning] No risk factors found for {ticker} in 10-Q filing")
            return ""

    def get_unregistered_sales_of_equity_10q(self, ticker):
        """
        Get unregistered sales of equity information from the latest 10-Q filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Unregistered sales of equity content from the 10-Q filing.
        """
        data = self.get_sec_filing("10-Q", ticker)
        if "unregistered_sales_of_equity" in data:
            return data["unregistered_sales_of_equity"]
        else:
            logger.warning(f"[Warning] No unregistered sales of equity found for {ticker} in 10-Q filing")
            return ""

    def get_business_info_10k(self, ticker):
        """
        Get business information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Business information content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "business_info" in data:
            return data["business_info"]
        else:
            logger.warning(f"[Warning] No business info found for {ticker} in 10-K filing")
            return ""

    def get_risk_factors_10k(self, ticker):
        """
        Get risk factors from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Risk factors content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "risk_factors" in data:
            return data["risk_factors"]
        else:
            logger.warning(f"[Warning] No risk factors found for {ticker} in 10-K filing")
            return ""

    def get_properties_of_properties_10k(self, ticker):
        """
        Get properties information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Properties information content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "properties_of_properties" in data:
            return data["properties_of_properties"]
        else:
            logger.warning(f"[Warning] No properties of properties found for {ticker} in 10-K filing")
            return ""

    def get_legal_proceedings_10k(self, ticker):
        """
        Get legal proceedings information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Legal proceedings content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "legal_proceedings" in data:
            return data["legal_proceedings"]
        else:
            logger.warning(f"[Warning] No legal proceedings found for {ticker} in 10-K filing")
            return ""

    def get_market_for_registrants_common_stock_10k(self, ticker):
        """
        Get market information for registrant's common stock from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Market information for registrant's common stock content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "market_for_registrants_common_stock" in data:
            return data["market_for_registrants_common_stock"]
        else:
            logger.warning(f"[Warning] No market for registrants common stock found for {ticker} in 10-K filing")
            return ""

    def get_managements_discussion_and_analysis_10k(self, ticker):
        """
        Get management's discussion and analysis from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Management's discussion and analysis content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "managements_discussion_and_analysis" in data:
            return data["managements_discussion_and_analysis"]
        else:
            logger.warning(f"[Warning] No managements discussion and analysis found for {ticker} in 10-K filing")
            return ""

    def get_quantitative_and_qualitative_disclosures_10k(self, ticker):
        """
        Get quantitative and qualitative disclosures from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Quantitative and qualitative disclosures content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "quantitative_and_qualitative_disclosures" in data:
            return data["quantitative_and_qualitative_disclosures"]
        else:
            logger.warning(f"[Warning] No quantitative and qualitative disclosures found for {ticker} in 10-K filing")
            return ""

    def get_financial_statements_and_supplementary_10k(self, ticker):
        """
        Get financial statements and supplementary data from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Financial statements and supplementary data content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "financial_statements_and_supplementary" in data:
            return data["financial_statements_and_supplementary"]
        else:
            logger.warning(f"[Warning] No financial statements and supplementary found for {ticker} in 10-K filing")
            return ""

    def get_directors_executive_officers_and_10k(self, ticker):
        """
        Get information about directors and executive officers from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Directors and executive officers information content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "directors_executive_officers_and" in data:
            return data["directors_executive_officers_and"]
        else:
            logger.warning(f"[Warning] No directors executive officers and found for {ticker} in 10-K filing")
            return ""

    def get_controls_and_procedures_10k(self, ticker):
        """
        Get controls and procedures information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Controls and procedures content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "controls_and_procedures" in data:
            return data["controls_and_procedures"]
        else:
            logger.warning(f"[Warning] No controls and procedures found for {ticker} in 10-K filing")
            return ""

    def get_executive_compensation_10k(self, ticker):
        """
        Get executive compensation information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Executive compensation content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "executive_compensation" in data:
            return data["executive_compensation"]
        else:
            logger.warning(f"[Warning] No executive compensation found for {ticker} in 10-K filing")
            return ""

    def get_security_ownership_of_certain_10k(self, ticker):
        """
        Get security ownership information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Security ownership content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "security_ownership_of_certain" in data:
            return data["security_ownership_of_certain"]
        else:
            logger.warning(f"[Warning] No security ownership of certain found for {ticker} in 10-K filing")
            return ""

    def get_exhibit_and_financial_statement_10k(self, ticker):
        """
        Get exhibit and financial statement information from the latest 10-K filing for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            str: Exhibit and financial statement content from the 10-K filing.
        """
        data = self.get_sec_filing("10-K", ticker)
        if "exhibit_and_financial_statement" in data:
            return data["exhibit_and_financial_statement"]
        else:
            logger.warning(f"[Warning] No exhibit and financial statement found for {ticker} in 10-K filing")
            return ""

    def get_gdp_growth_rate(self):
        """
        Get the GDP growth rate for the last 12 periods.
        Returns:
            list: A list of GDP growth rate data for the last 12 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=GDP&apikey={self.apiKey}"
        gdp = requests.get(url)
        gdp = gdp.json()
        gdp = gdp[:12]
        return gdp

    def get_unemployment_rate(self):
        """
        Get the unemployment rate for the last 12 periods.
        Returns:
            list: A list of unemployment rate data for the last 12 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=unemploymentRate&apikey={self.apiKey}"
        unemployment_rate = requests.get(url)
        unemployment_rate = unemployment_rate.json()
        unemployment_rate = unemployment_rate[:12]
        return unemployment_rate

    def get_inflation_rate(self):
        """
        Get the inflation rate for the last 10 periods.
        Returns:
            list: A list of inflation rate data for the last 10 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=inflation&apikey={self.apiKey}"
        inflation_rate = requests.get(url)
        inflation_rate = inflation_rate.json()
        inflation_rate = inflation_rate[:10]
        return inflation_rate

    def get_retail_sales(self):
        """
        Get retail sales data for the last 36 periods.
        Returns:
            list: A list of retail sales data for the last 36 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=retailSales&apikey={self.apiKey}"
        retail_sales = requests.get(url)
        retail_sales = retail_sales.json()
        retail_sales = retail_sales[:36]
        return retail_sales

    def get_total_vehical_sales(self):
        """
        Get total vehicle sales data for the last 36 periods.
        Returns:
            list: A list of total vehicle sales data for the last 36 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=totalVehicleSales&apikey={self.apiKey}"
        total_vehical_sales = requests.get(url)
        total_vehical_sales = total_vehical_sales.json()
        total_vehical_sales = total_vehical_sales[:36]
        return total_vehical_sales

    def get_mortgage_rates(self):
        """
        Get 30-year fixed-rate mortgage average data for the last 24 periods.
        Returns:
            list: A list of mortgage rate data for the last 24 periods.
        """
        url = f"https://financialmodelingprep.com/api/v4/economic?name=30YearFixedRateMortgageAverage&apikey={self.apiKey}"
        mortgage_rates = requests.get(url)
        mortgage_rates = mortgage_rates.json()
        mortgage_rates = [mortgage_rates[x] for x in range(0, len(mortgage_rates)) if x % 4 == 0]
        mortgage_rates = mortgage_rates[:24]
        return mortgage_rates

    def get_current_ticker_price(self, ticker):
        """
        Get the current stock price for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            float: The current stock price.
        """
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={self.apiKey}"
        current_price = requests.get(url)
        current_price = current_price.json()
        return current_price[0]["price"]

    def get_price_chart_historical(self, ticker):
        """
        Get historical price data for a given ticker for the last 251 trading days.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of historical price data for the last 251 trading days.
        """
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={self.apiKey}"
        historical_price = requests.get(url)
        historical_price = historical_price.json()
        historical_price = historical_price["historical"]
        return historical_price[:251]

    def get_analyst_price_targets(self, ticker):
        """
        Get analyst price targets for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of the last 25 analyst price targets.
        """
        url = f"https://financialmodelingprep.com/api/v4/price-target?symbol={ticker}&apikey={self.apiKey}"
        price_targets = requests.get(url)
        price_targets = price_targets.json()
        price_targets = price_targets[:25]
        return price_targets

    def get_pe_ratio(self, ticker):
        """
        Get the current price-to-earnings (P/E) ratio for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            float: The current P/E ratio.
        """
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={self.apiKey}"
        current_price = requests.get(url)
        current_price = current_price.json()
        return current_price[0]["pe"]

    def get_market_cap(self, ticker):
        """
        Get the current market capitalization for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            float: The current market capitalization.
        """
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={self.apiKey}"
        current_price = requests.get(url)
        current_price = current_price.json()
        return current_price[0]["marketCap"]

    def get_eps(self, ticker):
        """
        Get the current earnings per share (EPS) for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            float: The current EPS.
        """
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={self.apiKey}"
        current_price = requests.get(url)
        current_price = current_price.json()
        return current_price[0]["eps"]

    def get_insider_trades(self, ticker):
        """
        Get recent insider trading data for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of recent insider trades.
        """
        url = f"https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker}&page=0&apikey={self.apiKey}"
        insider_trades = requests.get(url)
        insider_trades = insider_trades.json()
        purchased = [item["securitiesTransacted"] for item in insider_trades if item["transactionType"] == "P-Purchase"]
        purchased = sum(purchased) if purchased else 0
        sold = [item["securitiesTransacted"] for item in insider_trades if item["transactionType"] == "S-Sale"]
        sold = sum(sold) if sold else 0
        return insider_trades

    def get_institutional_ownership(self, ticker):
        """
        Get the latest institutional ownership data for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of institutional ownership data.
        """
        url = f"https://financialmodelingprep.com/api/v3/institutional-holder/{ticker}?apikey={self.apiKey}"
        institutional_ownership = requests.get(url)
        institutional_ownership = institutional_ownership.json()
        latest_date = institutional_ownership[0]["dateReported"]
        institutional_ownership = [item for item in institutional_ownership if item["dateReported"] == latest_date]
        return institutional_ownership

    def get_stock_peers(self, ticker):
        """
        Get a list of peer stocks for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of peer stock tickers.
        """
        url = f"https://financialmodelingprep.com/api/v4/stock_peers?symbol={ticker}&apikey={self.apiKey}"
        stock_peers = requests.get(url)
        stock_peers = stock_peers.json()
        if len(stock_peers) == 0:
            logger.warning(f"[Warning] No stock peers found for {ticker}")
            return []
        if "peersList" not in stock_peers[0]:
            logger.warning(f"[Warning] No stock peers found for {ticker}")
            return []
        return stock_peers[0]["peersList"]

    def get_ticker_news(self, ticker):
        """
        Get recent news articles related to a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of recent news articles.
        """
        cache_key = f"{ticker}_news"
        
        with shelve.open(self.cache_file) as cache:
            if cache_key in cache:
                cached_data = cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < self.cache_expiry:
                    return cached_data['content']
        
        all_news = []
        for page in range(0, 25):
            url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&page={page}&apikey={self.apiKey}&limit=50"
            news = requests.get(url)
            news = news.json()
            all_news.extend(news)

        with shelve.open(self.cache_file) as cache:
            cache[cache_key] = {
                'content': all_news,
                'timestamp': datetime.now()
            }

        return all_news

    def get_historical_earnings(self, ticker):
        """
        Get historical earnings data for a given ticker.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list: A list of the last 16 historical earnings data points.
        """
        url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{ticker}?apikey={self.apiKey}"
        historical_earnings = requests.get(url)
        historical_earnings = historical_earnings.json()
        historical_earnings = [item for item in historical_earnings if item["eps"] is not None]
        return historical_earnings[:16]

    def get_response_from_a_large_language_model(self, prompt):
        """
        Generate a response from a large language model based on the given prompt.
        Args:
            prompt (str): The input prompt for the language model.
        Returns:
            str: The generated response from the language model.
        """
        return generate_llm_response(prompt, temperature=0.0)


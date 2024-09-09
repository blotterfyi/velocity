import os
import pytz
import json
import shutil
import shelve
import random
from tqdm import tqdm
from datetime import datetime, timedelta
from downloader import Downloader
from llm import generate_llm_response, self_reflect
from config import SEC_INSIGHTS
from agent import Agent
from logger import get_logger
logger = get_logger(__name__)

class SECAgent(Agent):
    def __init__(self, ticker):
        self.ticker = ticker
        self.functions_to_call = {
            "get_financial_statements_10q": Downloader().get_financial_statements_10q(self.ticker),
            "get_managements_discussion_and_analysis_10q": Downloader().get_managements_discussion_and_analysis_10q(self.ticker),
            "get_quantitative_and_qualitative_disclosures_10q": Downloader().get_quantitative_and_qualitative_disclosures_10q(self.ticker),
            "get_controls_and_procedures_10q": Downloader().get_controls_and_procedures_10q(self.ticker),
            "get_legal_proceedings_10q": Downloader().get_legal_proceedings_10q(self.ticker),
            "get_risk_factors_10q": Downloader().get_risk_factors_10q(self.ticker),
            "get_unregistered_sales_of_equity_10q": Downloader().get_unregistered_sales_of_equity_10q(self.ticker),
            "get_business_info_10k": Downloader().get_business_info_10k(self.ticker),
            "get_risk_factors_10k": Downloader().get_risk_factors_10k(self.ticker),
            "get_legal_proceedings_10k": Downloader().get_legal_proceedings_10k(self.ticker),
            "get_managements_discussion_and_analysis_10k": Downloader().get_managements_discussion_and_analysis_10k(self.ticker),
            "get_quantitative_and_qualitative_disclosures_10k": Downloader().get_quantitative_and_qualitative_disclosures_10k(self.ticker),
            "get_financial_statements_and_supplementary_10k": Downloader().get_financial_statements_and_supplementary_10k(self.ticker),
            "get_directors_executive_officers_and_10k": Downloader().get_directors_executive_officers_and_10k(self.ticker),
            "get_controls_and_procedures_10k": Downloader().get_controls_and_procedures_10k(self.ticker),
            "get_executive_compensation_10k": Downloader().get_executive_compensation_10k(self.ticker),
            "get_security_ownership_of_certain_10k": Downloader().get_security_ownership_of_certain_10k(self.ticker),
            "get_exhibit_and_financial_statement_10k": Downloader().get_exhibit_and_financial_statement_10k(self.ticker),
        }

    def extract(self):
        """
        Extract insights from a randomly selected SEC filing section.
        Returns:
            str: A paragraph of insights with a heading/title in the first line,
                 based on the selected SEC filing section.
        """

        agent_data = random.choice(list(self.functions_to_call.keys()))
        agent_data = self.functions_to_call[agent_data]
        prompt = f"""
        You are an expert financial analyst at reading SEC filings and drawing conclusions that only a PhD level quant can draw.
        You are given an unstructured part of an SEC 10K/10Q and your job is to carefully read it, and extract some kind of a unique insight.
        We are going to use these insights to make decisions about building a rating (buy, hold, sell) for the stock.
        You have to be technical, quantitative, use numbers, and most of all, creative. You cannot act like a 2 year old.

        Here is the data dump:
        ```
        {agent_data}
        ```

        Now return a one paragraph insights from this data. Add a heading/title in the first line. The heading should explain the paragraph, should not be generic. For instance, a title like `AAPL's next support is at 138' is better than 'AAPL's support levels'
        No prefix, suffix, starting with `here is`, etc. Start directly with insights. Use numbers and statistics where you can.
        """

        result = generate_llm_response(prompt, model="gpt-4o-mini")
        return result

    def run(self):
        """
        Execute the main workflow of the SECAgent.
        This method extracts multiple insights from various SEC filing sections.
        Returns:
            list: A list of insights extracted from SEC filings.
        """
        
        logger.info(f"[Task] Gathering insights from SEC filings for {self.ticker}")
        logger.info(f"[Task] Running SEC agent to extract {SEC_INSIGHTS} insights")
        insights = []
        for _ in tqdm(range(SEC_INSIGHTS), desc="Extracting SEC insights", unit="insight"):
            data = self.extract()
            insights.append(data)
        logger.info(f"[Task] Success, extracted {len(insights)} insights from SEC filings for {self.ticker}")
        return insights
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
from config import NEWS_ANALYST_TYPES, NEWS_INSIGHTS
from sandbox import run_code
from agent import Agent
from logger import get_logger
logger = get_logger(__name__)

class NewsAgent(Agent):
    def __init__(self, ticker):
        self.ticker = ticker

    def extract(self):
        """
        Extract insights from news data related to the ticker.
        This method fetches news data, processes it, and generates insights
        based on a randomly selected analyst type.
        Returns:
            str: A paragraph of insights with a heading/title in the first line,
                 based on the news data and selected analyst type.
        """

        news_data = Downloader().get_ticker_news(self.ticker)
        news_data_dump = ""
        for item in news_data:
            news_data_dump += f"{item['title']}\n{item['text']}\n\n"

        analyst_type = random.choice(NEWS_ANALYST_TYPES)
        prompt = f"""
        You are an expert financial analyst at reading news about {self.ticker} and drawing conclusions that only a PhD level quant can draw.
        You are given an unstructured news data and your job is to carefully read it, and extract some kind of a unique insight.
        We are going to use these insights to make decisions about building a rating (buy, hold, sell) for the stock.
        You have to be technical, quantitative, use numbers, and most of all, creative. You cannot act like a 2 year old.

        The type of agent you have to act like is: {analyst_type} - make sure your analysis revolves around this theme.

        Here is the data dump from the last 6 months of news:
        ```
        {news_data_dump}
        ```

        Now return a one paragraph insights from this data. Add a heading/title in the first line. The heading should explain the paragraph, should not be generic. For instance, a title like `AAPL's next support is at 138' is better than 'AAPL's support levels'
        No prefix, suffix, starting with `here is`, etc. Start directly with insights. Use numbers and statistics where you can.

        Again, your analyst should revolve around {analyst_type} since thats what you are.
        """

        result = generate_llm_response(prompt, model="gpt-4o-mini")
        return result

    def run(self):
        """
        Execute the main workflow of the NewsAgent.
        This method extracts multiple insights from news data.
        Returns:
            list: A list of insights extracted from news data.
        """
        
        insights = []
        logger.info(f"[Task] Extracting {NEWS_INSIGHTS} insights from news data for {self.ticker}")
        for _ in tqdm(range(NEWS_INSIGHTS), desc="Extracting insights from news", unit="insight"):
            data = self.extract()
            insights.append(data)

        logger.info(f"[Task] Success, extracted {NEWS_INSIGHTS} insights from news data for {self.ticker}")
        return insights
        

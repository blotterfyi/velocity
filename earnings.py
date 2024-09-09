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
from config import EARNINGS_TRANSCRIPT_INSIGHTS
from sandbox import run_code
from agent import Agent
from logger import get_logger
logger = get_logger(__name__)

class EarningsAgent(Agent):
    def __init__(self, ticker):
        self.ticker = ticker

    def extract(self):
        """
        Extract insights from the latest earnings transcript for the given ticker.
        Returns:
            str: A string containing two paragraphs of insights (risks and strengths) 
                 with a heading/title in the first line.
        """
        transcript = Downloader().get_earnings_transcript(self.ticker)
        prompt = f"""
        You are an expert financial analyst at reading earnings transcripts and drawing conclusions that only a PhD level quant can draw.
        You are given an unstructured earnings transcript and your job is to carefully read it, and extract some kind of a unique insight.
        We are going to use these insights to make decisions about building a rating (buy, hold, sell) for the stock.
        You have to be technical, quantitative, use numbers, and most of all, creative. You cannot act like a 2 year old.
        Remember to discuss both risks and strengths.

        Here is the data dump from the latest transcript:
        ```
        {transcript}
        ```

        Now return a two paragraphs insights from this data (risks and strengths). Add a heading/title in the first line. The heading should explain the paragraph, should not be generic. For instance, a title like `AAPL's next support is at 138' is better than 'AAPL's support levels'
        No prefix, suffix, starting with `here is`, etc. Start directly with insights. Use numbers and statistics where you can.
        """

        result = generate_llm_response(prompt, model="gpt-4o-mini")
        return result

    def run(self):
        """
        Run the earnings analysis process, extracting multiple insights from earnings transcripts.
        Returns:
            list: A list of insights extracted from earnings transcripts.
        """

        logger.info(f"[Task] Extracting {EARNINGS_TRANSCRIPT_INSIGHTS} insights from earnings transcript data for {self.ticker}")
        insights = []
        for _ in tqdm(range(EARNINGS_TRANSCRIPT_INSIGHTS), desc="Extracting insights from earnings transcripts", unit="insight"):
            data = self.extract()
            insights.append(data)
        logger.info(f"[Task] Success, extracted {EARNINGS_TRANSCRIPT_INSIGHTS} insights from earnings transcript data for {self.ticker}")
        return insights
    
import os
import pytz
import json
import shutil
import shelve
from datetime import datetime, timedelta
from downloader import Downloader
from parser import Parser
from sec_edgar_downloader import Downloader as SECDownloader
from datetime import datetime, timedelta
from llm import generate_llm_response, self_reflect
from coder import CodingAgent
from news import NewsAgent
from sec import SECAgent
from earnings import EarningsAgent
from analyst import Analyst
from htmler import HTMLer
import argparse
from logger import get_logger
logger = get_logger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Velocity analysis for a given stock ticker')
    parser.add_argument('--ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--openai_key', type=str, help='OpenAI API key')
    parser.add_argument('--fmp_key', type=str, help='Financial Modeling Prep API key')
    return parser.parse_args()

def set_api_keys(args):
    if args.openai_key:
        os.environ['OPENAI_API_KEY'] = args.openai_key
    if args.fmp_key:
        os.environ['FMP_API_KEY'] = args.fmp_key

def validate_inputs(args):
    if not args.ticker:
        raise ValueError("Ticker symbol is required.")
    
    if 'OPENAI_API_KEY' not in os.environ and not args.openai_key:
        raise ValueError("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable or provide it using the --openai_key argument.")
    
    if 'FMP_API_KEY' not in os.environ and not args.fmp_key:
        raise ValueError("Financial Modeling Prep API key is required. Please set the FMP_API_KEY environment variable or provide it using the --fmp_key argument.")




class Velocity:
    def __init__(self, ticker):
        self.ticker = ticker
        self.cache_file = 'cache/insights.db'
        self.cache_expiry = timedelta(minutes=300)  # Cache expires after 30 minutes
        self.historical_price = Downloader().get_price_chart_historical(self.ticker)
        self.analyst = Analyst(self.ticker)

    def gather_insights(self):
        """
        Gather insights for the ticker from various sources and cache the results.
        Returns:
            list: A list of insights from different agents.
        """
        logger.info(f"[Plan] Gathering insights for {self.ticker} from all the data I have, including SEC filings, news, earnings, price, institutions, etc, I need some time for this, lets go...")
        # check in cache and load
        with shelve.open(self.cache_file) as cache:
            if self.ticker in cache and cache[self.ticker]['timestamp'] > datetime.now() - self.cache_expiry:
                logger.info(f"[Cache] Data already cached for {self.ticker}, using it.")
                return cache[self.ticker]['insights']

        insights = []
        insights.append(SECAgent(self.ticker).run())
        insights.append(CodingAgent(self.ticker).run())
        insights.append(NewsAgent(self.ticker).run())
        insights.append(EarningsAgent(self.ticker).run())

        # save to cache with timestamp
        logger.info(f"[Cache] Saving insights for {self.ticker} to cache so that we dont have to re-do them again")
        with shelve.open(self.cache_file) as cache:
            cache[self.ticker] = {
                'insights': insights,
                'timestamp': datetime.now()
            }

        return insights

    def run(self):
        """
        Execute the main Velocity analysis workflow.
        This method gathers insights, performs analysis, and saves the results.
        """
        insights = self.gather_insights()
        insights_string = ""
        for category in insights:
            for insight in category:
                insights_string += f"{insight}\n\n"

        logger.info(f"[Plan] Insights retrieved, we are now going to do some analysis")
        radar = self.analyst.radar(insights_string)
        
        targets = self.analyst.price_target(insights_string)
        bull_case = self.analyst.bull_case(insights_string)
        bear_case = self.analyst.bear_case(insights_string)
        base_case, heading_case = self.analyst.base_case(insights_string, bull_case, bear_case)
        risk_reward_themes = self.analyst.risk_reward_themes(insights_string)
        thesis = self.analyst.thesis(insights_string)
        heading = self.analyst.heading(insights_string)
        
        current_price = self.analyst.current_stock_price
        
        # save this output in a json in output/ticker.json
        logger.info(f"[Task] Saving the output to a json file in output/{self.ticker}.json")
        data = {
            "ticker": self.ticker,
            "price_target": targets,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "base_case": base_case,
            "risk_reward_themes": risk_reward_themes,
            "thesis": thesis,
            "heading": heading,
            "heading_case": heading_case,
            "current_price": current_price,
            "radar": radar,
            "chart": self.historical_price
        }

        
        # check if output directory exists, if not create it
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # save the data to a JSON file
        with open(os.path.join(output_dir, f"{self.ticker}.json"), "w") as f:
            json.dump(data, f)

        # save as html
        HTMLer(self.ticker).to_html()

def main():
    args = parse_arguments()
    set_api_keys(args)
    validate_inputs(args)
    Velocity(args.ticker).run()

if __name__ == "__main__":
    main()
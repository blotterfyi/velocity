import os
import pytz
import json
import shutil
import shelve
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
from downloader import Downloader
from datetime import datetime, timedelta
from llm import generate_llm_response, self_reflect
import argparse
from logger import get_logger
logger = get_logger(__name__)


class Analyst:
    def __init__(self, ticker):
        self.ticker = ticker
        self.current_stock_price = Downloader().get_current_ticker_price(self.ticker)
        
    def bull_case(self, insights_string):
        logger.info(f"[Task] Building a bull case for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.

        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a bull case for {self.ticker}.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here is the dump of insights:
        ```
        {insights_string}
        ```
        
        Output Format:
        Your output must be a json with two fields.
        - price_target
        - thesis

        Your price target should be based on your thesis, so write that first. Thesis should be 50-100 words at max. Your language should be plain, but your answer must be super technical with respect to numbers,
        fundamentals, technicals, strengths, risks, etc. Your answer must only talk about a bull thesis, do not talk about risks, or caution. We have other analysts for that. Do not mention that price target in your thesis. An example of a bull thesis is

        ```Subscription streaming adoption increases more rapidly than in base case and Spotify maintains global share: Total Premium subscribers reach ~315M by 2026E. Greater scale, price increases, and market-leading position give the company operating leverage. This contributes to greater gross margin growth than```

        example:
        {{"thesis": "...", "price_target": "500"}}

        Do not start with ```json, start with the first bracket.
        """

        bull_case =  generate_llm_response(prompt, temperature = 0.25)
        return json.loads(bull_case)

    def bear_case(self, insights_string):
        logger.info(f"[Task] Building a bear case for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.
        
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a bear case for {self.ticker}.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here is the dump of insights:
        ```
        {insights_string}
        ```

        Output Format:
        Your output must be a json with two fields.
        - price_target
        - thesis

        Your price target should be based on your thesis, so write that first. Thesis should be 50-100 words at max. Your language should be plain, but your answer must be super technical with respect to numbers,
        fundamentals, technicals, strengths, risks, etc. Your answer must only talk about a bear thesis, do not talk about strengths, or caution. We have other analysts for that. Do not mention that price target in your thesis. An example of a bull thesis is

        ```
        Driving subscription streaming adoption proves to be more challenging, with Spotify losing global market share: Total Premium subscribers reach ~290M by 2026E. Smaller scale limits leverage from the advertising business, but non-core service offerings and monetization of non-music content listening help increase gross margins...
        ```

        example:
        {{"thesis": "...", "price_target": "120"}}

        Do not start with ```json, start with the first bracket.
        """

        bear_case = generate_llm_response(prompt, temperature = 0.25)
        return json.loads(bear_case)

    def base_case(self, insights_string, bull_case, bear_case):
        logger.info(f"[Task] Building a base case for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.
        
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a base case for {self.ticker}.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here is the dump of insights:
        ```
        {insights_string}
        ```

        Your price target must be between the bull and bear case, which are given below. Your thesis could however be completely different.
        {bull_case}
        {bear_case}

        Output Format:
        Your output must be a json with two fields.
        - price_target
        - thesis

        Your price target should be based on your thesis, so write that first. Thesis should be 50-100 words at max. Your language should be plain, but your answer must be super technical with respect to numbers,
        fundamentals, technicals, strengths, risks, etc. Your answer must only talk about a base thesis, you can include whatever you want in it. We have other analysts for that. Do not mention that price target in your thesis. Example of a base case is

        ```
        Streaming adoption ramps nicely, while Spotify protects its market share and revenue grows ~16% on a CAGR basis: Total Premium subscribers reach ~300M by 2026E. Scale, along with non-core service offerings and monetization of non-music content listening collectively drive gross margin expansion to approach 35%...
        ```

        example:
        {{"thesis": "...", "price_target": "120"}}

        Do not start with ```json, start with the first bracket.
        """

        base_case =  generate_llm_response(prompt, temperature = 0.25)

        # get a shorter base case
        prompt = f"""
            You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
            You are tasked with writing a base case for {self.ticker}. You already have a base case written, you just need to now shorten it in 1 sentence (20 words max), and use first person (I).

            e.g
            ```
            Our $400 price target implies a ~22x YE25 EV / fwd. EBITDA multiple, and implies shares trade in line with current levels on EV / fwd. gross profit.
            ```.

            Only return the base case, dont return any price targets. No suffix, no prefix, no starting with `here is`, start with the base case directly. Language shouldnt be copied from the original base case,
            it should look different. More technical, more numbers. But should be understandable by a layman.

            Here is the longer base  case:
            {base_case}
        """
        shorter_base_case = generate_llm_response(prompt, temperature = 0.25)
        return json.loads(base_case), shorter_base_case

    def risk_reward_themes(self, insights_string):
        risk_reward_summary = """
        Contrarian
        Positive: Stock call and key underlying numbers are materially above / more bullish than Consensus.
        Negative: Stock call and key underlying numbers are materially below / more bearish than Consensus.
        Disruption
        Positive: Company has significantly altered, or could potentially alter, the business paradigm within at least one industry.
        Negative: Company is exposed to risk of disruptive innovations from competitors (e.g. new technologies, business models, or product features).
        Electric Vehicles
        Positive: Company is expected to be a leading beneficiary of EV penetration by developing / manufacturing electric vehicles or complementary products (e.g. batteries, chemicals,
        tech hardware, and software).
        Negative: Company is expected to be 1) a traditionalist, due to continued strategic focus on fossil fuels or 2) a laggard in the transition to renewables, due to limited capabilities
        or technical complexities.
        Market Share
        Positive: Company has significant opportunity to grow market share in the near to medium term (i.e. next 1-2 years).
        Negative: Company is at risk of losing market share in the near to medium term (i.e. next 1-2 years).
        New Data Era
        Positive: Company is expected to be a leading provider of at least one emerging technologies (e.g. IoT, AI, VR/AR, or Automation) in the new data-centered computing cycle.
        Negative: Company is expected to be 1) a traditionalist, due to continued strategic focus on existing technologies or 2) a laggard in providing new technologies, due to
        underinvestment or limited capabilities.
        Pricing Power
        Positive: Investment thesis includes benefits from exercising pricing power in the near to medium term (i.e. next 1-2 years), where pricing power is material enough to support the
        stock's valuation.
        Negative: Investment thesis includes inability to raise prices, temporarily or structurally.
        Renewable Energy
        Positive: Company is investing heavily in the generation, distribution, and storage of renewables (e.g. solar and wind), which are expected to drive growth as a result of demand
        for alternative energy solutions.
        Negative: Company is expected to be 1) a traditionalist, due to continued strategic focus on fossil fuels or 2) a laggard in the transition to renewables, due to limited capabilities or
        technical complexities.
        Secular Growth
        Positive: Company's primary earnings drivers operate independently of the macro environment.
        Negative: Company's primary earnings drivers are impacted by secular trends that can reshape or disrupt economies, sectors, and business models.
        Self-help
        Positive: Company is undertaking internal initiatives such as management, governance, strategy, or capital structure changes expected to drive shareholder returns.
        Negative: Management has little to no opportunity to undertake specific actions to create value.
        Special Situation
        Positive: An ongoing or potential future event (e.g. spinoff, merger, or acquisition) is likely to have positive implications for company's valuation.
        Negative: An ongoing or potential future event is likely to have negative implications for company's valuation.
        Technology Diffusion
        Positive: Company is investing heavily in the adoption of technologies aimed at accelerating productivity growth and creating a competitive advantage.
        Negative: Company is underinvesting in technology adoption, leading to inefficient processes, lower productivity, and higher costs
        """
        
        prompt = f"""
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        Your job is to pick three risk reward themes in the list provided below, then carefully go through all the data provided next about {self.ticker}, and extract
        the top 3 risk reward themes with their values (positive, negative).

        Risk Reward Themes:
        ```
        {risk_reward_summary}
        ```

        Insights:
        ```
        {insights_string}
        ```

        Output Format:
        Your output must be a list with three dictionaries, each dictionary will have the theme name and value would be positive or negative. Thats all we need.
        
        e.g (just an example)
        {{"Secular Growth": "positive", ....}}

        Do not start with ```json, start with the first bracket.
        """

        risk_reward_themes = generate_llm_response(prompt, temperature = 0.25)
        return json.loads(risk_reward_themes)

    def thesis(self, insights_string):
        logger.info(f"[Task] Building a thesis for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.
        
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing an analyst rating for {self.ticker}, i.e Underweight, Overweight or Equal-weight.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here is the dump of insights:
        ```
        {insights_string}
        ```

        Output Format:
        Your output must be a json with two fields.
        - analyst_rating
        - thesis

        Your analyst rating should be based on your thesis, so write that first.. Thesis should be 50-100 words at max, in 3 bullet points. Your language should be plain, but your answer must be super technical with respect to numbers, fundamentals, technicals, strengths, risks, etc. Your answer should explain the analyst rating in 3 bullet points, you can include whatever you want in it. We have other analysts for that. 

        Example of three thesis points are
        ```
        Spotify is the market leader in subscription streaming, with growing user engagement, and we believe scale brings an opportunity for ancillary revenues including podcasts and artist/label tools
        We see the 3bn+ global smartphones (ex-China) as a large opportunity currently in early innings, with ~15% penetration today
        Advertising is also a significant opportunity, with the company's current $2bn+ advertising business a fraction of the overall $20bn global radio ad market opportunity
        ```

        example:
        {{"thesis": ["...", "...", "..."], "analyst_rating": "Overweight"}}

        Do not start with ```json, start with the first bracket.
        """
        thesis = generate_llm_response(prompt, temperature = 0.25)
        return json.loads(thesis)

    def price_target(self, insights_string):
        targets = []
        logger.info(f"[Task] Building price targets for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.
        
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a price target for {self.ticker}.

        Your output must be of the following format.
        <thinking>
        write down your thoughts here
        </thinking>
        <reflection>
        reflect on your thoughts, see if there is any issue with them, revise them.
        </reflection>
        <price>
        write down your price target as an integer here. There should only be a single integer in these tags.
        </price>

        Think of the future growth, risks, strengths, all of the stuff that a senior analyst would think about. Dont be shallow, think deep. Be creative, what is something that people might miss?

        Here is the information provided to you:
        ```
        {insights_string}
        ```
        """

        for _ in tqdm(range(10), desc="Generating price targets"):
            target = generate_llm_response(prompt, temperature = 1, model="gpt-4o")
            target = target.split("<price>")[-1].split("</price>")[0]
            targets.append(float(target))
        return targets

    def heading(self, insights_string):
        logger.info(f"[Task] Building a heading for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.

        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a heading for the report. At max 6-10 words.

        An example of a great heading is 
        `Market leader in a secular online music streaming industry` (just an example dont copy it)

        - Heading should be related to what the company does.

        Here is the data you have
        ```
        {insights_string}
        ```

        Return a heading only, no prefix, suffix, no starting with `here is.`, just the heading. Dont use words amid, delve, keep it basic english.
        """
        heading = generate_llm_response(prompt, temperature = 0.5, model="gpt-4o-mini")
        return heading
    
    def radar(self, insights_string):
        logger.info(f"[Task] Building health metrics & ratings for {self.ticker}")
        prompt = f"""
        Current price of {self.ticker} is {self.current_stock_price}.
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with finding a radar chart data for {self.ticker}.

        We are going to build a radar chart for a company where we score the company on 5 different axis, and we score out of 5. 
        The higher the score, the better the company for that axis. Axis are:

        - Growth
        - Valuation
        - Risk
        - Profitability
        - Health
        
        Your output must be of the following format.
        <thinking>
        write down your thoughts here
        </thinking>
        <reflection>
        reflect on your thoughts, see if there is any issue with them, revise them.
        </reflection>
        <data>
        in a json format, write down your ratings for each of the following categories out of 5. 5 is the highest rating, 1 is the lowest. An example output is
        {{"Growth": 5, "Valuation": 4, "Risk": 3, "Momentum": 2, "Quality": 1}}
        </data>

        Make sure there is a valid json inside the data tag.
        Here is the insights dump.
        ```
        {insights_string}
        ```
        """

        results = []
        
        for _ in tqdm(range(5), desc="Generating AI ratings"):
            radar = generate_llm_response(prompt, temperature=0.5, model="gpt-4o")
            radar_data = radar.split("<data>")[-1].split("</data>")[0]
            results.append(json.loads(radar_data))
        
        # Extract keys and average the results for each key
        categories = ["Growth", "Valuation", "Risk", "Profitability", "Health"]
        averaged_radar = {category: np.mean([result[category] for result in results]) for category in categories}
        
        # Round to the nearest integer
        averaged_radar = {key: int(round(value)) for key, value in averaged_radar.items()}

        return averaged_radar

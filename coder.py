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
from config import CODING_AGENT_TYPES, FUNCTION_MAPPINGS, FINANCIAL_STATISTICAL_INSIGHTS
from sandbox import run_code
from agent import Agent
from logger import get_logger
logger = get_logger(__name__)

class CodingAgent(Agent):
    def __init__(self, ticker):
        self.ticker = ticker
        self.downloader = Downloader(self.ticker)
    
    def insights(self, plan, result):
        """
        Generate insights based on the given plan and result.
        Args:
            plan (str): The original plan or task given to the analyst.
            result (str): The results or output from the analyst's work.
        Returns:
            str: A paragraph of insights with a heading/title in the first line.
        """

        prompt = f"""
        You are a financial analyst and a wizard are building complex analyst reports for companies. Your reports are famous for how creative, and how valuable they are 
        to analysts, and large hedge funds.

        You gave a task to another analyst and the results for that are given below. But that analyst is pretty new and only gave the work you asked for.
        Your job now is to extract a one paragraph insight from the work of this intern, but make sure that insight is really `insightful`. Act like a quantitative analyst
        at one of the big hedge funds, truly act like it.

        Here was the plan for the intern:
        {plan}

        Here are the results:
        {result}

        Now return a one paragraph insights from this data. Add a heading/title in the first line. The heading should explain the paragraph, should not be generic. For instance, a title like `AAPL's next support is at 138' is better than 'AAPL's support levels'
        No prefix, suffix, starting with `here is`, etc. Start directly with insights. Use numbers and statistics where you can.
        """

        response = generate_llm_response(prompt, model = "gpt-4o", temperature = 0.2)
        return response
    

    def code(self):
        """
        Generate a Python code snippet for financial analysis.
        Returns:
            str: A Python code snippet for analyzing financial data.
        """

        agent_type = random.choice(CODING_AGENT_TYPES)
        plan_prompt = f"""
            You are a quantitative programmer working at a big hedge fund. Your job is to build insights as an ```{agent_type}```. It is important that you act like this analyst. You are given a list of functions that you can directly call without implementing them to write your code. Your job comes where you have to then call any given function, and then build statistics on top of that, and then print them in your code.

            The stock we are analyzing today is: {self.ticker} [as part of this, sometimes you can also just skip the stock related functions and focus on economics data]

            ##############
            These functions are readily available to you and you can just call them directly as Downloader().function_name_goes_here. We are basically providing you all the APIs you will need to retrieve data, so that you can focus more on the actual quant analysis. Do not implement them, remember they are already implemented, you just have to call them. Remember to import downloader as from downloader import Downloader.

            ```
            {str(FUNCTION_MAPPINGS)}
            ```

            Carefully look at the `output_schema` in the function mappings, and make sure you are calling the right functions and expecting the right output. Dont confuse strings with jsons and jsons with strings, and floats and whatever. You must look at the output_schema type to avoid bugs.
            ##############

            You can use any library you want for statistical analysis. Try to avoid using pandas since you make a lot of mistakes with it. Now write code that will give us some insights into the data. Insights can be simple such as net selling vs buying, or they could be complex such as statistical analysis, correlations, etc. All are good.

            Make sure to print your results. Do not make charts, just stick with textual outputs.
            
            Stick with any single topic only for your analysis. You must only return python code. No prefix or suffix text. Do not start with ```, or python, just write code.  
            
            In the first line, write how your analysis is specific to being an {agent_type} (in a commnet). At the end of your code, write in comments on how to best use the data to find insights, i.e what to do if any of the data values are high, low, how to then use the data to build analyst reports, such as those published in Goldman sachs, JP Morgan, and other big funds.

            DO NOT ASSUME ANYTHING, YOU ARE AN EXPERT. MAKE SURE YOU KNOW WHAT YOU ARE DOING. ADD CHECKS FOR THINGS LIKE DIVISION, TYPES, KEY CHECKS, NULL CHECKS ETC.
        """

        response = generate_llm_response(plan_prompt, model = "gpt-4o", temperature = 0.2)
        response = response.replace("```python", "")
        response = response.replace("```", "")
        return response


    def run(self):
        """
        Execute the main workflow of the CodingAgent.
        This method generates multiple statistical insights by creating code plans,
        running the code, and extracting insights from the results.
        Returns:
            list: A list of insights generated from the statistical analysis.
        """
        insights = []
        logger.info(f"[Task] Running CODING Agent to extract statistical insights for {self.ticker}")
        logger.info(f"[Coding...]")
        for _ in tqdm(range(FINANCIAL_STATISTICAL_INSIGHTS), desc="Coding & extracting statistical insights", unit="insight"):
            code_plan = self.code()
            analysis = run_code(code_plan)
            if analysis is None or analysis == "":
                continue

            insight = self.insights(plan = code_plan, result = analysis)
            insights.append(insight)

        logger.info(f"[Task] Success, Extracted {len(insights)} statistical insights for {self.ticker}")
        return insights
        
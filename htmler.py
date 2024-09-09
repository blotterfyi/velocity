import os
import pytz
import json
import argparse
import webbrowser
from logger import get_logger

logger = get_logger(__name__)
class HTMLer:   
    def __init__(self, ticker):
        self.ticker = ticker

    def calculate_percentage_difference(self, old, new):
        return (((new - old) / old) * 100)

    def to_html(self):
        """
        Generate an HTML report for the given ticker using data from a JSON file.
        This method reads data from a JSON file, processes it, and creates an HTML report
        using a template. The report includes various financial metrics and visualizations.
        The resulting HTML file is saved in the output directory.
        """
        if os.path.exists(f'output/{self.ticker}.json'):
            with open(f'output/{self.ticker}.json', 'r') as f:
                data = json.load(f)
                html_template = open("html/template.html", "r").read()

                # calculate overweight, equal-weight, underweight
                overweight = len([item for item in data["price_target"] if self.calculate_percentage_difference(data["current_price"], item) > 10]) / len(data["price_target"])
                underweight = len([item for item in data["price_target"] if self.calculate_percentage_difference(data["current_price"], item) < -10]) / len(data["price_target"])
                equal_weight = len([item for item in data["price_target"] if self.calculate_percentage_difference(data["current_price"], item) > -10 and self.calculate_percentage_difference(data["current_price"], item) < 10]) / len(data["price_target"])
                overweight = overweight * 100
                underweight = underweight * 100
                equal_weight = equal_weight * 100
                
                # replace overweight, equal_weight, underweight with data
                html_template = html_template.replace("{{overweight}}", str(overweight))
                html_template = html_template.replace("{{equal_weight}}", str(equal_weight))
                html_template = html_template.replace("{{underweight}}", str(underweight))
                
                # replace with data
                data["heading"] = data["heading"].strip('"')
                html_template = html_template.replace("{{ticker}}", data["ticker"])
                html_template = html_template.replace("{{heading}}", data["heading"])
                html_template = html_template.replace("{{heading_case}}", data["heading_case"])
                html_template = html_template.replace("{{analyst_rating}}", data["thesis"]["analyst_rating"])
                html_template = html_template.replace("{{thesis_one}}", data["thesis"]["thesis"][0])
                html_template = html_template.replace("{{thesis_two}}", data["thesis"]["thesis"][1])
                html_template = html_template.replace("{{thesis_three}}", data["thesis"]["thesis"][2])
                html_template = html_template.replace("{{bull_price_target}}", data["bull_case"]["price_target"])
                html_template = html_template.replace("{{base_price_target}}", data["base_case"]["price_target"])
                html_template = html_template.replace("{{bear_price_target}}", data["bear_case"]["price_target"])
                html_template = html_template.replace("{{bull_thesis}}", data["bull_case"]["thesis"])
                html_template = html_template.replace("{{base_thesis}}", data["base_case"]["thesis"])
                html_template = html_template.replace("{{bear_thesis}}", data["bear_case"]["thesis"])
                html_template = html_template.replace("{{theme_1}}", list(data["risk_reward_themes"][0].keys())[0])
                html_template = html_template.replace("{{theme_1_sentiment}}", list(data["risk_reward_themes"][0].values())[0].title())
                html_template = html_template.replace("{{theme_2}}", list(data["risk_reward_themes"][1].keys())[0])
                html_template = html_template.replace("{{theme_2_sentiment}}", list(data["risk_reward_themes"][1].values())[0].title())
                html_template = html_template.replace("{{theme_3}}", list(data["risk_reward_themes"][2].keys())[0])
                html_template = html_template.replace("{{theme_3_sentiment}}", list(data["risk_reward_themes"][2].values())[0].title())

                targets = data["price_target"] # its a list
                low_target = min(targets)
                mean_target = sum(targets) / len(targets)
                high_target = max(targets)

                html_template = html_template.replace("{{low_target_raw}}", str(low_target))
                html_template = html_template.replace("{{high_target_raw}}", str(high_target))

                low_target= min(low_target, data["current_price"])
                high_target = max(high_target, data["current_price"])
                html_template = html_template.replace("{{low_target}}", str(low_target))
                html_template = html_template.replace("{{mean_target}}", str(mean_target))
                html_template = html_template.replace("{{high_target}}", str(high_target))

                # chart
                html_template = html_template.replace("{{chart}}", json.dumps(data["chart"]))
                radar = data["radar"]
                html_template = html_template.replace("{{radar}}", json.dumps(radar))

                # current_price
                html_template = html_template.replace("{{current_price}}", str(data["current_price"]))
                
                # save this html in output/ticker.html
                with open(f'output/{self.ticker}.html', 'w') as f:
                    f.write(html_template)
                
                webbrowser.open('file://' + os.path.realpath(f'output/{self.ticker}.html'))
                logger.info(f'HTML file for {self.ticker} created. Open it up in a browser to see the risk reward report')
        else:
            logger.error(f'No data found for {self.ticker}')
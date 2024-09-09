import os
SEC_INSIGHTS = 10 # how many insights to extract from SEC data
FINANCIAL_STATISTICAL_INSIGHTS = 10 # how many statistical insights to extract from data
NEWS_INSIGHTS = 10 # how many insights to extract from news data
EARNINGS_TRANSCRIPT_INSIGHTS = 10 # how many insights to extract from earnings transcript data
CODING_AGENT_TYPES = [
    "Monte Carlo Price Estimator",
    "Monte Carlo Earnings Estimator",
    "MACD Crossover Detector",
    "Insider Sentiment Evaluator",
    "Institutional Ownership Trend Spotter",
    "Earnings Surprise Predictor",
    "Analyst Target Price Consensus Tracker",
    "Peer Performance Comparator",
    "Value vs Growth Classifier",
    "Dividend Stability Assessor",
    "Volume Trend Analyzer",
    "Price Support/Resistance Identifier",
    "Macroeconomic Sensitivity Estimator",
    "Management Effectiveness Scorer",
    "Sector Rotation Alignment Checker",
    "Short Interest Trend Analyzer",
    "Option Volume Unusual Activity Detector",
    "Technical Breakout Pattern Recognizer",
    "Fundamental-Technical Divergence Spotter",
    "Insider-Analyst Sentiment Aligner",
    "Price Momentum Strength Evaluator",
    "Volatility Analyst",
    "Correlation Expert Analyst",
    "Historical Earings Analyst",
    "Economics Analyst",
    "Employment Analyst",
    "Macro Analyst",
    "Industry Peers Analyst",
    "Technical Analyst",
    "Growth Analyst",
    "Risk Analyst",
    "PhD in Financial Statistics Analyst",
    "S&P Performance Comparison Analyst"
]

NEWS_ANALYST_TYPES = [
    "Sentiment Trend Analyzer",
    "Keyword Frequency Tracker",
    "Comparative Analyst",
    "Crisis Detection Specialist",
    "Product Launch Impact Assessor",
    "Management Change Evaluator",
    "Regulatory Impact Predictor",
    "Supply Chain Disruption Detector",
    "Merger and Acquisition Rumor Tracker",
    "Competitive Landscape Mapper",
    "Innovation Pipeline Monitor",
    "Environmental, Social, Governance (ESG) Scorer",
    "Market Expansion Opportunity Identifier",
    "Legal Risk Assessor",
    "Brand Perception Tracker",
    "Industry Trend Correlator",
    "Executive Statement Analyzer",
    "Financial Performance Expectation Setter",
    "Social Media Buzz Quantifier",
    "Geopolitical Risk Evaluator"
]

FUNCTION_MAPPINGS = {
    "get_company_information": {
        "description": "Get the company information for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A json with keys 'symbol', 'price', 'beta', 'volAvg', 'mktCap', 'lastDiv', 'range', 'changes', 'companyName'"
        }
    },
    "get_gdp_growth_rate": {
        "description": "Get the GDP growth rate for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the GDP rate. List contains the GDP data for the last 12 quarters"
        }
    },
    "get_unemployment_rate": {
        "description": "Get the unemployment rate for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the unemployment rate. List contains the unemployment rate data for the last 12 months"
        }
    },
    "get_inflation_rate": {
        "description": "Get the inflation rate for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the inflation rate. List contains the inflation rate data for the last 10 years"
        }
    },
    "get_retail_sales": {
        "description": "Get the retail sales for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the retail sales. List contains the retail sales data for the last 36 months"
        }
    },
    "get_total_vehical_sales": {
        "description": "Get the total vehicle sales for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the total vehicle sales. List contains the total vehicle sales data for the last 36 months"
        }
    },
    "get_mortgage_rates": {
        "description": "Get the mortgage rates for US.",
        "parameters": {
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date` and `value`. Date is in the format of `YYYY-MM-DD` and value is the mortgage rates. List contains the mortgage rates data for the last 24 months"
        }
    },
    "get_current_ticker_price": {
        "description": "Get the current price for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "float",
            "description": "The current price of the ticker"
        }
    },
    "get_price_chart_historical": {
        "description": "Get the historical price chart for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date`, `open`, `high`, `low`, `close`, `volume`. Date is in the format of `YYYY-MM-DD` and other fields are the price and volume in float. List contains the price data for the last 252 days"
        }
    },
    "get_analyst_price_targets": {
        "description": "Get the analyst price targets for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `symbol`, `analystName`, `publishedDate`, `priceTarget`, `priceWhenPosted`, `analystCompany`"
        }
    },
    "get_pe_ratio": {
        "description": "Get the PE ratio for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "float",
            "description": "The PE ratio of the ticker"
        }
    },
    "get_market_cap": {
        "description": "Get the market cap for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "float",
            "description": "The market cap of the ticker"
        }
    },
    "get_eps": {
        "description": "Get the earnings per share for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "float",
            "description": "The earnings per share of the ticker"
        }
    },
    "get_insider_trades": {
        "description": "Get the insider trades for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `transactionDate`, `symbol`, `transactionType`, `securitiesTransacted`, `price`, `typeOfOwner`, `reportingName`. Transaction type can be 'P-Purchase' or 'S-Sale', or any other value should be ignored. securitiesTransacted is the number of shares transacted, and price is at which price."
        }
    },
    "get_institutional_ownership": {
        "description": "Get the institutional ownership for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `holder`, `shares`, `dateReported`, `change`. Holder is the name of the fund, shares is the number of shares, dateReported is the date when the report was filed, and change is the change in shares from the previous quarter."
        }
    },
    "get_stock_peers": {
        "description": "Get the stock peers for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of tickers like ['AAPL', 'QQQ']"
        }
    },
    "get_historical_earnings": {
        "description": "Get the historical earnings for the given ticker.",
        "parameters": {
            "ticker": {
                "type": "string",
                "description": "The ticker of the company"
            }
        },
        "output_schema": {
            "type": "json",
            "description": "A list of jsons with keys `date`, `eps`, `epsEstimated`, `revenue`, `revenueEstimated`. List contains the last 16 quarters data"
        }
    },
}

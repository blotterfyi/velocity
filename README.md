<p align="center">
    <img src="https://blotter.fyi/static/assets/images/nvda-report.png" width="800" alt="Velocity sample report for Apple">
</p>

------

<p align="center">
  <img src="https://blotter.fyi/static/assets/images/velocity-logo.png" alt="Velocity Logo" width="300">
</p>

**Velocity** is a financial analysis tool built by [Blotter](https://blotter.fyi) that performs rapid analysis for a given stock ticker by aggregating insights from various sources such as SEC filings, news, earnings reports, and institutional data. It uses AI to mine large amounts of data in minutes, which would otherwise take a human hours. Our goal is to eventually build AI analysts, on par with top analysts on wall street.

## How does it work?

Velocity leverages Large Language Models (LLMs) to extract valuable insights from vast amounts of financial data. The tool is built around the concept of **agents**, each designed to focus on a specific type of financial data. These agents work in unison to gather and process information from multiple sources, creating a comprehensive view of a stock's performance.

### Insights

The core of Velocity is the **insight-gathering process**. Insights are extracted from various sources, including:

- **SEC filings**: Analyzed by the `SECAgent`, providing insights into legal and compliance information about the company.
- **News**: Handled by the `NewsAgent`, extracting relevant financial news affecting the stock.
- **Earnings Reports**: Analyzed by the `EarningsAgent` to gain insights from the company's quarterly and yearly reports.
- **Code Analysis**: `CodingAgent` performs automated code-based analysis to extract patterns from data.

The gathered insights are passed through the LLMs for self-reflection and interpretation, generating outputs such as price targets, bull/bear cases, and risk/reward assessments.

### Agents

Velocity's modular architecture allows for multiple agents, each responsible for a specific aspect of financial data:

- `SECAgent`: Processes and extracts insights from SEC filings.
- `NewsAgent`: Extracts key news affecting the stock.
- `EarningsAgent`: Analyzes earnings reports to extract important metrics.
- `CodingAgent`: Automates coding-based data extraction.
- `Analyst`: Performs the overall analysis and synthesizes the final report, including risk themes and stock price targets.

All the collected insights are then combined into a cohesive output, saved in JSON and HTML formats for further review.

## Usage

Velocity can be run from the command line, taking in several parameters to configure its behavior.

### Command-line Arguments

- `--ticker`: **(Required)** Stock ticker symbol for the company you want to analyze. Example: `AAPL` for Apple Inc.
  
- `--openai_key`: **(Required)** Your OpenAI API key for enabling the use of LLMs. If not provided via the argument, it can be set as an environment variable `OPENAI_API_KEY`.

- `--fmp_key`: **(Required)** Financial Modeling Prep (FMP) API key, used for fetching financial data. Similar to the OpenAI key, it can also be set as an environment variable `FMP_API_KEY`.

### Configuration

A `config.py` file is used to store configurations related to different agent types. This file allows you to:

- Customize the **types of agents** being used.
- Set **cache expiration** times for insights.
- Manage **data sources** for each agent.

By editing `config.py`, you can fine-tune the behavior of the agents and adjust the overall analysis flow.

### Example Usage

```bash
python3.9 velocity.py --ticker AAPL --openai_key <YOUR_OPENAI_API_KEY> --fmp_key <YOUR_FMP_API_KEY>
```

**Note:** It only works with python3.9 right now. Make sure that is available on your system and can be accessed by python3.9

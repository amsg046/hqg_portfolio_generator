# High Quality Growth Portfolio Generator : Project Overview
* Created a tool that determines a score for stocks based on various growth and value metrics
* Scraped data for all stocks in the S&P 500 from morningstar, including key ratios and revenue & earnings growth
* Calculated growth and value scores by tracking metric percentiles for each feature from the scraped data

## Code and Resources Used
**Python Version:** 3.7.4 <br />
**Packages:** bs4, json, numpy, pandas, requests, scipy, statistics <br />
**Inspiration:** https://github.com/nickmccullum/algorithmic-trading-python/blob/master/finished_files/003_quantitative_value_strategy.ipynb

## Web Scraping
Wrote several functions that took get requests and ticker symbol as inputs, and retrieved / parsed the following for each stock:

**Value Metrics:**
* Price-to-Earnings (P/E Ratio)
* Price-to-Book (P/B Ratio)
* Price-to-Sales (P/S Ratio)
* Debt-to-Equity (D/E Ratio)

**Growth Metrics:**
* % Change Revenue (1-Yr)
* % Change Revenue (3-Yr)
* % Change EBITDA (1-Yr)
* % Change EBITDA (3-Yr)

## Data Cleaning
After scraping the data, the following steps were taken before using the data to perform the necessary analysis

* Ensured that both values were positive for revenue / ebitda change in any given instance, when this wasn't the case np.NaN was used instead as a default null value
* Incorporated error handling that defaulted to appending np.NaN values to the dataframe as well
* Filled in missing data (np.NaN) with the mean value across all stocks for any given feature

## Result Criteria

**Value Score:** <br />
The value score is calculated by taking the average of the value metrics

**Growth Score:** <br />
The growth score is calculated by taking the average of the growth metrics

**Total Score:** <br />
The total score is calculated as follows: <br /> <br />
*Total Score = ( Value<sub>weight</sub> * Value Score ) + ( Growth<sub>weight</sub> * Growth Score )* <br /> <br />
where: <br /> <br /> 
*Value<sub>weight</sub> + Growth<sub>weight</sub> = 1*

## Potential Use Cases / Limitations

**Here are a few limitations that must be considered when using this tool:**
* The 1-year and 3-year metrics that are scraped are from the period ending in June, and thus can trail other scraped data
* Since percentage increase is used in certain metrics, small numbers can have a disproportionate impact on the score
* This tool only looks at certain metrics and does not capture the fundamentals of the underlying asset / analyze the strategy or quality of management

**Potential Use Cases:**
* Portfolio Evaluation
* Stock Discovery (For example: can be used on Russell 3000 index instead of S&P 500 to determine which stocks to analyze further when dealing with a large number of stocks)



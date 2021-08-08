# -*- coding: utf-8 -*-
"""
Created on Sat Aug 7 17:57:00 2021

@author: Amar Singh
"""

import pandas as pd

from scipy import stats
from statistics import mean

# Import Scraped Data into DataFrame (S&P 500)
df = pd.read_csv('scraped_data.csv')

# Fill in missing values
for column in ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'D/E Ratio', '% Change in Revenue (1-Year)', '% Change in Revenue (3-Year)', '% Change in EBITDA (1-Year)', '% Change in EBITDA (3-Year)']:
    df[column].fillna(df[column].mean(), inplace = True)

### Calculate Scoring Criteria
# Calculate percentile values

from scipy.stats import percentileofscore as score
value_metrics = {
    'P/E Ratio' : 'P/E Percentile',
    'P/B Ratio' : 'P/B Percentile',
    'P/S Ratio' : 'P/S Percentile',
    'D/E Ratio' : 'D/E Percentile'
}

growth_metrics = {
    '% Change in Revenue (1-Year)' : '1 Year Revenue Change Percentile',
    '% Change in Revenue (3-Year)' : '3 Year Revenue Change Percentile',
    '% Change in EBITDA (1-Year)' : '1 Year EBITDA Change Percentile',
    '% Change in EBITDA (3-Year)' : '3 Year EBITDA Change Percentile'
}

for metric in value_metrics.keys():
    for row in df.index:
        df.loc[row, value_metrics[metric]] = 100 - score( df[metric], df.loc[row, metric])
for metric in growth_metrics.keys():
    for row in df.index:
        df.loc[row, growth_metrics[metric]] = score( df[metric], df.loc[row, metric])

# Specify weight of value & growth criteria (value_weight & growth_weight should add to 1.o to keep 100.0 scale for total score)
value_weight = .20
growth_weight = .80

# Calculate Value, Growth, & Total Scores
for row in df.index:
    value_percentiles = []
    growth_percentiles = []
    for metric in value_metrics.keys():
        value_percentiles.append(df.loc[row, value_metrics[metric]])
    for metric in growth_metrics.keys():
        growth_percentiles.append(df.loc[row, growth_metrics[metric]])
    df.loc[row, 'Value Score'] = mean(value_percentiles)
    df.loc[row, 'Growth Score'] = mean(growth_percentiles)
    df.loc[row, 'Total Score'] = (value_weight * df.loc[row, 'Value Score']) + (growth_weight * df.loc[row, 'Growth Score'])

### Results
# Sort by total score, extract top 50 stocks

df.sort_values('Total Score', ascending=False, inplace = True)
final_df = df[:50]
final_df

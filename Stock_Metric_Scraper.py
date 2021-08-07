# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 16:32:25 2021

@author: Amar Singh
"""

import json
import numpy as np
import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from scipy import stats
from statistics import mean

# Import List of Candidate Stocks (S&P 500)
stocks = pd.read_csv('sp_500_stocks.csv')


# ### Define Data Scraping Functions / Helper Functions

# Create a function that determines the correct URL for a given ticker symbol and then generates the corresponding get request

def get_val_request(symbol):
    url_value_NYS = f'http://financials.morningstar.com/valuate/valuation-history.action?&t=XNYS:{symbol}&region=usa&culture=en-US&cur=&type=price-earnings&'
    url_value_NAS = f'http://financials.morningstar.com/valuate/valuation-history.action?&t=XNAS:{symbol}&region=usa&culture=en-US&cur=&type=price-earnings&'
    r_NYS = requests.get(url_value_NYS)
    r_NAS = requests.get(url_value_NAS)
    r = (r_NYS if r_NYS.text else r_NAS)

    return r

def get_deb_request(symbol):
    url_NYS = f'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=jsonp1626044235897&t=XNYS:{symbol}&region=usa&culture=en-US&cur=&order=asc&_=1626044237707'
    url_NAS = f'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=jsonp1626044235897&t=XNAS:{symbol}&region=usa&culture=en-US&cur=&order=asc&_=1626044237707'
    r_NYS = requests.get(url_NYS)
    r_NAS = requests.get(url_NAS)
    r = (r_NYS if r_NYS.text else r_NAS)

    return r

def get_growth_request(symbol):
    url_NYS = f'http://financials.morningstar.com/ajax/ReportProcess4HtmlAjax.html?&t=XNYS:{symbol}&region=usa&culture=en-US&cur=&reportType=is&period=12&dataType=A&order=asc&columnYear=5&curYearPart=1st5year&rounding=3&view=raw&r=783414&callback=jsonp1626764458821&_=1626764460992'
    url_NAS = f'http://financials.morningstar.com/ajax/ReportProcess4HtmlAjax.html?&t=XNAS:{symbol}&region=usa&culture=en-US&cur=&reportType=is&period=12&dataType=A&order=asc&columnYear=5&curYearPart=1st5year&rounding=3&view=raw&r=783414&callback=jsonp1626764458821&_=1626764460992'
    r_NYS = requests.get(url_NYS)
    r_NAS = requests.get(url_NAS)
    r = (r_NYS if r_NYS.text else r_NAS)

    return r

# Function that takes a ticker symbol, get_request, and the ratio type as arguments, and returns the current ratio value
def current_value_ratio(symbol, request, ratio_type):
    data_list = []
    ratio_text_dict = {'pe' : 'Price/Earnings', 'pb' : 'Price/Book', 'ps' : 'Price/Sales'}
    ratio_text = ratio_text_dict[ratio_type]
    soup = BeautifulSoup(request.text, "lxml")
    line = soup.find('th', {'abbr' : f'{ratio_text} for {symbol}'})

    try:
        while line.next_sibling.next_sibling != None:
            line = line.next_sibling.next_sibling
            try:
                data_list.append(float(line(text=True)[0]))
            except ValueError:
                data_list.append(np.NaN)
    except AttributeError:
        data_list.append(np.NaN)

    return data_list[-1]

# Function that takes ticker symbol and get request as arguments, and returns current debt / equity ratio
def current_debteq_ratio(symbol, request):
    data_list = []
    r = request.text.encode("utf-8").decode("unicode-escape")
    soup = BeautifulSoup(r, "lxml")
    line = soup.find('th', {'id' : 'i68'})

    try:
        while line.next_sibling != None:
            line = line.next_sibling
            try:
                data_list.append(float(line(text=True)[0]))
            except ValueError:
                data_list.append(np.NaN)
    except AttributeError:
        data_list.append(np.NaN)

    return data_list[-1]

# Function that takes ticker symbol and get request as arguments, and returns a list of growth parameters
def growth_list(symbol, request):
    r = request.text.encode("utf-8").decode("unicode-escape")

    soup = BeautifulSoup(r, "lxml")
    line = soup.find('div', {'id' : 'data_i30'})
    data = line.get_text('\t')
    growth_list_1 = data.split('\t')

    line = soup.find('div', {'id' : 'label_i86'})
    data = line.get_text('\t')
    growth_list_2 = data.split('\t')

    data_list = [growth_list_1, growth_list_2]

    return data_list

# Function that converts data from source format to int ( ex. input: '(1,234)' -> output: -1234 )
def data_to_int(data):
    for ind, symbol in enumerate(['(', ',', ')']):
        replacement = ['-', '', '']
        data = data.replace(symbol, replacement[ind])
    data = int(data)
    return data


# ### Build Dataframe

df_columns = ['Ticker', 'P/E Ratio', 'P/E Percentile', 'P/B Ratio', 'P/B Percentile', 'P/S Ratio',
              'P/S Percentile', 'D/E Ratio', 'D/E Percentile', '% Change in Revenue (1-Year)',
              '1 Year Revenue Change Percentile', '% Change in Revenue (3-Year)', '3 Year Revenue Change Percentile',
              '% Change in EBITDA (1-Year)', '1 Year EBITDA Change Percentile', '% Change in EBITDA (3-Year)',
              '3 Year EBITDA Change Percentile', 'Value Score', 'Growth Score', 'Total Score']
df = pd.DataFrame(columns=df_columns)

for symbol in stocks['Ticker']:
    EF_1 = EF_2 = 0
    r_val = get_val_request(symbol)
    pe_ratio = current_value_ratio(symbol, r_val, 'pe')
    pb_ratio = current_value_ratio(symbol, r_val, 'pb')
    ps_ratio = current_value_ratio(symbol, r_val, 'ps')

    r_deb = get_deb_request(symbol)
    de_ratio = current_debteq_ratio(symbol, r_deb)

    r_growth = get_growth_request(symbol)

    try:
        data_list_2 = growth_list(symbol, r_growth)[1]

        RE_CY = (data_to_int(data_list_2[13]) if data_list_2[13] != '—' else np.NaN)
        RE_1Y = (data_to_int(data_list_2[12]) if data_list_2[12] != '—' else np.NaN)
        RE_3Y = (data_to_int(data_list_2[10]) if data_list_2[10] != '—' else np.NaN)
    except AttributeError:
        EF_1 = 1    # Set Error Flag
    try:
        data_list = growth_list(symbol, r_growth)[0]

        EB_CY = (data_to_int(data_list[160]) if data_list[160] != '—' else np.NaN)
        EB_1Y = (data_to_int(data_list[159]) if data_list[159] != '—' else np.NaN)
        EB_3Y = (data_to_int(data_list[157]) if data_list[157] != '—' else np.NaN)
    except AttributeError:
        EF_2 = 1    # Set Error Flag

    RE_1Y_CH = ((((RE_CY - RE_1Y) / RE_1Y) * 100) if (RE_CY > 0 and RE_1Y > 0 and EF_1 == 0) else np.NaN)
    RE_3Y_CH = ((((RE_CY - RE_3Y) / RE_3Y) * 100) if (RE_CY > 0 and RE_3Y > 0 and EF_1 == 0) else np.NaN)

    EB_1Y_CH = ((((EB_CY - EB_1Y) / EB_1Y) * 100) if (EB_CY > 0 and EB_1Y > 0 and EF_2 == 0) else np.NaN)
    EB_3Y_CH = ((((EB_CY - EB_3Y) / EB_3Y) * 100) if (EB_CY > 0 and EB_3Y > 0 and EF_2 == 0) else np.NaN)

    df = df.append(
            pd.Series(
                [
                    symbol,
                    pe_ratio,
                    'N/A',
                    pb_ratio,
                    'N/A',
                    ps_ratio,
                    'N/A',
                    de_ratio,
                    'N/A',
                    RE_1Y_CH,
                    'N/A',
                    RE_3Y_CH,
                    'N/A',
                    EB_1Y_CH,
                    'N/A',
                    EB_3Y_CH,
                    'N/A',
                    'N/A',
                    'N/A',
                    'N/A'
                ],
                index = df_columns
            ),
            ignore_index = True
        )
    
    
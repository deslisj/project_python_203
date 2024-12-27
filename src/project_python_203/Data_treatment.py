import yfinance as yf
import pandas as pd 
from sec_cik_mapper import StockMapper
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging 
from scipy.optimize import minimize
import numpy as np

import matplotlib.pyplot as plt

import pybacktestchain
from pybacktestchain import data_module
from pybacktestchain.data_module import DataModule

@dataclass
class Data_treatment:
    data: pd.DataFrame

    def compute_moving_average(self, short_window=5, long_window=20):
            """
            Computes short-term and long-term moving averages for each ticker.

            Parameters:
                short_window (int): Window size for short-term moving average.
                long_window (int): Window size for long-term moving average.

            Returns:
                pd.DataFrame: Original DataFrame with two new columns ['Short_MA', 'Long_MA'].
            """
            # Ensure the data is sorted by 'ticker' and 'Date'
            self.data = self.data.sort_values(by=['ticker', 'Date'])

            # Group by 'ticker' and apply rolling window to compute moving averages
            self.data['Short_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.rolling(window=short_window, min_periods=1).mean()
            )
            
            self.data['Long_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.rolling(window=long_window, min_periods=1).mean()
            )

            return self.data




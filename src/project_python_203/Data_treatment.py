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

    def compute_moving_average(self, short_window=50, long_window=200, short_type='simple', long_type='simple'):
        """
        Computes short-term and long-term moving averages for each ticker.

        Parameters:
            short_window (int): Window size for short-term moving average.
            long_window (int): Window size for long-term moving average.
            short_type (str): Type of short-term moving average ('simple' or 'exponential').
            long_type (str): Type of long-term moving average ('simple' or 'exponential').

        Returns:
            pd.DataFrame: a new DataFrame with two new columns ['Short_MA', 'Long_MA'].
        """

        # we check that the data is sorted by 'ticker' and 'Date'
        self.data = self.data.sort_values(by=['ticker', 'Date'])

        # Compute short-term moving average
        if short_type == 'simple':
            # we group by 'ticker' and apply rolling window to compute moving averages
            self.data['Short_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.rolling(window=short_window).mean() # if we don't want Nan, put : ,min_periods=1 
            )
        elif short_type == 'exponential':
            # we group by 'ticker' and apply exponential weighted moving to compute moving averages
            self.data['Short_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.ewm(span=short_window, adjust=False).mean() # if we don't want Nan, put : ,min_periods=1 
            )
        else:
            raise ValueError("Invalid short_type. Choose 'simple' or 'exponential'.")

        # Compute long-term moving average
        if long_type == 'simple':
            # we group by 'ticker' and apply rolling window to compute moving averages
            self.data['Long_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.rolling(window=long_window).mean() # if we don't want Nan, put : ,min_periods=1 
            )
        elif long_type == 'exponential':
            # we group by 'ticker' and apply exponential weighted moving to compute moving averages
            self.data['Long_MA'] = self.data.groupby('ticker')['Adj Close'].transform(
                lambda x: x.ewm(span=long_window, adjust=False).mean() # if we don't want Nan, put : ,min_periods=1 
            )
        else:
            raise ValueError("Invalid long_type. Choose 'simple' or 'exponential'.")
        
        # we return the new DataFrame with selected columns (keep only relevant columns)
        return self.data[['Date', 'Adj Close', 'Volume', 'ticker', 'Short_MA', 'Long_MA']]

    def plot_moving_average(self, ticker):
        """
        Plots the adjusted close prices and moving averages for a specific ticker.

        Parameters:
            ticker (str): The ticker symbol to filter and plot.

        Returns:
            None: Displays the plot.
        """
        # we filter the data for the selected ticker
        ticker_data = self.data[self.data['ticker'] == ticker]

        # we plot the adjusted close prices and moving averages
        plt.figure(figsize=(12, 6))
        plt.plot(ticker_data['Date'], ticker_data['Adj Close'], label='Adj Close', linewidth=1)
        plt.plot(ticker_data['Date'], ticker_data['Short_MA'], label='Short-Term MA', linewidth=1)
        plt.plot(ticker_data['Date'], ticker_data['Long_MA'], label='Long-Term MA', linewidth=1)

        # Add labels, legend, and title
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Moving Averages for {ticker}')
        plt.legend()
        plt.grid(True)
        plt.show()

@dataclass
class TradingStrategy:
    data_MA: pd.DataFrame # data with moving averages computed with the Data_treatment class

    def compute_trading_signals(self):
        """
        Computes trading signals based on short-term and long-term moving averages.

        Returns:
            pd.DataFrame: DataFrame with additional 'Signal' and 'Position' columns.
        """
        # we compute the Signal column
        self.data_MA['Signal'] = 0
        self.data_MA['Signal'] = (self.data_MA['Short_MA'] > self.data_MA['Long_MA']).astype(int)

        # we compute the Position column within each ticker group
        self.data_MA['Position'] = self.data_MA.groupby('ticker')['Signal'].diff()

        # Drop rows where 'Position' is NaN (delete the observation for each ticker)
        self.data_MA = self.data_MA.dropna(subset=['Position']).reset_index(drop=True)

        return self.data_MA

    def plot_trading_signals(self, ticker):
        """
        Plots the trading signals on the price and moving average chart for a specific ticker.

        Parameters:
            ticker (str): The ticker symbol to filter and plot.

        Returns:
            None: Displays the plot.
        """
        # Filter data for the selected ticker
        ticker_data = self.data_MA[self.data_MA['ticker'] == ticker]

        # Plot adjusted close prices and moving averages
        plt.figure(figsize=(12, 6))
        plt.plot(ticker_data['Date'], ticker_data['Adj Close'], label='Adj Close', linewidth=1)
        plt.plot(ticker_data['Date'], ticker_data['Short_MA'], label='Short-Term MA', linewidth=1)
        plt.plot(ticker_data['Date'], ticker_data['Long_MA'], label='Long-Term MA', linewidth=1)

        # Plot buy and sell signals
        buy_signals = ticker_data[ticker_data['Position'] == 1]
        sell_signals = ticker_data[ticker_data['Position'] == -1]

        plt.scatter(buy_signals['Date'], buy_signals['Adj Close'], label='Buy Signal', marker='^', color='green', s=100)
        plt.scatter(sell_signals['Date'], sell_signals['Adj Close'], label='Sell Signal', marker='v', color='red', s=100)

        # Add labels, legend, and title
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Trading Signals for {ticker}')
        plt.legend()
        plt.grid(True)
        plt.show() 


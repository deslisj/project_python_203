import yfinance as yf
import pandas as pd 
from sec_cik_mapper import StockMapper
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging 
from scipy.optimize import minimize
import numpy as np
import os

import matplotlib.pyplot as plt

import pybacktestchain
from pybacktestchain import data_module, broker
from pybacktestchain.data_module import *
from pybacktestchain.broker import *
from project_python_203.Data_treatment import *
from pybacktestchain.broker import Broker
from pybacktestchain.utils import generate_random_name

@dataclass
class Trades:
    strategy: TradingStrategy
    broker: Broker
    max_allocation: float = 0.2 # we set the maximum allocation per asset as a percentage of the portfolio value

    def execute_trades(self, data_MA: pd.DataFrame):
        """
        Execute trades based on the strategy's signals for all dates in the data.

        Parameters:
            data_MA (pd.DataFrame): The DataFrame containing market data and signals.

        Returns:
            pd.DataFrame: A DataFrame of executed trades for all dates. (it is the transaction_log)
        """

        # Ensure the 'Position' column exists
        if 'Position' not in data_MA.columns:
            raise KeyError("The 'Position' column is missing from the data. Ensure trading signals are computed beforehand.")

        # initialize the portfolio value
        portfolio_values = []

        for date in sorted(data_MA['Date'].unique()):
            # we need to have the market value for each date and for each asset
            filtered_data_for_date = data_MA[data_MA['Date'] == date] # we filter the data for the selected date
            # we then transform the data into a dictionary with the ticker as key and the adjusted close price as value
            market_val = dict(zip(filtered_data_for_date['ticker'], filtered_data_for_date['Adj Close']))
            # we get the portfolio value for the selected date
            portfolio_value = self.broker.get_portfolio_value(market_prices=market_val)
            
            """ to delete
            print("date", date, "portolio value", portfolio_value)
            """

            for ticker in data_MA['ticker'].unique():
                ticker_data = data_MA[data_MA['ticker'] == ticker]
                if ticker_data.empty:
                    continue

                latest_data = ticker_data[ticker_data['Date'] == date]
                if latest_data.empty:
                    continue

                latest_data = latest_data.iloc[0]
                signal = latest_data['Position']
                price = latest_data['Adj Close']

                # Calculate maximum position size based on allocation constraint
                max_position_value = portfolio_value * self.max_allocation
                max_quantity = int(max_position_value / price)

                if signal == 1:  # Buy signal
                    available_cash = self.broker.get_cash_balance()
                    quantity = min(max_quantity, int(available_cash / price))
                    if quantity > 0:
                        self.broker.buy(ticker, quantity, price, date)

                elif signal == -1:  # Sell signal
                    if ticker in self.broker.positions:
                        quantity = self.broker.positions[ticker].quantity
                        self.broker.sell(ticker, quantity, price, date)
            
            portfolio_values.append({'Date': date, 'Portfolio Value': portfolio_value})

            #print("date", date,"positions : ", self.broker.positions,"\nportolio value", portfolio_value)
            

            """ to delete
            portfolio_value = self.broker.get_portfolio_value(market_prices=market_val)
            print("date", date, "portolio value", portfolio_value)
            """

        """ To use for backtesting"""
        # Return a DataFrame of the executed trades
        # create backtests folder if it does not exist
        if not os.path.exists('backtests'):
            os.makedirs('backtests')

        # save to csv, use the backtest name 
        backtest_name = generate_random_name()
        
        output_trades = self.broker.transaction_log
        
        output_trades.to_csv(f"backtests/{backtest_name}.csv")

        portfolio_values = pd.DataFrame(portfolio_values)
        
        return output_trades, portfolio_values


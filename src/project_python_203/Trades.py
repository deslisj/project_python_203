import yfinance as yf
import pandas as pd 
from sec_cik_mapper import StockMapper
from dataclasses import dataclass, field
from typing import List
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
        
        output_trades = self.broker.transaction_log

        portfolio_values = pd.DataFrame(portfolio_values)
        
        return output_trades, portfolio_values


@dataclass
class MyBacktest:
    initial_date: datetime
    final_date: datetime
    universe: List[str] = field(default_factory=lambda: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'INTC', 'CSCO', 'NFLX'])
    initial_cash: int = 1000000  # Initial cash in the portfolio
    verbose: bool = True
    broker = Broker(cash=initial_cash, verbose=verbose)
    short_window: int = 20
    long_window: int = 100
    short_type: str = 'simple'
    long_type: str = 'simple'
    
    def run_backtest(self):
        """
        Run the backtest from the initial to the final date.

        Returns:
            pd.DataFrame: A DataFrame of executed trades for all dates.
        """
        logging.info(f"Running backtest from {self.initial_date} to {self.final_date}.")
        logging.info(f"Retrieving price data for universe")

        # Get the data for the backtest period
        data = get_stocks_data(self.universe, self.initial_date, self.final_date)

        #Data_treatment
        data_treatment = Data_treatment(data)

        # Compute moving averages
        data_MA = data_treatment.compute_moving_average(
            short_window=self.short_window, long_window=self.long_window, 
            short_type=self.short_type, long_type=self.long_type
            )
        
        # Trading strategy based on moving averages 
        Trading_strat = TradingStrategy(data_MA)

        # Compute trading signals
        signals = Trading_strat.compute_trading_signals()

        # Execute trades
        trades = Trades(Trading_strat, self.broker)

        # Execute trades based on signals
        output_trades, portfolio_values = trades.execute_trades(signals)

        logging.info(f"Backtest completed. Final portfolio value: {portfolio_values.iloc[-1]['Portfolio Value']}")

        # Return a DataFrame of the executed trades
        # create backtests folder if it does not exist
        if not os.path.exists('backtests'):
            os.makedirs('backtests')

        # save to csv, use the backtest name 
        backtest_name = generate_random_name()

        output_trades.to_csv(f"backtests/{backtest_name}.csv")

        return output_trades, portfolio_values
        
        

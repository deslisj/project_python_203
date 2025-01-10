import pytest
from project_python_203.Data_treatment import *
from project_python_203.Trades import *
from pybacktestchain.data_module import *
from pybacktestchain.broker import *

from datetime import datetime
import pandas as pd

tickers = ['AAPL', 'MSFT']
start_date = '2010-01-01'
end_date = '2020-01-01'

def test_execute_trades():
    data = get_stocks_data(tickers, start_date, end_date)
    data_treatment = Data_treatment(data)
    data_MA = data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="simple", long_type="simple")

    # we intialize broker
    broker = Broker(cash=10000)

    # we create TradingStrategy using the moving averages data
    trading_strategy = TradingStrategy(data_MA)
    
    # we compute trading signals
    signals  = trading_strategy.compute_trading_signals()

    # we initialize Trades
    trades = Trades(strategy=trading_strategy, broker=broker)

    # we execute trades
    output_trades, portfolio_values = trades.execute_trades(signals)

    # we validate executed trades
    assert isinstance(output_trades, pd.DataFrame)
    assert not output_trades.empty
    assert "Date" in output_trades.columns
    assert "Action" in output_trades.columns

    # we validate portfolio values
    assert isinstance(portfolio_values, pd.DataFrame)
    assert not portfolio_values.empty
    assert "Portfolio Value" in portfolio_values.columns


def test_run_backtest():
    # we nitialize MyBacktest with test parameters
    backtest = MyBacktest(
        initial_date=start_date,
        final_date=end_date,
        universe=tickers,
        initial_cash=100000,
        short_window=20,
        long_window=100,
        short_type='simple',
        long_type='simple'
    )

    # we run the backtest
    output_trades, portfolio_values = backtest.run_backtest()

    # we validate executed trades DataFrame
    assert isinstance(output_trades, pd.DataFrame), "output_trades should be a DataFrame"
    assert not output_trades.empty, "output_trades should not be empty"
    assert "Date" in output_trades.columns, "output_trades should contain a 'Date' column"
    assert "Action" in output_trades.columns, "output_trades should contain an 'Action' column"
    assert "Ticker" in output_trades.columns, "output_trades should contain a 'Ticker' column"

    # we validate portfolio values DataFrame
    assert isinstance(portfolio_values, pd.DataFrame), "portfolio_values should be a DataFrame"
    assert not portfolio_values.empty, "portfolio_values should not be empty"
    assert "Date" in portfolio_values.columns, "portfolio_values should contain a 'Date' column"
    assert "Portfolio Value" in portfolio_values.columns, "portfolio_values should contain a 'Portfolio Value' column"

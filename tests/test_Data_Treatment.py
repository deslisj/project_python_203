import pytest
from project_python_203.Data_treatment import *
from pybacktestchain.data_module import *

import pandas as pd

tickers = ['AAPL', 'MSFT']
start_date = '2010-01-01'
end_date = '2020-01-01'


def test_compute_moving_average_simple():
    data = get_stocks_data(tickers, start_date, end_date)

    # we use data to compute data_treatment
    data_treatment = Data_treatment(data)

    # we compute the moving averages
    result = data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="simple", long_type="simple")

    # we ensure no null values
    assert isinstance(result, pd.DataFrame)
    assert "ticker" in result.columns
    assert not result.empty
    assert result["ticker"].nunique() == 2

def test_compute_moving_average_exponential():
    data = get_stocks_data(tickers, start_date, end_date)

    # we use data to compute data_treatment
    data_treatment = Data_treatment(data)

    # we compute the moving averages
    result = data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="exponential", long_type="exponential")

    # we ensure no null values
    assert isinstance(result, pd.DataFrame)
    assert "ticker" in result.columns
    assert not result.empty
    assert result["ticker"].nunique() == 2

def test_plot_moving_average():
    data = get_stocks_data(tickers, start_date, end_date)

    # we use data to compute Data_treatment
    data_treatment = Data_treatment(data)

    # we compute moving averages
    data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="simple", long_type="simple")

    # we test the plot function
    try:
        data_treatment.plot_moving_average(ticker="AAPL")
    except Exception as e:
        pytest.fail(f"plot_moving_average raised an exception: {e}")

def test_compute_trading_signals():
    data = get_stocks_data(tickers, start_date, end_date)

    # we use data to compute Data_treatment
    data_treatment = Data_treatment(data)

    # we compute moving averages
    data_MA = data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="simple", long_type="simple")

    # we use moving averages to initialize TradingStrategy
    trading_strategy = TradingStrategy(data_MA)

    # we compute trading signals
    signals = trading_strategy.compute_trading_signals()

    # we check that the returned DataFrame contains required columns
    assert "Signal" in signals.columns
    assert "Position" in signals.columns

    # we ensure no NaN values in Signal and Position columns
    assert not signals["Signal"].isnull().any()
    assert not signals["Position"].isnull().any()

def test_plot_trading_signals():
    data = get_stocks_data(tickers, start_date, end_date)

    # we use data to compute Data_treatment
    data_treatment = Data_treatment(data)

    # we compute moving averages
    data_MA = data_treatment.compute_moving_average(short_window=20, long_window=100, short_type="simple", long_type="simple")

    # we use moving averages to initialize TradingStrategy
    trading_strategy = TradingStrategy(data_MA)

    # we compute trading signals
    trading_strategy.compute_trading_signals()

    # we test the plot function
    try:
        trading_strategy.plot_trading_signals(ticker="AAPL")
    except Exception as e:
        pytest.fail(f"plot_trading_signals raised an exception: {e}")

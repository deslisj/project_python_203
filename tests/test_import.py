# content of test_pybacktestchain.py
def test_Data_Treatment_import():
    from project_python_203.Data_treatment import Data_treatment, TradingStrategy
    assert Data_treatment is not None
    assert TradingStrategy is not None
def test_Trade_import():
    from project_python_203.Trades import Trades, MyBacktest
    assert Trades is not None
    assert MyBacktest is not None
    


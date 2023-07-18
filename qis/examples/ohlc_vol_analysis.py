import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from enum import Enum
from statsmodels.tsa.ar_model import AutoReg
from typing import Literal, List
import yfinance as yf
import qis
from qis import OhlcEstimatorType

AF_MULTIPLIERS = {'1d': 1, '1h': 24, '30m': 2*24, '15m': 4*24, '5m': 12*24, '1m': 60*24}


def fetch_hf_ohlc(ticker: str = 'SPY',
                  interval: Literal['1d', '1h', '30m', '15m', '5m', '1m'] = '30m'
                  ) -> pd.DataFrame:
    """
    fetch hf data using yf
    """
    asset = yf.Ticker(ticker)
    if interval == '1d':  # close to close
        # ohlc_data = asset.history(period="730d", interval='1d')
        ohlc_data = yf.download(tickers=ticker, start=None, end=None, ignore_tz=True)
        ohlc_data.index = ohlc_data.index.tz_localize('UTC')
    elif interval == '1h':
        ohlc_data = asset.history(period="730d", interval="1h")
    elif interval == '30m':
        ohlc_data = asset.history(period="60d", interval="30m")
    elif interval == '15m':
        ohlc_data = asset.history(period="60d", interval="15m")
    elif interval == '5m':
        ohlc_data = asset.history(period="60d", interval="5m")
    elif interval == '1m':
        ohlc_data = asset.history(period="7d", interval="1m")
    else:
        raise NotImplementedError(f"interval={interval}")
    ohlc_data = ohlc_data[['Open', 'High', 'Low', 'Close']].rename({'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, axis=1)
    ohlc_data.index = ohlc_data.index.tz_convert('UTC')
    return ohlc_data


def estimate_hf_vol(ticker: str = 'SPY',
                    agg_freq: str = 'B',
                    af: float = 260,
                    freqs: List[str] = ['1d', '1h', '30m', '15m', '5m'],
                    ohlc_estimator_type: OhlcEstimatorType = OhlcEstimatorType.PARKINSON
                    ) -> pd.DataFrame:
    # need to scale up the vol
    vols = {}
    for freq in freqs:
        ohlc_data = fetch_hf_ohlc(ticker=ticker, interval=freq)
        vols[freq] = qis.estimate_hf_ohlc_vol(ohlc_data=ohlc_data,
                                              ohlc_estimator_type=ohlc_estimator_type,
                                              agg_freq=agg_freq,
                                              af=af*AF_MULTIPLIERS[freq])
    vols = pd.DataFrame.from_dict(vols, orient='columns').dropna()
    return vols


def plot_hf_vols(ticker: str = 'SPY',
                 agg_freq: str = 'B',
                 af: float = 260,
                 freqs: List[str] = ['1d', '1h', '30m', '15m', '5m'],
                 ohlc_estimator_type: OhlcEstimatorType = OhlcEstimatorType.PARKINSON
                 ):
    vols = estimate_hf_vol(ticker=ticker,
                           agg_freq=agg_freq,
                           af=af,
                           freqs=freqs,
                           ohlc_estimator_type=ohlc_estimator_type)

    with sns.axes_style("darkgrid"):
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))
        qis.plot_time_series(df=vols,
                             x_date_freq='W-MON',
                             var_format='{:,.2%}',
                             ax=ax)


class UnitTests(Enum):
    HF_PRICES = 1
    HF_VOL = 2
    PLOT_HF_VOL = 3


def run_unit_test(unit_test: UnitTests):
    # to save pds
    LOCAL_PATH = "C://Users//artur//OneDrive//analytics//outputs//"

    if unit_test == UnitTests.HF_PRICES:
        intervals = ['1h', '30m', '15m', '1m']
        # 'BTC-USD'
        df = fetch_hf_ohlc(ticker='BTC-USD', interval='1d')
        print(df)

    elif unit_test == UnitTests.HF_VOL:
        # use small number of num_samples for illustration
        df = estimate_hf_vol(ticker='SPY', agg_freq='B', af=260)
        print(df)
        df.plot()

    elif unit_test == UnitTests.PLOT_HF_VOL:
        # plot_hf_vols(ticker='SPY', agg_freq='B', af=260)
        plot_hf_vols(ticker='BTC-USD', agg_freq='D', af=365,
                     ohlc_estimator_type=OhlcEstimatorType.CLOSE_TO_CLOSE)

    plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.PLOT_HF_VOL

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
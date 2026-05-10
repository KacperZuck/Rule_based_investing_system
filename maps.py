from Indicators.SMA import Indicator
# from Indicators import (EMA,SMA,MACD,STOCH,RSI,ADX,ATR,ROC,
#                         precent_R, ULT, MFI, TRIX, BOP, BB)

from Indicators.SMA import SMA
from Indicators.EMA import EMA
from Indicators.RSI import RSI
from Indicators.BB import BB
from Indicators.MFI import MFI
from Indicators.TRIX import TRIX
from Indicators.BOP import BOP
from Indicators.ATR import ATR
from Indicators.ADX import ADX
from Indicators.ROC import ROC
from Indicators.ULT import ULT
from Indicators.STOCH import STOCH
from Indicators.William_pR import William_pR

BUY = 1
SELL = -1
NEUTRAL = 0

SIGNALS_MAP = {
    "THRESHOLD": "_logic_threshold",
    "CROSSOVER": "_logic_crossover",
    "POSITION": "_logic_position" # np. cena powyżej średniej
}

CANDLESTICK ={
    "OPEN": "Otwarcie", "HIGH": "Najwyzszy",
    "LOW": "Najnizszy", "CLOSE": "Zamkniecie",
    "Volume": "Wolumen",
}
INDICATOR_MAP = {
    # "SMA": SMA, git
    # "EMA": EMA, git
    # "RSI": RSI,
    # "MACD": MACD,
    # "ADX": ADX,
    # "STOCH": STOCH,
    # "ATR": ATR, git
    "ROC": ROC,
    "William_pR": William_pR,
    "ULT": ULT,
    "MFI": MFI,
    "TRIX": TRIX,
    "BOP": BOP,
    "BB": BB
}
def get_source_cols(source_type):
    mapping = {
        "HIGH": [CANDLESTICK["HIGH"]],
        "CLOSE": [CANDLESTICK["CLOSE"]],
        "OHLC": [CANDLESTICK["OPEN"], CANDLESTICK["HIGH"], CANDLESTICK["LOW"], CANDLESTICK["CLOSE"]],
        "HLC": [CANDLESTICK["HIGH"], CANDLESTICK["LOW"], CANDLESTICK["CLOSE"]],
        "ALL": [CANDLESTICK["OPEN"], CANDLESTICK["HIGH"], CANDLESTICK["LOW"], CANDLESTICK["CLOSE"],CANDLESTICK["Volume"]],
    }
    return mapping.get(source_type, [CANDLESTICK["CLOSE"]])

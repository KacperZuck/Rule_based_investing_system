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
from Indicators.MACD import MACD

INDICATOR_MAP = {
    "SMA": SMA,
    "EMA": EMA,
    "RSI": RSI,
    # "MACD": MACD,
    "ADX": ADX,
    "STOCH": STOCH,
    "ATR": ATR,
    "ROC": ROC,
    "William_pR": William_pR,
    "ULT": ULT,
    "MFI": MFI,
    "TRIX": TRIX,
    "BOP": BOP,
    "BB": BB
}
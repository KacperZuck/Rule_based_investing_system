from pip._internal.index import sources
from pygments.styles import default
from Logic.maps import *
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

# INDICATOR_MAP = {
#     # "SMA": SMA,
#     "EMA": EMA,
#     "RSI": RSI,
#     "MACD": MACD,
#     "ADX": ADX,
#     "STOCH": STOCH,
#     "ATR": ATR,
#     "ROC": ROC,
#     "William_pR": William_pR,
#     "ULT": ULT,
#     "MFI": MFI,
#     "TRIX": TRIX,
#     "BOP": BOP,
#     "BB": BB
# }

INDICATOR_MAP = {
    "SMA": {
        "class": SMA,
        "display_name": "Simple Moving Average",
        "params": {
            "N":{"type": "int", "min": 2, "max": 200, "default": 12}
        },
        "logic": ["CROSSOVER"]
    },
    "EMA": {
        "class": EMA,
        "display_name": "Exponential Moving Average",
        "params": {
            "N": {"type": "int", "min": 2, "max": 200, "default": 14}
        },
        "logic": ["CROSSOVER"]
    },
    "RSI": {
        "class": RSI,
        "display_name": "Relative Strength Index",
        "params": {
            "N": {"type": "int", "min": 2, "max": 200, "default": 14}
        },
        "logic": ["THRESHOLD"]
    },
    "MACD": {
        "class": MACD,
        "display_name": "Moving Average Convergence Divergence",
        "params": {
            "fast_ema": {"type": "int", "min": 2, "max": 50, "default": 12},
            "slow_ema": {"type": "int", "min": 2, "max": 100, "default": 26},
            "signal": {"type": "int", "min": 2, "max": 50, "default": 9}
        },
        "logic": ["CROSSOVER"]
    },
    "ADX": {
        "class": ADX,
        "display_name": "Average Directional Index",
        "params":{
            "N": {"type": "int", "min": 2, "max": 100, "default": 14}
        },
        "source": "OHLC",
        "logic": ["CROSSOVER"]
    },
    "STOCH": {
        "class": STOCH,
        "display_name": "Stochastic Oscillator",
        "params": {
            "K": {"type": "int", "min": 1, "max": 100, "default": 14},
            "D": {"type": "int", "min": 1, "max": 50, "default": 3},
            "smooth": {"type": "int", "min": 1, "max": 50, "default": 3}
        },
        "source": "OHLC",
        "logic": ["THRESHOLD", "CROSSOVER"]
    },
    "ATR": {
        "class": ATR
    },
    "ROC": {
        "class": ROC
    },
    "William_pR": {
        "class": William_pR
    },
    "ULT": {
        "class": ULT
    },
    "MFI": {
        "class": MFI,
        "display_name": "Money Flow Index",
        "params": {
            "period": {"type": "int", "min": 2, "max": 100, "default": 14}
        },
        "source": "ALL" # Wymaga OHLCV
    },
    "TRIX": {
        "class": TRIX
    },
    "BOP": {
        "class": BOP
    },
    "BB": {
        "class": BB,
        "display_name": "Bollinger Bands",
        "params": {
            "N": {"type": "int", "min": 5, "max": 100, "default": 20},
            "K": {"type": "float", "min": 0.1, "max": 5.0, "default": 2.0}
        },
        "logic": ["CROSSOVER"]
    }
}
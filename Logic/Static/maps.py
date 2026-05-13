
BUY = 1
SELL = -1
NEUTRAL = 0

SIGNALS_MAP = {
    "THRESHOLD": "logic_threshold",
    "CROSSOVER": "logic_crossover",
    "POSITION": "logic_position" # np. cena powyżej średniej
}

CANDLESTICK ={
    "OPEN": "Otwarcie", "HIGH": "Najwyzszy",
    "LOW": "Najnizszy", "CLOSE": "Zamkniecie",
    "Volume": "Wolumen", "TIME": "Data"
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

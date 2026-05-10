from plotly.subplots import make_subplots

from Logic.maps import CANDLESTICK


def plot_data(df):
    # Tworzymy 2 rzędy: górny dla ceny, dolny dla oscylatorów (RSI/MACD)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # 1. Wykres świecowy
    fig.add_trace(go.Candlestick(
        x=df.index, open=df[CANDLESTICK["OPEN"]], high=df[CANDLESTICK["HIGH"]],
        low=df[CANDLESTICK["LOW"]], close=df[CANDLESTICK["CLOSE"]], name="Cena"
    ), row=1, col=1)

    # 2. Automatyczne nakładanie średnich na wykres ceny
    for col in df.columns:
        if any(x in col for x in ["SMA", "EMA", "BB"]):
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, opacity=0.7), row=1, col=1)

        # 3. Oscylatory na dolny panel
        if "RSI" in col:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=2, col=1)
        if "MACD" in col:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, height=800, title="Analiza Techniczna")
    fig.show()
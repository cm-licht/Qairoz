import plotly.graph_objects as go
import pandas as pd

class Visualizer:
    def __init__(self):
        self.outputFile = "chart.html"
    
    def update_chart(self, df, anchor, level05, pivot):
        if df.empty:
            return

        fig = go.Figure()

        fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="BTCUSDT"))

        if anchor is not None:
            fig.add_hline(y=anchor, line_dash="dash", line_color="black", annotation_text="1")

        if level05 is not None:
            fig.add_hline(y=level05, line_dash="dash", line_color="red", annotation_text="0.5")

        if pivot is not None:
            fig.add_hline(y=pivot, line_dash="dash", line_color="black", annotation_text="0")

        fig.update_layout(title="Intraday Plan", yaxis_title="Price", xaxis_title="Time", template="plotly_white", height=800)

        fig.write_html(self.outputFile)

        with open(self.outputFile, "r") as f:
            htmlContent = f.read()
        refreshTag = '<meta http-equiv="refresh" content="5">'
        updateHTML = htmlContent.replace('<head>', f'<head>{refreshTag}')
        with open(self.outputFile, "w") as f:
            f.write(updateHTML)

        print("Chart updated")

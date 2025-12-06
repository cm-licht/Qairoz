import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class Visualizer:
    def __init__(self, pair):
        self.outputFile = "chart.html"
        self.bgColor = "#232136" 
        self.foreColor = "#393552"
        self.red = "#ea9a97"
        self.green = "#3e8fb0"
        self.gold = "#f6c177"
        self.anchor = "#f2e9e1"
        self.text = "#e0def4"
        self.pair = pair

    def update_chart(self, df, anchor, level05, pivot):
        if df.empty:
            return
        
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.05, 
            row_width=[0.2, 0.7],
            subplot_titles=(f"<b>{self.pair} - 5m</b>", "")
        )
        fig.update_annotations(font=dict(
            size=24,
            color=self.text
            ))

        colors = [self.green if row["close"] >= row["open"] else self.red for index, row in df.iterrows()]
        config = {"displayModeBar" : False}
        axisConfig = dict(showgrid=True, gridcolor=self.foreColor, zerolinecolor=self.foreColor)

        fig.add_trace(go.Candlestick(
            x=df["date"],
            increasing_line_color=self.green,
            decreasing_line_color=self.red,
            open=df["open"], high=df["high"],
            low=df["low"], close=df["close"],
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=df["date"],
            y=df["volume"],
            marker_color=colors,
        ), row=2, col=1)

        highIdx = df["high"].idxmax()
        lowIdx = df["low"].idxmin()
        
        dayHighVal = df.loc[highIdx, "high"]
        dayHighTime = df.loc[highIdx, "date"]
        
        dayLowVal = df.loc[lowIdx, "low"]
        dayLowTime = df.loc[lowIdx, "date"]

        fig.add_annotation(
            x=dayHighTime,    
            y=dayHighVal,   
            xref='x',           
            yref='y',
            text=f"<b>{dayHighVal:,.2f}</b>",
            font=dict(color=self.gold),
            showarrow=True,     
            arrowhead=1,
            arrowcolor=self.gold,
            yshift=5,       
            row=1, col=1
        )

        fig.add_annotation(
            x=dayLowTime,
            y=dayLowVal,
            xref='x', 
            yref='y',
            text=f"<b>{dayLowVal:,.2f}</b>",
            font=dict(color=self.gold),
            showarrow=True,
            arrowhead=1,
            arrowcolor=self.gold,
            ay=30,      
            yshift=-5,
            row=1, col=1
        )
        currentDateStr = df["date"].iloc[-1].strftime("%b %d, %Y")
        
        fig.update_xaxes(
            # Force format to HH:MM only. This hides "Dec 6" on the far left.
            tickformat="%H:%M",
            
            # Remove the default labels that Plotly sometimes adds
            showticklabels=True,
            
            # Bottom Chart (Volume) Settings
            title_text=f"<b>{currentDateStr}</b>", # Your Custom Center Title
            title_font=dict(size=20, color=self.text),
            title_standoff=20,
            
            row=2, col=1
        )
        def info_fib_line(val, label, color, style="dash"):
            fig.add_hline(y=val, line_dash=style, line_color=color, line_width=1,annotation_font_color=self.gold, annotation_text=f"{label} ({val: .2f})", annotation_position="top left", row=1, col=1) 

        if anchor is not None:
            info_fib_line(anchor, "1", self.gold)

        if level05 is not None:
            info_fib_line(level05, "0.5", self.gold)

        if pivot is not None:
            info_fib_line(pivot, "0", self.gold)

            diff = anchor - pivot
            level0236 = pivot + (0.236 * diff)
            info_fib_line(level0236, "0.236", self.gold)
            negLevel0236 = pivot + (-0.236 * diff)
            info_fib_line(negLevel0236, "-0.236", self.gold)

        fig.update_layout(template="plotly_white", font=dict(size=20, color=self.text), showlegend=False, plot_bgcolor=self.bgColor, paper_bgcolor=self.bgColor, height=1080, xaxis_rangeslider_visible=False)
        fig.update_xaxes(**axisConfig)
        fig.update_yaxes(**axisConfig)

        fig.write_html(self.outputFile,  config=config)

        with open(self.outputFile, 'r') as f:
            htmlContent = f.read()
        refreshTag = '<meta http-equiv="refresh" content="60">'
        updateHTML = htmlContent.replace('<head>', f'<head>{refreshTag}')
        with open(self.outputFile, 'w') as f:
            f.write(updateHTML)

        print("Chart updated")

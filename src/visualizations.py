import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None):
    """Cria gráfico de barras"""
    fig = px.bar(df, x=x, y=y, title=title, color=color, text=y)
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(showlegend=True, height=500)
    return fig


def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    """Cria gráfico de pizza"""
    fig = px.pie(df, names=names, values=values, title=title)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None):
    """Cria gráfico de linhas"""
    fig = px.line(df, x=x, y=y, title=title, color=color, markers=True)
    fig.update_layout(showlegend=True, height=500)
    return fig


def create_scatter_chart(df: pd.DataFrame, x: str, y: str, title: str, 
                        color: str = None, size: str = None):
    """Cria gráfico de dispersão"""
    fig = px.scatter(df, x=x, y=y, title=title, color=color, size=size)
    fig.update_layout(showlegend=True, height=500)
    return fig


def create_gauge(value: float, title: str, max_value: float = 100):
    """Cria gauge/velocimetro"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_value/3], 'color': "lightgray"},
                {'range': [max_value/3, 2*max_value/3], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9}
        }
    ))
    fig.update_layout(height=300)
    return fig


def create_heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str):
    """Cria mapa de calor"""
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(pivot, title=title, aspect="auto", color_continuous_scale='RdYlGn')
    return fig


def create_funnel_chart(df: pd.DataFrame, x: str, y: str, title: str):
    """Cria gráfico de funil"""
    fig = px.funnel(df, x=x, y=y, title=title)
    return fig


def create_timeline(df: pd.DataFrame, x_start: str, x_end: str, y: str, title: str, color: str = None):
    """Cria timeline/gantt chart"""
    fig = px.timeline(df, x_start=x_start, x_end=x_end, y=y, title=title, color=color)
    fig.update_yaxes(autorange="reversed")
    return fig


def create_table(df: pd.DataFrame, title: str = None):
    """Cria tabela formatada"""
    if title:
        return {"title": title, "data": df}
    return {"data": df}
from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

df = pd.read_csv('./data/TimeSeriesData.csv')
app = Dash()

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

stride_cols = [
    "Stride Count Gallop",
    "Stride Count Canter/Light Gallop",
    "Stride Count Trot/Jog",
    "Stride Count Walk"
]
df_stride = df.dropna(subset=stride_cols, how="all").copy()
df["dTotal Strides"] = df["Total Strides"].diff(4)
df["dStride Count Gallop"] = df["Stride Count Gallop"].diff(4)
df["dStride Count Canter/Light Gallop"] = df["Stride Count Canter/Light Gallop"].diff(4)
df["dStride Count Trot/Jog"] = df["Stride Count Trot/Jog"].diff(4)
df["dStride Count Walk"] = df["Stride Count Walk"].diff(4)

cols_to_remove = df.filter(like='Recovery', axis=1)
df = df[[col for col in df.columns if col not in cols_to_remove]]

app.layout = [
    html.Div(children='My first App'),
    dag.AgGrid(
        rowData=df.to_dict('records'),
        columnDefs=[{"field": i} for i in df.columns]
    )
]

if __name__ == '__main__':
    app.run(debug = True)

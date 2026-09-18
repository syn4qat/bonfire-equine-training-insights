from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

# load data and initialize app
df = pd.read_csv('./data/TimeSeriesData.csv')
app = Dash()
horse_name = df["Horse Name"].iloc[0]
# Data conversion
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# colum set for further processing
stride_cols = [
    "Stride Count Gallop",
    "Stride Count Canter/Light Gallop",
    "Stride Count Trot/Jog",
    "Stride Count Walk"
]
# new dataframe for stride analysis, dropping rows where all stride columns are NaN
df_stride = df.dropna(subset=stride_cols, how="all").copy()
for stride in stride_cols:
    df_stride[stride] = pd.to_numeric(df_stride[stride], errors='coerce')
    df_stride["d" + stride] = df_stride[stride].diff().fillna(0)

# mapping the delta stride columns to gait names
delta_cols = ["d" + stride for stride in stride_cols]
gait_names = {
    "dStride Count Gallop": "Gallop",
    "dStride Count Canter/Light Gallop": "Canter/Light Gallop",
    "dStride Count Trot/Jog": "Trot/Jog",
    "dStride Count Walk": "Walk"
}
df_stride["Gait"] = df_stride[delta_cols].idxmax(axis=1).map(gait_names)
df_stride["Gait"] = df_stride["Gait"].fillna("No Stride")

# removing unecessary columns
cols_to_remove = df_stride.filter(like='Recovery', axis=1)
df_stride = df_stride[[col for col in df_stride.columns if col not in cols_to_remove]]

fig_scatter = px.scatter(df_stride, x="Timestamp", y="Gait", color="Gait", title="Stride Analysis Over Time")
fig_scatter.update_yaxes(categoryorder='array', categoryarray=list(gait_names.values()) + ["No Stride"])
fig_scatter.update_layout(
    xaxis_title="Timestamp",
    yaxis_title="Gait"
)

app.layout = [
    html.Div(children=f"Training Visualization - {horse_name}"),
    dcc.Graph(figure=fig_scatter),
    dag.AgGrid(
        rowData=df_stride.to_dict('records'),
        columnDefs=[{"field": i} for i in df_stride.columns]
    )
]

if __name__ == '__main__':
    app.run(debug = True)

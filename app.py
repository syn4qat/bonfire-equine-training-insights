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
df["Activity Duration timedelta"] = pd.to_timedelta(df["Activity Duration"])
df["Activity Duration in Seconds"] = df["Activity Duration timedelta"].dt.total_seconds()
df["Activity Duration Axis"] = pd.to_datetime('1970/01/01') + df["Activity Duration timedelta"] # workaround as plotly express does not support timedelta as a type
df["Distance (m)"] = df["Distance (m)"].fillna(0)
# colum set for further processing
stride_cols = [
    "Stride Count Gallop",
    "Stride Count Canter/Light Gallop",
    "Stride Count Trot/Jog",
    "Stride Count Walk"
]
######################### STRIDE ANALYSIS #########################
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
df_stride.loc[
    df_stride[delta_cols].sum(axis=1) == 0, "Gait"
] = "No Stride"

# removing unecessary columns
cols_to_remove = df_stride.filter(like='Recovery', axis=1)
df_stride = df_stride[[col for col in df_stride.columns if col not in cols_to_remove]]

# simple scatter figure to visualize the stride analysis over time
fig_scatter = px.scatter(df_stride, x="Activity Duration Axis", y="Gait", color="Gait", )
fig_scatter.update_yaxes(categoryorder='array', categoryarray= ["No Stride"] + list(gait_names.values())[::-1])
fig_scatter.update_xaxes(tickformat="%M:%S")
fig_scatter.update_layout(
    xaxis_title="Activity Duration",
    yaxis_title="Gait"
)

################### HEART RATE ANALYSIS ###################
# simple line figure to visualize the heart rate over time
fig_heart_rate = px.line(df, x="Activity Duration Axis", y="Heart Rate")
fig_heart_rate.update_xaxes(tickformat="%M:%S", title="Activity Duration")
fig_heart_rate.update_yaxes(title="Heart Rate (bpm)")


app.layout = html.Div(
    className="dashboard",
    children=[
        # Header
        html.Div(
            className="header",
            children=[
                html.Div(
                    children=[
                        html.H1("Training Dashboard"),
                        html.P(
                            f"{horse_name} - Training Session",
                            className="subtitle"
                        )
                    ]
                )
            ]
        ),

        # KPI Cards
        html.Div(
            className="kpi_container",
            children=[
                html.Div(
                    className="kpi_card",
                    children=[
                        html.Div("Horse", className="kpi_label"),
                        html.Div(horse_name, className="kpi_value")
                    ]
                ),

                html.Div(
                    className="kpi_card",
                    children=[
                        html.Div("Session Duration", className="kpi_label"),
                        html.Div(
                            str(df["Activity Duration"].max()),
                            className="kpi_value"
                        )
                    ]
                ),

                html.Div(
                    className="kpi_card",
                    children=[
                        html.Div("Max Heart Rate", className="kpi_label"),
                        html.Div(
                            f"{df['Heart Rate'].max():.0f} bpm",
                            className="kpi_value"
                        )
                    ]
                ),

                html.Div(
                    className="kpi_card",
                    children=[
                        html.Div("Distance", className="kpi_label"),
                        html.Div(
                            f"{df['Distance (m)'].max():.0f} m",
                            className="kpi_value"
                        )
                    ]
                )
            ]
        ),

        # Stride Analysis Graph
        html.Div(
            className="card",
            children=[
                html.H2("Stride Analysis Over Time"),
                dcc.Graph(figure=fig_scatter)
            ]
        ),

        # Heart Rate Graph
        html.Div(
            className="card",
            children=[
                html.H2("Heart Rate Over Time"),
                dcc.Graph(figure=fig_heart_rate)
            ]
        ),

        # Data Table
        html.Div(
            className="card",
            children=[
                html.H2("Session Data"),
                dag.AgGrid(
                    rowData=df_stride.to_dict('records'),
                    columnDefs=[{"field": i} for i in df_stride.columns]
                )
            ]
        )
    ]
)
if __name__ == '__main__':
    app.run(debug = True)

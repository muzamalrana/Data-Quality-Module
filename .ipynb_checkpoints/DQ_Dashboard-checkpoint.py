import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import flask
import threading
import webbrowser
from datetime import datetime
from functools import reduce

def generate_table_data(df):
    table_data = df.copy()
    table_data['Count Bar'] = table_data['Count']
    
    def get_icon(percent):
        if percent < 10:
            return "✓"
        elif percent < 30:
            return "!"
        else:
            return "✖"
    
    table_data['Status Icon'] = table_data['Percentage'].apply(get_icon)
    return table_data

# ---------- Flask Server ----------
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# ---------- Sample Data ----------
null_count = pd.read_csv('dq_results/nulls.csv')
outliers_count = pd.read_csv('dq_results/outliers.csv')
placeholder_count = pd.read_csv('dq_results/placeholder_counts.csv')

# Ensure consistent column name for merge key
def rename_key_column(df):
    for col in df.columns:
        if col.lower() in ['column', 'column_name', 'key']:
            df.rename(columns={col: 'key'}, inplace=True)
    return df

null_count = rename_key_column(null_count)
outliers_count = rename_key_column(outliers_count)
placeholder_count = rename_key_column(placeholder_count)

dfs = [null_count, outliers_count, placeholder_count]

# Full outer join all dfs on 'key'
summary_data = reduce(lambda left, right: pd.merge(left, right, on='key', how='outer'), dfs)

# Replace NaN with 0
summary_data.fillna(0, inplace=True)

def get_icon(p):
    if p == 0:
        return "✓"
    elif p < 10:
        return "!"
    else:
        return "✖"

summary_data["Status"] = summary_data[['null_percentage', 'outlier_percentage', 'placeholder_percentage']].max(axis=1).apply(get_icon)
summary_data["Count Bar"] = summary_data[['null_count', 'outlier_count', 'placeholder_count']].sum(axis=1)

outlier_data = pd.read_csv('dq_results/outliers_by_date.csv')
placeholder_data = pd.read_csv('dq_results/placeholder_counts_by_date.csv')
null_data = pd.read_csv('dq_results/nulls_by_date.csv')
flagged_records = pd.read_excel('dq_results/combined_anomalies.xlsx')

# ---------- Utilities ----------
def get_icon(p):
    if p == 0:
        return "\u2705"
    elif p < 10:
        return "\u26A0"
    else:
        return "\u274C"

# ---------- Layout ----------
app.layout = html.Div(style={
    "backgroundColor": "white",
    "padding": "20px",
    "fontFamily": "Calibri",
    "color": "#333",
    "fontSize": "18px"  # Base font size increased
}, children=[
    html.H2("\U0001F4CA Data Quality Profiler", style={
        "textAlign": "center",
        "fontSize": "32px"
    }),

    html.Div(id="summary-cards", style={
        "display": "flex",
        "gap": "15px",
        "justifyContent": "center",
        "marginBottom": "20px"
    }),

    html.Button("Reset Filters", id="reset-button", n_clicks=0, style={
        "marginBottom": "10px",
        "fontSize": "16px",
        "padding": "8px 15px"
    }),

    # Main Summary Table
    dash_table.DataTable(
        id="summary-table",
        data=summary_data.to_dict("records"),
        columns=[
            {"name": "key", "id": "key", "type": "text"},
            {"name": "null_count", "id": "null_count", "type": "numeric"},
            {"name": "outlier_count", "id": "outlier_count", "type": "numeric"},
            {"name": "placeholder_count", "id": "placeholder_count", "type": "numeric"},
            {"name": "null_percentage", "id": "null_percentage", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "outlier_percentage", "id": "outlier_percentage", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "placeholder_percentage", "id": "placeholder_percentage", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Count Bar", "id": "Count Bar", "type": "numeric"},
            {"name": "Status", "id": "Status", "type": "text"}
        ],
        sort_action="native",
        filter_action="native",
        row_selectable='single',
        page_size=20,
        style_table={"marginBottom": "30px", "overflowX": "auto"},
        style_cell={
            "padding": "10px",
            "fontFamily": "Calibri",
            "color": "#333",
            "textAlign": "center",
            "fontSize": "16px",  # Increased font size
            "minWidth": "100px",
            "maxWidth": "200px",
            "whiteSpace": "normal"
        },
        style_header={
            "backgroundColor": "#f2f2f2",
            "fontWeight": "bold",
            "border": "1px solid #ccc",
            "fontSize": "17px"  # Increased header font size
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#fafafa"},

            # Status icon colors
            {
                "if": {"filter_query": '{Status} = "✓"', "column_id": "Status"},
                "color": "green", "fontWeight": "bold"
            },
            {
                "if": {"filter_query": '{Status} = "!"', "column_id": "Status"},
                "color": "orange", "fontWeight": "bold"
            },
            {
                "if": {"filter_query": '{Status} = "✖"', "column_id": "Status"},
                "color": "red", "fontWeight": "bold"
            },

            # Data bar for Count Bar column
            {
                "if": {"column_id": "Count Bar"},
                "background": (
                    "linear-gradient(90deg, #007bff 0%, "
                    "#007bff calc(min(100%, ({Count Bar} / 1000) * 100%)), "
                    "transparent calc(min(100%, ({Count Bar} / 1000) * 100%)))"
                ),
                "color": "#000"
            }
        ],
        style_as_list_view=True
    ),

    # Charts in one row
    html.Div([
        dcc.Graph(id="outlier-chart", style={"flex": 1}),
        dcc.Graph(id="null-chart", style={"flex": 1}),
        dcc.Graph(id="placeholder-chart", style={"flex": 1})
    ], style={"display": "flex", "gap": "10px"}),

    # Flagged Records section
    html.H3("Flagged Records", style={
        "marginTop": "30px",
        "fontSize": "26px"
    }),

    dash_table.DataTable(
        data=flagged_records.to_dict("records"),
        columns=[{"name": i, "id": i} for i in flagged_records.columns],
        page_size=5,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "fontFamily": "Calibri",
            "color": "#333",
            "fontSize": "16px"
        },
        style_header={
            "backgroundColor": "#f2f2f2",
            "fontWeight": "bold",
            "fontSize": "17px"
        }
    ),

    html.Div("Created by RMP", style={
        "textAlign": "right",
        "marginTop": "20px",
        "fontStyle": "italic",
        "fontSize": "14px"
    })
])

# ---------- Callbacks ----------
@app.callback(
    [Output("summary-cards", "children"),
     Output("outlier-chart", "figure"),
     Output("null-chart", "figure"),
     Output("placeholder-chart", "figure"),
     Output("summary-table", "selected_rows")],
    [Input("summary-table", "selected_rows"),
     Input("reset-button", "n_clicks")],
    [State("summary-table", "selected_rows")]
)
def update_dashboard(selected_rows, reset_clicks, state_selected_rows):
    if dash.callback_context.triggered_id == "reset-button":
        selected_rows = []

    column = summary_data.iloc[selected_rows[0]]['key'] if selected_rows else None

    if column is None:
        cards = [
            html.Div([
                html.H4(metric, style={"marginBottom": "5px", "fontSize": "20px"}),
                html.Div([
                    html.Div(f"{summary_data[c + '_count'].sum():,}", style={"fontWeight": "bold", "fontSize": "22px"}),
                    html.Div("(total)", style={"fontSize": "16px"})
                ])
            ], style={"backgroundColor": "#eaeaea", "padding": "10px", "borderRadius": "10px", "width": "18%"})
            for metric, c in zip(["nulls", "outlier", "placeholder"], ["null", "outlier", "placeholder"])
        ]

        def all_line(df, title):
            df['date_only'] = pd.to_datetime(df['date_only'])
            df['month'] = df['date_only'].dt.to_period('M').dt.to_timestamp()
            numeric_df = df.drop(columns=['date_only', 'column', 'month'], errors='ignore')
            df_agg = numeric_df.groupby(df['month']).sum().reset_index()
            count_col = df_agg.filter(like='_count').sum(axis=1)
            percentage_cols = df_agg.filter(like='_percentage')
            if not percentage_cols.empty:
                perc_col = percentage_cols.mean(axis=1)
            else:
                perc_col = pd.Series([0] * len(df_agg))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_agg['month'], y=count_col,
                mode='lines', name='Count',
                yaxis='y1', fill='tozeroy', line_shape='spline'))
            fig.add_trace(go.Scatter(
                x=df_agg['month'], y=perc_col,
                mode='lines', name='%',
                yaxis='y2', fill='tozeroy', line_shape='spline'))
            fig.update_layout(
                title=title,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={"family": "Calibri", "color": "#333", "size": 16},
                legend={"orientation": "h", "x": 0.5, "xanchor": "center"},
                xaxis=dict(title='Month', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14}),
                yaxis=dict(title='Count', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14}),
                yaxis2=dict(title='%', overlaying='y', side='right', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14})
            )
            return fig

        return cards, all_line(outlier_data, "Outliers Over Time"), all_line(null_data, "Nulls Over Time"), all_line(placeholder_data, "Placeholders Over Time"), []

    # When a column is selected:
    col_counts = summary_data[summary_data['key'] == column].iloc[0]
    cards = []
    for anomaly_type in ['null', 'outlier', 'placeholder']:
        cards.append(html.Div([
            html.H4(anomaly_type.capitalize(), style={"marginBottom": "5px", "fontSize": "20px"}),
            html.Div([
                html.Div(f"{col_counts[anomaly_type + '_count']:,}", style={"fontWeight": "bold", "fontSize": "22px"}),
                html.Div(f"{col_counts[anomaly_type + '_percentage']:.2f}% {get_icon(col_counts[anomaly_type + '_percentage'])}", style={"fontSize": "16px"})
            ])
        ], style={"backgroundColor": "#eaeaea", "padding": "10px", "borderRadius": "10px", "width": "18%"}))

    def make_area_chart(df, col, title):
        df_filtered = df[df['column'] == col].copy()
        if df_filtered.empty:
            return go.Figure()
    
        df_filtered['date_only'] = pd.to_datetime(df_filtered['date_only'])
        df_filtered['month'] = df_filtered['date_only'].dt.to_period('M').dt.to_timestamp()
    
        count_col = [c for c in df_filtered.columns if '_count' in c and c != 'total_count']
        perc_col = [c for c in df_filtered.columns if '_percentage' in c]
    
        if not count_col or not perc_col:
            return go.Figure()
    
        agg_df = df_filtered.groupby('month').agg({
            count_col[0]: 'sum',
            perc_col[0]: 'mean'
        }).reset_index()
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg_df['month'], y=agg_df[count_col[0]],
            mode='lines', name='Count',
            yaxis='y1', fill='tozeroy', line_shape='spline'))
        fig.add_trace(go.Scatter(
            x=agg_df['month'], y=agg_df[perc_col[0]],
            mode='lines', name='%',
            yaxis='y2', fill='tozeroy', line_shape='spline'))
        fig.update_layout(
            title=title,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={"family": "Calibri", "color": "#333", "size": 16},
            legend={"orientation": "h", "x": 0.5, "xanchor": "center"},
            xaxis=dict(title='Month', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14}),
            yaxis=dict(title='Count', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14}),
            yaxis2=dict(title='%', overlaying='y', side='right', showgrid=False, titlefont={"size": 16}, tickfont={"size": 14})
        )
        return fig

    # Create figures for selected column
    outlier_fig = make_area_chart(outlier_data, column, "Outliers Over Time")
    null_fig = make_area_chart(null_data, column, "Nulls Over Time")
    placeholder_fig = make_area_chart(placeholder_data, column, "Placeholders Over Time")

    return cards, outlier_fig, null_fig, placeholder_fig, selected_rows

# ---------- Auto Open in Browser ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)

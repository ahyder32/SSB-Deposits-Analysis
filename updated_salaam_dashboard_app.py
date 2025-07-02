
import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px

# Load the cleaned snapshot data
df = pd.read_csv("cleaned_single_snapshot.csv")

# Calculate KPIs
kpi_dormant = df["is_dormant"].sum()
kpi_drop = df["flagged_for_drop"].sum()
kpi_over_100k = df["over_100k"].sum()
kpi_rise = df["flagged_for_rise"].sum()
kpi_new_accounts = (df["account_age_days"] <= 30).sum()
kpi_high_growth = (df["balance_change_pct"] > 1.0).sum()

# Filter only flagged accounts for table
flagged_df = df[
    (df["is_dormant"]) | 
    (df["flagged_for_drop"]) | 
    (df["over_100k"])
]

# Create the Dash app
app = dash.Dash(__name__)
app.title = "Stearns Salaam Deposit Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Stearns Salaam Weekly Deposit Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H4("Dormant Accounts ($0)"),
            html.H2(kpi_dormant, style={'color': 'red'})
        ], className="two columns"),

        html.Div([
            html.H4("Dropped >50%"),
            html.H2(kpi_drop, style={'color': 'orange'})
        ], className="two columns"),

        html.Div([
            html.H4("Over $100K (White-label)"),
            html.H2(kpi_over_100k, style={'color': 'green'})
        ], className="two columns"),

        html.Div([
            html.H4("Increased >50%"),
            html.H2(kpi_rise, style={'color': 'blue'})
        ], className="two columns"),

        html.Div([
            html.H4("New Accounts (≤30 days)"),
            html.H2(kpi_new_accounts, style={'color': 'purple'})
        ], className="two columns"),

        html.Div([
            html.H4("High Growth (>100%)"),
            html.H2(kpi_high_growth, style={'color': 'teal'})
        ], className="two columns"),

    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Br(),

    dcc.Dropdown(
        id='state_filter',
        options=[{"label": s, "value": s} for s in sorted(df['account_state'].dropna().unique())],
        placeholder="Filter by State",
        style={"width": "50%", "margin": "auto"}
    ),

    html.Br(),

    dcc.Graph(id="balance_by_product_chart"),

    html.Br(),

    html.H3("⚠️ Accounts Flagged for Follow-Up", style={"textAlign": "center"}),

    dash_table.DataTable(
        id='flagged_table',
        columns=[{"name": i, "id": i} for i in flagged_df.columns],
        data=flagged_df.to_dict('records'),
        page_size=15,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{is_dormant} = True', 'column_id': 'is_dormant'},
                'backgroundColor': '#ffcccc',  # light red
                'color': 'black'
            },
            {
                'if': {'filter_query': '{flagged_for_drop} = True', 'column_id': 'flagged_for_drop'},
                'backgroundColor': '#fff3cd',  # light yellow
                'color': 'black'
            },
            {
                'if': {'filter_query': '{over_100k} = True', 'column_id': 'over_100k'},
                'backgroundColor': '#d4edda',  # light green
                'color': 'black'
            }
        ]
    )
])

# Chart callback
@app.callback(
    dash.dependencies.Output("balance_by_product_chart", "figure"),
    [dash.dependencies.Input("state_filter", "value")]
)
def update_chart(selected_state):
    filtered_df = df[df['account_state'] == selected_state] if selected_state else df
    fig = px.bar(filtered_df,
                 x="product_description",
                 y="current_balance",
                 color="product_description",
                 title="Current Balance by Product Type",
                 labels={"current_balance": "Balance ($)", "product_description": "Product"},
                 height=400)
    return fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)

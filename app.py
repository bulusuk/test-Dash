import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import os

# CSV file path
DATA_FILE = 'boat_data.csv'

# Initialize the data file if not exists
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=['Last Name', 'First Name', 'Number of Pennies', 'Boat Volume'])
    df_init.to_csv(DATA_FILE, index=False)

app = dash.Dash(__name__)
server = app.server  # for deployment

app.layout = html.Div([
    html.H2("Tinfoil Boat Entry"),
    html.Div([
        html.Label('Last Name'),
        dcc.Input(id='last_name', type='text', value=''),
        html.Br(),
        html.Label('First Name'),
        dcc.Input(id='first_name', type='text', value=''),
        html.Br(),
        html.Label('Number of Pennies Used'),
        dcc.Input(id='num_pennies', type='number', min=1, value=''),
        html.Br(),
        html.Label('Volume of the Tinfoil Boat (cm^3)'),
        dcc.Input(id='boat_volume', type='number', min=0.01, value=''),
        html.Br(),
        html.Button('Submit', id='submit_btn', n_clicks=0),
        html.Div(id='error_msg', style={'color': 'red'}),
    ]),
    html.H3("Pennies vs. Boat Volume"),
    dcc.Graph(id='scatter_plot'),
])

@app.callback(
    [Output('scatter_plot', 'figure'),
     Output('error_msg', 'children')],
    [Input('submit_btn', 'n_clicks')],
    [State('last_name', 'value'),
     State('first_name', 'value'),
     State('num_pennies', 'value'),
     State('boat_volume', 'value')]
)
def update_output(n_clicks, last_name, first_name, num_pennies, boat_volume):
    error = ""
    # Load existing data
    df = pd.read_csv(DATA_FILE)

    # On submit, try to validate and add new entry
    if n_clicks and n_clicks > 0:
        if not (last_name and first_name and num_pennies and boat_volume):
            error = "Please fill out all fields."
        else:
            try:
                num_pennies = int(num_pennies)
                boat_volume = float(boat_volume)
                if num_pennies <= 0 or boat_volume <= 0:
                    error = "Pennies and volume must be positive."
                else:
                    # Append new row and write to CSV
                    new_row = {
                        'Last Name': last_name,
                        'First Name': first_name,
                        'Number of Pennies': num_pennies,
                        'Boat Volume': boat_volume
                    }
                    df = df._append(new_row, ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
            except ValueError:
                error = "Pennies must be integer, volume numeric."

    # Reload possibly updated data for display
    df = pd.read_csv(DATA_FILE)
    if df.shape[0] > 0:
        fig = px.scatter(df,
                         x='Number of Pennies',
                         y='Boat Volume',
                         hover_data=['Last Name', 'First Name'],
                         title='Number of Pennies Used vs. Boat Volume (cm^3)',
                         trendline="ols",
                         trendline_color_override="red") # Set trendline color to red
        # Make the trendline dashed
#         for trace in fig.data:
#             if trace.mode == 'lines':  # This targets the trendline
#                 trace.update(line=dict(dash='dash', width=4))  # Example: dashed, width 4
        # Optional: change CI band color/opacity
        for trace in fig.data:
                # This identifies the confidence band, which uses fill='toself'
            if getattr(trace, 'fill', None) == 'toself':
                trace.update(fillcolor='rgba(0, 200, 255, 0.25)')  # Custom RGBA fill color
#                 trace.update(line=dict(color='rgba(0,0,0,0)'))      # Hide the outline if desired      
                trace.update(line=dict(dash='dash', width=4))  # Example: dashed, width 4
                
        fig.update_traces(marker=dict(size=15)) # Sets all markers to a size of 15
        fig.write_html("plot.html")
    else:
        fig = px.scatter(title='No data yet!')
        fig.update_layout(xaxis={'visible': False}, yaxis={'visible': False})
        fig.write_html("plot.html")

    return fig, error

if __name__ == '__main__':
    app.run_server(debug=False)

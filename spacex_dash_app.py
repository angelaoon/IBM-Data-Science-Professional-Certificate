# Import required libraries
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create the dropdown menu options
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                                    [{'label': i, 'value': i} for i in launch_sites],
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload, max=min_payload,step=1000,
                                                marks={0: '0', 100: '100'},
                                                tooltip={"placement": "bottom", "always_visible": True}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    data = spacex_df.copy()
    
    if entered_site == 'ALL':
        data = data.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(data, values='class',
                     names='Launch Site',
                     title="Total Success Launches by Site")
    else:
        filtered_df = data[data['Launch Site'] == entered_site]
        data = filtered_df['class'].value_counts().reset_index()
        fig = px.pie(data, values='class',
                     title=f"Total Success Launches for Site {entered_site}")
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id='site-dropdown', component_property='value'), 
                Input(component_id="payload-slider", component_property="value")])

# check if ALL sites were selected or just a specific launch site was selected
def get_scattered_chart(entered_site, payload_range):
    low, high = payload_range
    data = spacex_df.copy()
    mask = (data['Payload Mass (kg)'] >= low) & (data['Payload Mass (kg)'] <= high)
    
    if entered_site == 'ALL':
        filtered_df = data[mask]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title="Correlation between Payload and Success for All Sites")
    else:
        filtered_df = data[(data['Launch Site'] == entered_site) & mask]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title=f"Correlation between Payload and Success for Site {entered_site}")
    
    return fig
        
        
# Run the app
if __name__ == '__main__':
    app.run_server()
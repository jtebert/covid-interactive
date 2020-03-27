import os
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import data_process as dp


# Data sources (from NYT repository as submodule)
data_dir = 'covid-19-data'
county_data_filename = 'us-counties.csv'
state_data_filename = 'us-states.csv'

county_df = dp.import_data(os.path.join(data_dir, county_data_filename))
state_df = dp.import_data(os.path.join(data_dir, state_data_filename))
state_df = dp.get_doubling_rate(state_df, 'cases')
state_df = dp.get_doubling_rate(state_df, 'deaths')

states = state_df.state.unique()
states.sort()

# ------------------------------------------------------------------------------


def dict_to_options(dict_in):
    return [{'label': value, 'value': key} for (key, value) in dict_in.items()]


yaxis_type_options = {
    'linear': 'Linear',
    'log': 'Logarithmic'
}

cases_or_deaths_options = {
    'cases': 'Cases',
    'deaths': 'Deaths'
}
y_data_options = {
    '': 'Total count',
    'change': 'Daily change',
    'doubling_rate': 'Doubling rate (days)'
}

# ------------------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='US COVID-19 Data'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Label('Y-axis Display'),
    dcc.RadioItems(
        id='yaxis-type',
        options=dict_to_options(yaxis_type_options),
        value='log'
    ),
    html.Label('Show number of...'),
    dcc.RadioItems(
        id='cases-or-deaths',
        options=dict_to_options(cases_or_deaths_options),
        value='cases'
    ),
    html.Label('Show..'),
    dcc.RadioItems(
        id='y-data',
        options=dict_to_options(y_data_options),
        value=''
    ),

    dcc.Graph(
        id='case-count',
        style={'height': 900}
    ),

])


@app.callback(
    Output(component_id='case-count', component_property='figure'),
    [Input(component_id='yaxis-type', component_property='value'),
     Input(component_id='cases-or-deaths', component_property='value'),
     Input(component_id='y-data', component_property='value')]
)
def update_case_count(yaxis_type, cases_or_deaths, y_data):
    title_str = '{} of {}'.format(
        y_data_options[y_data], cases_or_deaths_options[cases_or_deaths])

    # Get the data pandas column name based on selected options
    y_key = cases_or_deaths
    if y_data:
        y_key = y_key + '_' + y_data

    # Set bounds for doubling rate
    if y_data == 'doubling_rate':
        upper_bound = 30
    else:
        upper_bound = np.max(state_df[y_key])
    if yaxis_type == 'log':
        upper_bound = np.log10(upper_bound)

    date_range = [
        np.min(state_df['date']),
        np.max(state_df['date']) + datetime.timedelta(days=1),
    ]

    return {
        'data': [
            dict(
                x=state_df[state_df['state'] == s]['date'],
                y=state_df[state_df['state'] == s][y_key],
                # text=s,
                mode='line',
                marker={
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=s
            ) for s in states
        ],
        'layout': {
            'title': title_str,
            'yaxis': {
                'type': yaxis_type,
                'title': title_str,
                'range': [0, upper_bound],
            },
            'xaxis': {
                'range': date_range,
            },
            'hovermode': 'closest',
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)

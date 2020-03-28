import os
import datetime
from urllib.request import urlopen
import json

import plotly.express as px

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

county_df = dp.process_data(dp.import_data(os.path.join(data_dir, county_data_filename)))
state_df = dp.process_data(dp.import_data(os.path.join(data_dir, state_data_filename)))
# state_df = dp.get_doubling_rate(state_df, 'cases', 'deaths')
# county_df = dp.get_doubling_rate(county_df, 'cases', 'deaths')
county_df_nanless = county_df[county_df['fips'].notnull()]

states = state_df.state.unique()
states.sort()

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


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
    '': 'Total Count',
    'change': 'Daily Change (ratio)',
    'doubling_rate': 'Doubling Rate (days)'
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

    html.Label('Map date:'),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=state_df['date'].min(),
        max_date_allowed=state_df['date'].max(),
        # initial_visible_month=dt(2017, 8, 5),
        date=str(state_df['date'].max()),
        display_format='MMM D YYYY'
    ),

    dcc.Graph(
        id='case-map',
        style={'height': 900}
    ),

    dcc.Graph(
        id='case-count',
        style={'height': 900}
    ),

])


def get_column_name(cases_or_deaths, y_data):
    # Get the data pandas column name based on selected options
    y_key = cases_or_deaths
    if y_data:
        y_key = y_key + '_' + y_data
    return y_key


@app.callback(
    Output(component_id='case-map', component_property='figure'),
    [Input(component_id='yaxis-type', component_property='value'),
     Input(component_id='cases-or-deaths', component_property='value'),
     Input(component_id='y-data', component_property='value'),
     Input(component_id='date-picker', component_property='date'),
     ]
)
def update_case_map(yaxis_type, cases_or_deaths, y_data, use_date):
    y_key = get_column_name(cases_or_deaths, y_data)

    title_str = '{} of {}'.format(
        y_data_options[y_data], cases_or_deaths_options[cases_or_deaths])

    fig = px.choropleth(
        dp.col_filter(county_df_nanless, date=use_date),
        locations='fips',
        color=y_key,
        geojson=counties,
        color_continuous_scale="Viridis",
        # range_color=(0, 100),
        scope="usa",
        hover_name='title',
        # locationmode='USA-states',
        # text=county_df_nanless['cases'],
        labels={cases_or_deaths_options[cases_or_deaths]: cases_or_deaths},
        # county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}
    )

    fig.update_layout(
        title=title_str + ' by County on ' + str(use_date).split(' ')[0],
        coloraxis_colorbar=dict(
            title=title_str,
        ),
        # county_df_nanless['cases']
    )
    # fig.update_traces(marker=dict(line=dict(color="green")))
    # fig.update_traces(marker_line_color='black')
    line_color = 'white'
    fig.update_traces(
        marker_line={'color': line_color, 'width': 0.5},
        text='cases',
        # colorbar_title_text="This is a test"
    )
    fig.update_geos(showsubunits=True, subunitcolor=line_color, subunitwidth=1.5)
    return fig


@app.callback(
    Output(component_id='case-count', component_property='figure'),
    [Input(component_id='yaxis-type', component_property='value'),
     Input(component_id='cases-or-deaths', component_property='value'),
     Input(component_id='y-data', component_property='value')]
)
def update_case_count(yaxis_type, cases_or_deaths, y_data):
    title_str = '{} of {}'.format(
        y_data_options[y_data], cases_or_deaths_options[cases_or_deaths])

    y_key = get_column_name(cases_or_deaths, y_data)

    # Set bounds for doubling rate
    lower_bound = 0
    if y_data == 'doubling_rate':
        upper_bound = 30
    else:
        upper_bound = np.max(state_df[y_key])
    if yaxis_type == 'log':
        upper_bound = np.log10(upper_bound)
        lower_bound = 0

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
                'range': [lower_bound, upper_bound],
            },
            'xaxis': {
                'range': date_range,
            },
            'hovermode': 'closest',
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)

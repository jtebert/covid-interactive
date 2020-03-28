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

import dash_bootstrap_components as dbc

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


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.LITERA, 'style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

info_text = dcc.Markdown('''
    This is a set of interactive plots for the COVID-19 data from The New York Times, based on reports from state and local health agencies.

    Source data: [github/nytimes](https://github.com/nytimes/covid-19-data).

    Source code: [github/jtebert](https://github.com/jtebert/covid-interactive)
    ''')

header_content = html.H1('US COVID-19 Data', className="page-title")

layout_buttons = [

    dbc.Alert([
        html.H4("Total Cases"),
        html.H2(id="cases-total")
    ], color="warning"),
    dbc.Alert([
        html.H4("Total Deaths"),
        html.H2(id="deaths-total")
    ], color="danger"),

    dbc.FormGroup([
        dbc.Label('Date:'),
        html.Br(),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=state_df['date'].min(),
            max_date_allowed=state_df['date'].max(),
            # initial_visible_month=dt(2017, 8, 5),
            date=str(state_df['date'].max()),
            display_format='MMM D YYYY'
        ),
    ]),

    dbc.FormGroup([
        dbc.Label('Data Scaling:'),
        dbc.RadioItems(
            id='yaxis-type',
            options=dict_to_options(yaxis_type_options),
            value='log'
        )
    ]),

    dbc.FormGroup([
        dbc.Label('Show number of...'),
        dbc.RadioItems(
            id='cases-or-deaths',
            options=dict_to_options(cases_or_deaths_options),
            value='cases'
        ),
    ]),

    dbc.FormGroup([
        dbc.Label('Show..'),
        dbc.RadioItems(
            id='y-data',
            options=dict_to_options(y_data_options),
            value=''
        ),
    ]),

    html.Br(),
    info_text
]


map_graph = dcc.Graph(
    id='case-map',
    style={
        'height': '85vh',
        'width': '100%',
    }
)

time_graph = dcc.Graph(
    id='case-count',
    style={
        'height': '85vh',
        'width': '100%'
    }
)

app.layout = html.Div([
    html.Div([
        # html.Div(["Hello"], className="top-left"),
        html.Div(dbc.Container(layout_buttons, fluid=True), className="bottom")
    ], className="column bg-light", id="left"),
    html.Div(
        [
            # html.Div(header_content, className="top-right"),
            html.Div(
                dbc.Container(
                    [header_content,
                     dbc.Tabs([dbc.Tab(map_graph, label="Map"),
                               dbc.Tab(time_graph, label="Time Series")])],
                    fluid=True), className="bottom")
        ],
        className="column", id="right"),

], className='flex-container')


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

    if yaxis_type == 'log':
        z_data = np.log10(dp.col_filter(county_df_nanless, date=use_date)[cases_or_deaths])
    else:
        z_data = dp.col_filter(county_df_nanless, date=use_date)[cases_or_deaths]

    fig = px.choropleth(
        dp.col_filter(county_df_nanless, date=use_date),
        locations='fips',
        color=y_key,
        geojson=counties,
        color_continuous_scale="RdYlGn_r",
        # range_color=(0, 100),
        scope="usa",
        hover_name='title',
        # labels=county_df_nanless['title'],
        # labels={cases_or_deaths_options[cases_or_deaths]: cases_or_deaths},
    )

    date = datetime.datetime.strptime(use_date.split(' ')[0], '%Y-%m-%d')
    date_string = date.strftime('%b %d, %Y')

    fig.update_layout(
        # title=title_str + ' by County on ' + date_string,
        coloraxis_colorbar=dict(
            title=title_str,
        ),
    )
    # fig.update_traces(marker=dict(line=dict(color="green")))
    # fig.update_traces(marker_line_color='black')
    line_color = 'white'
    fig.update_traces(z=z_data)
    fig.update_traces(
        marker_line={'color': line_color, 'width': 0.5},
        # hoverinfo='text',
        hoverinfo="location+z+text",
        # hovertext=county_df_nanless['title'],
        # hovertext='title',
        text=county_df_nanless['title'],
        # z=z_data,
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
            # 'title': title_str,
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


def counter_str(date, key):
    if date is not None:
        date = datetime.datetime.strptime(date.split(' ')[0], '%Y-%m-%d')
        date_string = date.strftime('%b %d, %Y')

        death_count = dp.col_filter(state_df, date=date)[key].sum()

        return '{:,}'.format(death_count)
        # return 'Total {} by {}: {:,}'.format(key, date_string, death_count)


@app.callback(
    Output('deaths-total', 'children'),
    [Input('date-picker', 'date')])
def update_output(date):
    return counter_str(date, 'deaths')


@app.callback(
    Output('cases-total', 'children'),
    [Input('date-picker', 'date')])
def update_output(date):
    return counter_str(date, 'cases')


if __name__ == '__main__':
    app.run_server(debug=False)

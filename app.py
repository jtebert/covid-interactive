import os
import datetime
from urllib.request import urlopen
import json

import plotly.express as px
import plotly.graph_objects as go

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
    'change': 'Daily Change (count)',
    'doubling_rate': 'Doubling Rate (days)'
}

display_options = {
    # 'colors': 'Use fixed color scale',
    'map': 'Show background map'
}

# ------------------------------------------------------------------------------


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.LITERA, 'style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'US COVID-19 Data'

info_text = dcc.Markdown('''
    This is a set of interactive plots for the COVID-19 data from The New York Times, based on reports from state and local health agencies.

    [Read here](https://github.com/jtebert/covid-interactive#graph-options) for more information about graph options.

    Source data: [Github/nytimes](https://github.com/nytimes/covid-19-data)

    Source code: [Github/jtebert](https://github.com/jtebert/covid-interactive)

    Questions or comments: [Email me](mailto:julia@juliaebert.com)
    ''')

header_content = html.H1('US COVID-19 Data', className="page-title")

graph_descriptor = html.P(id='graph-descriptor')

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

    dbc.FormGroup(
        [
            dbc.Label("Display Options:"),
            dbc.Checklist(
                options=dict_to_options(display_options),
                value=[],
                id="display-switches",
                switch=True,
            ),
        ]
    ),

    html.Br(),
    info_text
]


map_graph = dcc.Graph(
    # figure=go.Figure(px.choropleth_mapbox()),
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
                     graph_descriptor,
                     dbc.Tabs([dbc.Tab(map_graph, label="Map", tab_id='tab-map'),
                               dbc.Tab(time_graph, label="Time Series", tab_id='tab-graph')])],
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
     Input(component_id='display-switches', component_property='value'),
     ]
)
def update_case_map(yaxis_type, cases_or_deaths, y_data, use_date, display_switches):
    y_key = get_column_name(cases_or_deaths, y_data)

    title_str = '{}<br>of {}'.format(
        y_data_options[y_data], cases_or_deaths_options[cases_or_deaths])

    # Remove edge cases where number of cases/deaths decreased
    # df[(df['col1'] >= 1) & (df['col1'] <= 1)]
    if y_data in ['doubling_rate']:
        key = cases_or_deaths+'_doubling_rate'
        use_df = county_df_nanless[
            (county_df_nanless['date'] == use_date) &
            (county_df_nanless[key].notnull()) &
            (county_df_nanless[key] >= 0)
        ]
    else:
        use_df = use_df = county_df_nanless[county_df_nanless['date'] == use_date]

    if yaxis_type == 'log':
        z_data = np.log10(use_df[y_key])
    else:
        z_data = use_df[y_key]

    # Higher is better (green) for all cases except doubling rate, so reverse
    # the colorscale for that one
    if y_data == 'doubling_rate':
        colorscale = 'RdYlGn'
    else:
        colorscale = 'RdYlGn_r'

    choropleth_vals = dict(
        locations='fips',
        color=y_key,
        geojson=counties,
        color_continuous_scale=colorscale,
    )

    # Use background map or not
    if 'map' in display_switches:
        fig = px.choropleth_mapbox(
            use_df,
            mapbox_style="carto-positron",
            zoom=4,
            center={"lat": 37.0902, "lon": -95.7129},
            opacity=0.5,
            **choropleth_vals
        )
    else:
        fig = px.choropleth(
            use_df,
            scope='usa',
            **choropleth_vals
        )

    date = datetime.datetime.strptime(use_date.split(' ')[0], '%Y-%m-%d')
    date_string = date.strftime('%b %d, %Y')

    # Make logarithmic scale labels
    if yaxis_type == 'log':
        tickmax = np.round(z_data[z_data != np.inf].max())
        tickrange = list(range(int(tickmax)))
        ticklabels = [10**t for t in tickrange]
        fig.update_layout(
            coloraxis_colorbar=dict(
                tickvals=tickrange,
                ticktext=ticklabels
            )
        )

    # Create hover label based on data to be displayed
    hover_template = "<b>%{customdata[0]}</b><br>" +\
        "Cases: %{customdata[1]:,} (+%{customdata[3]:,})<br>" +\
        "Deaths: %{customdata[2]:,} (+%{customdata[4]:,})<br>"
    if y_data == 'doubling_rate':
        y_key_str = cases_or_deaths_options[cases_or_deaths] + ' doubling rate'
        # hover_template = hover_template + y_key_str + "%{customdata[5]:,}"
        hover_template = hover_template + y_key_str + ": %{customdata[5]:.2f} days"

    fig.update_layout(
        coloraxis_colorbar=dict(
            title=title_str,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    line_color = 'white'
    fig.update_traces(z=z_data)
    fig.update_traces(
        marker_line={'color': line_color, 'width': 0.5},
        hoverinfo="location+z+text",
        customdata=np.stack(
            (use_df['title'], use_df['cases'], use_df['deaths'],
             use_df['cases_change'], use_df['deaths_change'],
             use_df[y_key]),
            axis=-1),
        hovertemplate=hover_template,
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
        state_df['date'].min(),
        state_df['date'].max() + datetime.timedelta(days=1),
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
            'margin_t': {"r": 0, "t": 0, "l": 0, "b": 0}

        }
    }


def counter_str(date, key):
    # Get and format the total number of deaths or cases for this date
    if date is not None:
        counter = dp.col_filter(state_df, date=date)[key].sum()

        return '{:,}'.format(counter)


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


@app.callback(
    Output('graph-descriptor', 'children'),
    [Input(component_id='yaxis-type', component_property='value'),
     Input(component_id='cases-or-deaths', component_property='value'),
     Input(component_id='y-data', component_property='value'),
     Input(component_id='date-picker', component_property='date'),
     Input(component_id='display-switches', component_property='value'),
     ]
)
def get_graph_descriptor(yaxis_type, cases_or_deaths, y_data, use_date, display_switches):
    # Summary string based on all the options selected
    date = datetime.datetime.strptime(use_date.split(' ')[0], '%Y-%m-%d')
    date_string = date.strftime('%B %d, %Y')
    if yaxis_type == 'log':
        log_txt = ', on a logarithmic scale'
    else:
        log_txt = ''

    title_str = '{type} of {data} on {date}{log}.'.format(
        type=y_data_options[y_data].lower().capitalize(),
        data=cases_or_deaths_options[cases_or_deaths].lower(),
        date=date_string.capitalize(),
        log=log_txt)
    return title_str


if __name__ == '__main__':
    app.run_server(debug=True)

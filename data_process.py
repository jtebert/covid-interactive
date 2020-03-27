# Used for processing the raw NYTimes CSV files into usable Pandas DataFrames
import datetime

import pandas as pd
import numpy as np


def import_data(filename):
    def dateparser(x): return datetime.datetime.strptime(x, "%Y-%m-%d")
    df = pd.read_csv(filename, parse_dates=['date'], date_parser=dateparser)
    # df = pd.read_csv(filename, index_col='date', parse_dates=True)
    return df


def col_filter(df, **kwargs):
    query_str = ' & '.join(['{}=="{}"'.format(key, val) for (key, val) in kwargs.items()])
    return df.query(query_str)


def get_counties(df, state):
    # List all the counties in the state with data
    return col_filter(df, state=state)['county'].unique()


def get_states(df):
    # List all the states in the data
    return df['state'].unique()


def get_doubling_rate(df, key):
    # Get the rate (number of days) for the number of {cases, deaths} to double
    # by STATE. (This won't make any sense if you try to pass in the county data)
    # This uses the one-day percentage increase in cases and adds it as a col.
    # `key` specifies 'cases' or 'deaths'
    state_changes = []
    for state in get_states(df):
        state_changes.append(col_filter(df, state=state)[key].pct_change())
    change_series = pd.concat(state_changes)
    df[key+'_change'] = change_series
    df[key+'_doubling_rate'] = 1 / np.log2(1+df[key+'_change'])
    return df


if __name__ == "__main__":
    import_data('covid-19-data/us-counties.csv')

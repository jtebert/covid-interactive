# Used for processing the raw NYTimes CSV files into usable Pandas DataFrames
import datetime

import pandas as pd
import numpy as np


def import_data(filename):
    def dateparser(x): return datetime.datetime.strptime(x, "%Y-%m-%d")
    df = pd.read_csv(filename,
                     parse_dates=['date'], date_parser=dateparser,
                     dtype={"fips": str})
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


def process_data(df):
    df = get_doubling_rate(df, 'cases', 'deaths')
    # Add text shortname
    if 'county' in df.columns:
        df['title'] = df['county'] + ' County, ' + df['state']
    else:
        df['title'] = df['state']
    return df


def get_doubling_rate(df, *keys):
    """
    Get the rate (number of days) for the number of {cases, deaths} to double by
    state or county, based on unique FIPS codes. This uses the one-day
    percentage increase in cases and adds it as a col. `keys` specify 'cases' or
    'deaths'
    """
    for key in keys:
        changes = []
        changes_count = []
        for fips in df.fips.unique():
            filtered = col_filter(df, fips=fips)[key]
            changes.append(filtered.pct_change())
            changes_count.append(filtered.diff())
        # Add the change/doubling columns to the existing dataframe
        df[key+'_change'] = pd.concat(changes_count)
        df[key+'_doubling_rate'] = 1 / np.log2(1+pd.concat(changes))
    return df


def get_moving_average(df, y_key, num_days):
    """
    Compute a moving average of the data in the `y_key` column of the dataframe
    over `num_days` days.
    """
    avgs = []
    for fips in df.fips.unique():
        filtered = col_filter(df, fips=fips)[y_key]
        avgs.append(filtered.rolling(window=num_days).mean())
    df[y_key+'_avg'] = pd.concat(avgs)
    return df


if __name__ == "__main__":
    import_data('covid-19-data/us-counties.csv')

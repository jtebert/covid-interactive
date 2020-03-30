# Interactive COVID-19 tracker

This is an interactive interface for the New York Times COVID-19 data, which is [available here](https://github.com/nytimes/covid-19-data).

### [VIEW HERE](http://covid-19.juliaebert.com)

## Install

Clone the project with its dependency:

```shell
git clone --recurse-submodules git@github.com:jtebert/covid-interactive.git
```

Within the cloned directory, set up the Python environment:

```shell
python3 -m venv venv  # Create a virtual environment for the dependencies
source venv/bin/activate  # Activate the virtual environment
pip install -r requirements.txt  # Install the dependencies for the project
```

To update the data from the submodule, run:

```shell
git submodule update --remote
```

## Run

```shell
python app.py
```

Open the interactive graph in the browser, probably at [localhost:8050](http://127.0.0.1:8050/)

I used [these instructions](https://dash.plotly.com/deployment) to deploy to Heroku.

## License

This project is available under the [MIT license](LICENSE.md).

[Data is from The New York Times, based on reports from state and local health agencies](https://github.com/nytimes/covid-19-data).

## Graph Options

This is an explanation of the options for displaying data in the map and time series graph.

**Date:** The date for which data is displayed in the map and alerts but does not affect the time series graph.

**Data Scaling:** Map colors and time series graph can be scaled linearly or logarithmically (base 10). This changes the map color scale and time series y-axis.

**Show number of...** Show graphs based on either the number of confirmed cases or confirmed deaths.

**Show...** Choose how to process and display the death/case data.
- **Total Count:** Show the raw count of confirmed cases/deaths.
- **Daily Change (count):** Show the change in number of cases/deaths from the preceding day.
- **Doubling rate (days):** Show how many days it currently takes for the number of cases/deaths to double. This is computed as:
  <img src="https://render.githubusercontent.com/render/math?math=1/\log_2(\frac{\text{today}}{\text{yesterday}})">

**Display Options:**
- **Show background map:** Turn on/off a detailed map underneath the county data
- *More coming soon*
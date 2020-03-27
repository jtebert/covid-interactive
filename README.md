# Interactive COVID-19 tracker

This is an interactive interface for the New York Times COVID-19 data, which is [available here](https://github.com/nytimes/covid-19-data).

## Installation

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

## Run

```shell
python app.py
```

Open the interactive graph in the browser, probably at [localhost:8050](http://127.0.0.1:8050/)

## License

This project is available under the [MIT license](LICENSE.md).

[Data is from The New York Times, based on reports from state and local health agencies](https://github.com/nytimes/covid-19-data).
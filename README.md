# ENPM611 Project Team 6

## Contents

- [Repository Structure](#repository-structure)
- [Implementation](#Implementation)
- [📁 Milestone&nbsp;1 Files](#-milestone-1-files)
- [📁 Milestone&nbsp;2 Files](#-milestone-2-files)
- [Setup](#setup)
  - [Install dependencies](#install-dependencies)
  - [‼️ mplcyberpunk ‼️ (fix)](#️-mplcyberpunk-️)
  - [Download and configure the data file](#download-and-configure-the-data-file)
  - [Run an analysis](#run-an-analysis)
- [Instructions for running the unit tests](#instructions-for-running-the-unit-tests)
- [VSCode run configuration](#vscode-run-configuration)
- [What your commands produce](#what-your-commands-produce)


## Repository Structure
```
project-team-6/
├── .github/            ← CI workflow (GitHub Actions)
│   └── workflows/
│       └── python-app.yml
├── .vscode/            ← handy launch / debug settings (optional)
├── data/               ← raw + cleaned GitHub‑issues JSON
├── design/             ← UML & ER diagrams (SVG + TXT)
├── misc/               ← screenshots referenced in the README
├── Utils/              ← generic helpers (e.g. data_loader)
├── models/             ← Python dataclasses / enums for issues
├── analyses/           ← **feature‑specific analysis modules**
│   ├── cycle_time_analysis.py
│   ├── top_twenty_analysis.py
│   └── first_response_time.py
├── config/             ← runtime config + secrets template
├── run.py              ← command‑line entry point (`--feature N`)
├── example_analysis.py ← simple demo / template (feature 0)
├── requirements.txt    ← Python dependencies
└── README.md           ← you are here 🚀
```

## Implementation

We have identified three core areas of GitHub issue analysis for the `python-poetry/poetry` repository:

1. **Cycle‑Time Analysis**
   - **Computes** cycle time (in days) for every issue that is  
     • labeled **kind/bug** & **state = closed**  
     • close date taken from first `closed` event (falls back to `updated_date`)
   - **Detects** repeated / related bugs  
     • normalises titles and tallies duplicates  
     • lists the 10 most‑repeated bug titles
   - **Visual output**
     - Histogram of cycle times with an interpolated trend line (hover shows bin counts)
     - Bar‑chart of the **top repeated bug titles**
   - **Console extras**
     - Prints overall **average** and **median** cycle time
     - Flags the fastest & slowest 5 % of fixes (issue # + days)


2. **Top‑Twenty Analysis**
   - **Builds** a set of real contributors for every issue  
     • Issue creators • Assignees • Commenters • Closers  
     • Any login containing “bot” is excluded; case/space duplicates are merged
   - **Creates** three interactive bar‑charts  
     1. **Top 20 Contributors** – total issues involved (any role)  
     2. **Top 20 Issue Creators** – issues opened  
     3. **Top 20 Closers** – issues closed
   - **Console output**  
     • Total number of real contributors  
     • Name and count of the single most active contributor, creator, and closer



3. **First‑Response Time Analysis**
   - **Calculates** the first‑response delay for every issue  
     • time (in hours) from creation → first external action  
     • *self‑responses by the issue author are ignored*
   - **Visual output**
     - Histogram of first‑response times (all issues)
     - Bar‑chart of **average response time by label**
     - Line plot of **monthly trend** in average response time
   - **Highlights** the **5 slowest‑responded issues** (issue # + hours)
   - **Console stats** — prints overall **average** and **median** first‑response times

---

## 📁 Milestone 1 Files

The following files have been created and submitted as part of Milestone 1:

### 🔢 Data

- `data/poetry.json` — Raw GitHub issue data with timeline events, labels, metadata
- `data/poetry_trimmed.json` — Cleaned version of the above containing only relevant event data

### 🧱 Diagrams

- `design/team_6class_diagram.svg` — Class diagram (UML format)
- `design/team_6class_diagram.txt` — Text version of the class diagram
- `design/team_6erd.svg` — Entity-Relationship (ER) Diagram (SVG format)
- `design/team_6erd.txt` — Text version of the ER diagram

## 📁 Milestone 2 Files

### Analysis

- `analysis/cycle_time_analysis.py` — Feature 1
- `analysis/top_twenty_analysis.py` — Feature 2
- `analysis/first_response_time_analysis.py` — Feature 3

---
This is the template for the ENPM611 class project. Use this template in conjunction with the provided data to implement an application that analyzes GitHub issues for the [poetry](https://github.com/python-poetry/poetry/issues) Open Source project and generates interesting insights.

This application template implements some of the basic functions:

- `data_loader.py`: Utility to load the issues from the provided data file and returns the issues in a runtime data structure (e.g., objects)
- `model.py`: Implements the data model into which the data file is loaded. The data can then be accessed by accessing the fields of objects.
- `config.py`: Supports configuring the application via the `config.json` file. You can add other configuration paramters to the `config.json` file.
- `run.py`: This is the module that will be invoked to run your application. Based on the `--feature` command line parameter, one of the three analyses you implemented will be run. You need to extend this module to call other analyses.

With the utility functions provided, you should focus on implementing creative analyses that generate intersting and insightful insights.

In addition to the utility functions, an example analysis has also been implemented in `example_analysis.py`. It illustrates how to use the provided utility functions and how to produce output.

## Setup

To start using the code clone the repository to your system and follow the steps below:

### Install dependencies

In the root directory of the application, create a virtual environment, activate that environment, and install the dependencies like so:

```bash
pip install -r requirements.txt
```

## ‼️ mplcyberpunk ‼️

Make sure you grab the latest version of mplcyberpunk.
Older versions will result in **IsADirectoryError: [Errno 21] Is a directory**

If the issue persists even after installing the latest version. In -

``` cmd
[path_to_your_virtual_pt_env]/lib/python3.9/site-packages/mplcyberpunk/__init__.py
```

Change :

```py
with importlib.resources.path("mplcyberpunk", "data") as data_path:
    cyberpunk_stylesheets = mpl.style.core.read_style_directory(data_path)
    mpl.style.core.update_nested_dict(mpl.style.library, cyberpunk_stylesheets)
```

To :

```py
from importlib.resources import files

data_path = files("mplcyberpunk").joinpath("data")
cyberpunk_stylesheets = mpl.style.core.read_style_directory(data_path)
mpl.style.core.update_nested_dict(mpl.style.library, cyberpunk_stylesheets)
```

### Download and configure the data file

Download the data file (in `json` format) from the project assignment in Canvas and update the `config.json` with the path to the file. Note, you can also specify an environment variable by the same name as the config setting (`ENPM611_PROJECT_DATA_PATH`) to avoid committing your personal path to the repository.

### Run an analysis

With everything set up, you should be able to run the existing example analysis:

```bash
python run.py --feature <Feature_Number>
```

There are only three features starting from 1.

That will output basic information about the issues to the command line.

## VSCode run configuration

To make the application easier to debug, runtime configurations are provided to run each of the analyses you are implementing. When you click on the run button in the left-hand side toolbar, you can select to run one of the three analyses or run the file you are currently viewing. That makes debugging a little easier. This run configuration is specified in the `.vscode/launch.json` if you want to modify it.

The `.vscode/settings.json` also customizes the VSCode user interface sligthly to make navigation and debugging easier. But that is a matter of preference and can be turned off by removing the appropriate settings.

## Instructions For Running The Unit Tests
> make sure `pytest` and `pytest-cov` packages are available in your python environment

The unit tests are written using the `pytest` framework, along with `pytest-cov` to generate coverage metrics. The tests cover the following modules:
* analysis
* config
* models
* utils
* run

Note that the `tests` module and the `__init__.py` files are excluded from coverage. You can modify this behavior by editing the `.coveragerc` configuration file. 

To run the tests and generate coverage metrics, execute the following command from the root directory:
```bash
pytest
```

The `pytest.ini` file defines the `testpath`, and other `pytest configurations`. Alternatively, you can run the following command to get coverage metrics for all modules in the project:
```bash
pytest --cov=.
```

## What your commands produce

```bash
python run.py --feature 1
```

![Image showing the cycle time - figure 1](./misc/1.1.png)
![Image showing Top Repeated Bugs and their issue Count - figure 2](./misc/1.2.png)


```bash
python run.py --feature 2
```

![Image showing the Top 20 contributers - figure 1](./misc/2.1.png)
![Image showing the Top 20 issue creators - figure 2](./misc/2.2.png)
![Image showing the Top 20 closers - figure 3](./misc/2.3.png)

```bash
python run.py --feature 3
```

![Image showing the response times in days - figure 1](./misc/3.1.png)
![Image showing the average response time by label - figure 2](./misc/3.2.png)
![Image showing the average response time over a period - figure 3](./misc/3.3.png)

# Github Analytics

Scripts to extract multiple metrics from Github Projects.

## Install

```bash
pip install git+ssh://git@github.com/datacebo/github-analytics
```

### Development

For development, clone the repository and install `dev-requirements.txt`:

```bash
git clone git@github.com:datacebo/github-analytics
cd github-analytics
pip install -r dev-requirements.txt
```

# Usage

To collect metrics from github you need to provide:
1. A Github Token. Documentation about how to create a Personal Access Token can be found
   [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
2. A list of Github Repositories for which to collect the metrics. The repositories need
   to be given as `{org-name}/{repo-name}`, like `sdv-dev/SDV`.
3. (Optional) A filename where the output will be stored. If a name containing the `.xlsx`
   extension is given (like `path/to/my-filename.xlsx`), it will be used as provided.
   Otherwise, a filename will be created as `github-metrics-{name}-{today}.xlsx` within
   the same folder where the scrpit is run. For example, if `sdv` is passed as the name,
   and the script is run on November, 9th, 2021, the output file will be
   `github-metrics-sdv-2021-11-09.xlsx`.

## Python Interface

In order to run the collection script from python, the `collect_project_metrics` function
needs to be imported from the `github_analytics` package and executed passing the values
indicated above.

**NOTE**: For detailed output, logging must be enabled as shown in the example below.

```python3
>>> import logging
>>> logging.basicConfig(level=logging.INFO)
>>> from github_analytics import collect_project_metrics
>>> repositories = ['sdv-dev/RDT', 'sdv-dev/SDV', 'sdv-dev/Copulas', 'sdv-dev/CTGAN']
>>> output_name = 'sdv-dev'
>>> token = '<my-github-token>'
>>> collect_project_metrics(token, repositories, output_name)
INFO:github_analytics.main:Getting information for repository sdv-dev/RDT
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 195.00it/s]
100%|███████████████████████████████████████████████████████████████| 182/182 [00:00<00:00, 364.64it/s]
100%|███████████████████████████████████████████████████████████████| 37/37 [00:00<00:00, 91020.09it/s]
INFO:github_analytics.main:Getting information for repository sdv-dev/SDV
100%|███████████████████████████████████████████████████████████████| 389/389 [00:02<00:00, 193.20it/s]
100%|███████████████████████████████████████████████████████████████| 219/219 [00:00<00:00, 231.17it/s]
100%|███████████████████████████████████████████████████████████████| 561/561 [00:03<00:00, 158.39it/s]
INFO:github_analytics.main:Getting information for repository sdv-dev/Copulas
100%|███████████████████████████████████████████████████████████████| 138/138 [00:00<00:00, 333.27it/s]
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 287.29it/s]
100%|███████████████████████████████████████████████████████████████| 245/245 [00:01<00:00, 204.88it/s]
INFO:github_analytics.main:Getting information for repository sdv-dev/CTGAN
100%|███████████████████████████████████████████████████████████████| 113/113 [00:00<00:00, 287.26it/s]
100%|██████████████████████████████████████████████████████████████| 64/64 [00:00<00:00, 134824.44it/s]
100%|███████████████████████████████████████████████████████████████| 498/498 [00:02<00:00, 171.11it/s]
INFO:github_analytics.main:Getting 164 missing users
 99%|██████████████████████████████████████████████████████████████▌| 163/164 [00:01<00:00, 121.99it/s]
INFO:github_analytics.output:Creating file github-metrics-sdv-dev-2021-11-12.xlsx
```


## Command Line Interface

In order to run the collection script from the command line, the `github-analytics collect` command
must be called passing the following optional arguments:

- `-c / --config-file CONFIG_FILE`: Path to the config file to use. Defaults to `config.yaml`.
  Format of the `config.yaml` file is documented below.
- `-o / --output-folder OUTPUT_FILDER`: Path to the folder in which spreadsheets will be created.
  Defaults to the value given in the config file, or to `'.'` if there is none, and supports
  `gdrive://<folder-name>` format for Google Drive folders.
- `-p / --projects PROJECT [PROJECT [PROJECT...]]`: Names of the projects to pull. These will be
  used to search for repository lists inside the config file. If not given, defaults to all the
  projects found in the config file.
- `-r / --repositories REPOSITORY [REPOSITORY [REPOSITORY...]]`: Optional, list of repositories
  to extract for the indicated project. If this is given, one and only one `project` must be
  passed, which will be used as the name for the output spreasheet.
- `-m / --add-metrics`: If indicated, add a `Metrics` tab with the project metrics to the
  spreadsheet.
- `-n / --not-incremental`: If indicated, collect data from scratch instead of doing it
  incrementally over the existing data.
- `-t / --token`: Github token to use. If not given, it will be requested in a prompt.
- `-l / --logfile LOGFILE`: Write logs to the indicated logfile.
- `-v / --verbose`: Be more verbose.

```bash
$ github-analytics github -p sdv-dev -c config.yaml
Please input your Github Token: <my-github-token>
2021-11-12 15:42:43,100 - INFO - Getting information for repository sdv-dev/RDT
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 300.87it/s]
100%|███████████████████████████████████████████████████████████████| 182/182 [00:00<00:00, 324.25it/s]
100%|███████████████████████████████████████████████████████████████| 37/37 [00:00<00:00, 88276.02it/s]
2021-11-12 15:42:45,862 - INFO - Getting information for repository sdv-dev/SDV
100%|███████████████████████████████████████████████████████████████| 389/389 [00:01<00:00, 203.20it/s]
100%|███████████████████████████████████████████████████████████████| 219/219 [00:00<00:00, 228.34it/s]
100%|███████████████████████████████████████████████████████████████| 561/561 [00:03<00:00, 152.64it/s]
2021-11-12 15:42:54,465 - INFO - Getting information for repository sdv-dev/CTGAN
100%|███████████████████████████████████████████████████████████████| 113/113 [00:00<00:00, 283.67it/s]
100%|██████████████████████████████████████████████████████████████| 64/64 [00:00<00:00, 134486.70it/s]
100%|███████████████████████████████████████████████████████████████| 498/498 [00:02<00:00, 179.84it/s]
2021-11-12 15:42:59,545 - INFO - Getting information for repository sdv-dev/Copulas
100%|███████████████████████████████████████████████████████████████| 138/138 [00:00<00:00, 318.99it/s]
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 303.94it/s]
100%|███████████████████████████████████████████████████████████████| 245/245 [00:01<00:00, 170.51it/s]
2021-11-12 15:43:04,178 - INFO - Getting 164 missing users
 99%|██████████████████████████████████████████████████████████████▌| 163/164 [00:01<00:00, 110.06it/s]
2021-11-12 15:43:05,688 - INFO - Creating file github-metrics-sdv-dev-2021-11-12.xlsx
```

## Output

The result is a spreasheet that will contain 5 tabs:

- **Issues**:
    Where all the issues are listed, including data about
    the users who created them.
- **Pull Requests**:
    Where all the pull requests are listed, including data about
    the users who created them.
- **Unique Issue Users**:
    Where the unique users that created issues
    are listed with all the information existing in their profile
- **Unique Contributors**:
    Where the unique users that created pull requests
    are listed with all the information existing in their profile
- **Unique Stargazers**:
    Where the unique users that stargazed the repositories
    are listed with all the information existing in their profile

Optionally, and additional spreadsheet called **Metrics** will be created with the
aggregation metrics for the entire project.

## Google Drive Integration

Github Analytics is capable of reading and writing results in Google Spreadsheets.

For this to work, the following things are required:

1. The `output_path` needs to be given as a Google Drive path with the following format:
   `gdrive://<folder-id>/<filename>`. For example: `***REMOVED***/sdv-dev`

2. A set of Google Drive Credentials need to be provided in the format required by `PyDrive`. The
   credentials can be stored in a `credentials.json` file within the working directory, alongside
   the corresponding `settings.yaml` file, or passed via the `PYDRIVE_CREDENTIALS` environment
   variable.

# Config File Format

The Github Analytics script can be configured using a YAML file with the following contents:
* `output_folder`: Folder where results will be written. Can be a Google Drive in the format
  gdrive://<folder-name>
* `projects`: YAML Dictionary with project names as keys and repository list as values

```yaml
output_folder: <folder-name>
projects:
  <project-name>:
    - <organization>/<repository>
    - <organization>/<repository>
    - ...
  <project-name>:
    - <organization>/<repository>
    - <organization>/<repository>
    - ...
  ...
```

For example, the following config file would only collect data for the `SDV` project,
which would include all the `sdv-dev` libraries, and would store the results inside a
Google Drive folder:

```yaml
output_folder: ***REMOVED***
projects:
  sdv-dev:
  - sdv-dev/SDV
  - sdv-dev/RDT
  - sdv-dev/SDMetrics
  - sdv-dev/SDGym
  - sdv-dev/Copulas
  - sdv-dev/CTGAN
  - sdv-dev/DeepEcho
```

## Default Configuration File

By default, Github Analytics collects the projects configured in the [config.yaml](config.yaml) file
included in the project.

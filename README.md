# OSS Metrics

Scripts to extract multiple metrics from OSS projects.

## Install

```bash
pip install git+ssh://git@github.com/datacebo/oss-metrics
```

### Development

For development, clone the repository and install `dev-requirements.txt`:

```bash
git clone git@github.com:datacebo/oss-metrics
cd oss-metrics
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

In order to run the collection script from python, the `get_github_metrics` function
needs to be imported from the `oss_metrics` package and executed passing the values
indicated above.

**NOTE**: For detailed output, logging must be enabled as shown in the example below.

```python3
>>> import logging
>>> logging.basicConfig(level=logging.INFO)
>>> from oss_metrics import get_github_metrics
>>> repositories = ['sdv-dev/RDT', 'sdv-dev/SDV', 'sdv-dev/Copulas', 'sdv-dev/CTGAN']
>>> output_name = 'sdv-dev'
>>> token = '<my-github-token>'
>>> get_github_metrics(token, repositories, output_name)
INFO:oss_metrics.main:Getting issues and stargazers for sdv-dev/RDT
100%|████████████████████████████████████████████████████| 142/142 [00:00<00:00, 298.76it/s]
100%|███████████████████████████████████████████████████| 37/37 [00:00<00:00, 316067.71it/s]
INFO:oss_metrics.main:Getting issues and stargazers for sdv-dev/SDV
100%|████████████████████████████████████████████████████| 387/387 [00:01<00:00, 200.34it/s]
100%|████████████████████████████████████████████████████| 553/553 [00:03<00:00, 149.46it/s]
INFO:oss_metrics.main:Getting issues and stargazers for sdv-dev/Copulas
100%|████████████████████████████████████████████████████| 138/138 [00:00<00:00, 300.36it/s]
100%|████████████████████████████████████████████████████| 245/245 [00:01<00:00, 217.21it/s]
INFO:oss_metrics.main:Getting issues and stargazers for sdv-dev/CTGAN
100%|████████████████████████████████████████████████████| 112/112 [00:00<00:00, 298.79it/s]
100%|████████████████████████████████████████████████████| 494/494 [00:02<00:00, 175.42it/s]
INFO:oss_metrics.main:Getting users
100%|███████████████████████████████████████████████████▊| 212/213 [00:01<00:00, 122.67it/s]
INFO:oss_metrics.output:Creating file github-metrics-sdv-dev-2021-11-09.xlsx
```


## Command Line Interface

In order to run the collection script from the command line, the `oss-metrics github` command
must be called, passing the output filename with the `-o` flag, the Github token with the
`-t` flag, and the list of repository names separated by spaces.

If the `-t` flag is not provided, the github token will be requested in a prompt:

```bash
$ oss-metrics github -o sdv-dev sdv-dev/RDT sdv-dev/SDV sdv-dev/CTGAN sdv-dev/Copulas
Please input your Github Token: <my-github-token>
2021-11-09 21:05:14,380 - INFO - Getting issues and stargazers for sdv-dev/RDT
100%|████████████████████████████████████████████████████| 142/142 [00:00<00:00, 233.73it/s]
100%|████████████████████████████████████████████████████| 37/37 [00:00<00:00, 73306.21it/s]
2021-11-09 21:05:16,097 - INFO - Getting issues and stargazers for sdv-dev/SDV
100%|████████████████████████████████████████████████████| 387/387 [00:02<00:00, 188.62it/s]
100%|████████████████████████████████████████████████████| 553/553 [00:03<00:00, 152.76it/s]
2021-11-09 21:05:23,149 - INFO - Getting issues and stargazers for sdv-dev/CTGAN
100%|████████████████████████████████████████████████████| 112/112 [00:00<00:00, 259.83it/s]
100%|████████████████████████████████████████████████████| 494/494 [00:02<00:00, 179.36it/s]
2021-11-09 21:05:27,755 - INFO - Getting issues and stargazers for sdv-dev/Copulas
100%|████████████████████████████████████████████████████| 138/138 [00:00<00:00, 348.97it/s]
100%|████████████████████████████████████████████████████| 245/245 [00:01<00:00, 192.98it/s]
2021-11-09 21:05:30,737 - INFO - Getting users
100%|███████████████████████████████████████████████████▋| 212/213 [00:01<00:00, 110.94it/s]
2021-11-09 21:05:32,651 - INFO - Creating file github-metrics-sdv-dev-2021-11-09.xlsx
```

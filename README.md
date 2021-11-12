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
INFO:oss_metrics.main:Getting information for repository sdv-dev/RDT
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 195.00it/s]
100%|███████████████████████████████████████████████████████████████| 182/182 [00:00<00:00, 364.64it/s]
100%|███████████████████████████████████████████████████████████████| 37/37 [00:00<00:00, 91020.09it/s]
INFO:oss_metrics.main:Getting information for repository sdv-dev/SDV
100%|███████████████████████████████████████████████████████████████| 389/389 [00:02<00:00, 193.20it/s]
100%|███████████████████████████████████████████████████████████████| 219/219 [00:00<00:00, 231.17it/s]
100%|███████████████████████████████████████████████████████████████| 561/561 [00:03<00:00, 158.39it/s]
INFO:oss_metrics.main:Getting information for repository sdv-dev/Copulas
100%|███████████████████████████████████████████████████████████████| 138/138 [00:00<00:00, 333.27it/s]
100%|███████████████████████████████████████████████████████████████| 143/143 [00:00<00:00, 287.29it/s]
100%|███████████████████████████████████████████████████████████████| 245/245 [00:01<00:00, 204.88it/s]
INFO:oss_metrics.main:Getting information for repository sdv-dev/CTGAN
100%|███████████████████████████████████████████████████████████████| 113/113 [00:00<00:00, 287.26it/s]
100%|██████████████████████████████████████████████████████████████| 64/64 [00:00<00:00, 134824.44it/s]
100%|███████████████████████████████████████████████████████████████| 498/498 [00:02<00:00, 171.11it/s]
INFO:oss_metrics.main:Getting 164 missing users
 99%|██████████████████████████████████████████████████████████████▌| 163/164 [00:01<00:00, 121.99it/s]
INFO:oss_metrics.output:Creating file github-metrics-sdv-dev-2021-11-12.xlsx
```


## Command Line Interface

In order to run the collection script from the command line, the `oss-metrics github` command
must be called, passing the output filename with the `-o` flag, the Github token with the
`-t` flag, and the list of repository names separated by spaces.

If the `-t` flag is not provided, the github token will be requested in a prompt:

```bash
$ oss-metrics github -o sdv-dev sdv-dev/RDT sdv-dev/SDV sdv-dev/CTGAN sdv-dev/Copulas
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

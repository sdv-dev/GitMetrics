# Data collected by GitHub Analytics
The GitHub Analytics project collects data about GitHub activity for a given repository using
the GitHub API.

This guide explains the metrics that are being collected.

## Aggregation Metrics

If the `--add-metrics` option is passed to `github-analytics`, a spreadsheet with the following
metrics will be added to the results CSV file for each repository.

* **By Month:** Number of downloads per month and increase in the number of downloads from month to month.
* **num_issues**: Total number of Issues
* **num_pull_requests**: Total number of Pull Requests
* **num_users**: Total number of Issue Users
* **num_contgributors**: Total number of Contributors
* **num_stargazers**: Total number of Stargazers
* **num_non_contributor_users**: Total number of Users that are not Contributors
* **num_non_contributor_stargazers**: Total number of Stargazers that are not Contributors
* **USR**: Users / Stargazers ratio
* **USR-C**: USR Excluding Contributors

## Results

The other spreadsheets that are added are an itemized list of the following:

* **Issues**: The GitHub issues that have been created in the given repository.
* **Pull Requests**: The GitHub pull requests that have been created in the given repository.
* **Unique Issue Users**: The GitHub users that have opened issues in the given repository.
* **Unique Contributors**: The GitHub users that have contributed code to the given repository.
* **Unique Stargazers**: The GitHub users that have starred the given repository.

## Adding a new metric

In order to add a new metric to the aggregation metrics speadsheet, please update the
[metrics.py](https://github.com/datacebo/github-analytics/blob/main/github_analytics/metrics.py) file and add the new metric as a column to the returned DataFrame.

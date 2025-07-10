# GitMetrics Configuration

The GitMetrics script can be configured using a YAML file that indicates which repositories
to collect and where to store the collected data.

Additionally, [GitMetrics Workflows](.github/workflows) are being used to trigger the
collection of such projects either manually or on a scheduled basis.

## Configuration file format

The configuration file for `gitmetrics` must have the following contents:

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
which would include all the repositories listed, and would store the results inside a
Google Drive folder:

```yaml
output_folder: gdrive://1OPhUPTFWN994QnbcrSojQ9Egf9s7MuHV
projects:
  SDV:
  - sdv-dev/SDV
  - sdv-dev/RDT
  - sdv-dev/SDMetrics
  - sdv-dev/SDGym
  - sdv-dev/Copulas
  - sdv-dev/CTGAN
  - sdv-dev/DeepEcho
```

### Adding an entire organization

Optionally, an organization or user name can be added to the confiuration instead of the
individual repositories, and then `gitmetrics` will translate that into the list of
repositories owned by that user or organization *which are not forks of other repositories*.

For example, this configuration file would include all the repositories listed above,
as well as any other public repository that exists within the `sdv-dev` organization and is
not a fork:

```yaml
projects:
  SDV:
  - sdv-dev
```

Notice that combining this format with a list of individual repositories is possible.

The following configuration would include all the public repositories within the `alteryx`
organization as well as the `featurlabs/henchman` and `featurelabs/predict-restaurant-rating`
repositories, but would skip any other repository from the `featurelabs` organization that
is not explicitly listed:

```yaml
projects:
  featuretools:
  - alteryx
  - featurlabs/henchman
  - featurelabs/predict-restaurant-rating
```

## Default Configuration File

By default, GitMetrics collects the projects configured in the [config.yaml](config.yaml)
file included in the project. However, passing a different configuration file when running the
command line script is possible via the `-c` flag, as shown in the example above:

```bash
$ gitmetrics collect -c my_config_file.yaml ...
```

### Importing other configuration files

When defining a configuration file it is possible to import and re-use the contents of another
configuration file with the `import_config` entry.

For example, this configuration file would implicitly contain the same projects as the
`config.yaml` file, because it imports it, but point at a different output folder:

```yaml
import_config: config.yaml
output_folder: my_output
```

### Importing the projects of another configuration file

When another configuration file is imported, it is possible to define a custom set of projects
(and repositories), while re-using some of the projects listed in the imported config file.

For example, if the contents of the `my_base_config.yaml` file are:

```yaml
output_folder: an_output_folder
projects:
  sdv-dev:
  - sdv-dev/SDV
  - sdv-dev/RDT
  - sdv-dev/CTGAN
  - sdv-dev/Copulas
  - sdv-dev/DeepEcho
  - sdv-dev/SDMetrics
  - sdv-dev/SDGym
  pycaret:
  - pycaret/pycaret
  scikit-learn:
  - scikit-learn/scikit-learn
  featuretools:
  - alteryx
```

The following configuration file would collect data for the `sdv-dev` and `featuretools` projects
listed above (i.e. all the `sdv-dev` repositories listed above + all the repositories in the
`alteryx` organization), as well as the `pandas-dev/pandas` repository that is added here, and
store the results in a different output folder:

```yaml
import_config: my_base_config.yaml
output_folder: another_output_folder
projects:
  sdv-dev:
  featuretools:
  pandas:
  - pandas-dev/pandas
```

## Daily and Weekly Collection

GitMetrics is configured to collect data daily and weekly via the
[.github/workflow/daily.yaml](.github/workflow/daily.yaml) and [.github/workflow/weekly.yaml](
.github/workflow/weekly.yaml) GitHub Action Workflows.

These workflows are configured to execute the `gitmetrics collect` command using the
[daily.yaml](daily.yaml) and [weekly.yaml](weekly.yaml) configuration files respectively,
which:
- Import the [config.yaml](config.yaml) file, where all the project repositories are listed
- Define the output folder that will be used for each periodicity
- Define the list of projects that will be collected, re-using the list of repositories
  defined in the base [config.yaml](config.yaml) file.

### Adding new projects an/or repositories

In order to add new projects or repositories to the daily or weekly collection, the following
steps must be followed:

1. Edit the [config.yaml](config.yaml) file to add the new projects and/or repositories.
2. If a new project was added, edit the [daily.yaml](daily.yaml) or [weekly.yaml](weekly.yaml)
   file (depending on the desired periodicity) and add the project name to the list without
   adding any of the underlying project repositories, since these will be taken from the
   [config.yaml](config.yaml) file.

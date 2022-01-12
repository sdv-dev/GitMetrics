# GitHub Analytics Setup

The GitHub Analytics project requires privileged access to the following resources:
- Google Drive, which is accessed via the `PyDrive` library.

In this document we cover how to generate generate and configure credentials to authenticate
with these two services.

## Local Setup

### PyDrive Cretentials

In order to authenticate with Google Drive you will need the OSS Metrics GCP application keys,
which should be stored in a `settings.yaml` file within the project folder with the following
format:

```yaml
client_config_backend: settings
client_config:
  client_id: <client-id>
  client_secret: <client-secret>

save_credentials: True
save_credentials_backend: file
save_credentials_file: credentials.json
```

**IMPORTANT**: Notice that this file should never be committed alongside the code, since
if contains the application KEY which should never be made public.

TODO 

## Github Actions Setup

When using GitHub Analytics via GitHub Actions, the authentication credentials for Google
Drive and Big Query must be passed as repository `secrets`, which will later on be declared
as environment variables.

1. Open the [Settings page of the GitHub Analytics repository](
   https://github.com/datacebo/github-analytics/settings/secrets/actions) and click on `Secrets`.

2. If the `secret` that you will create does not exist yet, click on `New Repository Secret`,
   otherwise click on the `Update` button of the corresponding secret to update its value.

3. Paste the contents of the credentials JSON file in the box and click update. The following
   secrets need to be created for each credentials file:
   - `PYDRIVE_CREDENTIALS` for the `credentials.json` file that you created in the steps above.

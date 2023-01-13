# Python Migrate Tool

Custom tool to migrate data from one GitHub environment to another.

## Dev Container

The project is configured to run in a [VS Code Dev Container](https://code.visualstudio.com/docs/remote/containers). This allows you to run the project in a Docker container with all the required dependencies installed. It can also run on Codespaces. The environment is pre-configured with the following:
- PyTest
- Flake8
- Black
- VS Code extensions to support the development.

## Configuration

The code supports both command line options and a configuration file in the following format:

```yml
dest_token: ghp_SOMETOKEN
dest_org: dest-org

src_hostname: api.github.com
src_token: ghp_DESTTOKEN
src_org: erc-org
```

This enables the command line parameters to be centralized and referenced from a single location using `-c config.yml` or `--config config.yml`. To support commands that need to target a single environment, `-p src` or `-p dest` can be used to filter the configuration file to provide `hostname`, `org`, and `token`.
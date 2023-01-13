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

## Modules

- `migrate` - Main module for the tool
  - `main.py` - Main entry point, responsible for pulling in the handlers and options.
  - `common` - Common functions and classes
    - `types.py` - Shared type definitions (enumerations and dataclass base)
    - `api.py` - Shared methods for interacting with the GitHub API using GhApi
    - `options.py` - Shared methods for parsing command line options using Click. This is divided into two primary groups of options: TargetState (commands targeting a single GitHub environment) and MigrationState (commands targeting a source and destination GitHub environment). TargetState context commands support using `-p` or `prefix` to remove a prefix from keys in a configuration file. Both contexts support using `-c` or `config` to specify a configuration file. MigrationState based commands use `pass_migrationstate` to pass the common parameters and `migration_options` to configure the Click `options`. TargetState based commands use `pass_targetstate` to pass the common parameters and `target_options` to configure the Click `options`.
    - `environment` - Repository Environment-related APIs
    - `orgs` - Organization-related APIs
    - `repos` - Repository-related APIs
  - `handlers` - defines the Click-based command line options, with a handler per group of commands. These can be refactored into additional subcommands in the future.
    - `orgs` - Organization-related command line options. Invokes the appropriate APIs to operate on organizations, generally from `common.orgs`.
    - `repos` - Repository-related command line options. Invokes the appropriate APIs to operate on repositories, generally from `common.repos`.
- `tests` - Unit and integration tests

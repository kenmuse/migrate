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
    - `org` - Organization-related command line options. Invokes the appropriate APIs to operate on organizations, generally from `common.orgs`. Modules in this package implement additional subcommands.
    - `repo` - Repository-related command line options. Invokes the appropriate APIs to operate on repositories, generally from `common.repos`. Modules in this package implement additional subcommands.
    - `enterprise` - Enterprise-related command line options. Invokes the appropriate APIs to operate on enterprise resources. Modules in this package implement additional subcommands.
- `tests` - Unit and integration tests

At the root of the project are the following files which support the packaging and deployment process:

- `entitlements.plist` - macOS entitlements file. This supports compiling a signable console application on macOS.
- `migrate.py` - PyInstaller entry point. This is a wrapper around `migrate.main` to support running as a script. PyInstaller does not support running modules directly and requires the entry script to not contain relative imports. There are known issues with the module resolution if the script is located within the root package folder.
- `migrate.spec` - PyInstaller configuration file, configured to use the entry point `migrate.py` and the `--onefile option` (to create a single executable file).
- `pyproject.toml` - Python project configuration file. This is used to manage the dependencies and build the application.

## Command-line

The application is invoked using `python -m migrate.main`. By default, help will be displayed for each verb or action that is available. The application also supports running as a script using `python migrate/main.py`.

## Platform-specific compilation

The application is compiled to a native executabl using PyInstaller. The following command is used to compile the application:

```bash
pyinstaller migrate.spec
```

or alternatively,

```bash
pyinstaller --onefile migrate.py
```

Note that PyInstaller does not support cross-compilation and will only compile for the currently targeted system.
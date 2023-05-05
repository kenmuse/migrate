# Python Migrate Tool

Custom tool to migrate data from one GitHub environment to another.

## Dev Container

The project is configured to run in a [VS Code Dev Container](https://code.visualstudio.com/docs/remote/containers). This allows you to run the project in a Docker container with all the required dependencies installed. It can also run on Codespaces. The environment is pre-configured with the following:
- PyTest
- Flake8
- Black
- VS Code extensions to support the development.

## Dependencies

The dependencies are automatically installed when running in the dev container. If a dev container is not being used, you'll need to ensure Python 3.11 is installed. They run the following:

```bash
python3 -m pip install --user --editable .
python3 -m pip install --user --editable ".[dev]"
```

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

## Virtual Environments

If you're using the dev container directly, virtual environments are not needed. The container is configured as a dedicated space, and the packages are automatically installed using `pip` when the container starts. This includes the developer extras, such as `pyinstaller`. If you're creating a virtual environment, you can use the following commands to install the packages needed for development:

```bash
python -m pip install -e .
python -m pip install ".[dev]"
```

## Platform-specific compilation

The application can be compiled to a native executable using PyInstaller. The following command is used to compile the application, creating a single executable file in the `/dist` folder:

Use the provided spec file:

```bash
pyinstaller migrate.spec
```

Or, use the equivalent command line:

```bash
pyinstaller --onefile --hidden-import=cffi --hidden-import=charset_normalizer migrate.py
```

Note that PyInstaller does not support cross-compilation and will only compile for the currently targeted system. The `--hidden-import` option is required to ensure that indirectly referenced modules are properly included when building on macOS and Windows.

For builds outside of the dev container, a standalone script `build.sh` is provided which can restore the required packages and compile the application.

## Building for Linux in Docker

The dev container can be used to build the application for systems derived from Debian 11.

Starting on the command line in the root of the project, use the following commands to create a container and run the build:

```bash
cd .devcontainer
docker build -t python311 .
docker run -it --rm -v "$(pwd)/..:/src" python311 /src/build.sh
```

The executable will be located in the `dist` folder in the root of the project.
Optionally, you can use `--platform linux/amd64` or `--platform linux/arm64` with both `docker run` and `docker build` to compile for a specific platform. For example:

```bash
cd .devcontainer
docker build --platform linux/arm64 -t python311 .
docker run --rm --platform linux/arm64 -it -v "$(pwd)/..:/src" python311 /src/build.sh
```

## Building for Centos 7

To compile for Centos using the provided Dockerfile, use the `Dockerfile.centos` file in the `docker` folder. To build the image for the current system architecture, use the following command:

```bash
docker build -f docker/Dockerfile.centos -t python311-centos7 .
```

To build for a specific architectures (`linux/arm64`, `linux/amd64`), specify the `--platform` option:

```bash
docker build --platform linux/amd64 -f docker/Dockerfile.centos -t python311-centos7  .
```

To run the container, use the following command:

```bash
docker run -it -v "$(pwd)/..:/src" --rm python311-centos7 /src/build.sh
```

## Building for Windows in Linux (Wine)

The application can be compiled using Windows with Python or using Wine in Docker. For example, the `tobix/pywine:3.11` image can be used to create a valid executable.

To build the executable, use the following command:

```bash
docker run -it -v "$(pwd)/..:/src" --rm tobix:/pywine:3.11 /src/build_wine.sh
```

The executable will be located in the `dist` folder in the root of the project.

## Building for macOS

The steps are the same as for Linux, except that Docker is not used:

```bash
python3 -m pip install --user .
python3 -m pip install --user ".[dev]"
pyinstaller migrate.spec
```

Note that outside of a development environment, Apple requires the application to be signed for distribution. Otherwise, users will see a warning. The details for signing an application can be found [here](https://www.kenmuse.com/blog/notarizing-dotnet-console-apps-for-macos/#signing-the-code). An entitlements file is provided in the root of the project to support this process.

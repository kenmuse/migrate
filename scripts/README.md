# Build scripts

This folder contains build scripts for compiling the application.

| Script | Description |
| ------ | ----------- |
| build_linux.sh | Builds the application in Python on Linux. |
| build_windows.ps1 | Builds the application in Python on Windows. |
| build_wine.sh | Builds the application for Windows using Wine on Linux (via `tobix/pywine` image). The PowerShell script is not invoked due to the lack of support for PowerShell in Wine. There are ways to workaround the problem using PowerShell core, but that isn't implemented yet. |
| build.py | The main build script, encapsulating all of the steps to build executables for all of the various platforms. Validates the environment and runs the above scripts in an appropriate container. This could also be written in any scripting language or using build tools such as Make. |

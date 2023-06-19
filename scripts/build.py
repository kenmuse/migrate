#!/usr/bin/env python3

######################################################################
# This script builds the binary applications for Linux and Windows
# using a Debian or Ubuntu host
######################################################################

import argparse
import os
import pathlib
import platform
import subprocess
import shutil
import sys
import tempfile

######################################################################
# Constants
######################################################################

"""The maximum time to wait for a process to complete"""
MAX_PROCESSING_TIME = 200 * 60  # in seconds (200 minutes)

"""Local image name for the Centos 7 image created to build the binaries"""
CENTOS_IMAGE_NAME = "python-centos"

"""Indicates whether the script is executing on a GitHub Action runner"""
IS_RUNNER = os.environ.get("RUNNER_USER", None) is not None

"""Location for source files on the Docker images"""
SOURCE_ROOT = "/src"

"""Folder containing build scripts """
SCRIPT_FOLDER = "scripts"

"""Location for build scripts on the Docker images"""
SCRIPT_ROOT = f"{SOURCE_ROOT}/scripts"

"""The version of Python to use by default for builds"""
DEFAULT_PYTHON_VERSION = "3.11"

######################################################################
## Identify the root path to the source code
######################################################################
dir_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()

######################################################################
## Configure a parser to read the command line arguments
######################################################################
parser = argparse.ArgumentParser
parser = argparse.ArgumentParser(
    description="Build script", formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    "-v",
    "--pythonVersion",
    help="Python image version for builds",
    default=DEFAULT_PYTHON_VERSION,
)
parser.add_argument(
    "-f", "--folder", help="Artifacts folder", default=os.path.join(dir_path, "artifacts")
)
parser.add_argument(
    "-t",
    "--targets",
    help="Comma separated OS (windows, linux, centos) and arch (amd64, arm64)",
    type=str,
)
args = parser.parse_args()

targets = (
    args.targets.split(",")
    if args.targets
    else ["linux/amd64", "centos/amd64", "windows/amd64"]  # "centos/arm64", "linux/arm64"
)

######################################################################
## Helper Functions
######################################################################


def log_group_start(message):
    """Logs a message, starting a group on an Actions runner"""
    if not IS_RUNNER:
        print(message)
    else:
        print(f"::group::{message}")


def log_group_end(message):
    """Logs a message, ending a group on an Actions runner"""
    print(message)
    if IS_RUNNER:
        print("::endgroup::")


def get_user_id():
    """Gets the user identifier to use for building the Docker container"""

    # Return the current user for local dev container runs
    # Inside Actions, this will always be root (0:0), so ignore
    # return ['--user', f'{os.getuid()}:{os.getgid()}'] if not IS_RUNNER else []
    return ["--user", "root"]


def create_volume_map():
    """Maps volumes required by the Docker container"""

    return ["-v", f"{dir_path}:{SOURCE_ROOT}"]


def move_to_output(platform, file_name):
    """Moves the compiled binary to the artifacts folder"""

    target_folder = get_artifact_folder(platform)
    source = os.path.join(dir_path, "dist", file_name)
    target = os.path.join(target_folder, file_name)
    shutil.copy(source, target)


def get_artifact_folder(platform_identifier):
    """Gets the folder to store the build artifacts for a specific platform"""
    artifacts_folder = os.path.abspath(args.folder)
    target_folder = os.path.join(artifacts_folder, platform_identifier)
    os.makedirs(target_folder, exist_ok=True)
    return target_folder


def clean_build_folders():
    """Cleans the build and dist folders used for the compilation steps
    Note: Requires `sudo` to delete folders that are owned by root
    """

    build_folder = os.path.join(dir_path, "build")
    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    dist_folder = os.path.join(dir_path, "dist")
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)


def run_docker(message, parameters):
    """Runs a docker command"""

    log_group_start(f"Start: {message}")

    command = " ".join(parameters)
    print(f"Running: docker {command}")
    try:
        argument_list = ["docker"] + parameters
        result = subprocess.run(argument_list, timeout=MAX_PROCESSING_TIME)
        result.check_returncode()
        log_group_end(f"Complete: {message}")

    except (subprocess.CalledProcessError, FileNotFoundError):
        log_group_end(f"Failed: {message}")
        exit(1)

def get_powershell_executable():
    """Gets the name of the PowerShell executable"""
    if app_must_exist('pwsh', exit_on_failure=False):
        return 'pwsh'
    elif app_must_exist('powershell', parameters=['/?'], exit_on_failure=True):
        return 'powershell'

def app_must_exist(app_name, parameters=["--version"], exit_on_failure=True):
    """Ensures the application exists on the host and exits or returns false if it is missing"""

    try:
        print(f"Searching for {app_name}...")
        result = subprocess.run([app_name] + parameters, timeout=10)
        result.check_returncode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Failed to find {app_name}")
        if exit_on_failure:
            exit(1)
        else:
            return False
    return True


def get_docker_run_arguments(platform_arch, image, script):
    base = ["run", "--rm", "--platform", f"linux/{platform_arch}", "-w", SOURCE_ROOT]
    target = [image, f"{SCRIPT_ROOT}/{script}"]
    volume_map = create_volume_map()
    return base + get_user_id() + volume_map + target


def build_linux_platform(image, platform_arch):
    """Builds Linux binaries using the Docker image"""

    clean_build_folders()
    docker_args = get_docker_run_arguments(platform_arch, image, "build_linux.sh")
    run_docker(
        f"Pulling {platform_arch} image",
        ["pull", "--platform", f"linux/{platform_arch}", image],
    )
    run_docker(f"Building {platform_arch} binaries", docker_args)
    move_to_output(f"linux-{platform_arch}", "migrate")


def ensure_qemu_configured():
    """Ensures QEMU is installed and configured (enables builds for multiple architectures)"""

    if sys.platform != "win32" and not IS_RUNNER:
        print(
            "Confirming setup - Requires apt-get install qemu qemu-user-static binfmt-support"
        )
        if platform.machine() != "aarch64":
            app_must_exist("qemu-aarch64-static")
        else:
            app_must_exist("qemu-x86_64-static")
        app_must_exist("update-binfmts")
        run_docker(
            "Setting up multiarch support",
            [
                "run",
                "--rm",
                "--privileged",
                "tonistiigi/binfmt:latest",
                "--install",
                "-all",
            ],
        )


def build_windows():
    """Builds the Windows binaries using PyWine"""

    clean_build_folders()
    if sys.platform != "win32":
        pywine_image = f"tobix/pywine:{args.pythonVersion}"
        docker_args = get_docker_run_arguments("amd64", pywine_image, f"build_wine.sh")
        run_docker(
            f"Pulling PyWine image", ["pull", "--platform", f"linux/amd64", pywine_image]
        )
        run_docker(f"Building Windows binaries", docker_args)
        move_to_output("windows-amd64", "migrate.exe")
    elif sys.version.startswith(args.pythonVersion):
        print("Supported Python runtime detected. Running local Windows build")
        ps_exe = get_powershell_executable()
        subprocess.run(
            [ps_exe, os.path.join(dir_path, SCRIPT_FOLDER, "build_windows.ps1")], timeout=MAX_PROCESSING_TIME
        ).check_returncode()
        move_to_output(f"win-amd64", "migrate.exe")
    else:
        print(
            f"Windows build not supported on Windows host without Python {args.pythonVersion}"
        )


def build_centos_platform(platform_arch):
    """Compiles the Centos 7 binaries targeting a specific platform architecture"""

    clean_build_folders()
    build_centos_container_image(platform_arch)
    docker_args = get_docker_run_arguments(platform_arch, CENTOS_IMAGE_NAME, "build_linux.sh")
    run_docker(f"Building for {platform_arch}", docker_args)
    move_to_output(f"centos-{platform_arch}", "migrate")


def build_centos_container_image(target_platform):
    """Creates required multi-arch Centos 7 container images for building code"""

    run_docker("Configuring BuildX", ["buildx", "create", "--use"])
    run_docker(
        "Creating CentOS images",
        [
            "buildx",
            "build",
            "--output=type=docker",
            "--platform",
            target_platform,
            "-f",
            "docker/Dockerfile.centos",
            "-t",
            CENTOS_IMAGE_NAME,
            ".",
        ],
    )


######################################################################
# Build process
######################################################################


def build():
    """Implements the steps of the build process"""

    ## Select a Python Docker image. The MCR variant defines a non-root user.
    # image = f'python:{args.pythonVersion}-bullseye'
    image = f"mcr.microsoft.com/devcontainers/python:{args.pythonVersion}-bullseye"

    ## Steps
    app_must_exist("docker")

    ## Requires apt-get install packages: qemu qemu-user-static binfmt-support
    ensure_qemu_configured()

    centos_arch = [target.split("/")[1] for target in targets if "centos/" in target]
    for arch in centos_arch:
        build_centos_platform(arch)

    linux_arch = [target.split("/")[1] for target in targets if "linux/" in target]
    for arch in linux_arch:
        build_linux_platform(image, arch)

    if "windows/amd64" in targets:
        build_windows()


######################################################################
# Entrypoint
######################################################################

if __name__ == "__main__":
    build()

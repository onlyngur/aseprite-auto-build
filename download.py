import requests
import os
import platform
import subprocess
import sys

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME_MACOS = 'Skia-macOS-Release-arm64.zip'

def get_latest_tag(repository):
    """Fetch the latest tag from the given GitHub repository."""
    url = f'https://api.github.com/repos/{repository}/releases/latest'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['tag_name']

def save_tag_to_file(tag, filename='version.txt'):
    """Save the given tag to a file."""
    with open(filename, 'w') as f:
        f.write(tag)

def clone_repository(repository, tag, dest_folder):
    """Clone a Git repository with a specific tag and initialize submodules."""
    clone_url = f'https://github.com/{repository}.git'
    git_cmd = ['git', 'clone', '-b', tag, clone_url, dest_folder, '--depth', '1']
    try:
        subprocess.run(git_cmd, check=True)
        subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'], cwd=dest_folder, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}", file=sys.stderr)
        sys.exit(1)

def clone_depot_tools():
    """Clone depot_tools repository and update the PATH environment variable."""
    home_deps = os.path.expanduser('~/deps')
    depot_tools_path = os.path.join(home_deps, 'depot_tools')
    
    os.makedirs(home_deps, exist_ok=True)
    
    if not os.path.exists(depot_tools_path):
        try:
            subprocess.run(['git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git', depot_tools_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning depot_tools: {e}", file=sys.stderr)
            sys.exit(1)
    
    path_entry = f'{depot_tools_path}:{os.environ.get("PATH", "")}'
    os.environ['PATH'] = path_entry
    
    with open('/github_env', 'w') as f:
        f.write(f'PATH={path_entry}\n')

def download_and_extract_skia(tag):
    """Download and extract the SKIA release file for macOS."""
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME_MACOS}'
    try:
        file_response = requests.get(download_url)
        file_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading SKIA release: {e}", file=sys.stderr)
        sys.exit(1)

    save_path = os.path.expanduser(f'~/deps/{SKIA_RELEASE_FILE_NAME_MACOS}')
    extract_path = os.path.expanduser('~/deps/skia')

    try:
        with open(save_path, 'wb') as f:
            f.write(file_response.content)

        subprocess.run(['unzip', save_path, '-d', extract_path], check=True)
    except (IOError, subprocess.CalledProcessError) as e:
        print(f"Error handling SKIA file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to orchestrate the tasks."""
    try:
        aseprite_tag = get_latest_tag(ASEPRITE_REPOSITORY)
        save_tag_to_file(aseprite_tag)
        clone_repository(ASEPRITE_REPOSITORY, aseprite_tag, 'src/aseprite')

        skia_tag = get_latest_tag(SKIA_REPOSITORY)

        if platform.system() == 'Darwin':
            clone_depot_tools()
            download_and_extract_skia(skia_tag)
        else:
            print("This script currently only supports macOS.")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
import requests
import os
import platform

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME_MACOS = 'Skia-macOS-Release-arm64.zip'  # Assume there's a macOS build

def get_latest_tag_aseprite():
    response = requests.get(f'https://api.github.com/repos/{ASEPRITE_REPOSITORY}/releases/latest')
    response.raise_for_status()
    response_json = response.json()
    return response_json['tag_name']

def save_aseprite_tag(tag):
    with open('version.txt', 'w') as f:
        f.write(tag)

def clone_aseprite(tag):
    clone_url = f'https://github.com/{ASEPRITE_REPOSITORY}.git'
    git_cmd = f'git clone -b {tag} {clone_url} src/aseprite --depth 1'
    os.system(git_cmd)
    os.system('cd src/aseprite && git submodule update --init --recursive')

def get_latest_tag_skia():
    response = requests.get(f'https://api.github.com/repos/{SKIA_REPOSITORY}/releases/latest')
    response.raise_for_status()
    response_json = response.json()
    return response_json['tag_name']

def clone_depot_tools():
    home_deps = os.path.expanduser('$HOME/deps')
    depot_tools_path = os.path.join(home_deps, 'depot_tools')
    
    # Create the directory if it does not exist
    os.makedirs(home_deps, exist_ok=True)
    
    # Clone depot_tools repository
    if not os.path.exists(depot_tools_path):
        subprocess.run(['git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git', depot_tools_path], check=True)
    
    # Update PATH environment variable
    path_entry = f'{depot_tools_path}:{os.environ.get("PATH", "")}'
    os.environ['PATH'] = path_entry
    
    # Write PATH update to the environment variable file
    with open('/github_env', 'w') as f:
        f.write(f'PATH={path_entry}\n')

def download_skia_for_macos(tag):
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME_MACOS}'
    file_response = requests.get(download_url)
    file_response.raise_for_status()

    # Define the paths for saving and extracting
    save_path = os.path.expanduser(f'$HOME/deps/{SKIA_RELEASE_FILE_NAME_MACOS}')
    extract_path = os.path.expanduser(f'$HOME/deps/skia')

    # Save the downloaded file
    with open(save_path, 'wb') as f:
        f.write(file_response.content)

    # Unzip the downloaded file
    os.system(f'unzip {save_path} -d {extract_path}')

if __name__ == '__main__':
    aseprite_tag = get_latest_tag_aseprite()
    clone_aseprite(aseprite_tag)
    save_aseprite_tag(aseprite_tag)

    skia_tag = get_latest_tag_skia()
    
    if platform.system() == 'Darwin':  # Checks if the OS is macOS
		clone_depot_tools()
        download_skia_for_macos(skia_tag)
    else:
        print("This script currently only supports macOS.")
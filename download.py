import requests
import os
import subprocess
import platform

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME_MACOS = 'Skia-macOS-Release-arm64.zip'

def get_latest_tag(repo):
    response = requests.get(f'https://api.github.com/repos/{repo}/releases/latest')
    response.raise_for_status()
    return response.json()['tag_name']

def save_tag(tag, filename='version.txt'):
    with open(filename, 'w') as f:
        f.write(tag)

def clone_repository(repo, tag, dest, depth=1):
    clone_url = f'https://github.com/{repo}.git'
    subprocess.run(['git', 'clone', '-b', tag, clone_url, dest, '--depth', str(depth)], check=True)
    subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'], cwd=dest, check=True)

def clone_depot_tools():
    home_deps = os.path.expanduser('$HOME/deps')
    depot_tools_path = os.path.join(home_deps, 'depot_tools')
    
    os.makedirs(home_deps, exist_ok=True)
    
    if not os.path.exists(depot_tools_path):
        subprocess.run(['git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git', depot_tools_path], check=True)
    
    # Update PATH environment variable
    path_entry = f'{depot_tools_path}:{os.environ.get("PATH", "")}'
    os.environ['PATH'] = path_entry
    
    # Write PATH update to the environment variable file
    with open('/github_env', 'w') as f:
        f.write(f'PATH={path_entry}\n')

def download_and_extract_skia(tag):
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME_MACOS}'
    response = requests.get(download_url)
    response.raise_for_status()
    
    save_path = os.path.expanduser(f'$HOME/deps/{SKIA_RELEASE_FILE_NAME_MACOS}')
    extract_path = os.path.expanduser(f'$HOME/deps/skia')

    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    subprocess.run(['unzip', '-o', save_path, '-d', extract_path], check=True)

if __name__ == '__main__':
    aseprite_tag = get_latest_tag(ASEPRITE_REPOSITORY)
    clone_repository(ASEPRITE_REPOSITORY, aseprite_tag, 'src/aseprite')
    save_tag(aseprite_tag)

    skia_tag = get_latest_tag(SKIA_REPOSITORY)
    
    if platform.system() == 'Darwin':  # macOS check
        clone_depot_tools()
        download_and_extract_skia(skia_tag)
    else:
        print("This script currently only supports macOS.")
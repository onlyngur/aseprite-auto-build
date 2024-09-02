import requests
import os
import platform

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME_MACOS = 'Skia-macOS-Release-x64.zip'  # Assume there's a macOS build

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

def download_skia_for_macos(tag):
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME_MACOS}'
    file_response = requests.get(download_url)
    file_response.raise_for_status()

    # Save the downloaded file
    with open(f'src/{SKIA_RELEASE_FILE_NAME_MACOS}', 'wb') as f:
        f.write(file_response.content)

    # Unzip the downloaded file
    os.system(f'unzip src/{SKIA_RELEASE_FILE_NAME_MACOS} -d src/skia')

if __name__ == '__main__':
    aseprite_tag = get_latest_tag_aseprite()
    clone_aseprite(aseprite_tag)
    save_aseprite_tag(aseprite_tag)

    skia_tag = get_latest_tag_skia()
    
    if platform.system() == 'Darwin':  # Checks if the OS is macOS
        download_skia_for_macos(skia_tag)
    else:
        print("This script currently only supports macOS.")
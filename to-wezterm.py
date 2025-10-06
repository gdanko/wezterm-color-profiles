#!/usr/bin/env python3

from glob import glob
from pathlib import Path
from pprint import pprint
from urllib.parse import urlparse
import argparse
import json
import os
import plistlib
import re
import shutil
import string
import subprocess
import sys
import tempfile

def which(binary: str) -> bool:
    return shutil.which(binary)

def clone_repo(tempdir: str=None, repo_url: string=None):
    parsed = urlparse(repo_url)
    repo_name = Path(parsed.path).stem
    repo_root = Path(tempdir.name) / repo_name

    print(f'Cloning {repo_url} to {repo_root}....')

    command = ['git', 'clone', repo_url, repo_root]
    result = subprocess.run(
        command,
        capture_output = True,
        text           = True,
        check          = False,
    )

    return result.returncode, result.stderr.strip(), repo_root

# iTerm2 stuff
def rgba_to_hex(d):
    r = int(d['Red Component'] * 255)
    g = int(d['Green Component'] * 255)
    b = int(d['Blue Component'] * 255)
    return f'#{r:02X}{g:02X}{b:02X}'.lower()

def extract_colors(data):
    keys = {
        'foreground'   : f'Foreground Color',
        'background'   : f'Background Color',
        'cursor_bg'    : f'Cursor Color',
        'cursor_fg'    : f'Cursor Text Color',
        'selection_bg' : f'Selection Color',
        'selection_fg' : f'Selected Text Color',
        'ansi'         : [f'Ansi {i} Color' for i in range(8)],
        'brights'      : [f'Ansi {i} Color' for i in range(8, 16)],
    }

    colors = {}
    for k, v in keys.items():
        try:
            if isinstance(v, list):
                colors[k] = [rgba_to_hex(data[name]) for name in v if name in data]
            else:
                if v in data:
                    colors[k] = rgba_to_hex(data[v])
        except KeyError:
            pass
    return colors

def convert_iterm2_colors(repo_root):
    all_themes = {}
    files = glob(f'{repo_root}/schemes/*.itermcolors')
    files = sorted(files)

    for path in files:
        theme_name = os.path.splitext(os.path.basename(path))[0]
        with open(path, 'rb') as f:
            data = plistlib.load(f)

        theme_entry = {}
        theme_entry = extract_colors(data)
        all_themes[theme_name] = theme_entry

    return all_themes

# Kitty Term stuff
def convert_kitty_colors(repo_root):
    all_themes = {}
    files = glob(f'{repo_root}/themes/*.conf')
    files = sorted(files)

    for path in files:
        field_map = {
            'foreground'           : 'foreground',
            'background'           : 'background',
            'cursor_text_color'    : 'cursor_fg',
            'cursor'               : 'cursor_bg',
            'selection_foreground' : 'selection_fg',
            'selection_background' : 'selection_bg',
        }
        color_scheme = {}
        path_no_ext = Path(path).stem
        title = path_no_ext.replace('_', ' ').replace('-', ' ')
        if ' ' in title:
            title = string.capwords(title)
        else:
            title = title.title()

        all_themes[title] = {
            'ansi'    : [],
            'brights' : [],
        }

        with open(path, 'r') as f:
            contents = f.read()
            for key, value in field_map.items():
                match = re.search(rf'{key}\s+(#[a-zA-Z0-9]+)', contents, re.MULTILINE)
                if match:
                    all_themes[title][value] = match.group(1).lower()
            
            for idx in [0, 1, 2, 3, 4, 5, 6, 7]:
                match = re.search(rf'color{idx}\s+(#[a-zA-Z0-9]+)', contents, re.MULTILINE)
                if match:
                    all_themes[title]['ansi'].append(match.group(1).lower())

            for idx in [8, 9, 10, 11, 12, 13, 14, 15]:
                match = re.search(rf'color{idx}\s+(#[a-zA-Z0-9]+)', contents, re.MULTILINE)
                if match:
                    all_themes[title]['brights'].append(match.group(1).lower())

    return all_themes

def do_iterm2(tempdir: str=None):
    repo_url = 'https://github.com/mbadolato/iTerm2-Color-schemes.git'
    returncode, stderr, repo_root = clone_repo(tempdir=tempdir, repo_url=repo_url)
    if returncode != 0:
        print(f'Failed to clone the iTerm2 themes repository: {str(stderr)}')
        sys.exit(1)
    
    print('Generating the WezTerm color themes from Iterm2 themes....')
    return convert_iterm2_colors(repo_root)

def do_kitty(tempdir: str=None):
    repo_url = 'https://github.com/kovidgoyal/kitty-themes.git'
    returncode, stderr, repo_root = clone_repo(tempdir=tempdir, repo_url=repo_url)
    if returncode != 0:
        print(f'Failed to clone the Kitty Term themes repository: {str(stderr)}')
        sys.exit(1)
    
    print('Generating the WezTerm color themes from Kitty Term themes....')
    return convert_kitty_colors(repo_root)

def main():
    parser = argparse.ArgumentParser(description='Convert iTerm2 and/or Kitty Term color themes to a format WezTerm can read')
    parser.add_argument('-i', '--iterm2', action='store_true', help='Convert iTerm2 color themes')
    parser.add_argument('-k', '--kitty', action='store_true', help='Convert Kitty term color themes')
    parser.add_argument('-a', '--all', action='store_true', help='Convert both iTerm2 and Kitty term color themes')
    parser.add_argument('-o', '--outfile', help='Specify an output filename')
    args = parser.parse_args()

    if not which('git'):
        print('Please install git')
        sys.exit(1)

    if int(args.iterm2) + int(args.kitty) + int(args.all) > 1:
        print('Only one of --iterm2, --kitty, and --all is allowed')
        sys.exit(1)

    all_themes = {}

    if args.all:
        args.iterm2 = True
        args.kitty = True
    
    tempdir = tempfile.TemporaryDirectory()

    if args.iterm2:
        iterm2_themes = do_iterm2(tempdir=tempdir)
        pprint(iterm2_themes)

    if args.kitty:
        kitty_themes = do_kitty(tempdir=tempdir)
        pprint(kitty_themes)
    
if __name__ == '__main__':
    main()

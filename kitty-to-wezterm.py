#!/usr/bin/env python3

from glob import glob
from pathlib import Path
from urllib.parse import urlparse
import json
import os
import re
import shutil
import string
import subprocess
import tempfile

def which(binary: str) -> bool:
    return shutil.which(binary)

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

def main():
    if not which('git'):
        print('Please install git')
        sys.exit(1)
    
    tempdir  = tempfile.TemporaryDirectory()
    repo_url = 'https://github.com/kovidgoyal/kitty-themes.git'
    parsed = urlparse(repo_url)
    repo_name = Path(parsed.path).stem
    repo_root = Path(tempdir.name) / repo_name

    print(f'Cloning the repository to {repo_root}....')
    
    command = ['git', 'clone', repo_url, repo_root]
    result = subprocess.run(
        command,
        capture_output = True,
        text           = True,
        check          = False,
    )
    stderr = result.stderr.strip()
    rc = result.returncode

    if rc == 0:
        print('Generating the WezTerm profiles....')
        themes_json = convert_kitty_colors(repo_root)

        outfile = 'color-schemes-kitty.json'
        with open(outfile, 'w') as f:
            json.dump(themes_json, f, indent=4)

        print(f'Generated {len(themes_json)} themes in {outfile}')
    else:
        error = stderr if stderr else 'Unknown error'
        print(f'Failed to clone the repository: {error}')
        sys.exit(1)

# Example usage:
if __name__ == "__main__":
    main()

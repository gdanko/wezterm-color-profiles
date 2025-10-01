#!/usr/bin/env python3

from glob import glob
from pathlib import Path
from urllib.parse import urlparse
import json
import os
import plistlib
import shutil
import subprocess
import tempfile

def which(binary: str) -> bool:
    return shutil.which(binary)

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

def convert_iterm_colors(repo_root):
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

def main():
    if not which('git'):
        print('Please install git')
        sys.exit(1)
    
    tempdir = tempfile.TemporaryDirectory()
    repo_url = 'https://github.com/mbadolato/iTerm2-Color-Schemes.git'
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
        themes_json = convert_iterm_colors(repo_root)

        outfile = 'color-schemes-iterm2.json'
        with open(outfile, 'w') as f:
            json.dump(themes_json, f, indent=4)
        
        print(f'Generated {len(themes_json)} themes in {outfile}')
    else:
        error = stderr if stderr else 'Unknown error'
        print(f'Failed to clone the repository: {error}')
        sys.exit(1)

if __name__ == '__main__':
    main()

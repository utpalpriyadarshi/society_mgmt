# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the project root directory
project_root = os.getcwd()

# Collect all data files from the project
datas = []
datas += collect_data_files('gui')
datas += collect_data_files('utils')
datas += collect_data_files('models')
datas += collect_data_files('assets', include_py_files=True)

# Include the ai_agent_utils directory
datas += collect_data_files('ai_agent_utils', include_py_files=True)

# Include migrations
datas += collect_data_files('ai_agent_utils/migrations', include_py_files=True)

# Include the database backup file
if os.path.exists(os.path.join(project_root, 'society_management.db.backup')):
    datas += [(
        os.path.join(project_root, 'society_management.db.backup'),
        '.'
    )]

# Include the requirements file
if os.path.exists(os.path.join(project_root, 'requirements.txt')):
    datas += [(
        os.path.join(project_root, 'requirements.txt'),
        '.'
    )]

# Include config file
if os.path.exists(os.path.join(project_root, 'config.json')):
    datas += [(
        os.path.join(project_root, 'config.json'),
        '.'
    )]

# Collect hidden imports
hiddenimports = []
hiddenimports += collect_submodules('gui')
hiddenimports += collect_submodules('utils')
hiddenimports += collect_submodules('models')
hiddenimports += collect_submodules('ai_agent_utils')

# Include PyQt5 plugins
datas += collect_data_files('PyQt5')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SocietyManagementSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # You may need to create this icon file
)
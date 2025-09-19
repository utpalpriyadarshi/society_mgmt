# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Get the project root directory
project_root = os.path.abspath('.')

# Collect all data files from the project
datas = []

# Include all Python files and data from the main directories
for directory in ['gui', 'utils', 'models']:
    if os.path.exists(directory):
        # Collect Python files
        datas += collect_data_files(directory, include_py_files=True)
        # Also collect any dynamic libraries
        datas += collect_dynamic_libs(directory)
        print(f"Collected data from {directory}")

# Include assets directory with all files
if os.path.exists('assets'):
    # Add all files in assets directory
    for root, dirs, files in os.walk('assets'):
        for file in files:
            file_path = os.path.join(root, file)
            # Get the relative path from the project root
            relative_path = os.path.relpath(root, project_root)
            datas.append((file_path, relative_path))
    print("Collected all files from assets")

# Include ai_agent_utils directory (but not as a Python package)
if os.path.exists('ai_agent_utils'):
    # Collect all files in ai_agent_utils directory
    for root, dirs, files in os.walk('ai_agent_utils'):
        for file in files:
            file_path = os.path.join(root, file)
            # Get the relative path from the project root
            relative_path = os.path.relpath(root, project_root)
            datas.append((file_path, relative_path))
    print("Collected all files from ai_agent_utils")

# Include specific files
additional_files = [
    'requirements.txt',
    'config.json',
    'society_management.db.backup',
    'asset_test.py'  # Include test script
]

for file in additional_files:
    if os.path.exists(file):
        datas.append((file, '.'))
        print(f"Included file: {file}")

# Collect hidden imports
hiddenimports = []

# Collect all submodules for the main packages
for package in ['gui', 'utils', 'models']:
    try:
        modules = collect_submodules(package)
        hiddenimports += modules
        print(f"Collected submodules from {package}: {len(modules)} modules")
    except Exception as e:
        print(f"Warning: Could not collect submodules from {package}: {e}")

# Add specific modules that might be missing
pyqt_modules = [
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'PyQt5.QtNetwork',
    'PyQt5.QtXml'
]

for module in pyqt_modules:
    try:
        __import__(module)
        hiddenimports.append(module)
        print(f"Added PyQt module: {module}")
    except ImportError:
        print(f"Warning: PyQt module not available: {module}")

# Add other required modules
required_modules = [
    'sqlite3',
    'bcrypt',
    'matplotlib',
    'matplotlib.backends.backend_agg',
    'pandas',
    'openpyxl',
    'reportlab',
    'fitz',  # PyMuPDF
    'pyotp',
    'qrcode',
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    'dateutil',
    'dateutil.parser'
]

for module in required_modules:
    try:
        __import__(module)
        hiddenimports.append(module)
        print(f"Added module: {module}")
    except ImportError:
        print(f"Warning: Module not available: {module}")

# Add any missing modules that might be imported dynamically
dynamic_modules = [
    'gui.login_dialog',
    'gui.main_window',
    'utils.security',
    'models.resident',
    'models.ledger',
    'utils.db_context',
    'ai_agent_utils.migrations.migration_manager'
]

for module in dynamic_modules:
    hiddenimports.append(module)
    print(f"Added dynamic module: {module}")

print(f"\nTotal datas entries: {len(datas)}")
print(f"Total hidden imports: {len(hiddenimports)}")

block_cipher = None

a = Analysis(
    ['asset_test.py'],  # Test with asset test script
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
    name='AssetTest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for test
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
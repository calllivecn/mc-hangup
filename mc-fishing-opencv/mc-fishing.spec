# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

def build_mouse_files():
	from keyboardmouse import mouse
	m = Path(mouse.__file__)
	mouse_parent = m.parent
	return [(mouse_parent, "keyboardmouse")]
	

datas_files = [("images/", "images/"), ("usage.txt", ".")]

#datas_files += build_mouse_files()
print("datas_files:", datas_files)


block_cipher = None


a = Analysis(
    ['mc-fishing2.py'],
    pathex=[],
    binaries=[],
    datas=datas_files,
    hiddenimports=["pyautogui", "keyboardmouse", "libevdev"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    #excludes=["pip", "setuptools", "wheel"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mc-fishing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mc-fishing',
)

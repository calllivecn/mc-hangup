# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


block_cipher = None

a = Analysis(
    ['mc-fishing2.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["pyautogui", "keyboardmouse", "libevdev"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    #excludes=[],
    excludes=["pip", "setuptools", "wheel"],
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



# 查看全局变量的值
print("="*20, "这是全局变量名和值：", "="*20)
print(f"{DISTPATH=}\n{HOMEPATH=}\n{SPEC=}\n{SPECPATH=}\n{workpath=}")
print(f"{exe.name=}, {coll.name=}")

import shutil

datas_files = [("images/", "images/"), ("usage.txt", "usage.txt")]
#print("datas_files:", datas_files)

p_coll = Path(coll.name)
for src, dst in datas_files:

	p_src = Path(src)

	if p_src.is_file():
		shutil.copyfile(src, p_coll / dst)
	else:
		shutil.copytree(src, p_coll / dst, symlinks=True)


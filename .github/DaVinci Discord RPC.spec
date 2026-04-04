# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None
base_path = os.getcwd()

a = Analysis(
    [os.path.join(base_path, '.github', 'DaVinci Discord RPC.pyw')],
    pathex=[base_path],
    binaries=[],
    datas=[(os.path.join(base_path, '.github', 'imgs', 'favicon.ico'), 'imgs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DaVinci Discord RPC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=os.path.join(base_path, '.github', 'imgs', 'favicon.ico'),
)

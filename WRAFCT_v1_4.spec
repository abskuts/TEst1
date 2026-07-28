# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for WRAFCT_v1_4.exe
# Build with: pyinstaller WRAFCT_v1_4.spec

from PyInstaller.utils.hooks import collect_all

datas_pandas, binaries_pandas, hiddenimports_pandas = collect_all("pandas")

a = Analysis(
    ["WRAFCT_v1_2_4.py"],
    pathex=[],
    binaries=binaries_pandas,
    datas=datas_pandas,
    hiddenimports=hiddenimports_pandas,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WRAFCT_v1_4",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # windowed – no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

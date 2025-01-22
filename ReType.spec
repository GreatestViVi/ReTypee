# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ReType.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('source/Flag_of_Ukraine.png', 'source'),
        ('source/Flag_of_United_Kingdom.png', 'source'),
        ('source/icon_r.ico', 'source'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='ReType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='source/icon_r.ico',
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ReType',
)

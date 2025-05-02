# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# List of data files
datas = [
    ("gui/layout/hl7133_ae_layout.xlsx", "gui/layout"),
    ("gui/layout/hl9800_aa_layout.xlsx", "gui/layout"),
    ("equipment/devices.yaml", "equipment"),
    ("project/hl9800/hl9800_aa_reg.yaml", "project/hl9800"),
    ("project/hl9800/hl9800_aa_status.yaml", "project/hl9800"),
    ("project/hl9800/hl9800_i2c.yaml", "project/hl9800"),
    ("project/hl7133/hl7133_ae_reg.yaml", "project/hl7133"),
    ("project/hl7133/hl7133_ae_status.yaml", "project/hl7133"),
    ("project/hl7133/hl7133_i2c.yaml", "project/hl7133"),
]

a = Analysis(
    ['gui/main.py'],
    pathex=[],  # Add any additional paths if needed
    binaries=[],
    datas=datas,
    hiddenimports=["gui.tabs"],  # Add hidden imports here
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='general_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for no console window
    icon=None,  # Add an icon file path if needed
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='general_gui',
)
# -*- mode: python ; coding: utf-8 -*-
"""Arquivo de especificação do PyInstaller para o PPT-Gen Studio.

Localizado em: packaging/ppt_gen.spec
Gera o executável standalone do PPT-Gen Studio no diretório dist/.
"""

from pathlib import Path

block_cipher = None

# Localiza dinamicamente a raiz do projeto a partir do diretório do spec
if "SPECPATH" in locals() and SPECPATH:
    root_dir = Path(SPECPATH).resolve().parent
else:
    root_dir = Path.cwd()

datas = [
    (str(root_dir / "src" / "web"), "web"),
    (str(root_dir / "src" / "presets.yaml"), "src"),
    (str(root_dir / "src" / "presets.yaml"), "."),
    (str(root_dir / "src" / "web" / "assets" / "logo.ico"), "assets"),
    (str(root_dir / "src" / "web" / "assets" / "logo.webp"), "assets"),
]

hiddenimports = [
    "clr",
    "pythonnet",
    "webview",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
    "fitz",
    "pptx",
    "PIL",
    "yaml",
    "box",
    "pydantic",
    "pydantic_settings",
]

a = Analysis(
    [str(root_dir / "run.py")],
    pathex=[str(root_dir / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "unittest", "pytest"],
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
    name="PPT-Gen Studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Janela nativa sem tela preta de terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root_dir / "src" / "web" / "assets" / "logo.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PPT-Gen-Studio",
)

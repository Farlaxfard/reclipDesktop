# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/main.py'],
    pathex=[],
    binaries=[('/opt/homebrew/bin/ffmpeg', '.')],
    datas=[('/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/templates', 'templates'), ('/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/static', 'static'), ('/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/assets', 'assets'), ('/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/assets/sounds', 'assets/sounds')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ReClip8K',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/static/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ReClip8K',
)
app = BUNDLE(
    coll,
    name='ReClip8K.app',
    icon='/Users/fardeen/Documents/GitHub/reclipDesktop/reclip_desktop/static/icon.icns',
    bundle_identifier='com.reclip.8k',
)

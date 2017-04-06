# -*- mode: python -*-

block_cipher = None


a = Analysis(['test_main.py'],
             pathex=['.\\'],
             binaries=[],
             datas=[('.\\api', '.\\api')],
             hiddenimports=[],
             hookspath=['.\\api'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='read_card',
          debug=False,
          strip=False,
          upx=True,
          icon='.\\read_card.ico',
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='read_card')

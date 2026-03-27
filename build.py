import PyInstaller.__main__
import os
import shutil

# 清理之前的构建
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# PyInstaller 命令
# --onefile: 打包成单个exe文件
# --windowed: 不显示控制台窗口（GUI程序）
# --name: 程序名称
# --icon: 图标（如果有）
# --add-data: 添加额外数据文件

PyInstaller.__main__.run([
    'app_pyqt.py',
    '--name=APIKeyManager',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    '--add-data=api_keys.json;.',
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=requests',
])

print("\n✅ 打包完成！")
print("可执行文件位置: dist/APIKeyManager.exe")
# 把成片的两段原字节拼回完整 MP4，并核对字节数和 SHA256（GitHub 单文件不能超过 100 MB，所以分段存放；不是重新编码）。
# 用法：python3 restore_final.py   → 在本目录生成 nainai-de-piying_1080p24.mp4
import hashlib, os, sys
here = os.path.dirname(os.path.abspath(__file__))
name, size, sha = 'nainai-de-piying_1080p24.mp4', 116326266, '45b03097a2e62baf6f88c2f79f4b4cde05753101db63363918a80b25e7e8b6b4'
data = b''.join(open(os.path.join(here, f'{name}.part{i}'), 'rb').read() for i in range(2))
if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
    sys.exit('核对失败：分段不完整或已损坏，没有写出文件')
open(os.path.join(here, name), 'wb').write(data)
print(name, size, 'SHA256 核对通过')

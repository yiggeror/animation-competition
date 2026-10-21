# 把成片的两段原字节拼回完整 MP4，并核对字节数和 SHA256（GitHub 单文件不能超过 100 MB，所以分段存放；不是重新编码）。
# 用法：python3 restore_final.py   → 在本目录生成 nainai-de-piying_1080p24.mp4
import hashlib, os, sys
here = os.path.dirname(os.path.abspath(__file__))
name, size, sha = 'nainai-de-piying_1080p24.mp4', 115461146, '43fac77450d315cfee22ce71e42f3140e58d051caf8a32d82d3224422b2fb949'
data = b''.join(open(os.path.join(here, f'{name}.part{i}'), 'rb').read() for i in range(2))
if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
    sys.exit('核对失败：分段不完整或已损坏，没有写出文件')
open(os.path.join(here, name), 'wb').write(data)
print(name, size, 'SHA256 核对通过')

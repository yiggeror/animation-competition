"""渲染器。

numba 的编译缓存（cache=True）只看函数自己所在文件的时间戳，不跟踪它调用的其他模块。
光照核心调用了 sdf、rt 里的函数，如果只改了 sdf.py，缓存里的旧版本会被继续使用——
所以这里在导入时检查本目录所有源码的哈希，一旦变化就清掉全部编译缓存。
"""
import hashlib
from pathlib import Path

_here = Path(__file__).resolve().parent


def _source_hash():
    h = hashlib.sha1()
    for p in sorted(_here.glob("*.py")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _refresh_numba_cache():
    cache = _here / "__pycache__"
    marker = cache / "numba_source.sha1"
    cur = _source_hash()
    try:
        old = marker.read_text().strip()
    except OSError:
        old = ""
    if old != cur:
        if cache.exists():
            for f in list(cache.glob("*.nbi")) + list(cache.glob("*.nbc")):
                try:
                    f.unlink()
                except OSError:
                    pass
        cache.mkdir(exist_ok=True)
        marker.write_text(cur)


_refresh_numba_cache()

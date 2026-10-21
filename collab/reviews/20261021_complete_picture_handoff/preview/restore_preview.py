from pathlib import Path
import hashlib
p=Path(__file__).resolve().parent
b=b''.join((p/f'workprint.mp4.part{i}').read_bytes() for i in (1,2))
assert len(b)==13377583
assert hashlib.sha256(b).hexdigest()=='0b19a165682a060be632469680a051bad728eb49c0a14bb468a7a7709c7e3c59'
f=p/'workprint_360p24_silent.mp4'; f.write_bytes(b)
print(f.name, len(b), 'SHA256 verified')

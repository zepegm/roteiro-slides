import hashlib

def retornarHashFile(file):
    hash_sha1 = hashlib.sha1()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def retornarHashString(valor):
    d = hashlib.sha1(bytes(str(valor), 'utf-8'))
    return d.hexdigest()
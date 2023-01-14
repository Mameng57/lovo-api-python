from hashlib import sha1, sha256, md5


def hash_sha1(string: str):
    return sha1(string.encode('utf8')).hexdigest()


def hash_sha256(string: str):
    return sha256(string.encode('utf8')).hexdigest()


def hash_md5(string: str):
    return md5(string.encode('utf8')).hexdigest()

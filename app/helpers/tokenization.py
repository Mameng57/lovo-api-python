if __name__ != '__main__':
    from helpers.hash import hash_md5
from random import choice


def generate_token(id: str):
    return hash_md5("".join(choice(id)))

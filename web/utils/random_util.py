# coding:utf-8
import random, string


def gen_str(length=8):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:length])


if __name__ == "__main__":
    print gen_str(8)

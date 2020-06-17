import collections


class 莉沫Error(Exception):
    None


def 错误简化(e):
    if len(e.args) == 1:
        return e.args[0]
    else:
        return e.args

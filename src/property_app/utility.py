from itertools import zip_longest


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def batch(iterable, batch_size=100):
    groups = grouper(iterable, batch_size)
    for group in groups:
        yield (i for i in group if i is not None)

#!/usr/bin/env python

from argparse import ArgumentParser
from collections import Counter, OrderedDict, defaultdict


def simulateCache(requests, size):
    """Cache simulator

    Note that this assumes that the python equality is sufficient
    to distinguish between unique requests; this may not be true,
    depending upon the hash and equality function implementations
    used in the C++ class.

    Parameters
    ----------
    requests : `list`
        List of cache requests.
    size : `int`
        Size of cache to simulate
    """
    print("Total number of requests:", len(requests))
    counts = Counter(requests)
    print("Number of unique requests:", len(counts.keys()))
    cache = OrderedDict()
    hits = defaultdict(int)
    for req in requests:
        if req in cache:
            hits[req] += 1
            cache.move_to_end(req)
        else:
            cache[req] = True
            if len(cache) > size:
                cache.popitem(False)
    print("Number of cache hits:", sum(hits.values()))
    print("Minimum/maximum cache hits:", min(hits.values()), max(hits.values()))


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", help="Filename for cache requests dump")
    parser.add_argument("size", default=100, type=int, help="Cache size to use in analysis")
    args = parser.parse_args()
    with open(args.filename) as ff:
        requests = ff.readlines()
    simulateCache(requests, args.size)


if __name__ == "__main__":
    main()

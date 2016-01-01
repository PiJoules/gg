#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re

from heapq import heappush, heappop, heapify
from collections import defaultdict


class Decoder(object):
    def __init__(self, encoding):
        """
        encoding:
            dict mapping code => char
        """
        self._encoding = encoding

    @classmethod
    def from_string(cls, s):
        """
        Get an encoding from a string in the format:
        char gGgg char Gggg char gGggG ...
        """
        p = re.compile("(\w) ([Gg]+)")
        # Flip the mappings from char => code to code => char
        matches = map(lambda x: (x[1], x[0], ), p.findall(s))
        return cls(dict(matches))

    @classmethod
    def from_char2code_map(cls, c2c_map):
        """
        Create a decoder from a flipped mapping.
        """
        new_map = {v: k for k, v in c2c_map.iteritems()}
        return cls(new_map)

    @property
    def encoding(self):
        return self._encoding

    def _get_head(self, s):
        """
        Trim the head of the string and return
        the head and rest of the body.
        """
        head = ""
        encoding = self._encoding
        while head not in encoding:
            if s == "":
                raise RuntimeError(
                    "Unable to find encoding for head '{}'.".format(head))
            head += s[0]
            s = s[1:]
        return head, s

    def decode(self, s):
        """
        Decode a string.
        """
        encoding = self._encoding
        result = ""
        while s != "":
            if not s[0].isalpha():
                result += s[0]
                s = s[1:]
                continue
            head, s = self._get_head(s)
            result += encoding[head]
        return result


class Encoder(object):
    def __init__(self, encoding):
        """
        encoding:
            dict mapping char => code
        """
        self._encoding = encoding

    @classmethod
    def from_frequencies(cls, freq_map, hi_char="G", lo_char="g"):
        """
        Create an encoder from a mapping of
        char => char frequencies in a string.
        """
        heap = [[wt, [sym, ""]] for sym, wt in freq_map.items()]
        heapify(heap)
        while len(heap) > 1:
            lo = heappop(heap)
            hi = heappop(heap)
            for pair in lo[1:]:
                pair[1] = hi_char + pair[1]
            for pair in hi[1:]:
                pair[1] = lo_char + pair[1]
            heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        encoding = dict(heappop(heap)[1:])
        return cls(encoding)

    @classmethod
    def from_string(cls, s):
        """
        Create an encoder from a string.
        The frequency map will be made here.
        """
        freq_map = defaultdict(int)
        for c in s:
            if c.isalpha():
                freq_map[c] += 1
        return cls.from_frequencies(freq_map)

    @property
    def encoding(self):
        return self._encoding

    def encode(self, s):
        """
        Encode a string.
        """
        encoding = self._encoding
        result = ""
        for c in s:
            if c.isalpha():
                result += encoding[c]
            else:
                result += c
        return result

    def __str__(self):
        items = self._encoding.iteritems()
        return " ".join(map(lambda (k, v): k + " " + v, items))


def main():
    if len(sys.argv) < 2:
        print("Usage: python {} {{encode,decode}} < input_file.txt"
              .format(sys.argv[0]))
        return 1

    if sys.argv[1] == "decode":
        # Test decoding
        encoding = sys.stdin.readline().strip()
        d = Decoder.from_string(encoding)
        str_to_decode = "\n".join(sys.stdin.readlines()).strip()
        print(d.decode(str_to_decode))
    elif sys.argv[1] == "encode":
        # Test encoding
        s = "\n".join(sys.stdin.readlines()).strip()
        e = Encoder.from_string(s)
        d = Decoder.from_char2code_map(e.encoding)
        encoded = e.encode(s)
        print("Encoding:", e)
        print("Encoded:", encoded)
        print("Decoded:", d.decode(encoded))

    return 0


if __name__ == "__main__":
    sys.exit(main())

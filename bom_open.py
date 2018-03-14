#!/usr/bin/env python3
import codecs
from io import TextIOWrapper

def bom_detect(bytes_str):
    encodings = ('utf-8-sig', ('BOM_UTF8',)), \
                ('utf-16', ('BOM_UTF16_LE', 'BOM_UTF16_BE')), \
                ('utf-32', ('BOM_UTF32_LE', 'BOM_UTF32_BE'))

    for enc, boms in encodings:
        for bom in boms:
            magic = getattr(codecs, bom)
            if bytes_str.startswith(magic):
                return enc

    return None

class bom_open():
    def __init__(self, filename, default_encoding='utf-8'):
        self.filename = filename
        self._default_encoding = default_encoding

    def __enter__(self):
        self._f = open(self.filename, 'r')
        peek = self._f.buffer.peek()
        detected_encoding = bom_detect(peek)

        self.encoding = detected_encoding or self._default_encoding

        # re-attach input/output with new encodings
        if self._f.encoding.lower() != self.encoding.lower():
            self._f = TextIOWrapper(self._f.detach(), encoding=self.encoding)

        return self._f

    def __exit__(self, type, value, traceback):
        self._f.close()

if __name__ == "__main__":
    with bom_open('plain.txt') as f:
        print(f.readlines())

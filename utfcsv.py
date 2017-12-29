import codecs
import csv
import sys
from io import TextIOWrapper

class dialect_pipe(csv.Dialect):
    delimiter='|'
    lineterminator='\n'
    quoting=csv.QUOTE_NONE

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

def firstline(string):
    for i, char in enumerate(string):
        if char in '\r\n':
            return string[:i]

    return string

def csv_stdout(*,
               header=False,
               delimiters='|,\t',
               default_encoding=None,
               output_encoding=None):
    """Parse arbitrary delimited text from stdin,
       reformat to pipe-delimited in stdout
    """
    peek = sys.stdin.buffer.peek()
    encoding = bom_detect(peek)

    if encoding:
        print('Detected Unicode BOM: {}'.format(encoding),
              file=sys.stderr)

    else:
        encoding = default_encoding or 'utf-8'
        print('No Unicode BOM, defaulting to {}'.format(encoding),
              file=sys.stderr)

    sys.stdin = TextIOWrapper(sys.stdin.detach(),
                              encoding=encoding)

    output_encoding = output_encoding or 'utf-8'
    print('Output encoding: {}'.format(output_encoding),
          file=sys.stderr)
    sys.stdout = TextIOWrapper(sys.stdout.detach(),
                               encoding=output_encoding)

    peek_line = firstline(peek.decode(encoding))
    dialect_auto = csv.Sniffer().sniff(peek_line, delimiters=delimiters)

    if header:
        sys.stdin.readline()

    reader = csv.reader(sys.stdin, dialect=dialect_auto)
    writer = csv.writer(sys.stdout, dialect=dialect_pipe())
    writer.writerows(reader)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--header",
                        action="store_true",
                        help="discard first row")
    parser.add_argument("--delimiters",
                        help="acceptable delimiters to search for, default '|,\\t'")
    parser.add_argument("--default-encoding",
                        help="input encoding to use if no Unicode BOM in file, UTF-8 when not specified")
    parser.add_argument("--output-encoding",
                        help="output encoding, UTF-8 when not specified")
    args = parser.parse_args()

    csv_stdout(header=args.header,
               delimiters=args.delimiters or '|,\t',
               default_encoding=args.default_encoding,
               output_encoding=args.output_encoding)

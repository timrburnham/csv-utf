import codecs
import csv
import sys
from io import TextIOWrapper

csv.register_dialect('pipe',
                     delimiter='|',
                     lineterminator='\n',
                     quoting=csv.QUOTE_NONE)

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

def csv_stdout(f,
               header=False,
               delimiters=None,
               input_encoding=None,
               output_encoding=None,
               output_dialect=None):
    peek = f.buffer.peek()
    encoding = bom_detect(peek)

    if encoding:
        print('Detected Unicode BOM: {}'.format(encoding),
              file=sys.stderr)

    else:
        encoding = input_encoding or 'utf-8'
        print('No Unicode BOM, defaulting to {}'.format(encoding),
              file=sys.stderr)

    delimiters = delimiters or '|,\t'
    output_encoding = output_encoding or 'utf-8'
    output_dialect = output_dialect or 'pipe'
    print('Output encoding: {}'.format(output_encoding),
          file=sys.stderr)

    # re-attach input/output with new encodings
    if f.encoding.lower() != encoding.lower():
        f = TextIOWrapper(f.detach(),
                          encoding=encoding)
    sys.stdout = TextIOWrapper(sys.stdout.detach(),
                               encoding=output_encoding)

    peek_line = firstline(peek.decode(encoding))
    dialect_auto = csv.Sniffer().sniff(peek_line, delimiters=delimiters)

    if header: # skip over
        f.readline()

    reader = csv.reader(f, dialect=dialect_auto)
    writer = csv.writer(sys.stdout, dialect=output_dialect)
    writer.writerows(reader)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE",
                        nargs='?',
                        default='-',
                        help="file to open, '-' or omit to pipe from stdin")
    parser.add_argument("--header",
                        action="store_true",
                        help="discard first row")
    parser.add_argument("--delimiters",
                        help="input delimiters to search for, default '|,\\t'")
    parser.add_argument("--input-encoding",
                        help="default encoding to use if no Unicode BOM in file, UTF-8 when not specified")
    parser.add_argument("--output-encoding",
                        help="output encoding, UTF-8 when not specified")
    parser.add_argument("--output-errors",
                        default="strict",
                        choices=['strict', 'replace', 'ignore', 'backslashreplace'],
                        help="response when input string can't be encoded to output-encoding.")
    parser.add_argument("--output-dialect",
                        choices=['pipe', 'excel', 'excel-tab', 'unix'],
                        help="output csv dialect, pipe delimited when not specified")
    args = parser.parse_args()

    if args.FILE in ('-', None):
        csv_stdout(f=sys.stdin,
                   header=args.header,
                   delimiters=args.delimiters,
                   input_encoding=args.input_encoding,
                   output_encoding=args.output_encoding,
                   output_dialect=args.output_dialect)
    else:
    # TODO: ValueError when --input-encoding doesn't match open file encoding
    # somehow still works?
        with open(args.FILE) as f:
            csv_stdout(f=f,
                       header=args.header,
                       delimiters=args.delimiters,
                       input_encoding=args.input_encoding,
                       output_encoding=args.output_encoding,
                       output_dialect=args.output_dialect)

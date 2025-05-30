#!/usr/bin/env python

# script must be compatible with both python2 & python3
# (for backward compat on old osx test @travis-ci)

import sys
import re

try:
    assert len(sys.argv) >= 8
    assert sys.argv[2] == '-o'
    assert sys.argv[4] == '-D'
    assert sys.argv[6] == '-l'
    if len(sys.argv) > 8:
        for x in sys.argv[8:]:
            assert x in ['-p', '-c', '-C']
        if '-c' in sys.argv[8:]:
            assert '-C' not in sys.argv[8:]
except AssertionError:
    print("Usage: %s <wordlist> -o <output> -D <dupfile> -l <max-line-size> [-pcC]" % sys.argv[0])
    print("Example: %s old.txt -o new.txt -D dupes.txt -l 14" % sys.argv[0])
    print("Example: %s old.txt -o new.txt -D dupes.txt -l 40 -p" % sys.argv[0])
    print("Example: %s old.txt -o new.txt -D dupes.txt -l 40 -p -C" % sys.argv[0])
    sys.exit(1)

with open(sys.argv[1], 'rb') as f:
    content = f.read()
OLD_CONTENT_LEN = len(content)

output = open(sys.argv[3], 'wb')
dupfile = open(sys.argv[5], 'wb')

MAX_LINE_SIZE = int(sys.argv[7])

FILTER_PRINTABLE = '-p' in sys.argv[8:]
LOWERCASE = '-c' in sys.argv[8:]
UPPERCASE = '-C' in sys.argv[8:]

if LOWERCASE:
    content = content.lower()
elif UPPERCASE:
    content = content.upper()

# use re.split(), because str.splitlines() assumes
# that single "\r" are newline chars too..
lines = re.split(b"\r\n|\n", content)


if sys.version_info.major == 3:
    def line_isprint(line):
        for c in line:
            if not 31 < c < 127:
                return False
        return True
elif sys.version_info.major == 2:
    def line_isprint(line):
        for c in line:
            if not 31 < ord(c) < 127:
                return False
        return True

dupes = []
uniques = []
for index, line in enumerate(lines):
    if not line:
        continue
    if len(line) > MAX_LINE_SIZE:
        continue
    if line.startswith(b"\0"):
        continue
    if FILTER_PRINTABLE and not line_isprint(line):
        continue
    if line in uniques:
        dupes.append(line)
        continue
    uniques.append(line)


result = b"\n".join(uniques)
if 0 < len(result) < OLD_CONTENT_LEN:
    result += b'\n'
output.write(result)
output.close()

if dupes:
    dupfile.write(b"\n".join(dupes)+b"\n")
dupfile.close()

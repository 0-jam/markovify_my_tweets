import re
from collections import deque


# Execute re.sub() to given str for multiple patterns
# patterns = deque([('pattern1', 'string1'), ('pattern2', 'string2'), ..., ('patternX', 'stringX')])
def replace(str, patterns):
    if len(patterns) == 0:
        return str

    pattern = patterns.popleft()
    str = re.sub(pattern[0], pattern[1], str)
    return replace(str, patterns)


def replace_str(str, patterns):
    return replace(str, deque(patterns))

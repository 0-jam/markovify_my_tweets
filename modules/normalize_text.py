import re
import unicodedata
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


def normalize(text):
    # すべての全角英数字，丸カッコ（），全角スペース　，！，？などをそれぞれ半角に置換
    text = unicodedata.normalize('NFKC', text)
    # 4回以上続くピリオド....，3回以上続く中黒・・・をピリオド3回...に統一
    # 波ダッシュ〜（上記normalize()で半角~に変換済み）を長音符ーに置換
    # 2回以上続く長音符ーーを1つーに統一
    # すべての半角カッコ{}[]()<>を丸カッコ()に統一
    # すべての全角かぎかっこ「」『』｢｣をこれ「」に統一
    # すべての二重引用符"“”をこれ"に統一
    # すべての引用符'‘’をこれ'に統一
    # すべてのダッシュ（≠長音符）・全角ハイフン−―‐，2回以上続くハイフン--をハイフン一つ-に統一
    # 各要素：(置換したい文字, 置換先の文字)
    patterns = [
        (r'\.{4,}|・{3,}', '...'),
        (r'~', 'ー'),
        (r'ー{2,}', 'ー'),
        (r'\[|{|<', '('),
        (r'\]|}|>', ')'),
        (r'｢|『', '「'),
        (r'』|｣', '」'),
        (r"“|”", '"'),
        (r"’|‘", "'"),
        (r'[−|―|‐]+?|-{2,}', '-'),
    ]
    text = replace_str(text, patterns)

    return text

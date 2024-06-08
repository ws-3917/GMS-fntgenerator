import pypinyin
def get_pinyin_or_unicode(s):
    """
    获取字符的拼音，如果不能转换成拼音则返回原字符
    """
    if '\u4e00' <= s <= '\u9fff':  # 判断是否是中文字符
        return ''.join(pypinyin.lazy_pinyin(s))
    return s

def sort_key(char):
    """
    生成排序的键
    """
    if '\u4e00' <= char <= '\u9fff':  # 中文字符
        return (1, get_pinyin_or_unicode(char))
    else:  # 非中文字符
        return (0, char)

def sort_text(text):
    """
    排序文本并每100个字符换行
    """
    # 将文本按字符分割
    characters = list(text)
    
    # 对字符进行排序
    characters_sorted = sorted(characters, key=sort_key)
    
    # 拼接排序后的字符，并按每100个字符换行
    result = []
    line = ""
    for char in characters_sorted:
        if len(line) + len(char) > 50:
            result.append(line)
            line = char
        else:
            line += char
    if line:
        result.append(line)
    
    return "\n".join(result)

# 读取文本文件
with open('font_info/char_cn_tw.txt', 'r', encoding='utf-8') as file:
    text = file.read().replace('\n', "")

# 对文本进行排序
sorted_text = sort_text(text)
# 写入排序后的文本到输出文件
with open('font_info/char_cn_tw.txt', 'w', encoding='utf-8') as file:
    file.write(sorted_text)

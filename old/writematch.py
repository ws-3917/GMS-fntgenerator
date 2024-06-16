import re

# 读取文件内容
with open('charfreq_tw.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# 匹配所有汉字字符
pattern = re.compile(r' [\u4e00-\u9fa5]')
matches = pattern.findall(content)

# 将匹配结果写入新文件
with open('charfreq_tw.txt', 'w', encoding='utf-8') as output_file:
    output_file.write(''.join(matches))

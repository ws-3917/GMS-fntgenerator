# sortsplit - 对字库内汉字进行分行和排序，用于合并字库时的预处理

fnt_source = "font_info/char_jp.txt"    # 字体路径
# 读取文件
ch_list = []
with open(fnt_source, "r", encoding="utf-8") as file:
    content_len = len(file.read())
    file.seek(0)
    for i in range(content_len):
        ch = file.read(1)
        if ch == '\n':
            continue
        # 将文件一次性读入内存
        ch_list.append(ch)
ch_list = list(set(ch_list))    # 去重
ch_list.sort()

# 写回新文件，默认写入到source路径下_dest文件名
# 如果要直接覆盖源文件，将 + :_dest.txt"去掉
fnt_dest = fnt_source[:fnt_source.find(".txt")] + ".txt"   
ct = 0

with open(fnt_dest, "w", encoding="utf-8") as file:
    for ch in ch_list:
        if ct == 50:
            file.write("\n")
            ct = 0
        file.write(ch)
        ct += 1

print("OK.")
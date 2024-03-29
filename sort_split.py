# 对字库内汉字进行分行和排序
fnt_source = "font_info/char_en.txt"
# 读取文件
ch_list = []
with open(fnt_source, "r", encoding="utf-8") as file:
    content_len = len(file.read())
    file.seek(0)
    for i in range(content_len):
        ch = file.read(1)
        if ch == '\n' or ch == ' ':
            continue
        # 将文件一次性读入内存
        ch_list.append(ch)
ch_list = list(set(ch_list))    # 去重
ch_list.sort()

# 写回新文件
fnt_dest = fnt_source[:fnt_source.find(".txt")] + "_dest.txt"
ct = 0
with open(fnt_dest, "w", encoding="utf-8") as file:
    for ch in ch_list:
        if ct == 50:
            file.write("\n")
            ct = 0
        file.write(ch)
        ct += 1
print("over.")
            
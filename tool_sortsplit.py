# sortsplit - Sorts and splits characters within a font library for preprocessing before merging font libraries

fnt_source = "font_info/char_cn.txt"    # Path to the font file
# Read the file
ch_list = []
with open(fnt_source, "r", encoding="utf-8") as file:
    content_len = len(file.read())
    file.seek(0)
    for i in range(content_len):
        ch = file.read(1)
        if ch == '\n':
            continue
        # Load the file into memory all at once
        ch_list.append(ch)
ch_list = list(set(ch_list))    # Remove duplicates
ch_list.sort()

# Write back to a new file, by default it writes under the source path with _dest.txt
# To overwrite the original file directly, remove "+ :_dest.txt"
fnt_dest = fnt_source[:fnt_source.find(".txt")] + "_dest.txt"
ct = 0

with open(fnt_dest, "w", encoding="utf-8") as file:
    for ch in ch_list:
        if ct == 50:
            file.write("\n")
            ct = 0
        file.write(ch)
        ct += 1

print("OK.")

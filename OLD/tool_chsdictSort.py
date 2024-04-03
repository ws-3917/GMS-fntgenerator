# 将 chs.txt 字库文件按 Unicode 码排序
def sort_and_rewrite_characters(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            # 去重并过滤Unicode超过65535的字符，这部分文件导入 UTMT 会出错
            characters = sorted(set(content) - set('\n'), key=lambda x: ord(x) if ord(x) <= 0xffff else 0xffff)
            characters = [c for c in characters if ord(c) <= 0xffff]

        # 每100个字符换行重新写入到文件
        with open(file_path, "w", encoding="utf-8") as file:
            for i in range(0, len(characters), 100):
                file.write("".join(characters[i:i+100]) + "\n")

    except FileNotFoundError:
        print("未找到文件，请确保文件已放在程序目录中。")
        input("按 Enter 重试。")
        return False
    
    return True

def main():
    input("请将 chs.txt 放在程序目录, 按下回车后程序会对字符按Unicode排序。")

    while not sort_and_rewrite_characters("chs.txt"):
        pass

    input("转换完成，按 Enter 关闭。")
if __name__ == "__main__":
    main()

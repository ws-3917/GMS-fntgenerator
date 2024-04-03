# Unicode 工具 - 可以快速查询字符的Unicode值, 方便定位和补字
# 该程序为重构前实现的小工具，交互的逻辑较多。

# unicode 查 char
def unicode_lookup():
    while True:
        code = input("请输入十进制或十六进制编码 (十六进制以0x开头, 输入q返回主菜单): ")
        if code.lower() == 'q':
            break
        try:
            if code.startswith("0x"):
                code = int(code, 16)
            else:
                code = int(code)
            print("对应的字符是:", chr(code))
        except ValueError:
            print("输入的编码无效. ")

# char 查 unicode
def char_encoding_lookup():
    while True:
        chars = input("请输入字符 (可输入多个字符, 输入quit返回主菜单): ")
        if chars.lower() == 'quit':
            break
        for char in chars:
            print(f"'{char}': 十进制={ord(char)}, 十六进制={hex(ord(char))}")

# 输出unicode范围内所有字符到文件
def output_unicode_range():
    filename = "char_cn.txt"    # 设置输出文件名

    # 交互
    print(f"如果{filename}已存在, 新内容将被追加到文件末尾. ")
    start = input("请输入范围的起始编码 (十六进制): ")
    end = input("请输入范围的结束编码 (十六进制): ")

    # 写入文件
    try:
        start = int(start, 16)
        end = int(end, 16)
        with open(filename, "a", encoding="utf-8") as file:
            for code in range(start, end + 1):
                file.write(chr(code))
        print(f"已输出到{filename}. ")
    except ValueError:
        print("输入的编码无效. ")

def main_menu():
    while True:
        print("\n功能选择: ")
        print("1. Unicode查询")
        print("2. 输入字符查询编码")
        print("3. 输出指定Unicode范围的所有字符到文件")
        print("4. 退出")
        choice = input("请输入选项 (1/2/3/4): ")
        if choice == "1":
            unicode_lookup()
        elif choice == "2":
            char_encoding_lookup()
        elif choice == "3":
            output_unicode_range()
        elif choice == "4":
            print("退出程序. ")
            break
        else:
            print("无效的选项, 请重新输入. ")

if __name__ == "__main__":
    main_menu()

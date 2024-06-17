import os, tools
def main():
    project = 'psot'    # psot 或 tsus
    langlist = ['en_US', 'symbols', 'zh_CN']   # en_US, zh_CN, zh_TW 或 ja_JP
    
    os.system(f"mkdir -p dist/{project}")
    tools.FontGlyph(project, langlist).task()
    print("--- 成功生成所有字图！")

if __name__ == '__main__':
    main()
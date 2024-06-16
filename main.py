import os, tools
def main():
    project = 'psot'    # 或 tsus
    langlist = ['en_US', 'zh_CN']   # 或 zh_TW, ja_JP
    
    os.system(f"mkdir -p dist/{project}")
    tools.FontGlyph(project, langlist).task()
    print("--- 成功生成所有字图！")

if __name__ == '__main__':
    main()
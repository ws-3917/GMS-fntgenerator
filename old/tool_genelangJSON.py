# 中文字符宽度调整
import json, os
# 新的宽度设置
new_widths = []

# 读取 JSON 文件
def load_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"未找到文件：{file_path}。")
        return None
    except json.JSONDecodeError:
        print(f"文件 {file_path} 内容无效，请重新指定。")
        return None

# 字体名称列表（除了sans和papyrus，这两个字体需要单独处理）
fontname_list = ['fnt_main', 'fnt_mainsm', 'fnt_dotumche_sm', 
                 'fnt_dotumche', 'fnt_dotumche_md', 'fnt_dotumche_mdlg', 'fnt_dotumche_lg']

game_config = None
while game_config is None:
    file_path = input("指定 JSON 配置文件位置(默认default.json): ") or "default.json"
    game_config = load_config(file_path)

# widthlist = [11, 11, 11, 11, 6]
widthlist = []
widthlist.append(int(input("指定主字体 main 宽度偏移量(整数, 默认11): ") or '11'))
widthlist.append(int(input("指定小字体 mainsm 宽度偏移量(整数, 默认6): ") or '6'))
widthlist.extend(list(map(int, input("指定 dotumche 字体族(dotumche_sm, dotumche, dotumche_md, dotumche_mdlg, dotumche_lg)\n"
                           "宽度偏移量(5个整数, 空格隔开, 默认4 6 8 12 16)").split() or "4 6 8 12 16".split())))

offsetlist = []
offsetlist.append(int(input("指定 sans 字体宽度偏移量(整数, 默认7): ") or '7'))
offsetlist.append(int(input("指定 papyrus 字体宽度偏移量(整数, 默认7): ") or '7'))

offset_sans = []
offset_papy = []

output_path = input("指定 JSON 输出名称(默认chs.json): ") or "chs.json"

def read_characters_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # 读取文件内容，并去掉换行符
            content = file.read().replace('\n', '').strip()
            return list(content)
    except FileNotFoundError:
        print("程序路径下未找到中文字库文件 chs.txt! ")
        print("可以从 ws3917.lanzout.com/iXSdT1pcg9ih 下载规范汉字和常用字符字库，")
        print("或手动创建并随后用 tool_unicodesort.py 将字符按照 Unicode 编码排序(否则会出现游戏内字体不显bug)")
        input("按 Enter 重试。")
        return None
characters_c = None
while characters_c is None:
    characters_c = read_characters_file("chs.txt")
    
# 对于字库 chs.txt 中每个字符，添加字符和新宽度
for i in range(len(widthlist)):
    new_widths.append([])  # 复制现有的宽度设置
    for char in characters_c:
        new_widths[i].append(char)
        new_widths[i].append(widthlist[i])

for char in characters_c:
    offset_sans.extend([char, offsetlist[0], 0, offsetlist[0]])
    offset_papy.extend([char, offsetlist[1], 0, offsetlist[1]])


# 更新游戏配置字典中的宽度设置
for it in range(len(fontname_list)):
    game_config['fonts'][fontname_list[it]]['characters']['widths'] = new_widths[it]

# 由于sans和papyrus有字体缩放问题，避免战斗云图和对话字体间距不统一采用offset
game_config['fonts']['fnt_papyrus']['characters']['offsets_x'] += offset_papy
game_config['fonts']['fnt_sans']['characters']['offsets_x'] += offset_sans

# 将更新后的配置写入到一个新的JSON文件中
folder = 'output'
if not os.path.exists(folder):
    os.makedirs(folder)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(game_config, f, ensure_ascii=False, indent=4)

print(f"配置文件已更新并保存为 output/{output_path}。")
input("按 Enter 关闭")
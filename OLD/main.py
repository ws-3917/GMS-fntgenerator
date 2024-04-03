# 主程序 - 导入自定义字体并输出字库图片 png 及位置信息 csv
# 注意：图片宽度为 4096，因此需要在 UTMT 中提前设置阈值。
from PIL import Image, ImageDraw, ImageFont
import os

def get_font_path(prompt, default):
    while True:
        font_path = input(prompt) or default
        try:
            # 尝试加载字体以验证路径是否正确
            font = ImageFont.truetype(font_path, 10)  # 使用任意大小尝试加载字体
            return font_path  # 字体加载成功，返回字体路径
        except IOError:
            print(f"未找到字体文件: {font_path}。请重新输入。")

# 锯齿化
def process_edge(pixels, width, height, threshold):
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a >= threshold and a != 0:
                pixels[x, y] = (255, 255, 255, 255)
            else:
                pixels[x, y] = (0, 0, 0, 0)

# 设置字体和大小
efont_path = get_font_path("指定英文字体路径(默认latin.ttf): ", "latin.ttf")
cfont_path = get_font_path("指定中文字体路径(默认cjk.ttf): ", "cjk.ttf")
efont_size = int(input("指定英文字号(整数, 默认32): ") or '32')
cfont_size = int(input("指定中文字号(整数, 默认24): ") or '24')
exportname = input("指定字体名称(不含\"fnt_\"前缀，默认main): ") or "main"
threshold = int(float(input("指定字体腐蚀度(0-1, 默认关闭, 增大能让字体变细): ") or '-1') * 255)
e_yoffset = int(input("指定英文字体纵向偏移量(整数可正负, 默认0, 正值代表向下偏移): ") or '0')
c_yoffset = int(input("指定中文字体纵向偏移量(整数, 同上): ") or '0')

# 使用4倍字号进行渲染
scale_factor = 4
efont = ImageFont.truetype(efont_path, efont_size * scale_factor)
cfont = ImageFont.truetype(cfont_path, cfont_size * scale_factor)

# 字符布局参数
start_x, start_y = 0, 0
spacing = 3
x, y = start_x, start_y

# CSV信息
csv_lines = []

# 添加初始信息
csv_lines.append(f"{exportname};{cfont_size};FALSE;FALSE;1;0;1;1")
width = 4096*scale_factor

spacing *= scale_factor
# 处理英文字体
char_width_e, char_height_e = efont_size * scale_factor, efont_size * scale_factor

# 处理中文字体，读取字库
# 异常检测
def read_characters_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # 读取文件内容，并去掉换行符
            content = file.read().replace('\n', '').strip()
            return list(content)
    except FileNotFoundError:
        print("程序路径下未找到中文字库文件 chs.txt！")
        print("可以从 ws3917.lanzout.com/iXSdT1pcg9ih 下载规范汉字和常用字符字库，")
        print("或手动创建并随后用 tool_unicodesort.py 将字符按照 Unicode 编码排序（否则会出现游戏内字体不显bug）")
        input("按 Enter 重试。")
        return None
characters_c = None
while characters_c is None:
    characters_c = read_characters_file("chs.txt")

char_width_c, char_height_c = cfont_size * scale_factor, cfont_size * scale_factor

# 计算每行可以容纳的字符数量（英文和中文字符宽度不同，需要分别计算）
chars_per_line_en = width // (char_width_e + spacing)  # 英文
chars_per_line_cn = width // (char_width_c + spacing)  # 中文

# 计算英文字符和中文字符总共需要的行数
lines_needed_en = (127 - 32) // chars_per_line_en + 1
lines_needed_cn = len(characters_c) // chars_per_line_cn + 1

# 计算图片总高度
total_lines = lines_needed_en + lines_needed_cn
height = total_lines * (char_height_c + spacing + 1) + spacing  # 加上间隔

# 重新创建图片对象以适应计算出的高度
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 处理英文字体
x, y = start_x, start_y

# 首先计算英文字符的高度
for ascii_code in range(32, 128):
    char = chr(ascii_code)
    # 使用textbbox获取字符的边界框
    bbox = draw.textbbox((x, y), char, font=efont)
    # 计算字符的高度
    char_height = bbox[3] - bbox[1]
    char_height_e = max(bbox[3], char_height_e) # 避免英文字体越界影响到中文字体

# 随后排列英文字体。
for ascii_code in range(32, 128):
    char = chr(ascii_code)
    # 使用textbbox获取字符的边界框
    bbox = draw.textbbox((x, y), char, font=efont)
    # 计算字符的宽度
    char_width = bbox[2] - bbox[0]
    draw.text((x, y), char, font=efont, fill=(255, 255, 255))
    csv_lines.append(f"{ascii_code};{x};{y};{char_width};{char_height_e};{char_width_e};0")
    x += char_width + spacing
    if x + char_width > img.width:
        x = start_x
        y += char_height_e + spacing

# 为中文字符换行
x = start_x
y += char_height_e + spacing + 1

# 排列中文字体
for char in characters_c:
    draw.text((x, y), char, font=cfont, fill=(255, 255, 255))
    csv_lines.append(f"{ord(char)};{x};{y};{char_width_c};{char_height_c};{char_width_c+4};0")
    x += char_width_c + spacing
    if x + char_width_c > img.width:
        x = start_x
        y += char_height_c + spacing

# 处理锯齿
if threshold >= 0:
    process_edge(img.load(), img.width, img.height, threshold)

# 缩小图片
scaled_width = width // scale_factor
scaled_height = height // scale_factor
img_scaled = img.resize((scaled_width, scaled_height), Image.NEAREST)

# 保存缩小后的图片
image_path = f"output/fnt_{exportname}.png"

# 检查路径中的文件夹是否存在，如果不存在，则创建
folder = os.path.dirname(image_path)
if not os.path.exists(folder):
    os.makedirs(folder)

img_scaled.save(image_path)
# 调整CSV坐标信息为缩小后的尺寸
csv_lines_scaled = [csv_lines[0]]  # 包含初始信息行
for line in csv_lines[1:]:
    parts = line.split(';')
    char_code, x, y, char_width, char_height, _, _ = parts
    # 缩放坐标和尺寸
    x_scaled = int(int(x) // scale_factor)
    y_scaled = int(int(y) // scale_factor)
    char_width_scaled = int(int(char_width) // scale_factor)
    char_height_scaled = int(int(char_height) // scale_factor)

    # 写入缩放后的宽高数据，并调节字体间距shift值
    # 对于英文
    if int(char_code) < 256:
        csv_lines_scaled.append(f"{char_code};{x_scaled};{y_scaled+e_yoffset};{char_width_scaled};{char_height_scaled-e_yoffset};{char_width_scaled};0")
    # 对于中文
    else:
        csv_lines_scaled.append(f"{char_code};{x_scaled};{y_scaled+c_yoffset};{char_width_scaled};{char_height_scaled-c_yoffset};{char_width_scaled+2};0")

# 保存缩小后的CSV
with open(f"output/glyphs_fnt_{exportname}.csv", "w", encoding="utf-8") as csv_file:
    csv_file.write("\n".join(csv_lines_scaled))

print("已输出png与csv到output文件夹, 可直接导入 UTMT 中。")
input("按 Enter 关闭")
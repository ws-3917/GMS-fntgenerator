# 字图配置生成
import csv, json, os
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 定义字图类
class FontGlyph:
    # 初始化
    width = height = 2048   # 大小

    def __init__(self, name, basicinfo_csv, glyphinfo_json) -> None:
        # 当前绘制的x,y位置
        self.__x = 0
        self.__y = 0
        self.__line_maxheight = 0   # 当前行字体的最大高度，用于换行
        self.__name = name

        # 主字图
        self.glyph = Image.fromarray(np.zeros((self.width, self.height, 2), np.uint8))
        self.__fontconfig = self.init_fontconfig(glyphinfo_json)

        # 主JSON，csv
        self.__jsonfile = self.init_json(basicinfo_csv)
        self.csv = list()

    # 初始化基本信息并写入json
    def init_json(self, basicinfo) -> dict:
        csv_reader = csv.reader(open(basicinfo, "r", encoding="UTF-8"))

        infoline = True
        for row in csv_reader:
            if infoline:
                infoline = False
                keys = row
                continue
            
            # 选择数据
            if row[0] == self.__name:
                data = dict(zip(keys, row))
                break

        # 对于 Outertale 的特殊处理
        data['shift'] = {"x": float(data['shift_x']), "y": float(data['shift_y'])}
        data.pop('shift_x')
        data.pop('shift_y')
        data['size'] = int(data['size'])

        # 准备绘制子图
        data['glyphs'] = []

        return data

    # 初始化字体信息
    def init_fontconfig(self, glyphinfo) -> dict:
        # 打开并读取JSON
        with open(glyphinfo, "r", encoding="UTF-8") as file:
            fullcfg = json.load(file)
        
        for info in fullcfg:
            if info['name'] == self.__name:
                return info['glyph_info']
        
        return None

    # 绘制单个字体字图
    def draw_singlefont(self, fontfile, currentchar, size, threshold) -> tuple:
        # 读取字体，生成 size*4 的字体对象
        # 绘制4倍size的字图
        # 将图片压制到原size大小，邻近像素
        # 二值化，返回字图矩阵
        font = ImageFont.truetype(fontfile, size)
        startpoint, endpoint = (font.getbbox(currentchar)[:2], font.getbbox(currentchar)[2:])

        # 初始化完毕，创建子图（二值图）
        fontimg = Image.new('L', endpoint)
        # 绘制
        drawtool = ImageDraw.Draw(fontimg)
        drawtool.text((0, 0), currentchar, fill=255, font=font)

        # 缩放步骤可以省略，转换为透明图
        fontimg = self.convert_pic(fontimg, threshold)
        fontinfo = (startpoint, endpoint, fontimg)

        return fontinfo

    # 将生成的二值图透明化，转为含Alpha的灰度图
    def convert_pic(self, fontimg, threshold) -> Image:
        fontimg_arr = np.asarray(fontimg)
        new_arr = np.empty((fontimg_arr.shape[0], fontimg_arr.shape[1], 2), np.uint8)

        # 二值化
        new_arr[..., 1] = new_arr[..., 0] = (fontimg_arr>threshold)*255

        # 转换回 Image 对象
        new_fontimg = Image.fromarray(new_arr, "LA")
        return new_fontimg
        
    # 将字体添加到总字图上
    def add_fontimg(self, fontinfo) -> None:
        # 主要处理换行和字体偏移量
        endpoint = fontinfo[1]
        fontimg = fontinfo[2]
        # 如果已经排到末尾，+1 是预留的间距
        if self.__x + endpoint[0] > self.width:
            # 移动到下一行开头
            self.__x = 0
            self.__y += self.__line_maxheight
            # 重置最大行
            self.__line_maxheight = 0
        
        # 粘贴图片
        self.glyph.paste(fontimg, (self.__x, self.__y))
        # 移动坐标
        self.__x += endpoint[0] 
        self.__line_maxheight = max(self.__line_maxheight, endpoint[1])

    # 写入字体信息到JSON (for Outertale)
    def write_fontimg_json(self, fontinfo, currentchar) -> None:
        # 在图片上添加字体后写入配置文件
        startpoint = fontinfo[0]
        endpoint = fontinfo[1]

        data = dict()

        # 构建 outertale 接受的 JSON 数据
        data['area'] = {
            "x": self.__x - endpoint[0] + startpoint[0],
            "y": self.__y + startpoint[1],
            "width": endpoint[0] - startpoint[0],
            "height": endpoint[1] - startpoint[1]
        }
        data['code'] = str(ord(currentchar))
        data['margin'] = endpoint[0] - startpoint[0]
        data['metrics'] = {
            "height": endpoint[1],
            "width": endpoint[1],
            "x": 0,
            "y": 0
        }

        # 数据构建完成，在原JSON中添加这条glyph记录
        self.__jsonfile['glyphs'].append(data)

    # 写入字体信息到csv (for GMS game, e.g. TS!Underswap)
    def write_fontimg_csv(self, fontinfo):
        pass

    
    # 字图制作与导入task
    def glyph_genetask(self) -> None:
        # 初始化后：对于glyph_info的每个字体记录读取基本信息
        for cfg in self.__fontconfig:
            fontfile = cfg['font']
            charset = cfg['char']
            size = cfg['size']
            threshold = cfg['threshold'] if 'threshold' in cfg else 0

            # 对于字库中的每个字符：不断读取并发送给绘制程序
            with open(charset, "r", encoding="UTF-8") as file:
                # 获取文件长度
                limit = len(file.read())
                file.seek(0, 0)

                for it in range(limit):
                    ch = file.read(1)
                    if ch == '\n':   # 跳过换行符
                        continue
                    # 首先，绘制字图
                    fontinfo = self.draw_singlefont(fontfile, ch, size, threshold)
                    # 随后，添加到主字图中
                    self.add_fontimg(fontinfo)
                    # 接着，更新JSON文件或CSV文件
                    self.write_fontimg_json(fontinfo, ch)
                    #self.write_fontimg_csv(fontinfo)
        
        # 完成JSON与字图的的更新，进行保存
        self.glyph.save(f"dest/{self.__name}.png")
        return self.__jsonfile


# # 模块2：将小字图拼接成大字图和对应的json
# def font_reader(fontfile, charset, size, out_fontpng, out_json, y_offset):
#     # 设定初始x，y坐标，画布大小，初始化glyph列表
#     # for 每个 charset 的字符：
#         # 调用 single_font 绘制图片
    
#         # 得到图片矩阵后，计算宽高
#         # 将单字图整合到全字图，如果x+宽超过画布大小，执行换行代码块（有点想用类）初始化x,y
#         # 修正x,y位置
    
#         # 利用x,y+y_offset,宽、高信息整合JSON，追加到glyphs
#         # 维护一个maxheight，用于换行时向下移动
    
#     # 返回字图矩阵与json
#     # return out_fontpng, out_json
#     pass

# # 模块3：拼接不同的字图，并整合与修正json
# def merge_fontinfo(infodict, glyphinfo_list, out_merged_png, out_merged_json):
#     # 对于list里面的每个font, char, size，调用font_reader生成字图矩阵和json
#     # offset参数初始为0，之后每次递增上一图片的高度值，作为写入整合的json的y值纵向偏移
#     # 每次返回的json进行拼接，再整合进infodict的glyph键对应的值
#     # 输出目标文件
#     # return out_merged_png, out_merged_json
#     pass

# # 模块4：对于每个字体进行一次制作
# def task(basicinfo_csv, glyphinfo_json):
#     # 打开csv和json

#     # for 每一行csv的信息：
#         # 根据name，shift等整合出一个info字典
#         # 在json中读取一条记录，获取该字体下的每一条font, char, size记录，添加到glyphinfo_list
#         # 导入的不同charset需要进行去重（前面的优先级高）
#         # glyphinfo的size是生成子图时使用的字体大小，不一定需要和字体基本配置的size一致
#         # infodict传入merge_fontinfo用于整合, glyphinfo_list传入merge_fontinfo 用于生成和拼接字图
#     pass

# 执行主程序
def main():
    # 文件路径
    csv_path = "font_info/basicinfo.csv"
    json_path = "font_info/glyphinfo.json"

    if os.path.exists("dest"):
        os.system("rm -r dest")
    os.mkdir("dest")

    fontnamelist = ["ComicSans",
                "CryptOfTomorrow",
                "DeterminationMono",
                "DeterminationSans",
                "DiaryOfAn8BitMage",
                "DotumChe",
                "MarsNeedsCunnilingus",
                "Papyrus"
    ]
    destjson = list()

    for name in fontnamelist:
        glyph = FontGlyph(name, csv_path, json_path)
        destjson.append(glyph.glyph_genetask())
    
    # 保存JSON文件
    with open(f"dest/fonts.json", "w", encoding="UTF-8") as json_file:
        json.dump(destjson, json_file, ensure_ascii=False, indent=4, separators=(", ", ": "))
    
    print("OK.")

if __name__ == '__main__':
    main()
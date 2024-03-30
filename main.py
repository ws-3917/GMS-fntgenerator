# 字图配置生成
import csv, json
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 定义字图类
class FontGlyph:
    # 初始化
    width = height = 4096   # 大小

    def __init__(self, name, basicinfo_csv, glyphinfo_json) -> None:
        # 当前绘制的x,y位置
        self.__x = 0
        self.__y = 0
        self.__line_maxheight = 0   # 当前行字体的最大高度，用于换行
        self.__name = name
        self.__basicinfo = basicinfo_csv
        self.__glyphinfo = glyphinfo_json

        # 主字图
        self.glyph = Image.fromarray(np.zeros((self.width, self.height, 2), np.uint8))

        # 主JSON，csv
        self.jsonfile = self.init_json()
        self.csv = list()

    # 初始化基本信息并写入json
    def init_json(self) -> dict:
        csv_reader = csv.reader(open(self.__basicinfo))

        infoline = True
        for row in csv_reader:
            if infoline:
                infoline = False
                keys = row
                continue
            
            # 选择数据
            if row['name'] == self.__name:
                data = dict(zip(keys, row))
                break

        # 对于 Outertale 的特殊处理
        data['shift'] = {"x": data['shift_x'], "y": data['shift_y']}
        data.pop('shift')

        # 准备绘制子图
        data['glyph'] = []

        return data

    # 绘制单个字体字图
    def draw_singlefont(self, fontfile, currentchar, size) -> tuple:
        # 读取字体，生成 size*4 的字体对象
        # 绘制4倍size的字图
        # 将图片压制到原size大小，邻近像素
        # 二值化，返回字图矩阵
        font = ImageFont.truetype(fontfile, size)
        startpoint, endpoint = font.getbbox(currentchar)[:2], font.getbbox(currentchar)[2:]

        # 初始化完毕，创建子图（二值图）
        fontimg = Image.new(1, endpoint)
        # 绘制
        drawtool = ImageDraw.Draw(fontimg)
        drawtool.text((0, 0), currentchar, fill=1)

        # 缩放步骤可以省略，转换为透明图
        fontimg = self.convert_pic(fontimg)
        fontinfo = (startpoint, endpoint, fontimg)

        return fontinfo

    # 将生成的二值图透明化，转为含Alpha的灰度图
    def convert_pic(self, fontimg) -> Image:
        fontimg_arr = np.asarray(fontimg)
        new_arr = np.empty((fontimg.shape[0], fontimg.shape[1], 2), np.uint8)

        # 将二值点转为 [255, 255] 或 [0, 0]
        new_arr[..., 1] = new_arr[..., 0] = fontimg_arr*255

        # 转换回 Image 对象
        new_fontimg = Image.fromarray(new_arr, "LA")
        return new_fontimg
        
    # 将字体添加到总字图上
    def add_fontimg(self, fontinfo) -> None:
        # 主要处理换行和字体偏移量
        endpoint = fontinfo[1]
        fontimg = fontinfo[2]
        # 如果已经排到末尾，+1 是预留的间距
        if self.__x + endpoint[0] + 1 > self.width:
            # 移动到下一行开头
            self.__x = 0
            self.__y += self.__line_maxheight + 1
            # 重置最大行
            self.__line_maxheight = 0
        
        # 粘贴图片
        self.glyph.paste(fontimg, (self.__x, self.__y))
        # 移动坐标
        self.__x += endpoint[0] + 1
        self.__line_maxheight = max(self.__line_maxheight, endpoint[1])

    # 写入字体信息到JSON (for Outertale)
    def write_fontimg_json(self, fontinfo, currentchar) -> None:
        pass

    # 写入字体信息到csv (for GMS game, e.g. TS!Underswap)
    def write_fontimg_csv(self, fontinfo):
        pass

    # 字图制作与导入task
    def outertale_task(self):
        pass


# 模块1：生成每个字体图
def single_font(fontfile, currentchar, size):

    pass


# 模块2：将小字图拼接成大字图和对应的json
def font_reader(fontfile, charset, size, out_fontpng, out_json, y_offset):
    # 设定初始x，y坐标，画布大小，初始化glyph列表
    # for 每个 charset 的字符：
        # 调用 single_font 绘制图片
    
        # 得到图片矩阵后，计算宽高
        # 将单字图整合到全字图，如果x+宽超过画布大小，执行换行代码块（有点想用类）初始化x,y
        # 修正x,y位置
    
        # 利用x,y+y_offset,宽、高信息整合JSON，追加到glyphs
        # 维护一个maxheight，用于换行时向下移动
    
    # 返回字图矩阵与json
    # return out_fontpng, out_json
    pass

# 模块3：拼接不同的字图，并整合与修正json
def merge_fontinfo(infodict, glyphinfo_list, out_merged_png, out_merged_json):
    # 对于list里面的每个font, char, size，调用font_reader生成字图矩阵和json
    # offset参数初始为0，之后每次递增上一图片的高度值，作为写入整合的json的y值纵向偏移
    # 每次返回的json进行拼接，再整合进infodict的glyph键对应的值
    # 输出目标文件
    # return out_merged_png, out_merged_json
    pass

# 模块4：对于每个字体进行一次制作
def task(basicinfo_csv, glyphinfo_json):
    # 打开csv和json

    # for 每一行csv的信息：
        # 根据name，shift等整合出一个info字典
        # 在json中读取一条记录，获取该字体下的每一条font, char, size记录，添加到glyphinfo_list
        # 导入的不同charset需要进行去重（前面的优先级高）
        # glyphinfo的size是生成子图时使用的字体大小，不一定需要和字体基本配置的size一致
        # infodict传入merge_fontinfo用于整合, glyphinfo_list传入merge_fontinfo 用于生成和拼接字图
    pass

# 执行主程序
def main():
    # 文件路径
    csv_path = "basicinfo.csv"
    json_path = "glyphinfo.json"

    task(csv_path, json_path)

if __name__ == '__main__':
    main()
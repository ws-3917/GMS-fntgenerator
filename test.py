from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image, ImageDraw, ImageFont

class MyFontTool:
    def __init__(self):
        self.__glyphs = {}  # 保存字形图像的字典
        self.__cmap = {}  # 保存字符到字形名称的映射

    def draw_singlefont(self, currentchar: str, fontcfg: dict) -> tuple:
        # 示例：创建一个简单的图像并绘制字符
        width, height = 64, 64
        img = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 48)
        draw.text((0, 0), currentchar, 255, font=font)

        # 将图像和字符保存到字典
        self.__glyphs[currentchar] = img
        self.__cmap[ord(currentchar)] = f"glyph{ord(currentchar)}"
        return img, (width, height)

    def generate_ttf(self, font_name: str) -> None:
        font = TTFont()

        # 添加基本表
        font['head'] = newTable('head')
        font['hhea'] = newTable('hhea')
        font['maxp'] = newTable('maxp')
        font['OS/2'] = newTable('OS/2')
        font['hmtx'] = newTable('hmtx')
        font['cmap'] = newTable('cmap')
        font['loca'] = newTable('loca')
        font['glyf'] = newTable('glyf')
        font['name'] = newTable('name')
        font['post'] = newTable('post')

        # 初始化 cmap 表
        cmap_table = font['cmap'].tables.append(newTable('cmap').table)
        cmap_table.platformID = 3
        cmap_table.platEncID = 1
        cmap_table.language = 0
        cmap_table.cmap = self.__cmap

        # 添加字形
        for char, img in self.__glyphs.items():
            glyph_name = f"glyph{ord(char)}"
            pen = TTGlyphPen(None)
            width, height = img.size

            # 创建字形轮廓
            pen.moveTo((0, 0))
            pen.lineTo((width, 0))
            pen.lineTo((width, height))
            pen.lineTo((0, height))
            pen.closePath()

            glyph = pen.glyph()
            glyph.width = width

            # 添加字形到字体
            font['glyf'][glyph_name] = glyph

        # 保存 TTF 文件
        font.save(f'psot_{font_name}.ttf')

# 示例用法
font_tool = MyFontTool()
font_tool.draw_singlefont('A', {})
font_tool.generate_ttf('example')

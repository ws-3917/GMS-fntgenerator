# 字图配置生成
import csv, json, os
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 定义字图类
class FontGlyph:
    # 初始化
    pic_width = 1024    # 全局宽度

    def __init__(self, name, basicinfo_csv, glyphinfo_json) -> None:
        # 当前绘制的x,y位置
        self.__x = 0
        self.__y = 0
        self.__name = name

        # 主字图
        self.__fontconfig = self.init_fontconfig(glyphinfo_json)
        self.pic_height = self.calc_height()
        self.glyph = Image.fromarray(np.zeros((self.pic_height, self.pic_width, 2), np.uint8))
        
        # 主JSON，csv
        self.__jsonfile = self.init_json(basicinfo_csv)
        self.__csv = list()

    # 4-1 更新：图像高度计算
    def calc_height(self):
        expectedheight = 0
        for cfg in self.__fontconfig:
            # 读取文件内字符总数
            with open(cfg["charset"], "r", encoding="UTF-8") as file:
                charlen = len(file.read())
            # 通过字符总数和字体矩阵宽度计算行数
            ch_perline = self.pic_width // cfg['width']
            linecount = charlen // ch_perline + int(charlen % ch_perline > 0)  # 向上取整

            expectedheight += linecount * cfg['height']
        
        return expectedheight

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
                # 4-1 更新：添加缺省值补全代码
                result = info['glyph_info']
                result = self.modify_glyphinfo(result)
                return result
        
        return None
    
    # 补全和设置字图信息中的缺省值
    def modify_glyphinfo(self, source) -> dict:
        cfglen = len(source)
        for it in range(cfglen):
            cfg = source[it]
            # 修正：添加像素字体选项
            cfg['pixel'] = cfg['pixel'] if 'pixel' in cfg else False
            if not 'threshold' in cfg or cfg['pixel']:
                cfg['threshold'] = 0
            
            # 4-1 Update: 全面取消 gap 参数
            # 采用矩形拼接的想法：将每种字体的字符放在一个宽度和高度固定的矩形框中
            # 矩形框的宽度和高度可手动指定，如果没有指定，则按照某一字符的endpoint指定
            # 指定了矩形框大小后，再指定每一个字体的绘制高度起点（可以是负数）
            font = ImageFont.truetype(cfg['fontfile'], size=cfg['size'])
            fontselect = ["A", "g", "赢"]

            optionalkeys = ['extrawidth', 'extraheight', "start_height", 'start_width']
            for keyname in optionalkeys:
                if keyname not in cfg:
                    cfg[keyname]  = 0

            # 字框大小设置
            cfg['width'] = max([font.getbbox(ch)[2] for ch in fontselect]) + cfg['extrawidth']
            cfg['height'] = max([font.getbbox(ch)[3] for ch in fontselect]) + cfg['extraheight']

            source[it] = cfg
            
        return source

    # 绘制单个字体字图
    def draw_singlefont(self, currentchar, fontcfg) -> tuple:
        font = ImageFont.truetype(fontcfg['fontfile'], fontcfg['size'])

        startpoint = [fontcfg['start_width'], fontcfg['start_height']]
        # 在图片上添加字体后写入配置文件
        fontcfg['drawwidth'] = fontcfg['width']
        fontcfg['drawheight'] = fontcfg['height']
        # 此处检测是否有专门指定width, height的字符
        if "spec_char" in fontcfg:
            for spec_char in fontcfg['spec_char']:
                if spec_char['char'] == currentchar:
                    startpoint[0] = spec_char['start_width'] if 'start_width' in spec_char else startpoint[0]
                    startpoint[1] = spec_char['start_height'] if 'start_height' in spec_char else startpoint[1]
                    if 'extrawidth' in spec_char:
                        fontcfg['drawwidth'] += spec_char['extrawidth'] - fontcfg['extrawidth']
                    if 'extraheight' in spec_char:
                        fontcfg['drawheight'] += spec_char['extraheight'] - fontcfg['extraheight']
                    break
        
        endpoint = (fontcfg['width'], fontcfg['height'])

        # 初始化完毕，创建子图（二值图）
        if fontcfg['pixel']:
            fontimg = Image.new('1', endpoint)
        else:
            fontimg = Image.new('L', endpoint)
        # 绘制
    
        drawtool = ImageDraw.Draw(fontimg)
        drawtool.text(startpoint, currentchar, fill=255, font=font)

        # 缩放步骤可以省略，转换为透明图
        fontimg = self.convert_pic(fontimg, fontcfg['threshold'])

        return fontimg

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
    def add_fontimg(self, fontimg, fontcfg) -> None:
        # 主要处理换行和字体偏移量
        width = fontcfg['width']
        height = fontcfg['height']
        # 如果已经排到末尾，+1 是预留的间距
        if self.__x + width > self.pic_width:
            # 移动到下一行开头
            self.__x = 0
            # 移动坐标
            self.__y += height
        
        # 粘贴图片
        self.glyph.paste(fontimg, (self.__x, self.__y))
        # 移动坐标
        self.__x += width

    # 写入字体信息到JSON (for Outertale)
    def write_fontimg_json(self, fontcfg, currentchar) -> None:
        width = fontcfg['drawwidth']
        height = fontcfg['drawheight']
        data = dict()

        # 构建 outertale 接受的 JSON 数据
        data['area'] = {
            "x": self.__x - width,
            #"y": self.__y + startpoint[1],
            # 高度修正
            "y": self.__y,
            "width": width,
            "height": height
        }
        data['code'] = str(ord(currentchar))
        data['margin'] = width
        data['metrics'] = {
            "height": height,
            "width": width,
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
            # 对于字库中的每个字符：不断读取并发送给绘制程序
            with open(cfg['charset'], "r", encoding="UTF-8") as file:
                # 获取文件长度
                limit = len(file.read())
                file.seek(0, 0)

                for _ in range(limit):
                    ch = file.read(1)
                    if ch == '\n':   # 跳过换行符
                        continue
                    # 首先，绘制字图
                    fontimg = self.draw_singlefont(ch, cfg)
                    # 随后，添加到主字图中
                    self.add_fontimg(fontimg, cfg)
                    # 接着，更新JSON文件或CSV文件
                    self.write_fontimg_json(cfg, ch)
                    #self.write_fontimg_csv(cfg, ch)
            
            # 修正：完成一份字体配置后，进行换行准备下一字体集导入
            self.__x = 0
            self.__y += cfg['height']

        # 完成JSON与字图的的更新，进行保存
        self.glyph.save(f"dest/{self.__name}.png")
        return self.__jsonfile

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
        json.dump(destjson, json_file, 
                  ensure_ascii=False, indent=4, separators=(", ", ": "))
    
    print("OK.")

if __name__ == '__main__':
    main()
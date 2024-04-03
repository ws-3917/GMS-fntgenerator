# 字图配置生成主程序
import csv, json, os
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 定义字图类
class FontGlyph:
    # 初始化
    def __init__(self, name, glyphinfo_json, basicinfo_csv, fallbackfont='', width=2048) -> None:
        # 当前绘制的x,y位置
        self.__x = 0
        self.__y = 0
        self.__name = name
        self.__charcount = []        # 用于字符计数
        self.__fbfontpath = fallbackfont    # 缺省字体路径

        # 主字图
        self.__fontconfig = self.init_fontconfig(glyphinfo_json)
        self.pic_width = width
        self.pic_height = self.calc_height()
        self.glyph = Image.fromarray(np.zeros((self.pic_height, self.pic_width, 2), np.uint8))

        # 主JSON，csv
        self.__jsonfile = self.init_json(basicinfo_csv)
        self.__csv = [
            [self.__name, self.__jsonfile['size'], False, False, 1, 0, 1, 1]    # 写入csv信息行
        ]

    # 04-01 更新：图像高度计算
    def calc_height(self):
        expectedheight = 0
        it = 0  # 迭代指标
        for cfg in self.__fontconfig:
            # 通过字符总数和字体矩阵宽度计算行数
            charlen = self.__charcount[it]

            ch_perline = self.pic_width // cfg['width']
            linecount = charlen // ch_perline + int(charlen % ch_perline > 0)  # 向上取整

            expectedheight += linecount * cfg['height']
            it += 1
        
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
        if data.get('shift_x') and data.get('shift_y'):
            data['shift'] = {"x": float(data.get('shift_x') or 0), "y": float(data.get('shift_y') or 0)}
            data.pop('shift_x')
            data.pop('shift_y')
        
        data['size'] = int(data['size'])

        # 准备绘制字图
        data['glyphs'] = []

        return data

    # 初始化字体信息
    def init_fontconfig(self, glyphinfo : str) -> dict:
        # 打开并读取JSON
        with open(glyphinfo, "r", encoding="UTF-8") as file:
            fullcfg = json.load(file)
        
        for info in fullcfg:
            if info['name'] == self.__name:
                # 04-01 更新：添加缺省值补全代码
                result = info['glyph_info']
                result = self.modify_glyphinfo(result)
                return result
        
        return None
    
    # 补全和设置字图信息中的缺省值
    def modify_glyphinfo(self, source : list) -> dict:
        cfglen = len(source)
        for it in range(cfglen):
            cfg = source[it]

            # 04-03 优化：在这一步骤顺带读取字符总数，追加到对象的变量中
            with open(cfg['charset'], "r", encoding="UTF-8") as file:
                self.__charcount.append(len(file.read()))
                
            # 03-30 修正：添加像素字体选项
            if 'pixel' not in cfg:
                cfg['pixel'] = False
            if not 'threshold' in cfg or cfg['pixel']:
                cfg['threshold'] = 0
            
            # 04-01 Update: 全面取消 gap 参数
            # 采用矩形拼接的想法：将每种字体的字符放在一个宽度和高度固定的矩形框中
            # 矩形框的宽度和高度可手动指定，如果没有指定，则按照某一字符的endpoint指定
            # 指定了矩形框大小后，再指定每一个字体的绘制高度起点（可以是负数）。
            fontselect = ["A", "g", "赢"]

            optionalkeys = ['extrawidth', 'extraheight', "start_height", 'start_width']
            for keyname in optionalkeys:
                if keyname not in cfg:
                    cfg[keyname] = 0

            # 字框大小设置
            font = ImageFont.truetype(cfg['fontfile'], cfg['size'])
            cfg['width'] = max([font.getbbox(ch)[2] for ch in fontselect]) + cfg['extrawidth']
            cfg['height'] = max([font.getbbox(ch)[3] for ch in fontselect]) + cfg['extraheight']

            source[it] = cfg
            
        return source

    # 04-03 更新：针对 spec_char 特定字符设定
    def get_font_config(self, currentchar : str, fontcfg : dict):
        # 使用默认配置
        config = {
            'startpoint': [fontcfg['start_width'], fontcfg['start_height']],
            'width': fontcfg['width'],
            'height': fontcfg['height']
        }

        # 根据字符调整配置
        spec_chars = fontcfg.get('spec_char', {})
        if currentchar in spec_chars:
            spec = spec_chars[currentchar]
            config['startpoint'][0] += spec.get('start_width', 0)
            config['startpoint'][1] += spec.get('start_height', 0)
            config['width'] += spec.get('extrawidth', 0)
            config['height'] += spec.get('extraheight', 0)

        return config
    
    # 绘制单个字体字图
    def draw_singlefont(self, currentchar : str, fontcfg : dict, fallback : bool = False) -> tuple:
        # 04-03 更新：分离 特殊字符处理和字符绘制的代码
        config = self.get_font_config(currentchar, fontcfg)
        
        startpoint = config['startpoint']
        endpoint = (config['width'], config['height'])

        # 初始化完毕，创建子图（二值图）
        imgtype = '1' if fontcfg['pixel'] else 'L'
        fontimg = Image.new(imgtype, endpoint)

        # 绘制
        drawtool = ImageDraw.Draw(fontimg)
        drawfont = self.__fbfont if fallback else self.__font
        
        drawtool.text(startpoint, currentchar, fill=255, font=drawfont)

        # 缩放步骤可以省略，转换为透明图
        fontimg = self.convert_pic(fontimg, fontcfg['threshold'], currentchar)
        return (fontimg, endpoint)

    # 将生成的二值图透明化，转为含Alpha的灰度图
    def convert_pic(self, fontimg : Image, threshold : int, currentchar : str) -> Image:
        fontimg_arr = np.asarray(fontimg)

        # 04-03 Update：如果发现绘制的字图全空白且对应字符不是空格，则直接跳过转换，返回None
        if currentchar != ' ' and np.all(fontimg_arr == 0):
            return None
        
        new_arr = np.empty((fontimg_arr.shape[0], fontimg_arr.shape[1], 2), np.uint8)

        # 二值化
        new_arr[..., 1] = new_arr[..., 0] = (fontimg_arr>threshold)*255

        # 转换回 Image 对象
        new_fontimg = Image.fromarray(new_arr, "LA")
        return new_fontimg
    
    # 将字体添加到总字图上
    def add_fontimg(self, fontimg : Image, endpoint : tuple) -> None:
        # 主要处理换行和字体偏移量
        (width, height) = endpoint
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

    # 更新字体信息到JSON (for Outertale)
    def update_fontimg_json(self, currentchar : str, endpoint: tuple) -> None:
        (width, height) = endpoint
        data = dict()

        # 构建 outertale 接受的 JSON 数据
        data['area'] = {
            "x": self.__x - width,
            #"y": self.__y + startpoint[1],
            # 03-30：高度修正
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

    # 获取生成的json
    def get_fontimg_json(self) -> dict:
        return self.__jsonfile
    
    # 04-03 Update：更新字体信息到csv (for GMS game, e.g. TS!Underswap)
    def update_fontimg_csv(self, currentchar : str, endpoint: tuple) -> None:
        (width, height) = endpoint

        # 构建数据
        data = [
            ord(currentchar),   # 字符编码
            self.__x - width, self.__y,  # 字图左上角坐标
            width, height,      # 宽、高
            width, 0            # 字距、偏移，之前已经调整，保持默认即可
        ]

        # 数据构建完成，添加记录
        self.__csv.append(data)

   # 04-03 Update：写入生成的csv到文件
    def write_fontimg_csv(self, distpath : str) -> None:
        with open(distpath, "w", encoding="UTF-8", newline='') as file:
            writerobj = csv.writer(file)
            writerobj.writerows(self.__csv)
    
    # 字图制作与导入task
    def glyph_genetask(self) -> None:
        # 初始化后：对于glyph_info的每个字体记录读取基本信息
        it = 0
        for cfg in self.__fontconfig:
            # 对于字库中的每个字符：不断读取并发送给绘制程序
            # 首先，对字体进行实例化
            self.__font = ImageFont.truetype(cfg['fontfile'], cfg['size'])
            # 04-03 更新：缺字时尝试调用缺省字体路径
            if os.path.exists(self.__fbfontpath):
                self.__fbfont = ImageFont.truetype(self.__fbfontpath, cfg['size'])  
            else:
                print("WARNING: fallback font not found.")
                self.__fbfont = None

            with open(cfg['charset'], "r", encoding="UTF-8") as file:
                # 获取字符集的字符个数
                # limit = len(file.read())
                # file.seek(0, 0)
                limit = self.__charcount[it]

                for _ in range(limit):
                    ch = file.read(1)
                    if ch == '\n':   # 跳过换行符
                        continue
                    # 首先，绘制单字字图
                    fontimg, endpoint = self.draw_singlefont(ch, cfg)
                    # 04-03 Update：如果发现空字图，说明当前字体缺少对应字符
                    if not fontimg:
                        # 此时，尝试调用缺省字体文件
                        if self.__fbfont:
                            # 如果发现缺省字体，则用缺省字体重新绘制
                            fontimg, endpoint = self.draw_singlefont(ch, cfg, fallback=True)
                        else:   # 否则，直接跳过这一字体
                            continue
                    # 随后，将单字添加到总的大字图
                    self.add_fontimg(fontimg, endpoint)
                    # 接着，更新JSON文件或CSV文件
                    self.update_fontimg_json(ch, endpoint)
                    self.update_fontimg_csv(ch, endpoint)
                it += 1     # 迭代指标

            # 03-30 修正：完成一份字体配置后，进行换行准备下一字体集导入
            self.__x = 0
            self.__y += cfg['height']

    # 04-03 优化：保存生成的字图
    def save_glyph(self, distpath : str) -> None:
        self.glyph.save(distpath)

# 执行主程序
def main():
    # 配置文件路径
    csv_path = "font_info/basicinfo.csv"
    json_path = "font_info/glyphinfo.json"

    # 输出路径
    if os.path.exists("dist"):
        os.system('powershell "rm -r dist"')
    os.mkdir("dist")

    # 字体名称
    fontnamelist = ["ComicSans",
                "CryptOfTomorrow",
                "DeterminationMono",
                "DeterminationSans",
                "DiaryOfAn8BitMage",
                "DotumChe",
                "MarsNeedsCunnilingus",
                "Papyrus"
    ]
    distjson = list()

    # 生成字图和配置文件
    for name in fontnamelist:
        glyph = FontGlyph(name, json_path, csv_path,
                          fallbackfont="fnt_zh-cn/unifont.otf", width=1024)    # 初始化字图对象
        glyph.glyph_genetask()  # 生成字图

        glyph.save_glyph(f"dist/{name}.png")          # 保存字图
        distjson.append(glyph.get_fontimg_json())     # 写入JSON
        glyph.write_fontimg_csv(f"dist/glyphs_fnt_{name}.csv")  # 写入csv
    
    # 保存JSON文件
    with open(f"dist/fonts.json", "w", encoding="UTF-8") as json_file:
        json.dump(distjson, json_file, 
                  ensure_ascii=False, indent=4, separators=(", ", ": "))
    
    print("OK.")

if __name__ == '__main__':
    main()
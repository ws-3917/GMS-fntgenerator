# 字图配置生成主程序 - 0616重置版
import csv, json
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from termcolor import colored

# 字图类，每个字体独立
class FontGlyph:
    # 所属项目（用来查询路径），语言列表，字图宽度
    def __init__(self, project : str, langlist : list, totalwidth:int = 2048):
        self.project = project
        self.langlist = langlist
        self.totalwidth = totalwidth
        self.rest = 4   # 松弛间隔，防止行之间重叠
        # 根据project读取对应路径下的base,获取字体列表和基本信息
        with open(f"info/{self.project}/base.json", encoding="utf-8") as file:
            self.baseinfo = dict(json.loads(file.read()))
        self.fontlist = tuple(self.baseinfo.keys())

        # 预加载所有配置信息到内存
        self.fontinfo = dict()
        self.charset = dict()
        for lang in self.langlist:
            with open(f"info/{self.project}/{lang}.json", encoding="utf-8") as file:
                self.fontinfo[lang] = dict(json.loads(file.read()))
            with open(f"charset/{lang}.txt", encoding="utf-8") as file:
                self.charset[lang] = file.read()
        
        # 读取fallback字体信息
        with open(f"info/{self.project}/fallback.json", encoding="utf-8") as file:
            self.fallbackinfo = dict(json.loads(file.read()))
    
    # 获取字体大小
    def loadsize(self, font) -> None:
        self.fontsize = dict()
        testfont = ["A", "g", "赢"]     # 用来确定字体实际大小的测试用汉字
        for lang in self.langlist:
            fontobj = ImageFont.truetype(
                self.fontinfo[lang][font]["fontfile"], 
                self.fontinfo[lang][font]["size"]
            )
            self.fontsize[lang] = (
                max([fontobj.getbbox(ch)[2] for ch in testfont]),
                max([fontobj.getbbox(ch)[3] for ch in testfont]),
            )
    
    # 自动计算图片高度
    def totalheight(self, font) -> int:
        height = 0
        for lang in self.langlist:
            charcount = len(self.charset[lang]) # 字符数
            height += (self.fontsize[lang][1] + self.rest) * (
                charcount // (self.totalwidth // self.fontsize[lang][0]) + 1
            )
        return height

    def check(self, ch) -> str:
        # 特殊字符直接放行或跳过
        if ch in [' ', '　']:
            return 'yep'
        if ch == '\n':
            return 'nope'
        testglyph = Image.new("1", (self.width, self.height), 0)
        ImageDraw.Draw(testglyph).text((0, 0), ch, fill=1, 
                                font=self.enfont if ord(ch) > 0xfee0 else self.font)  
        # 检查字图
        if testglyph:
            return 'yep'
        # 尝试使用fallback
        else:
            ImageDraw.Draw(testglyph).text((0, 0), ch, fill=1, font=self.fallbackfont)
            if testglyph:
                return 'fallback'
            else:
                return 'nope'
    
    def addfont(self, ch, fallback=False) -> None:
        # 先获取基本信息
        if fallback:
            cfg = self.fallbackcfg
            font = self.fallbackfont
        elif ord(ch) > 0xfee0:
            cfg = self.encfg
            font = self.enfont
        else:
            cfg = self.cfg
            font = self.font
        start_x = cfg.get("start_x", 0)
        start_y = cfg.get("start_y", 0)
        width = cfg.get("extra_x", 0) + self.width
        height = cfg.get("extra_y", 0) + self.height

        # 检查是否有单独的控制
        specials = cfg.get("special", {})
        if ch in specials:
            specialcfg = specials[ch]
            start_x += specialcfg.get("start_x", 0)
            start_y += specialcfg.get("start_y", 0)
            width += specialcfg.get("extra_x", 0)
            height += specialcfg.get("extra_y", 0)

        # 检查是否会换行
        if self.x + width > self.totalwidth:
            self.x = 0
            self.y += self.height + self.rest
        
        # 开始绘制
        self.drawtool.text((self.x + start_x, self.y + start_y),
                           ch, fill=255, font=font)

        # 添加csv数据
        self.csv.append((ord(ch), self.x, self.y, width, height,
                         0, 0, width, height))

        # 移动画笔，准备下一次绘制
        self.x += width
        self.y += height
   
    # 主任务：生成字图
    def task(self) -> None:
        # 对于每个字体
        for font in self.fontlist:
            # 创建新字图
            print(colored(f"--> {font}", "blue"))
            self.glyph = Image.new('LA', (self.totalwidth, self.totalheight(font)), 0)
            self.drawtool = ImageDraw.Draw(self.glyph)
            self.x = 0
            self.y = 0
            self.csv = [tuple(self.baseinfo[font].values())]
            self.loadsize(font)
            # 针对每种语言
            for lang in self.langlist:
                # 加载配置文件和字符集
                print(colored(f" -> {lang}", "yellow"))
                (self.width, self.height) = self.fontsize[lang]
                self.cfg = self.fontinfo[lang][font]
                self.font = ImageFont.truetype(self.cfg["fontfile"], self.cfg["size"])
                if lang == "en_US":
                    self.encfg = self.cfg
                    self.enfont = self.font
                self.fallbackcfg = self.fallbackinfo.get(self.cfg.get("fallback"))
                if self.fallbackcfg:
                    self.fallbackfont = ImageFont.truetype(self.fallbackcfg["fontfile"], self.fallbackcfg["size"])
                # 开始逐一绘制字符
                for ch in self.charset[lang]:
                    # 检查字符是否可用
                    status = self.check(ch) # 返回值有 yep, nope, fallback
                    if status == 'yep':
                        self.addfont(ch)    # addfont有csv的添加
                    elif status == 'fallback':
                        self.addfont(ch, fallback=True)
                    elif status == 'nope':
                        continue
                
                # 完毕后调整坐标位
                self.x = 0
                self.y += self.height + self.rest   # 此处和之前算height的+rest都是为了避免重叠打的补丁
            
            # 全部结束后，保存图片和csv到文件
            self.glyph.save(f"dist/{self.project}/{font}.png")
            with open(f"dist/{self.project}/{font}.csv", encoding="utf-8", newline='') as file:
                self.writer = csv.writer(file, delimiter=';')
                self.writer.writerows(self.csv)
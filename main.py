# 字图配置生成

# 模块1：生成每个字体图
def single_font(fontfile, currentchar, size):
    # 读取字体，生成 size*4 的字体对象
    # 绘制4倍size的字图
    # 将图片压制到原size大小，邻近像素
    # 二值化，返回字图矩阵

    # return out_singlefontpng
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
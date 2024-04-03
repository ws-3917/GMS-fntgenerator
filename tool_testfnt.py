# textfnt - 用于快速测试某些字符的绘图效果，
# 可以用于微调字体高度、尺寸，以及检验当前字体是否支持特定字符
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 字体路径、待显示字符、字体大小、绘图类型
# '1'代表二值图（黑白），'L'代表灰度图
fontfile = "fnt_zh-cn/fzsejt.ttf"   
ch = "你"
size = 18
glyphtype = '1'

font = ImageFont.truetype(fontfile, size)

# startpoint 为左上角绘制起点，endpoint为右下角绘制终点（图块大小）
# 可以用getbbox计算，也可以直接手动指定

#startpoint = (0, 0)
startpoint = font.getbbox(ch)[:2]
#endpoint = (18, 18)
endpoint = font.getbbox(ch)[2:]

# 绘图
newimg = Image.new(glyphtype, endpoint)
drawtool = ImageDraw.Draw(newimg)
drawtool.text(startpoint, ch, font=font, fill=255)

# 将二值图转为透明灰度图，使背景色透明，用于输出
arr = np.array(newimg)
# 创建一个新数组用于存储灰度和透明度
new_arr = np.empty((arr.shape[0], arr.shape[1], 2), dtype=np.uint8)
new_arr[..., 0] = new_arr[..., 1] = (arr>200)*255   # 设置灰度和透明度

# 预览时不方便查看透明图，可以将下面这一行代码注释掉，注释后透明化处理将不写入图片，预览为黑色背景
#newimg = Image.fromarray(new_arr, "LA")
#newimg.save("test.png")
newimg.show()

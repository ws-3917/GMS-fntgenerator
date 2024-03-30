from PIL import Image, ImageFont, ImageDraw
import numpy as np
fontfile = "fnt_zh-cn/unifont.otf"
ch = "!@#$!@#$!@#$"
fnt = ImageFont.truetype(fontfile, 16)
startpoint, endpoint = fnt.getbbox(ch)[:2], fnt.getbbox(ch)[2:]
newimg = Image.new('1', endpoint)
drawtool = ImageDraw.Draw(newimg)

# 将二值图转为透明灰度图
drawtool.text((0, 0), ch, font=fnt, fill=1)
arr = np.array(newimg)
# 创建一个新数组用于存储灰度和透明度
new_arr = np.empty((arr.shape[0], arr.shape[1], 2), dtype=np.uint8)

# 设置灰度和透明度
new_arr[..., 0] = arr*255  # 灰度
new_arr[..., 1] = arr*255  # 透明度（这里我们使透明度与灰度相同）

newimg = Image.fromarray(new_arr, "LA")
newimg.save("test.png")
# pic_startpoint, pic_endpoint --> fontpic
# 
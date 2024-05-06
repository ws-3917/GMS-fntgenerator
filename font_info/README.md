# README.md
This folder contains the font libraries and font information:

1. `char_cn.txt`: The main folder for storing Chinese fonts, which require sorting by Unicode encoding.
2. `char_en.txt`: The folder for storing Western fonts, which contain fewer characters and can be generated in bulk.
3. `char_sup_*.txt`: Supplementary font files, which can be used to retrieve additional characters as needed.
4. `basicinfo.csv`: A CSV file containing basic information about the fonts used in the game.
5. `glyphinfo.json`: Configuration information for generating font images.

The default set of Chinese fonts includes:
1. Common Chinese punctuation marks: 。、；：“”‘’（）【】《》—…！？·￥～〖〗〔〕
2. All primary common characters from the standard simplified Chinese character table.
3. The top 5000 most frequently used Chinese characters.
   (The character lists in 2 and 3 have been merged.)
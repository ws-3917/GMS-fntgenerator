# Undertale 同人作品汉化 字体导入及补字系统
<center>
    By. WS3917  2024-05-06
</center>

## 项目简介

该项目的目的是将 Game Maker Studio(以下简称 GMS) 制作的 UT 同人游戏的字图制作及配置文件的生成自动化。很多朋友在汉化相关作品时，经常遇到**中英文字体不对齐、缺字、字形异常**等恼人的问题，每次遇到只能手动排错，绘制、添加相应的字符，费时且无聊，所以打算开发一个将这些操作一键、自动化的操作。

该项目进行过重置，为了进行 PS! Outertale 游戏的汉化，重构后的代码加入了导出 JSON 配置文件的类方法（代码中将字图定义为一个类`Glyph`，绘制、拼接等操作定义为方法）。现在，可以使用该工具自动生成 PNG 格式的字图，及 JSON 和 CSV 格式的字体配置文件。

简而言之，该程序能**自动化 PS! Outertale 及 GMS 游戏（如 TS！Underswap、Undertale Yellow）的字库补齐、字形设置、字图生成等，支持多字体导入，每种字体可独立设置字形和字库**。


## 目录结构说明

本项目包括多个文件夹和脚本，用于生成和处理字体图像以及配置信息。以下是主要文件和文件夹的详细说明：

### 根目录
- `main.py`: 主脚本，用于生成字体图像和配置文件。
- `tool_sortsplit.py`: 工具脚本，用于对字符集文件进行排序和格式化。
- `tool_textfnt.py`: 工具脚本，用于测试和调整特定字符的绘图效果。
- `tool_unicode.py`: 工具脚本，提供Unicode值查询和字符编码查询等功能。

### `font_info` 文件夹
存放字体相关的配置文件和字符集列表，具体包括：
- `basicinfo.csv`: 包含游戏内使用的字体的基本信息，如字体名、尺寸等。
- `glyphinfo.json`: 存储字体图像生成时所需的详细字形配置信息。
- `char_cn.txt`: 存储中文字符集，包括常用汉字和标点符号。
- `char_en.txt`: 存储英文字符集，主要用于西文字体的生成。
- `char_sup_*.txt`: 补充字符文件，用于存放额外需要的特殊字符集。

### `dist` 文件夹
存放生成的字体图像和配置文件。在运行 `main.py` 脚本后，此文件夹将自动创建。生成的字体图像文件和配置信息将存于此处，其中：

1. `glyphs_*.csv` 是 GMS 游戏的字体配置文件，使用 Undertale Mod Tool 工具进行批量导入；
2. `*.png` 是字体字图，游戏在渲染字体时会选取字图中的子块；

## 使用方法

### 安装环境

确保你的系统中安装了 Python 3.x。首先，你需要安装 PIL 库和 numpy 库，这些库是处理图像和数组的重要工具。你可以通过以下命令安装所需的依赖：

```bash
pip install Pillow numpy
```

### 配置文件

在开始生成字图之前，需要确保字体信息和字形配置文件已经准备好。这些信息包括：

- `font_info/basicinfo.csv`：包含字体的基本信息，如字体名称、尺寸、字符集等。
- `font_info/glyphinfo.json`：定义了每种字体的字形信息，如字符宽高、绘制起点等。

确保这些文件正确填写并放置在适当的目录下。

### 运行程序

运行 `main.py` 脚本将自动执行字体图像生成和配置文件创建。你可以通过以下命令启动脚本：

```bash
python main.py
```

该脚本将处理列在 `font_info/basicinfo.csv` 中的每个字体，为每种字体生成一个 PNG 图像，并将配置数据写入 `dist/index.json` 文件中。所有生成的字图将保存在 `dist` 文件夹中。

### 检查输出

生成的字图和配置文件将存放在 `dist` 文件夹内。请检查这些文件确保它们符合预期的配置。PNG 文件中将包含每种字体的字图，而 JSON 文件中则包含字体的配置信息，可以用于游戏或其他程序中。

### 导入到游戏中

使用如 Undertale Mod Tool 的工具将生成的配置文件和字图导入到游戏中。导入过程中可能需要进行额外的配置调整，具体取决于游戏的具体需求和开发环境。

## 注意事项

- 确保在运行脚本前，`dist` 文件夹已清空或不存在，以避免旧文件影响新生成的文件。
- 脚本运行过程中，如果遇到字体文件缺失或字符集配置错误等问题，将会在控制台输出警告信息，请根据提示进行调整。

### 贡献指南

如果你想对项目做出贡献，可以通过以下方式：
- **提交问题**: 在 GitHub 仓库中提交问题报告，描述你遇到的问题或建议；
- **开发新功能**: 可以通过 Fork 项目，添加新功能或改进现有功能，然后通过 Pull Request 提交你的改动。

## 许可证
该项目采用 MIT 许可证，详见 `LICENSE` 文件。
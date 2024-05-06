# Undertale Fan Project Font Import and Completion System
<center>
    By. WS3917  2024-05-06
</center>

## Project Introduction

The purpose of this project is to automate the generation of font images and configuration files for Undertale fan games made with Game Maker Studio (hereinafter referred to as GMS). Many friends encounter annoying issues like misaligned Chinese and English fonts, missing characters, or abnormal glyph shapes when localizing such games. Each issue typically requires manual troubleshooting and adding the necessary characters, which is time-consuming and tedious. Therefore, we aim to develop a tool to automate these tasks.

Following a project reset to localize the PS! Outertale game, the refactored code now includes a class method for exporting JSON configuration files (with the font images defined as a `Glyph` class, and operations like drawing and concatenation defined as methods). Now, this tool can automatically generate PNG font images, along with JSON and CSV font configuration files.

In summary, this program automates the completion, glyph setting, and font image generation for PS! Outertale and GMS games (such as TS!Underswap, Undertale Yellow), supporting multiple font imports with individual settings for glyphs and font libraries.

## Directory Structure Explanation

This project includes multiple folders and scripts for generating and processing font images and configuration information. Here are detailed explanations of the main files and folders:

### Root Directory
- `main.py`: The main script for generating font images and configuration files.
- `tool_sortsplit.py`: A utility script for sorting and formatting character set files.
- `tool_textfnt.py`: A utility script for testing and adjusting the drawing effects of specific characters.
- `tool_unicode.py`: A utility script for Unicode value queries and character encoding queries.

### `font_info` Folder
Holds font-related configuration files and character set lists, specifically:
- `basicinfo.csv`: Contains basic information used within the game, such as font names, sizes, etc.
- `glyphinfo.json`: Stores detailed glyph configuration information needed for generating font images.
- `char_cn.txt`: Stores the Chinese character set, including commonly used characters and punctuation marks.
- `char_en.txt`: Stores the English character set, mainly used for generating Western fonts.
- `char_sup_*.txt`: Supplemental character files for storing additional special character sets needed.

### `dist` Folder
Stores generated font images and configuration files. This folder is automatically created after running the `main.py` script. The generated font images and configuration information are stored here, including:
1. `glyphs_*.csv` for GMS game font configuration files, used with tools like Undertale Mod Tool for batch import;
2. `*.png` for font images, where the game selects sub-blocks from the font images during rendering;

## Usage Guide

### Environment Installation

Ensure your system has Python 3.x installed. First, you need to install the PIL and numpy libraries, essential tools for image and array processing. Install the necessary dependencies with the following command:

```bash
pip install Pillow numpy
```

### Configuration Files

Before starting to generate font images, ensure that the font information and glyph configuration files are ready. This information includes:
- `font_info/basicinfo.csv`: Contains basic font information like name, size, character set, etc.
- `font_info/glyphinfo.json`: Defines the glyph information for each font, such as character width and height, drawing start point, etc.

Ensure these files are correctly filled out and placed in the appropriate directories.

### Running the Program

Running the `main.py` script will automatically execute the generation of font images and creation of configuration files. Start the script with the following command:

```bash
python main.py
```

The script will process each font listed in `font_info/basicinfo.csv`, generating a PNG image for each font and writing configuration data to the `dist/index.json` file. All generated font images will be saved in the `dist` folder.

### Checking Outputs

The generated font images and configuration files are stored in the `dist` folder. Check these files to ensure they meet the expected configurations. PNG files contain the font images, while JSON files contain configuration information for use in games or other programs.

### Importing into Games

Use tools like Undertale Mod Tool to import the generated configuration files and font images into the game. Additional configuration adjustments may be needed during the import process, depending on the specific needs of the game and development environment.

## Notes

- Ensure the `dist` folder is empty or does not exist before running the script to prevent old files from affecting the generation of new files.
- If font files are missing or there are configuration errors during the script run, warning messages will appear in the console. Please adjust according to the prompts.

### Contribution Guide

If you would like to contribute to the

 project, you can do so in the following ways:
- **Submit Issues**: Submit issue reports in the GitHub repository, describing the problems or suggestions you encounter;
- **Develop New Features**: Fork the project, add new features or improve existing ones, and submit your changes through a Pull Request.

## License
This project is licensed under the MIT license, see the `LICENSE` file for details.

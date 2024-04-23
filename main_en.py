import csv, json, os
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# Define the FontGlyph class
class FontGlyph:
    # Initialization
    def __init__(self, name, glyphinfo_json, basicinfo_csv, fallbackfont='', width=2048) -> None:
        # Current x,y drawing position
        self.__x = 0
        self.__y = 0
        self.__name = name
        self.__charcount = []  # For character counting
        self.__fbfontpath = fallbackfont  # Fallback font path

        # Main glyph image
        self.__fontconfig = self.init_fontconfig(glyphinfo_json)
        self.pic_width = width
        self.pic_height = self.calc_height()
        self.glyph = Image.fromarray(np.zeros((self.pic_height, self.pic_width, 2), np.uint8))

        # Main JSON, csv
        self.__jsonfile = self.init_json(basicinfo_csv)
        self.__csv = [
            [self.__name, self.__jsonfile['size'], False, False, 1, 0, 1, 1]  # CSV info line
        ]

    # Update 04-01: Calculate image height
    def calc_height(self):
        expectedheight = 0
        it = 0  # Iteration index
        for cfg in self.__fontconfig:
            # Calculate the number of lines based on the total number of characters and font matrix width
            charlen = self.__charcount[it]

            ch_perline = self.pic_width // cfg['width']
            linecount = charlen // ch_perline + int(charlen % ch_perline > 0)  # Round up

            expectedheight += linecount * cfg['height']
            it += 1
        
        return expectedheight

    # Initialize basic information and write to json
    def init_json(self, basicinfo) -> dict:
        csv_reader = csv.reader(open(basicinfo, "r", encoding="UTF-8"))

        infoline = True
        for row in csv_reader:
            if infoline:
                infoline = False
                keys = row
                continue
            
            # Select data
            if row[0] == self.__name:
                data = dict(zip(keys, row))
                break

        # Special processing for Outertale
        if data.get('shift_x') and data.get('shift_y'):
            data['shift'] = {"x": float(data.get('shift_x') or 0), "y": float(data.get('shift_y') or 0)}
            data.pop('shift_x')
            data.pop('shift_y')
        
        data['size'] = int(data['size'])

        # Prepare for drawing glyph image
        data['glyphs'] = []

        return data

    # Initialize font information
    def init_fontconfig(self, glyphinfo : str) -> dict:
        # Open and read JSON
        with open(glyphinfo, "r", encoding="UTF-8") as file:
            fullcfg = json.load(file)
        
        for info in fullcfg:
            if info['name'] == self.__name:
                # Update 04-01: Add default value completion code
                result = info['glyph_info']
                result = self.modify_glyphinfo(result)
                return result
        
        return None
    
    # Complete and set default values in glyph info
    def modify_glyphinfo(self, source : list) -> dict:
        cfglen = len(source)
        for it in range(cfglen):
            cfg = source[it]

            # Update 04-03: Read the total number of characters at this step, adding to the object's variable
            with open(cfg['charset'], "r", encoding="UTF-8") as file:
                self.__charcount.append(len(file.read()))
                
            # Correction 03-30: Add pixel font option
            if 'pixel' not in cfg:
                cfg['pixel'] = False
            if not 'threshold' in cfg or cfg['pixel']:
                cfg['threshold'] = 0
            
            # Update 04-01: Completely cancel the gap parameter
            # Rectangle stitching idea: put each type of font's characters in a rectangle with fixed width and height
            # The rectangle's width and height can be specified manually, if not specified, it's set by the endpoint of a character
            # After specifying the rectangle size, specify the drawing height start point for each font (can be negative).
            fontselect = ["A", "g", "赢"]

            optionalkeys = ['extrawidth', 'extraheight', "start_height", 'start_width']
            for keyname in optionalkeys:
                if keyname not in cfg:
                    cfg[keyname] = 0

            # Set the size of the character box
            font = ImageFont.truetype(cfg['fontfile'], cfg['size'])
            cfg['width'] = max([font.getbbox(ch)[2] for ch in fontselect]) + cfg['extrawidth']
            cfg['height'] = max([font.getbbox(ch)[3] for ch in fontselect]) + cfg['extraheight']

            source[it] = cfg
            
        return source

    # Update 04-03: Set up specific character settings for spec_char
    def get_font_config(self, currentchar : str, fontcfg : dict):
        # Use default configuration
        config = {
            'startpoint': [fontcfg['start_width'], fontcfg['start_height']],
            'width': fontcfg['width'],
            'height': fontcfg['height']
        }

        # Adjust configuration based on the character
        spec_chars = fontcfg.get('spec_char', {})
        if currentchar in spec_chars:
            spec = spec_chars[currentchar]
            config['startpoint'][0] += spec.get('start_width', 0)
            config['startpoint'][1] += spec.get('start_height', 0)
            config['width'] += spec.get('extrawidth', 0)
            config['height'] += spec.get('extraheight', 0)

        return config
    
    # Draw a single font glyph
    def draw_singlefont(self, currentchar : str, fontcfg : dict, fallback : bool = False) -> tuple:
        # Update 04-03: Separate the special character handling and character drawing code
        config = self.get_font_config(currentchar, fontcfg)
        
        startpoint = config['startpoint']
        endpoint = (config['width'], config['height'])

        # Initialization complete, create a sub-image (binary image)
        imgtype = '1' if fontcfg['pixel'] else 'L'
        fontimg = Image.new(imgtype, endpoint)

        # Draw
        drawtool = ImageDraw.Draw(fontimg)
        drawfont = self.__fbfont if fallback else self.__font
        
        drawtool.text(startpoint, currentchar, fill=255, font=drawfont)

        # Skip scaling step, convert to transparent image
        fontimg = self.convert_pic(fontimg, fontcfg['threshold'], currentchar)
        return (fontimg, endpoint)

    # Convert the binary image to an alpha-included grayscale image
    def convert_pic(self, fontimg : Image, threshold : int, currentchar : str) -> Image:
        fontimg_arr = np.asarray(fontimg)
        blankchr = [' ', '　']

        # Update 04-03: If the drawn glyph image is all blank and the corresponding character is not a space, skip conversion and return None
        if currentchar not in blankchr and np.all(fontimg_arr == 0):
            return None
        
        new_arr = np.empty((fontimg_arr.shape[0], fontimg_arr.shape[1], 2), np.uint8)

        # Binarization
        new_arr[..., 1] = new_arr[..., 0] = (fontimg_arr>threshold)*255

        # Convert back to Image object
        new_fontimg = Image.fromarray(new_arr, "LA")
        return new_fontimg
    
    # Add the font image to the main glyph image
    def add_fontimg(self, fontimg : Image, endpoint : tuple) -> None:
        # Handle line breaks and font offsets
        (width, height) = endpoint
        # If reaching the end of the line, +1 is a reserved gap
        if self.__x + width > self.pic_width:
            # Move to the beginning of the next line
            self.__x = 0
            # Move coordinates
            self.__y += height
        
        # Paste image
        self.glyph.paste(fontimg, (self.__x, self.__y))
        # Move coordinates
        self.__x += width

    # Update font information in JSON (for Outertale)
    def update_fontimg_json(self, currentchar : str, endpoint: tuple) -> None:
        (width, height) = endpoint
        data = dict()

        # Build JSON data accepted by Outertale
        data['area'] = {
            "x": self.__x - width,
            #"y": self.__y + startpoint[1],
            # Correction 03-30: Height correction
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

        # Data built, add this glyph record to the original JSON
        self.__jsonfile['glyphs'].append(data)

    # Get the generated json
    def get_fontimg_json(self) -> dict:
        return self.__jsonfile
    
    # Update 04-03: Update font information in CSV (for GMS game, e.g. TS!Underswap)
    def update_fontimg_csv(self, currentchar : str, endpoint: tuple) -> None:
        (width, height) = endpoint

        # Build data
        data = [
            ord(currentchar),   # Character encoding
            self.__x - width, self.__y,  # Top-left corner of the glyph
            width, height,      # Width, height
            width, 0            # Letter spacing, offset, previously adjusted, keep default
        ]

        # Data built, add record
        self.__csv.append(data)

   # Update 04-03: Write the generated CSV to file
    def write_fontimg_csv(self, distpath : str) -> None:
        with open(distpath, "w", encoding="UTF-8", newline='') as file:
            writerobj = csv.writer(file)
            writerobj.writerows(self.__csv)
    
    # Glyph creation and import task
    def glyph_genetask(self) -> None:
        # After initialization: Read basic information for each font record in glyph_info
        it = 0
        for cfg in self.__fontconfig:
            # For each character in the font library: Continuously send to the drawing program
            # First, instantiate the font
            self.__font = ImageFont.truetype(cfg['fontfile'], cfg['size'])
            # Update 04-03: Attempt to use the fallback font path when characters are missing
            if os.path.exists(self.__fbfontpath):
                self.__fbfont = ImageFont.truetype(self.__fbfontpath, cfg['size'])  
            else:
                print("WARNING: fallback font not found.")
                self.__fbfont = None

            with open(cfg['charset'], "r", encoding="UTF-8") as file:
                # Get the number of characters in the character set
                # limit = len(file.read())
                # file.seek(0, 0)
                limit = self.__charcount[it]

                for _ in range(limit):
                    ch = file.read(1)
                    if ch == '\n':   # Skip newline characters
                        continue
                    # First, draw the single character glyph
                    fontimg, endpoint = self.draw_singlefont(ch, cfg)
                    # Update 04-03: If an empty glyph is found, the current font lacks the corresponding character
                    if not fontimg:
                        # In this case, try to use the fallback font
                        if self.__fbfont:
                            # If the fallback font is available, redraw using the fallback font
                            fontimg, endpoint = self.draw_singlefont(ch, cfg, fallback=True)
                        else:   # Otherwise, skip this font
                            continue
                    # Next, add the single character to the main large glyph
                    self.add_fontimg(fontimg, endpoint)
                    # Then, update the JSON file or CSV file
                    self.update_fontimg_json(ch, endpoint)
                    self.update_fontimg_csv(ch, endpoint)
                it += 1     # Iteration index

            # Correction 03-30: After completing a font configuration, prepare for the next font set import by moving to the next line
            self.__x = 0
            self.__y += cfg['height']

    # Optimization 04-03: Save the generated glyph
    def save_glyph(self, distpath : str) -> None:
        self.glyph.save(distpath)

# Execute the main program
def main():
    # Configuration file paths
    csv_path = "font_info/basicinfo.csv"
    json_path = "font_info/glyphinfo.json"

    # Output path
    if os.path.exists("dist"):
        os.system('powershell "rm -r dist"')
    os.mkdir("dist")

    # Font names
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

    # Generate glyphs and configuration files
    for name in fontnamelist:
        glyph = FontGlyph(name, json_path, csv_path,
                          fallbackfont="fnt_zh-cn/unifont.otf", width=1024)    # Initialize glyph object
        glyph.glyph_genetask()  # Generate glyph

        glyph.save_glyph(f"dist/{name}.png")          # Save glyph
        distjson.append(glyph.get_fontimg_json())     # Write JSON
        #glyph.write_fontimg_csv(f"dist/glyphs_fnt_{name}.csv")  # Write csv
    
    # Save JSON file
    with open(f"dist/index.json", "w", encoding="UTF-8") as json_file:
        json.dump(distjson, json_file, 
                  ensure_ascii=False, indent=4, separators=(", ", ": "))
    
    print("OK.")

if __name__ == '__main__':
    main()

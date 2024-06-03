import json

def load_json_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_character_set(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        characters = file.read().replace('\n', '').strip()
    return list(characters)

def update_characters(json_data, char_set, font_list, size_list):
    for font, size in zip(font_list, size_list):
        json_data["fonts"][font]["characters"]["widths"] = []
        for char in char_set:
            json_data["fonts"][font]["characters"]["widths"].extend([char, size])
    return json_data

def save_updated_json(json_data, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

def main():
    json_template_path = 'source.json'
    char_set_path = 'char_cn.txt'
    output_file_path = 'zh_Hans.json'
    
    font_list = [
            "fnt_dotumche",
            "fnt_dotumche_lg",
            "fnt_dotumche_sm",
            "fnt_dotumche_md",
            "fnt_dotumche_mdlg",
            "fnt_main",
            "fnt_mainsm",
            "fnt_papyrus",
            "fnt_sans",
            "fnt_crypt",
            "fnt_mars"
    ]
    size_list = [6, 18, 4, 9, 14, 12, 12, 12, 16, 18, 11]  # Adjust sizes as needed for each font

    json_data = load_json_template(json_template_path)
    char_set = load_character_set(char_set_path)
    
    updated_json = update_characters(json_data, char_set, font_list, size_list)
    
    save_updated_json(updated_json, output_file_path)
    print(f"Updated JSON saved to {output_file_path}")

if __name__ == "__main__":
    main()

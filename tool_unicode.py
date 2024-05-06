# Unicode Tool - Quickly look up Unicode values of characters, useful for locating and filling in missing characters
# This program is a pre-refactor utility with extensive interactive logic.

# Unicode to character lookup
def unicode_lookup():
    while True:
        code = input("Enter a decimal or hexadecimal code (start with 0x for hex, enter 'q' to return to the main menu): ")
        if code.lower() == 'q':
            break
        try:
            if code.startswith("0x"):
                code = int(code, 16)
            else:
                code = int(code)
            print("The corresponding character is:", chr(code))
        except ValueError:
            print("Invalid encoding entered.")

# Character to Unicode lookup
def char_encoding_lookup():
    while True:
        chars = input("Enter characters (you can enter multiple characters, enter 'quit' to return to the main menu): ")
        if chars.lower() == 'quit':
            break
        for char in chars:
            print(f"'{char}': Decimal={ord(char)}, Hexadecimal={hex(ord(char))}")

# Output all characters within a Unicode range to a file
def output_unicode_range():
    filename = "char_cn.txt"    # Set the output file name

    # Interaction
    print(f"If {filename} already exists, new content will be appended to the end of the file.")
    start = input("Enter the start code of the range (hexadecimal): ")
    end = input("Enter the end code of the range (hexadecimal): ")

    # Write to file
    try:
        start = int(start, 16)
        end = int(end, 16)
        with open(filename, "a", encoding="utf-8") as file:
            for code in range(start, end + 1):
                file.write(chr(code))
        print(f"Output to {filename}.")
    except ValueError:
        print("Invalid encoding entered.")

def main_menu():
    while True:
        print("\nMenu options:")
        print("1. Unicode lookup")
        print("2. Input characters to lookup encoding")
        print("3. Output all characters in a specified Unicode range to a file")
        print("4. Exit")
        choice = input("Please enter your choice (1/2/3/4): ")
        if choice == "1":
            unicode_lookup()
        elif choice == "2":
            char_encoding_lookup()
        elif choice == "3":
            output_unicode_range()
        elif choice == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid option, please re-enter.")

if __name__ == "__main__":
    main_menu()

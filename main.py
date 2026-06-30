from tools import SubWordTokenizer

tokenizer = SubWordTokenizer()
text_source = "text_source/example.txt"

# Build a vocab from fox story
with open(text_source, "r", encoding="utf-8") as f:
    txt = f.read()
    tokenizer(txt)


running = True
while running:
    option = input("\nEncode(1) or Decode(2) (press E to Exit): ")

    if option.lower() == "e":
        running = False
        print("Exiting.")

    if option == '1':
        text = input("\nEnter a phrase to encode (press M to return to Menu): ")

        if text is not None:
            if text.lower() == "m":
                print("Returning.")
                continue
            else:
                encoded = tokenizer(text)
                print(encoded)
        continue

    elif option == '2':
        text = input("\nEnter a phrase to decode (press M to return to Menu): ")

        if text is not None:
            if text.lower() == "m":
                print("Returning.")
                continue
            else:
                decoded = tokenizer.decode(text)
                print(decoded)
        continue
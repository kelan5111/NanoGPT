from torch import nn
from tools import SubWordTokenizer

text_source = "text_source/example.txt"

tokenizer = SubWordTokenizer()

with open(text_source, "r", encoding="utf-8") as f:
    txt = f.read()
    print(tokenizer(txt))

print(tokenizer.vocab_size)

x_train = txt[:]
y_train = txt[1:]


# Embedding
vocab_size = tokenizer.vocab_size
embed_layer = nn.Embedding(vocab_size, embedding_dim=128)
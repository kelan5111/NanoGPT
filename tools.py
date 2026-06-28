from collections import Counter
import re


class SubWordTokenizer:
    def __init__(self, vocab=None, max_size=20000):
        if vocab is not None:
            self.vocab = vocab
        else:
            self.vocab = {0: "Ġ"}

        self.merge_rules = []
        self.vocab_size = len(self.vocab.keys())
        self.max_size = max_size

    def __call__(self, sequence, merge_limit=500):
        tokens = self._split_and_standardize(sequence)
        self.build_vocab(tokens, merge_limit)
        encoded_seq = self.encode(tokens)
        return encoded_seq

    def encode(self, tokens):
        encoded_seq = []

        for token in tokens:
            possible_rules = []
            for merge_rule in self.merge_rules:
                merged_token = self._apply_merge_rule_token(token, merge_rule)

                if merged_token != token:
                    possible_rules.append(merge_rule)
                    token = merged_token

            token_ids = self._to_token_id(token)

            for token_id in token_ids:
                encoded_seq.append(token_id)

            possible_rules.clear()

        return encoded_seq

    def decode(self, encoded_seq):
        decoded_seq = ""
        space_token = "Ġ"
        for tokenid in encoded_seq:
            token = [tok for tok, tid in self.vocab.items() if tid == tokenid][0]
            token = str(token).replace(space_token, " ")
            decoded_seq += token

        return decoded_seq

    def _to_token_id(self, token):
        return [self._index(sub_group) for sub_group in token]

    def _index(self, token):
        assert token in self.vocab.keys(), "Token does not exist in vocabulary."
        return self.vocab.get(token)

    def build_vocab(self, tokens, merge_limit):
        curr_merge = 0

        while curr_merge < merge_limit and self.vocab_size < self.max_size:

            most_common_pair = self._get_most_common_pair(tokens)
            if most_common_pair is None:
                break

            self._add_merge_rule(most_common_pair)

            tokens = self._apply_merge_rule_tokens(tokens, most_common_pair)

            curr_merge += 1

    def add_to_vocab(self, token):
        curr_index = len(self.vocab)
        if token not in self.vocab.keys():
            self.vocab[token] = curr_index
            print(f"'{token}' added to vocab.")

    def _apply_merge_rule_tokens(self, tokens, most_common_pair):
        new_tokens = []

        for token_index in range(len(tokens) - 1):
            new_token = []
            char_index = 0
            curr_token = tokens[token_index]

            while char_index < len(curr_token):
                curr_char = curr_token[char_index]

                if char_index == len(curr_token) - 1:
                    new_token.append(curr_char)
                    char_index += 1
                else:
                    pair = curr_char, curr_token[char_index + 1]
                    if pair == most_common_pair:
                        merged_pair = "".join(pair)
                        self.add_to_vocab(merged_pair)
                        new_token.append(merged_pair)
                        char_index += 2
                    else:
                        char_index += 1
                        new_token.append(curr_char)

            new_tokens.append(new_token)

        return new_tokens

    @staticmethod
    def _apply_merge_rule_token(token, merge_rule):
        new_token = []
        char_index = 0

        while char_index < len(token):
            # If we're at the last element, just copy it
            if char_index == len(token) - 1:
                new_token.append(token[char_index])
                char_index += 1
            else:
                pair = (token[char_index], token[char_index + 1])

                if pair == merge_rule:
                    merged_pair = "".join(pair)
                    new_token.append(merged_pair)
                    char_index += 2
                else:
                    new_token.append(token[char_index])
                    char_index += 1

        return new_token

    def _add_merge_rule(self, merge_pair):
        if merge_pair not in self.merge_rules:
            self.merge_rules.append(merge_pair)
            print(f"Added new merge rule: {merge_pair}")

    @staticmethod
    def _get_most_common_pair(tokens):
        min_freq = 1

        common_words = Counter()
        for token in tokens:
            for i in range(len(token) - 1):
                pair = token[i], token[i + 1]
                common_words[pair] += 1

        most_common_pair = common_words.most_common()
        if not most_common_pair:
            return None

        freq = most_common_pair[0][1]
        if freq <= min_freq:
            return None

        return most_common_pair[0][0]

    def _split_and_standardize(self, sequence):
        tokens = []

        sequence = self._apply_special_tokens(sequence)

        for word in sequence.split():
            token = re.findall(r'\S', word)
            for char in token:
                self.add_to_vocab(char)
            tokens.append(token)
        return tokens

    @staticmethod
    def _apply_special_tokens(sequence):
        space_token = "Ġ"

        new_sequence = ""
        index = 0
        while index < len(sequence):
            char = sequence[index]
            if char == ' ':
                next_char = sequence[index + 1]
                merged = space_token + next_char
                new_sequence += ' ' + merged
                index += 2
            else:
                new_sequence += char
                index += 1

        return new_sequence


swt = SubWordTokenizer()
sequence = ("the cat sat on the mat. the dog sat on the mat. the cat chased the mouse."
            " the mouse ran quickly under the wooden table. the dog barked loudly at the cat. "
            "the cat and the dog slowly became friends. the friends played together in the garden every day. "
            "the garden was large and full of colorful flowers. the flowers were red, blue, yellow, and purple. "
            "the sun was shining brightly and the weather was warm and pleasant. suddenly the weather changed "
            "and heavy rain started falling. the cat ran quickly inside the house. the dog followed the cat into "
            "the house because it was scared of the rain. inside the house it was warm, dry, and quiet. the cat "
            "slept peacefully on the soft sofa. the dog slept on the wooden floor near the door. they both dreamed "
            "of chasing the small mouse again in the garden. sometimes they woke up and looked outside at the rainy "
            "weather. other times they stayed asleep and dreamed of sunny days. the garden became green again after "
            "the rain stopped. flowers started growing again and bees came to visit them. the cat watched the bees "
            "while sitting on the window. the dog watched the cat and wagged its tail slowly. the mouse returned when "
            "the house became quiet again. it ran across the floor and under the table very quickly. the cat noticed it "
            "immediately and started chasing it again. the dog watched but did not move. the weather outside became stormy "
            "and loud thunder filled the sky. rain hit the windows and the wind shook the trees. inside, the cat and dog "
            "stayed warm and safe. after the storm passed, the sun returned and everything became bright again. "
            "the garden looked fresh and new with water on the leaves. birds flew back into the trees and started "
            "singing again. the cat and dog went outside and explored the garden together. they moved slowly through "
            "the grass and watched insects moving around. the mouse hid again but no one chased it this time. everything "
            "felt calm, peaceful, and quiet in the garden.")

encoded = swt(sequence)
print(f"Original tokens: {len(sequence)}\nEncoded tokens: {len(encoded)}")

print(len(swt.vocab))

sequence2 = ("The quick brown fox jumped over the old wooden fence just before sunrise. "
             "A cool breeze moved through the trees while birds sang from every branch. "
             "Emma walked along the narrow path carrying a small backpack filled with notebooks, pencils, "
             "and a bottle of water. She had planned this trip for weeks because she wanted a quiet place "
             "where she could think, write, and read without interruptions. Every few minutes she stopped "
             "to observe the wildlife around her. A squirrel climbed a nearby oak tree, a rabbit disappeared "
             "into the bushes, and a butterfly landed briefly on a bright yellow flower before flying away. "
             "As the morning became warmer, the forest grew busier. Hikers greeted one another with friendly"
             " smiles, children laughed as they explored the trails, and a family stopped beside a stream to"
             " eat breakfast together. The sound of flowing water mixed with the rustling leaves, creating a"
             " peaceful atmosphere. Emma sat on a large flat rock, opened her notebook, and began writing"
             " about everything she had seen during the walk. She described the colours of the flowers, the"
             " changing light beneath the trees, and the feeling of calm that surrounded her. Later that "
             "afternoon dark clouds gathered in the distance, and a gentle rain began to fall. Instead of "
             "rushing home, Emma found shelter beneath a wooden picnic shelter and continued reading her "
             "favourite novel. The rain lasted only twenty minutes before the sun returned, leaving tiny "
             "drops of water sparkling on every leaf and blade of grass. As she packed her belongings, "
             "she realised the day had been exactly what she needed. It reminded her that even a short journey"
             " into nature could provide inspiration, reduce stress, and create lasting memories. Before leaving"
             " the forest, she took one final look at the winding path and promised herself that she would return"
             " again before the end of summer.")

encoded2 = swt(sequence2)
decoded2 = swt.decode(encoded2)

for i in range(len(encoded2)):
    print(encoded2[i:i + 10])

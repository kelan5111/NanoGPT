from collections import Counter
import re


class SubWordTokenizer:
    def __init__(self, vocab=None, max_size=20000):
        if vocab is not None:
            self.vocab = vocab
        else:
            self.vocab = {0: "Ġ"}

        self.merge_rules = []
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

    @property
    def vocab_size(self):
        return len(self.vocab.values())
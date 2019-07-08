import re


# Insert space between the alphabet-only word
def insert_space_to_ascii(word):
    # Removed some characters from string.punctuation
    if re.match(r"^[A-Za-z0-9!#$%&\()*+,-./:;=?@^_|~]+$", word):
        word += ' '

    return word


# Apply function above to list of words
def combine_sentence(sentence):
    return ''.join(list(map(insert_space_to_ascii, sentence)))

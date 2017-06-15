import json
import tensorflow as tf
import string
from gensim.models.keyedvectors import KeyedVectors
from os import listdir

word_vec = KeyedVectors.load_word2vec_format('./embeddings.bin.gz', binary=True)

# print(word_vec['react'])
# print(word_vec['javascript'])
# print(word_vec['node'])
# print(word_vec['aws'])
# print(word_vec['vue'])

unknown = []
input = []
for filename in listdir("./_popular/"):
    with open("./_popular/" + filename, encoding='utf-8') as data:
        resource = json.load(data)
        resource['title'] = resource['title'].translate(str.maketrans('', '', string.punctuation)).split()
        
        vec_title = []
        for word in resource['title']:
            try:
                vec = word_vec[word]
                vec_title.append(vec)
            except KeyError:
                processed = process_unknown(word)
                if len(processed):
                    vec_title += processed
                else:
                    unknown.append(word)
                continue
        resource['title'] = vec_title

    input.append(resource)

with open("./unknown.json", "w") as ufile:
    json.dump(unknown, ufile)
    ufile.close()


def process_unknown(word):
    words = []
    last_pos = 0
    i = len(word)
    while i > 0 and last_pos != i:
        try:
            current = word[last_pos:i]
            vec = word_vec[current]
            words.append(vec)
            last_pos = i
            i = len(word)
        except KeyError:
            i -= 1
            continue
    
    return words

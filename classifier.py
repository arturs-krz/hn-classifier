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
                # try to process
                continue
        resource['title'] = vec_title

    input.append(resource)

print(input)
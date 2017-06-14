import json
import tensorflow as tf
from gensim.models.keyedvectors import KeyedVectors
from os import listdir

# word_vec = KeyedVectors.load_word2vec_format('./embeddings.bin.gz', binary=True)

# print(word_vec['react'])
# print(word_vec['javascript'])
# print(word_vec['node'])
# print(word_vec['aws'])
# print(word_vec['vue'])

for filename in listdir("./_popular/"):
    with open("./_popular/" + filename) as data:
        resource = json.load(data)
    
    print(resource)
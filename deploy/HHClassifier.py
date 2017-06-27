import tensorflow as tf
import numpy as np
import string
import json
import re
from gensim.models.keyedvectors import KeyedVectors
from flask import Flask, request

word_vec = KeyedVectors.load_word2vec_format('../embeddings.bin.gz', binary=True)

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


def pad_to_size(input, size):
    current_len = len(input)

    if size >= current_len:
        diff = size - current_len
        input += [np.zeros(300) for i in range(diff)]
    else:
        input = input[:size]
    return input

with open("../classifier_data.json", encoding='utf-8') as data:
    classifier = json.load(data)
    classes = classifier['tags']
    num_classes = len(classes)
    max_size = classifier['max_size']

def clean(seq):
    seq = seq.replace("Show HN:", "")
    # seq = " ".join(filter(lambda w: not w in common, seq.split()))
    seq = re.sub('[^\x00-\xFF]', '', seq)
    seq = re.sub('(?:\r\n|\r|\n)', '', seq)
    seq = re.sub('(?:\\[rn])+', '', seq)
    seq = re.sub('\t', '', seq)
    seq = re.sub(' +(?= )', '', seq)
    return seq.lower().strip()
    

def vectorize_title(title):
    title = title.translate(str.maketrans('', '', string.punctuation)).split()
        
    vec_title = []
    for word in title:
        try:
            vec = word_vec[word]
            vec_title.append(vec)
        except KeyError:
            processed = process_unknown(word)
            if len(processed):
                vec_title += processed
            continue    
    return vec_title

def get_top_tags(prediction):
    last = prediction[0].argsort()[-3:][::-1]
    last = last.tolist()
    return [{"tag": classes[i], "probability": prediction[0][i]} for i in last]

with tf.Session() as sess:
    saver = tf.train.import_meta_graph('../model.ckpt.meta')
    saver.restore(sess, '../model.ckpt')

    graph = tf.get_default_graph()
    data = graph.get_tensor_by_name('input_data:0')
    prediction = graph.get_tensor_by_name('prediction:0')
    

    api = Flask(__name__)
    

    @api.route('/classify')
    def classify():
        req = request.json
        print(req)
        return 'bump'
        # title = request.data['title']
        # print(title)
        # title = clean(title)
        # vec_title = pad_to_size(vectorize_title(title), max_size)
        # feed_dict = {data: [vec_title]}
        # return json.dumps(get_top_tags(prediction.eval(session=sess, feed_dict=feed_dict)))

    @api.route('/')
    def main():
        return 'hai'

    if __name__ == '__main__':
        api.run(host='0.0.0.0', port='5000')
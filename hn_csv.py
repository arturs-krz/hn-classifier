import tensorflow as tf
import numpy as np
import string
import json
import re
import csv
from gensim.models.keyedvectors import KeyedVectors

word_vec = KeyedVectors.load_word2vec_format('./embeddings.bin.gz', binary=True)

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

with open("./classifier_data.json", encoding='utf-8') as data:
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

def get_top_tags(predictions):
    results = []
    for prediction in predictions:
        last = prediction.argsort()[-3:][::-1]
        last = last.tolist()
        results.append({"predictions": [{"tag": classes[i], "probability": float(prediction[i])} for i in last]})
    return results

with tf.Session() as sess:
    saver = tf.train.import_meta_graph('./model.ckpt.meta')
    saver.restore(sess, './model.ckpt')

    graph = tf.get_default_graph()
    data = graph.get_tensor_by_name('input_data:0')
    prediction = graph.get_tensor_by_name('prediction:0')
    

    titles = []
    feed_dict = {data: []}
    with open('show_hn.csv', 'r') as hncsv:
        rows = csv.reader(hncsv, delimiter=';')
        for row in rows:
            title = row[4]
            titles.append(title)
            title = clean(title)
            vec_title = pad_to_size(vectorize_title(title), max_size)
            feed_dict[data].append(vec_title)
        hncsv.close()
    predictions = get_top_tags(prediction.eval(session=sess, feed_dict=feed_dict))
    for i, title in enumerate(titles):
        predictions[i]["title"] = title
    
    with open("./csv_results.json", "w") as cfile:
        json.dump(predictions, cfile)
        cfile.close()
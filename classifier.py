import json
import tensorflow as tf
import string
import re
import numpy as np
import random
from gensim.models.keyedvectors import KeyedVectors
from os import listdir
from nltk.corpus import stopwords

word_vec = KeyedVectors.load_word2vec_format('./embeddings.bin.gz', binary=True)
common = set(stopwords.words('english'))

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
    diff = size - current_len
    input += [np.zeros(300) for i in range(diff)]
    return input

# prepare class vector format 
with open("./custom_aliases.json", encoding='utf-8') as data:
    alias_dict = json.load(data)
    aliases = list(map(lambda entry: entry["tag"], alias_dict))
    num_classes = len(aliases)

def create_class_vec(tags):
    num_tags = len(tags)
    hot_val = 1.0 / num_tags
    vec = [hot_val if a in tags else 0.0 for a in aliases]
    return vec

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
            else:
                unknown.append(word)
            continue    
    return vec_title

def get_top_tags(prediction):
    last = prediction[0].argsort()[-3:][::-1]
    last = last.tolist()
    return [(aliases[i], prediction[0][i]) for i in last]


max_size = 0
unknown = []
resources = []
for filename in listdir("./_popular/"):
    with open("./_popular/" + filename, encoding='utf-8') as data:
        resource = json.load(data)
        vec_title = vectorize_title(resource['title'])

        resource['title'] = vec_title
        title_len = len(vec_title)
        if title_len > max_size:
            max_size = title_len

    resources.append(resource)

# with open("./unknown.json", "w") as ufile:
#     json.dump(unknown, ufile)
#     ufile.close()

# with open("./vectorized.txt", "w") as vfile:
#     np.savetxt(vfile, input)
#     vfile.close()


max_size += 15
num_hidden = 400

classifier_data = {"max_size": max_size, "tags": aliases}
with open('./classifier_data.json', "w") as dfile:
    json.dump(classifier_data, dfile)
    dfile.close()

print("Maximum title size: {}".format(max_size))
print("Total {} training samples...".format(len(resources)))
input_data = list(map(lambda res: pad_to_size(res['title'], max_size), resources))
labels = map(lambda res: res['tags'], resources)
labels = list(map(lambda tags: create_class_vec(tags), labels))

data = tf.placeholder(tf.float32, [None, max_size, 300], name="input_data")
target = tf.placeholder(tf.float32, [None, num_classes])

lstm_cell = tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True)
val, state = tf.nn.dynamic_rnn(lstm_cell, data, dtype=tf.float32)

# [max_size, batch, 300]
val = tf.transpose(val, [1, 0, 2])
last = tf.gather(val, int(val.get_shape()[0]) - 1)

weight = tf.Variable(tf.truncated_normal([num_hidden, num_classes]))
bias = tf.Variable(tf.constant(0.1, shape=[num_classes]))

prediction = tf.nn.softmax(tf.matmul(last, weight) + bias, name="prediction")
cross_entropy = -tf.reduce_sum(target * tf.log(tf.clip_by_value(prediction, 1e-10, 1.0)))

optimizer = tf.train.AdamOptimizer(learning_rate=0.005)
train_step = optimizer.minimize(cross_entropy)

init = tf.global_variables_initializer()
sess = tf.Session()

saver = tf.train.Saver()
sess.run(init)

# saver.restore(sess, "./model.ckpt")

batch_size = 100
batch_count = int(len(input_data) / batch_size)
epochs = 500
for e in range(epochs):
    
    indices = list(range(len(input_data)))
    random.shuffle(indices)
    shuffled_inp = [input_data[i] for i in indices]
    shuffled_labels = [labels[i] for i in indices]

    ptr = 0
    entropy_val = 0

    for i in range(batch_count):
        inp = shuffled_inp[ptr:ptr+batch_size]
        out = shuffled_labels[ptr:ptr+batch_size]
        ptr += batch_size
        train_step.run(session=sess,feed_dict={data: inp, target: out})

        entropy_val += sess.run([cross_entropy], feed_dict={data: inp, target: out})[0]
    
    print("Epoch {}, avg entropy: {}".format(e, entropy_val/(batch_count * batch_size)))

saver.save(sess, "./model.ckpt")

# tests = [
#     "dosycrypt homemade symmetric stream cipher with tunable parameters",
#     "blur photo background in ten seconds",
#     "basic manga reader powered by vue js",
#     "free search engine for everybody",
#     "argskwargs, flexible python lib for positional and keyword arguments",
#     "strukt visual shell for tabular data"
# ]

for filename in listdir("./_untagged/"):
    with open("./_untagged/" + filename, encoding='utf-8') as untagged:
        resource = json.load(untagged)
        title = clean(resource['title'])
        vec_title = pad_to_size(vectorize_title(title), max_size)
        feed_dict = {data: [vec_title]}
        print("{} => {}".format(resource['title'].encode('utf-8'), get_top_tags(prediction.eval(session=sess, feed_dict=feed_dict))))

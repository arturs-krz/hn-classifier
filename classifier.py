import json
import tensorflow as tf
import string
import numpy as np
from gensim.models.keyedvectors import KeyedVectors
from os import listdir

word_vec = KeyedVectors.load_word2vec_format('./embeddings.bin.gz', binary=True)

# print(word_vec['react'])
# print(word_vec['javascript'])
# print(word_vec['node'])
# print(word_vec['aws'])
# print(word_vec['vue'])

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
with open("./aliases.json", encoding='utf-8') as data:
    alias_dict = json.load(data)
    aliases = list(map(lambda entry: entry["tag"], alias_dict))
    num_classes = len(aliases)

def create_class_vec(tags):
    num_tags = len(tags)
    hot_val = 1.0 / num_tags
    vec = [hot_val if a in tags else 0.0 for a in aliases]
    return vec


max_size = 0
unknown = []
resources = []
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

input_data = list(map(lambda res: pad_to_size(res['title'], max_size), resources))
labels = map(lambda res: res['tags'], resources)
labels = list(map(lambda tags: create_class_vec(tags), labels))


data = tf.placeholder(tf.float32, [None, max_size, 300])
target = tf.placeholder(tf.float32, [None, num_classes])

lstm_cell = tf.contrib.rnn.LSTMCell(200, state_is_tuple=True)
val, state = tf.nn.dynamic_rnn(lstm_cell, data, dtype=tf.float32)

# [max_size, batch, 300]
val = tf.transpose(val, [1, 0, 2])
last = tf.gather(val, int(val.get_shape()[0]) - 1)

weight = tf.Variable(tf.truncated_normal([200, num_classes]))
bias = tf.Variable(tf.constant(0.1, shape=[num_classes]))

prediction = tf.nn.softmax(tf.matmul(last, weight) + bias)
cross_entropy = -tf.reduce_sum(target * tf.log(tf.clip_by_value(prediction, 1e-10, 1.0)))

optimizer = tf.train.AdamOptimizer()
train_step = optimizer.minimize(cross_entropy)

init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

batch_size = 100
batch_count = int(len(input_data) / batch_size)
epochs = 500
for e in range(epochs):
    ptr = 0
    entropy_val = 0
    for i in range(batch_count):
        inp = input_data[ptr:ptr+batch_size]
        out = labels[ptr:ptr+batch_size]
        ptr += batch_size
        train_step.run(sess=sess,feed_dict={data: inp, target: out})
        entropy_val += sess.run([cross_entropy], feed_dict={data: inp, target: out})
    
    print("Epoch {}, avg entropy: {}".format(e, entropy_val/batch_count))
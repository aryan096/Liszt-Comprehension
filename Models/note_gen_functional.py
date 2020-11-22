import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
from keras.layers import Dense, Dropout, GRU, Activation, Bidirectional, Flatten
from Transformers.Attention import MultiHeadAttention
from keras_self_attention import SeqSelfAttention
# from preprocess ...

def create_network(note_vocab_size, is_training=False):
    embedding_size = 30

    model = tf.keras.Sequential()

    model.add(tf.keras.layers.Embedding(note_vocab_size, embedding_size))

    model.add(Bidirectional(GRU(100, return_sequences=True)))
    model.add(SeqSelfAttention(attention_activation='sigmoid'))
    if is_training:
        model.add(Dropout(0.3))

    model.add(Bidirectional(GRU(100, return_sequences=True)))
    model.add(Dense(int(note_vocab_size/2)))
    model.add(tf.keras.layers.LeakyReLU(0.2))
    if is_training:
        model.add(Dropout(0.3))

    model.add(Flatten())  # Supposedly needed to fix stuff before dense layer
    model.add(Dense(note_vocab_size, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')

def train(model, input_data, labels):
    model.fit(input_data, labels, epochs=20, batch_size=250)








import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
from keras.layers import Dense, Dropout, GRU, Activation, Bidirectional, Flatten
from keras_multi_head import MultiHeadAttention
from .transformer_funcs import Multi_Headed
# from preprocess ...


def create_note_gen_network(note_vocab_size):
    embedding_size = 30

    model = tf.keras.Sequential()

    model.add(tf.keras.layers.Embedding(note_vocab_size, embedding_size))

    model.add(Bidirectional(GRU(100, return_sequences=True)))
    model.add(MultiHeadAttention(head_num=4))
    #Let's hope this works!
    #model.add(Multi_Headed(embedding_size,embedding_size,False,4))
    model.add(Dropout(0.3))

    model.add(Bidirectional(GRU(100, return_sequences=True)))
    model.add(Dense(int(note_vocab_size/2)))
    model.add(tf.keras.layers.LeakyReLU(0.2))
    model.add(Dropout(0.3))

    model.add(Dense(note_vocab_size, activation='softmax'))

    def perplexity(labels, probabilities):
        loss = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(labels, probabilities))
        return tf.exp(loss)

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=[perplexity])

    return model


def train_note_gen(model, input_data, labels, num_epocs):
    model.fit(input_data, labels, epochs=num_epocs, batch_size=250)


def test_note_gen(model, input_data, labels):
    model.evaluate(input_data, labels, batch_size=250)

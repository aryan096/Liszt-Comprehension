import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
from keras.layers import Dense, Dropout, GRU, Activation, Bidirectional, Flatten
from keras_multi_head import MultiHeadAttention
from Transformers.Transformer import *

def create_duration_gen_network(note_vocab_size, duration_vocab_size):
    embedding_size = 30


    model = tf.keras.Model()
    model.add(Transformer(1, 50, 4, 100, note_vocab_size, duration_vocab_size, 0.3))

    model.add(Dense(duration_vocab_size, activation='softmax'))


import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
# from preprocess ...

class NoteGen(Model):
    def __init__(self):
        '''initialize hyperparams, layers, optimizers'''
        pass

    def call(self, inputs):
        '''
        use LSTM and Attention along with dense layers after.
        :param inputs: string ids of shape (batch_size, piece_length)
        :return: logits (batch_size, piece_length, vocab_size)
        '''

        pass

    def loss(self, logits, labels):
        '''

        :param logits: (batch_size, piece_length, vocab_size)
        :param labels: (batch_size, piece_length)
        :return: reduce mean of sparse_categorical_loss
        '''

        pass

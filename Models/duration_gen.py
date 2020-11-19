import tensorflow as tf
import numpy as np
from tensorflow.keras import Model


# from preprocess ...

class DurationGen(Model):
    def __init__(self):
        '''initialize hyperparams, layers, optimizers'''
        pass

    def call(self, encoder_inputs, decoder_input):
        '''
        use Attention encoders and Attention decoders along with dense layers after.

        :param encoder_inputs: batched IDs corresponding to notes
        :param decoder_input: batched IDs corresponding to durations
        :return: The 3d probabilities as a tensor, [batch_size x piece_length x duration_vocab_size]
        '''

        pass

    def loss(self, prbs, labels, mask):
        '''

        :param prbs: (batch_size, piece_length, duration_vocab_size)
        :param labels: (batch_size, piece_length)
        :param mask: padding mask [batch_size x piece_length]
        :return: reduce mean of sparse_categorical_loss
        '''

        return tf.reduce_sum(tf.boolean_mask(tf.keras.losses.sparse_categorical_crossentropy(labels, prbs), mask))

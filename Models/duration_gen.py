import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
import transformer_funcs as transformer


# from preprocess ...
# TODO - re-implement transformers using Keras tutorial online

class DurationGen(Model):
    def __init__(self, note_vocab_size, duration_vocab_size, piece_length):
        '''initialize hyperparams, layers, optimizers'''
        # TODO - this might all change after re-implementing transformers

        super(DurationGen, self).__init__()

        self.piece_length = piece_length
        self.note_vocab_size = note_vocab_size
        self.duration_vocab_size = duration_vocab_size

        self.batch_size = 100 # TODO - change as required, increase if GPU
        self.embedding_size = 30 # TODO - change as required
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        self.note_embedding = tf.keras.layers.Embedding(self.note_vocab_size, self.embedding_size)
        self.duration_embedding = tf.keras.layers.Embedding(self.duration_vocab_size, self.embedding_size)

        self.note_position = transformer.Position_Encoding_Layer(self.piece_length, self.embedding_size)
        self.duration_position = transformer.Position_Encoding_Layer(self.piece_length, self.embedding_size)

        # TODO - add more encoders if necessary
        self.encoder1 = transformer.Transformer_Block(self.embedding_size, is_decoder=False, multi_headed=False)
        # TODO - add more decoders if necessary
        self.decoder1 = transformer.Transformer_Block(self.embedding_size, is_decoder=True, multi_headed=False)

        self.dense1 = tf.keras.layers.Dense(300, activation='relu') # TODO - change as required
        self.dense2 = tf.keras.layers.Dense(self.duration_vocab_size, activation='softmax') # TODO - change as required
        # TODO - add more dense layers if necessary
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

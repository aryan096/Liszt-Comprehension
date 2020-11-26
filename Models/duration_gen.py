import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
import Models.transformer_funcs as transformer


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

    def call(self, encoder_input, decoder_input):
        '''
        use Attention encoders and Attention decoders along with dense layers after.

        :param encoder_input: batched IDs corresponding to notes
        :param decoder_input: batched IDs corresponding to durations
        :return: The 3d probabilities as a tensor, [batch_size x piece_length x duration_vocab_size]
        '''
        # 1) Add the positional embeddings to french sentence embeddings
        notes_with_position = self.note_position(self.note_embedding(encoder_input))
        # 2) Pass the french sentence embeddings to the encoder
        encoder1_out = self.encoder1(notes_with_position)
        # 3) Add positional embeddings to the english sentence embeddings
        duration_with_position = self.duration_position(self.duration_embedding(decoder_input))
        # 4) Pass the english embeddings and output of your encoder, to the decoder
        decoder1_out = self.decoder1(duration_with_position, encoder1_out)
        # 5) Apply dense layer(s) to the decoder out to generate probabilities
        dense1_out = self.dense1(decoder1_out)
        dense2_out = self.dense2(dense1_out)

        return dense2_out

    def loss_function(self, prbs, labels):
        '''

        :param prbs: (batch_size, piece_length, duration_vocab_size)
        :param labels: (batch_size, piece_length)
        :param mask: padding mask [batch_size x piece_length]
        :return: reduce mean of sparse_categorical_loss
        '''

        return tf.reduce_sum(tf.keras.losses.sparse_categorical_crossentropy(labels, prbs))

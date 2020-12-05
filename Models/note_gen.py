import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
from Transformers.Attention import MultiHeadAttention
# from preprocess ...

# DEPRECATED?

class NoteGen(Model):
    def __init__(self, note_vocab_size, piece_length):
        '''initialize hyperparams, layers, optimizers'''
        super(NoteGen, self).__init__()

        self.note_vocab_size = note_vocab_size
        self.piece_length = piece_length # TODO - change as required
        self.embedding_size = 30 # TODO - change as required
        self.batch_size = 500 # TODO - change as required, increase if GPU
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001) # TODO - change as required


        self.note_embedding = tf.keras.layers.Embedding(self.note_vocab_size, self.embedding_size)
        self.gru1 = tf.keras.layers.GRU(self.piece_length, return_sequences=True, return_state=True)
        # TODO - add more GRUs if necessary

        self.attention1 = MultiHeadAttention(128, 8)
        # TODO - add more attention layers if necessary

        self.gru2 = tf.keras.layers.GRU(self.piece_length, return_sequences=True, return_state=True)

        self.dense1 = tf.keras.layers.Dense(int(self.note_vocab_size/2), activation= 'relu')
        self.dense2 = tf.keras.layers.Dense(self.note_vocab_size, activation='softmax')


    def call(self, inputs, initial_state=None):
        '''
        use LSTM and Attention along with dense layers after.
        :param inputs: string ids of shape (batch_size, piece_length)
        :return: probabilities (batch_size, piece_length, note_vocab_size)
        '''
        note_embeddings = self.note_embedding(inputs)
        gru1_out, final_state = self.gru1(note_embeddings, initial_state=initial_state)
        # TODO - add more GRUs if necessary


        dense1_out = self.dense1(gru1_out)
        dense2_out = self.dense2(dense1_out)
        # TODO - add dropout/leaky relu/more layers if necessary

        return dense2_out, final_state

    def loss(self, probs, labels):
        '''

        :param probs: (batch_size, piece_length, vocab_size)
        :param labels: (batch_size, piece_length)
        :return: reduce mean of sparse_categorical_loss
        '''

        return tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(labels, probs))

import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
from keras.layers import Dense, Dropout, GRU, Activation, Bidirectional, Flatten
from keras_multi_head import MultiHeadAttention
from Transformers.Transformer import *

class DurationGen2(Model):
    def __init__(self, note_vocab_size, duration_vocab_size, piece_length):
        '''initialize hyperparams, layers, optimizers'''
        # TODO - this might all change after re-implementing transformers

        super(DurationGen2, self).__init__()

        self.piece_length = piece_length
        self.note_vocab_size = note_vocab_size
        self.duration_vocab_size = duration_vocab_size

        self.batch_size = 100 # TODO - change as required, increase if GPU
        self.embedding_size = 30 # TODO - change as required
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        #self.note_embedding = tf.keras.layers.Embedding(self.note_vocab_size, self.embedding_size)
        #self.duration_embedding = tf.keras.layers.Embedding(self.duration_vocab_size, self.embedding_size)

        self.trans = Transformer(1, 100, 4, 100, self.note_vocab_size, self.duration_vocab_size, 0.3)
        self.soft = tf.keras.layers.Activation('softmax')

    def call(self, encoder_input, decoder_input):
        '''
        use Attention encoders and Attention decoders along with dense layers after.

        :param encoder_input: batched IDs corresponding to notes
        :param decoder_input: batched IDs corresponding to durations
        :return: The 3d probabilities as a tensor, [batch_size x piece_length x duration_vocab_size]
        '''
        # 1) Add the positional embeddings to french sentence embeddings
        #note_embeddings = self.note_embedding(encoder_input)
        #duration_embeddings = self.duration_embedding(decoder_input)
        out, _ = self.trans.call((encoder_input, decoder_input))
        out = self.soft(out)
        return out

    def loss_function(self, prbs, labels):
        '''

        :param prbs: (batch_size, piece_length, duration_vocab_size)
        :param labels: (batch_size, piece_length)
        :param mask: padding mask [batch_size x piece_length]
        :return: reduce mean of sparse_categorical_loss
        '''

        return tf.reduce_sum(tf.keras.losses.sparse_categorical_crossentropy(labels, prbs))


def duration2_train(model, train_notes, train_duration):
    """
    Runs through one epoch - all training examples.

    :param model: the initialized model to use for forward and backward pass
    :param train_notes: notes train data (all data for training) of shape (num_pieces, piece_length)
    :param train_duration: duration train data (all data for training) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :return: None
    """
    print("Begin Training")

    num_trained = 0
    while num_trained < len(train_notes):
        notes_batch = train_notes[num_trained: num_trained + model.batch_size]
        duration_batch = train_duration[num_trained: num_trained + model.batch_size]

        with tf.GradientTape() as tape:
            # remove last token from english sentences
            #decoder_input = tf.convert_to_tensor([lst[:-1] for lst in duration_batch])
            probabilities = model(notes_batch, duration_batch)
            # remove first token from batch to create labels
            #labels = tf.convert_to_tensor([lst[1:] for lst in duration_batch], dtype="int64")
            #mask = np.where(labels == duration_padding_index, 0, 1)
            loss = model.loss_function(probabilities, duration_batch)

        num_trained += model.batch_size
        if num_trained % (1 * model.batch_size) == 0:
            print("     Loss on training after {} batches = {}".format(num_trained / (model.batch_size), loss))

        gradients = tape.gradient(loss, model.trainable_variables)
        model.optimizer.apply_gradients(zip(gradients, model.trainable_variables))



def duration2_test(model, test_notes, test_duration):
    """
    Runs through one epoch - all testing examples.

    :param model: the initialized model to use for forward and backward pass
    :param test_note: note test data (all data for testing) of shape (num_pieces, piece_length)
    :param test_duration: duration test data (all data for testing) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :returns: a tuple containing at index 0 the perplexity of the test set and at index 1 the per symbol accuracy on test set,
    e.g. (my_perplexity, my_accuracy)
    """
    print("Begin Testing")

    total_words = 0
    total_loss = 0
    total_accuracy = 0
    num_tested = 0
    while num_tested < len(test_notes):
        notes_batch = test_notes[num_tested: num_tested + model.batch_size]
        duration_batch = test_duration[num_tested: num_tested + model.batch_size]

        #decoder_input = tf.convert_to_tensor([lst[:-1] for lst in duration_batch])
        probabilities = model(notes_batch, duration_batch)
        # remove first token from batch to create labels
        #labels = tf.convert_to_tensor([lst[1:] for lst in duration_batch], dtype="int64")
        #mask = np.where(labels == duration_padding_index, 0, 1)
        num_words_in_batch =  model.batch_size * model.piece_length #np.count_nonzero(mask == 1)
        total_words += num_words_in_batch

        batch_loss = model.loss_function(probabilities, duration_batch)
        total_loss += batch_loss
        batch_accuracy = num_words_in_batch * model.accuracy_function(probabilities, duration_batch)
        total_accuracy += batch_accuracy

        num_tested += model.batch_size
        if num_tested % (1 * model.batch_size) == 0:
            print("     Tested {} batches".format(num_tested / (model.batch_size)))

    return np.exp(total_loss / total_words), total_accuracy / total_words


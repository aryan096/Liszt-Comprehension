import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
import Models.transformer_funcs as transformer


class DurationGen(Model):
    def __init__(self, note_vocab_size, duration_vocab_size, piece_length):
        """initialize hyperparams, layers, optimizers"""

        super(DurationGen, self).__init__()

        self.piece_length = piece_length
        self.note_vocab_size = note_vocab_size
        self.duration_vocab_size = duration_vocab_size

        self.batch_size = 100 # TODO - change as required, increase if GPU
        self.embedding_size = 75 # TODO - change as required
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        self.note_embedding = tf.keras.layers.Embedding(self.note_vocab_size, self.embedding_size)
        self.duration_embedding = tf.keras.layers.Embedding(self.duration_vocab_size, self.embedding_size)

        self.note_position = transformer.Position_Encoding_Layer(self.piece_length, self.embedding_size)
        self.duration_position = transformer.Position_Encoding_Layer(self.piece_length, self.embedding_size)

        self.encoder1 = transformer.Transformer_Block(self.embedding_size, is_decoder=False, multi_headed=True)
        self.decoder1 = transformer.Transformer_Block(self.embedding_size, is_decoder=True, multi_headed=True)

        self.dense1 = tf.keras.layers.Dense(100, activation='relu') # TODO - change as required
        self.dense2 = tf.keras.layers.Dense(100, activation='relu') # TODO - change as required
        self.dense3 = tf.keras.layers.Dense(self.duration_vocab_size, activation='softmax') # TODO - change as required

    def call(self, encoder_input, decoder_input):
        """
        use Attention encoders and Attention decoders along with dense layers after.

        :param encoder_input: batched IDs corresponding to notes
        :param decoder_input: batched IDs corresponding to durations
        :return: The 3d probabilities as a tensor, [batch_size x piece_length x duration_vocab_size]
        """

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
        dense3_out = self.dense3(dense2_out)

        return dense3_out

    def loss_function(self, prbs, labels):
        return tf.reduce_sum(tf.keras.losses.sparse_categorical_crossentropy(labels, prbs))


def duration_train(model, train_notes, train_duration, epochs):
    """
    Runs through one epoch - all training examples.

    :param model: the initialized model to use for forward and backward pass
    :param train_notes: notes train data (all data for training) of shape (num_pieces, piece_length)
    :param train_duration: duration train data (all data for training) of shape (num_pieces, piece_length)
    :param epochs: how many epochs model should train for
    :return: None
    """
    print("Begin Training")
    for i in range(epochs):
        print("  epoch {}:".format(i))

        shuffled_indices = tf.random.shuffle(tf.range(len(train_notes)))
        train_notes = tf.gather(train_notes, shuffled_indices)
        train_duration = tf.gather(train_duration, shuffled_indices)

        num_trained = 0
        while num_trained < len(train_notes):
            notes_batch = train_notes[num_trained: num_trained + model.batch_size]
            duration_batch = train_duration[num_trained: num_trained + model.batch_size]

            with tf.GradientTape() as tape:
                probabilities = model(notes_batch, duration_batch)
                loss = model.loss_function(probabilities, duration_batch)

            num_trained += model.batch_size
            if num_trained % (1 * model.batch_size) == 0:
                print("     Loss on training after {} batches = {}".format(num_trained / model.batch_size, loss))

            gradients = tape.gradient(loss, model.trainable_variables)
            model.optimizer.apply_gradients(zip(gradients, model.trainable_variables))


def duration_test(model, test_notes, test_duration):
    """
    Runs through one epoch - all testing examples.

    :param model: the initialized model to use for forward and backward pass
    :param test_notes: note test data (all data for testing) of shape (num_pieces, piece_length)
    :param test_duration: duration test data (all data for testing) of shape (num_pieces, piece_length)
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

        probabilities = model(notes_batch, duration_batch)
        # remove first token from batch to create labels
        num_words_in_batch = model.batch_size * model.piece_length
        total_words += num_words_in_batch

        batch_loss = model.loss_function(probabilities, duration_batch)
        total_loss += batch_loss

        # If there is an accuracy function:
        #batch_accuracy = num_words_in_batch * model.accuracy_function(probabilities, duration_batch)
        #total_accuracy += batch_accuracy

        num_tested += model.batch_size
        if num_tested % (1 * model.batch_size) == 0:
            print("     Tested {} batches".format(num_tested / model.batch_size))

    return np.exp(total_loss / total_words)

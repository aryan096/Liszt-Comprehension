import tensorflow as tf
from keras.layers import Dense, Dropout, GRU, Bidirectional


def create_note_gen_network(note_vocab_size):
    embedding_size = 30

    model = tf.keras.Sequential()

    model.add(tf.keras.layers.Embedding(note_vocab_size, embedding_size))
    model.add(Bidirectional(GRU(100, return_sequences=True)))
    model.add(Dropout(0.3))
    model.add(Bidirectional(GRU(100, return_sequences=True)))
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


def train_note_gen(model, input_data, labels, num_epochs):
    """
    Trains NoteGen
    """
    model.fit(input_data, labels, epochs=num_epochs, batch_size=250)


def test_note_gen(model, input_data, labels):
    """
    Tests NoteGen
    """
    result = model.evaluate(input_data, labels, batch_size=250)
    return result

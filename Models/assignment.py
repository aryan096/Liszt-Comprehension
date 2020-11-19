import os
import sys
import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
import time
#from preprocess ...

def note_train(model, train_inputs, train_labels):
    '''

    :param model:
    :param train_inputs: train inputs (all inputs for training) of shape (num_pieces, piece_length)
    :param train_labels: train labels (all labels for training) of shape (num_pieces, piece_length)
    :return:
    '''

    print("Begin Training")
    num_trained = 0
    while num_trained < len(train_inputs):
        input_batch = train_inputs[num_trained:num_trained + model.batch_size]
        label_batch = train_labels[num_trained:num_trained + model.batch_size]

        with tf.GradientTape() as tape:
            probabilities = model(input_batch, None)
            loss = model.loss(probabilities, label_batch)

        num_trained += model.batch_size
        if num_trained % (model.batch_size) == 0:
            print("      Loss on training after {} trained inputs: {}".format(num_trained * model.window_size, loss))

        gradients = tape.gradient(loss, model.trainable_variables)
        model.optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    pass

def note_test(model, test_inputs, test_labels):
    '''
    Runs through one epoch - all testing examples

    :param model: the trained model to use for prediction
    :param test_inputs: train inputs (all inputs for testing) of shape (num_inputs,)
    :param test_labels: train labels (all labels for testing) of shape (num_labels,)
    :returns: perplexity of the test set
    '''

    print("Begin Testing")
    loss_list = []
    num_tested = 0
    while num_tested < len(test_inputs):
        input_batch = test_inputs[num_tested:num_tested + model.batch_size]
        label_batch = test_labels[num_tested:num_tested + model.batch_size]

        probabilities = model(input_batch, None)
        loss = model.loss(probabilities, label_batch)
        loss_list.append(loss)

        num_tested += model.batch_size
        if num_tested % (model.batch_size) == 0:
            print("      Tested {} inputs".format(num_tested * model.window_size))

    return tf.exp(tf.reduce_mean(loss_list))

def duration_train(model, train_notes, train_duration, duration_padding_index):
    '''
    Runs through one epoch - all training examples.

    :param model: the initialized model to use for forward and backward pass
    :param train_notes: notes train data (all data for training) of shape (num_pieces, piece_length)
    :param train_duration: duration train data (all data for training) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :return: None
    '''

    pass

def duration_test(model, train_notes, train_duration, duration_padding_index):
    '''
    Runs through one epoch - all testing examples.

    :param model: the initialized model to use for forward and backward pass
    :param test_note: note test data (all data for testing) of shape (num_pieces, piece_length)
    :param test_duration: duration test data (all data for testing) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :returns: a tuple containing at index 0 the perplexity of the test set and at index 1 the per symbol accuracy on test set,
    e.g. (my_perplexity, my_accuracy)
    '''

    pass

def main():
    '''get data, init models, sys_arguments stuff,
     train and test note gen, mid process, train and test duration gen, post processing '''
    if len(sys.argv) != 2 or sys.argv[1] not in {"NOTE", "NOTE_DURATION"}:
        print("USAGE: python assignment.py <Model Type>")
        print("<Model Type>: [NOTE/NOTE_DURATION]")
        exit()

    start_time = time.time()

    # TODO - get data using pre-processing:
    # need note_gen_train_inputs and note_gen_train_labels (these are the same but shifted by 1)
    # need note_gen_test_inputs and note_gen_test_labels (these are the same but shifted by 1)
    # need note_vocab

    # TODO - initialize NoteGen model
    # TODO - train NoteGen model
    # TODO - test NoteGen model - print perplexity

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    # TODO - if NOTE_DURATION, then do the same for the duration model

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    pass

if __name__ == '__main__':
	main()
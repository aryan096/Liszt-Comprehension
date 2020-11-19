import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
#from preprocess ...

def note_train(model, train_inputs, train_labels):
    '''

    :param model:
    :param train_inputs: train inputs (all inputs for training) of shape (num_inputs,)
    :param train_labels: train labels (all labels for training) of shape (num_labels,)
    :return:
    '''

    pass

def note_test(model, test_inputs, test_labels):
    """
    Runs through one epoch - all testing examples

    :param model: the trained model to use for prediction
    :param test_inputs: train inputs (all inputs for testing) of shape (num_inputs,)
    :param test_labels: train labels (all labels for testing) of shape (num_labels,)
    :returns: perplexity of the test set
    """

    pass

def duration_train(model, train_notes, train_duration, duration_padding_index):
    """
    Runs through one epoch - all training examples.

    :param model: the initialized model to use for forward and backward pass
    :param train_notes: notes train data (all data for training) of shape (num_pieces, piece_length)
    :param train_duration: duration train data (all data for training) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :return: None
    """

    pass

def duration_test(model, train_notes, train_duration, duration_padding_index):
    """
    Runs through one epoch - all testing examples.

    :param model: the initialized model to use for forward and backward pass
    :param test_note: note test data (all data for testing) of shape (num_pieces, piece_length)
    :param test_duration: duration test data (all data for testing) of shape (num_pieces, piece_length)
    :param duration_padding_index: the padding index, the id of *PAD* token. This integer is used when masking padding labels.
    :returns: a tuple containing at index 0 the perplexity of the test set and at index 1 the per symbol accuracy on test set,
    e.g. (my_perplexity, my_accuracy)
    """

    pass

def main():
    '''get data, init models, sys_arguments stuff,
     train and test note gen, mid process, train and test duration gen, post processing '''

    pass

if __name__ == '__main__':
	main()

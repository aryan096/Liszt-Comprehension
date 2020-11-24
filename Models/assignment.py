import sys
import time
from Models.note_gen_functional import *
from processing.preprocess import *
from processing.generate_midi import *


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

def reverse_dictionary(dictionary: dict) -> dict:
    """
    Reverses a bijective dictionary
    :param dictionary: a bijective dictionary
    :return: the input dictionary with keys ad values reversed
    """
    return {value: key for key, value in dictionary.items()}

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
    note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii = get_data(
        r"/Users/herberttraub/PycharmProjects/CSCI1470/HW1/Liszt_Comprehension/data/Scarlatti", 250)

    id_to_ascii = reverse_dictionary(ascii_to_id)
    ascii_to_pitch = reverse_dictionary(pitch_to_ascii)
    # TODO - initialize NoteGen model
    note_model = create_note_gen_network(len(id_to_ascii))
    # TODO - train NoteGen model
    train_note_gen(note_model, note_id_inputs, note_id_labels)
    # TODO - test NoteGen model - print perplexity

    initial_note_ascii = "$"
    generate_midi(note_model, id_to_ascii, {}, ascii_to_pitch, initial_note_ascii, 250)

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    # TODO - if NOTE_DURATION, then do the same for the duration model

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    pass

if __name__ == '__main__':
    main()

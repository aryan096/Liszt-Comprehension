import sys
import time
from Models.note_gen_functional import *
from processing.preprocess import *
from processing.generate_midi import *
from Models.duration_gen2 import *


def duration_train(model, train_notes, train_duration):
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



def duration_test(model, test_notes, test_duration):
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
    corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches = get_data(
        r"/Users/herberttraub/PycharmProjects/CSCI1470/HW1/Liszt-Comprehension/data/Liszt", WINDOW_SIZE)

    id_to_ascii = reverse_dictionary(ascii_to_id)
    ascii_to_pitch = reverse_dictionary(pitch_to_ascii)
    # TODO - initialize NoteGen model
    note_model = create_note_gen_network(len(id_to_ascii))
    # TODO - train NoteGen model
    train_note_gen(note_model, note_id_inputs, note_id_labels)
    # TODO - test NoteGen model - print perplexity

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    # TODO - if NOTE_DURATION, then do the same for the duration model
    if sys.argv[1] == "NOTE_DURATION":
        duration_model = DurationGen2(len(id_to_ascii), len(dot_to_id), WINDOW_SIZE)
        prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)
        duration2_train(duration_model, prepped_note_ids, prepped_dot_ids)
    else:
        duration_model = None

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    initial_note_ascii = "$"
    generate_midi(note_model, id_to_ascii, reverse_dictionary(dot_to_id), ascii_to_pitch, initial_note_ascii, 100, duration_model)

if __name__ == '__main__':
    main()

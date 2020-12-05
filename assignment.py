import sys
import time
from Models.note_gen_functional import *
from processing.preprocess import *
from processing.generate_midi import *
from Models.duration_gen import *


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
        "./data/Chopin", WINDOW_SIZE)

    #id_to_ascii = reverse_dictionary(ascii_to_id)
    ascii_to_pitch = reverse_dictionary(pitch_to_ascii)
    # TODO - initialize NoteGen model
    note_model = create_note_gen_network(len(ascii_to_id))
    # TODO - train NoteGen model
    train_note_gen(note_model, note_id_inputs, note_id_labels, 1)
    # TODO - test NoteGen model - print perplexity

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    # TODO - if NOTE_DURATION, then do the same for the duration model
    if sys.argv[1] == "NOTE_DURATION":
        duration_model = DurationGen(len(ascii_to_id), len(dot_to_id), WINDOW_SIZE+2)
        prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)
        duration_train(duration_model, prepped_note_ids, prepped_dot_ids)
    else:
        duration_model = None

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    initial_note_ascii = "$"
    generate_midi(note_model, ascii_to_id, reverse_dictionary(dot_to_id), ascii_to_pitch, initial_note_ascii, 100, duration_model)
    #note_model.save_weights('./checkpoints/notes_model_checkpoint')
    #duration_model.save_weights('./checkpoints/duration_model_checkpoint')


def main2():
    '''Initialize, train, save'''
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
        "./data/Chopin", WINDOW_SIZE)

    #id_to_ascii = reverse_dictionary(ascii_to_id)
    ascii_to_pitch = reverse_dictionary(pitch_to_ascii)
    # TODO - initialize NoteGen model
    note_model = create_note_gen_network(len(ascii_to_id))
    # TODO - train NoteGen model
    #train_note_gen(note_model, note_id_inputs, note_id_labels, 1)
    # TODO - test NoteGen model - print perplexity

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    # TODO - if NOTE_DURATION, then do the same for the duration model
    if sys.argv[1] == "NOTE_DURATION":
        duration_model = DurationGen(len(ascii_to_id), len(dot_to_id), WINDOW_SIZE+2)
        prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)
        #duration_train(duration_model, prepped_note_ids, prepped_dot_ids)
    else:
        duration_model = None

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    note_model.save_weights('./checkpoints/notes_model_checkpoint')
    duration_model.save_weights('./checkpoints/duration_model_checkpoint')

if __name__ == '__main__':
    main()

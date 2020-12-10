import time
import os
from Models.note_gen_functional import *
from processing.preprocess import *
from processing.generate_midi import *
from Models.duration_gen import *
import random


def config():
    '''
    This function configures the processing and model based on user input.
    '''
    model = None
    while model not in {"NOTE", "NOTE_DURATION"}:
        model = input("NOTE or NOTE_DURATION? (type one of the options in all caps): ")

    train = None
    while train not in {"y", "n"}:
        train = input("Do you want to train and save? (y/n): ")

    load = None
    while load not in {"y", "n"}:
        load = input("Do you want to load and generate? (only say yes if you said yes in the previous question, or have trained before) (y/n): ")

    if train == "y":
        composer = None
        while composer not in {"Bach", "Mozart", "Beethoven", "Scarlatti", "Chopin", "Liszt"}:
            composer = input("Pick a composer: Bach, Mozart, Beethoven, Scarlatti, Chopin, Liszt: ")

        one_track = "n"
        if composer != "Scarlatti":
            one_track = input("OneTrack (y/n): ")

        note_gen_epochs = int(input("How many NoteGen epochs? (int): "))
        duration_gen_epochs = None
        if model == "NOTE_DURATION":
            duration_gen_epochs = int(input("How many DurationGen epochs? (int): "))

        if one_track == "y":
            file_path_training_data = "./OneTrackData/" + composer
            file_path_save_data = "./Dict Data/" + "OneTrack" + composer
            file_path_save_weights = "./Trained Weights/" + model + "_" + "OneTrack" + composer + ",{},{}".format(note_gen_epochs, duration_gen_epochs)
            file_path_read_weights = "./Trained Weights/" + model + "_" + "OneTrack" + composer + ",{},{}".format(note_gen_epochs, duration_gen_epochs)
        else:
            file_path_training_data = "./data/" + composer
            file_path_save_data = "./Dict Data/" + "MultiTrack" + composer
            file_path_save_weights = "./Trained Weights/" + model + "_" + "MultiTrack" + composer + ",{},{}".format(note_gen_epochs,
                                                                                              duration_gen_epochs)
            file_path_read_weights = "./Trained Weights/" + model + "_" + "MultiTrack" + composer + ",{},{}".format(note_gen_epochs,
                                                                                              duration_gen_epochs)
    else:
        file_path_training_data = None
        note_gen_epochs = None
        duration_gen_epochs = None
        file_path_save_weights = None
        if load == 'n':
            exit()
        else:
            possible_files = os.listdir("./Trained Weights")
            files_index = int(input("choose one number: \n" + "\n".join(["{} {}".format(i, elm) for i, elm in enumerate(possible_files)]) + "\n"))
            file_path_read_weights = "./Trained Weights/" + possible_files[files_index]

            possible_files = os.listdir("./Dict Data")
            files_index = int(input(
                "choose one number: \n" + "\n".join(["{} {}".format(i, elm) for i, elm in enumerate(possible_files)]) + "\n"))
            file_path_save_data = "./Dict Data/" + possible_files[files_index]

    return model, file_path_training_data, file_path_save_data, file_path_save_weights, file_path_read_weights, note_gen_epochs, duration_gen_epochs, train, load

def train_and_save(file_path_training_data, file_path_save_data, file_path_save_weights, model_type, note_gen_epochs, duration_gen_epochs):
    '''Initialize, train, save'''
    start_time = time.time()

    corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches = get_data(
        file_path_save_data, file_path_training_data, WINDOW_SIZE)

    note_model = create_note_gen_network(len(ascii_to_id))
    note_id_inputs_train, note_id_labels_train, note_id_inputs_test, note_id_labels_test = \
        split_train_and_test_data(note_id_inputs, note_id_labels)
    train_note_gen(note_model, note_id_inputs_train, note_id_labels_train, note_gen_epochs)
    test_note_gen(note_model, note_id_inputs_test, note_id_labels_test)

    note_gen_time = time.time()
    print("Time elapsed for NoteGen training/testing = {} minutes".format((note_gen_time - start_time)/60))

    if model_type == "NOTE_DURATION":
        duration_model = DurationGen(len(ascii_to_id), len(dot_to_id), WINDOW_SIZE+2)
        prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)
        prepped_note_ids_train, prepped_dot_ids_train, prepped_note_ids_test, prepped_dot_ids_test = \
            split_train_and_test_data(prepped_note_ids, prepped_dot_ids)
        duration_train(duration_model, prepped_note_ids_train, prepped_dot_ids_train, duration_gen_epochs)
        #duration_test(duration_model, prepped_note_ids_test, prepped_dot_ids_test)
    else:
        duration_model = None

    duration_gen_time = time.time()
    print("Time elapsed for DurationGen training/testing = {} minutes".format((duration_gen_time - note_gen_time)/60))

    note_model.save_weights(file_path_save_weights + '/notes_model_checkpoint')
    if model_type == "NOTE_DURATION":
        duration_model.save_weights(file_path_save_weights + '/duration_model_checkpoint')


def load_and_generate(file_path_read_data, file_path_read_weights, model_type):
    '''get data, init models, sys_arguments stuff,
     train and test note gen, mid process, train and test duration gen, post processing '''

    corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches = read_dicts_from_file(file_path_read_data)

    ascii_to_pitch = reverse_dictionary(pitch_to_ascii)
    note_model = create_note_gen_network(len(ascii_to_id))
    note_model.load_weights(file_path_read_weights + '/notes_model_checkpoint')

    if model_type == "NOTE_DURATION":
        duration_model = DurationGen(len(ascii_to_id), len(dot_to_id), WINDOW_SIZE+2)
        duration_model.load_weights(file_path_read_weights + '/duration_model_checkpoint')
    else:
        duration_model = None

    # initial_note = [REST_TOKEN]
    # x = [pitch_to_ascii[note] for note in initial_note]
    # x.sort()
    # initial_note_ascii = "".join(list(x))
    initial_note = input('Enter an initial note ( # for sharp, - for flat, and followed by the octave. Examples - A4, F#5, D-4. A random note will be chosen if you leave this blank or enter an invalid note.\n')
    if initial_note in pitch_to_ascii:
        initial_note_ascii = pitch_to_ascii[initial_note]
    else:
        initial_note_ascii = random.choice(list(ascii_to_id.keys()))
    generate_midi(note_model, ascii_to_id, reverse_dictionary(dot_to_id), ascii_to_pitch, initial_note_ascii, 100, duration_model)


if __name__ == '__main__':
    model, file_path_training_data, file_path_save_data, file_path_save_weights, file_path_read_weights, note_gen_epochs, duration_gen_epochs, train, load = \
        config()

    if train == "y":
        train_and_save(file_path_training_data, file_path_save_data, file_path_save_weights, model, note_gen_epochs, duration_gen_epochs)
    if load == 'y':
        load_and_generate(file_path_save_data, file_path_read_weights, model)

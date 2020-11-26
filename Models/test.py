import tensorflow as tf
import numpy as np

from Models.note_gen_functional import *
from processing.generate_midi import *
from Models.duration_gen import *
from Models.assignment import *
from Models.duration_gen2 import *


def test_generate():
    fake_id_to_ascii_dict = {i:l for i,l in enumerate("ABCDEFGHIJK")}
    initial_note_ascii = "J"

    model = create_note_gen_network(len(fake_id_to_ascii_dict))

    print(generate_notes(model, fake_id_to_ascii_dict, initial_note_ascii, 20))

#test_generate()

def get_inputs_and_labels(data):
    inputs = [data[i][:-1] for i in range(len(data))]
    labels = [data[i][1:] for i in range(len(data))]

    return inputs, labels

def test_train():
    fake_id_to_ascii_dict = {i: l for i, l in enumerate("ABCDEFGHIJK")}
    model = create_note_gen_network(len(fake_id_to_ascii_dict))

    fake_data = np.array([[np.random.choice(range(11)) for _ in range(50)],
                                [np.random.choice(range(11)) for _ in range(50)]])
    fake_input, fake_labels = get_inputs_and_labels(fake_data)

    #print(model.call(fake_input))
    train_note_gen(model, fake_input, fake_labels)
    print(test_note_gen(model, fake_input, fake_labels))
    print("success!")

#test_train()


def test_duration_gen():
    corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, duration_offset_dict, corpus_duration_offset_batches = get_data(
        r'C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\Chopin', 250
    )


    model = DurationGen2(len(ascii_to_id), len(duration_offset_dict), 250)
    prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)


    duration2_train(model, prepped_note_ids, prepped_dot_ids)
    #print(corpus_duration_offset_batches[0:1])
    #print(corpus_note_id_batches[0][0:1])
    out = model(tf.convert_to_tensor([prepped_note_ids[0]]), tf.convert_to_tensor([[START_ID, 1]]))
    print(out)

    # perplexity, accuracy = duration_test(model, test_french, test_english, eng_padding_index)
    # print("Model Perplexity = {}".format(perplexity))
    # print("Model Accuracy = {}".format(accuracy))

#test_duration_gen()

def test_dot_gen():
    corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, duration_offset_dict, corpus_duration_offset_batches = get_data(
        r'C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\Chopin', WINDOW_SIZE
    )

    model = DurationGen2(len(ascii_to_id), len(duration_offset_dict), 250)
    prepped_note_ids, prepped_dot_ids = prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_batches)

    duration2_train(model, prepped_note_ids, prepped_dot_ids)

    print(generate_durations_and_offsets(model, prepped_note_ids[0]))

test_dot_gen()
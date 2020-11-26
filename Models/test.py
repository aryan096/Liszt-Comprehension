import tensorflow as tf
import numpy as np

from Models.note_gen_functional import *
from processing.generate_midi import *
from Models.duration_gen import *
from Models.assignment import *


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

    model = DurationGen(len(ascii_to_id), len(duration_offset_dict), 250)


    duration_train(model, corpus_note_id_batches, corpus_duration_offset_batches)

    # perplexity, accuracy = duration_test(model, test_french, test_english, eng_padding_index)
    # print("Model Perplexity = {}".format(perplexity))
    # print("Model Accuracy = {}".format(accuracy))

test_duration_gen()
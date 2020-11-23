import tensorflow as tf
import numpy as np

from Liszt_Comprehension.Models.note_gen_functional import *
from Liszt_Comprehension.processing.generate_midi import *


def test_generate():
    fake_id_to_ascii_dict = {i:l for i,l in enumerate("ABCDEFGHIJK")}
    initial_note_ascii = "J"

    model = create_note_gen_network(len(fake_id_to_ascii_dict))

    print(generate_notes(model, fake_id_to_ascii_dict, initial_note_ascii, 20))

test_generate()

def get_inputs_and_labels(data):
    inputs = [data[i][:-1] for i in range(len(data))]
    labels = [data[i][1:] for i in range(len(data))]

    return inputs, labels

def test_train():
    fake_id_to_ascii_dict = {i: l for i, l in enumerate("ABCDEFGHIJK")}
    model = create_network(len(fake_id_to_ascii_dict))

    fake_data = np.array([[np.random.choice(range(11)) for _ in range(50)],
                                [np.random.choice(range(11)) for _ in range(50)]])
    fake_input, fake_labels = get_inputs_and_labels(fake_data)

    #print(model.call(fake_input))
    train_note_gen(model, fake_input, fake_labels)
    print(test_note_gen(model, fake_input, fake_labels))
    print("success!")


test_train()












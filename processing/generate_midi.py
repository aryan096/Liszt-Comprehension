from music21 import *
import numpy as np
import tensorflow as tf
import shutil
import os
import datetime
from processing.preprocess import REST_ASCII, START_ID, STOP_ID, START_TOKEN, WINDOW_SIZE, PAD_ID


def generate_notes(model, ascii_to_id_dict: dict, initial_note_ascii: str, length: int) -> list:
	"""
	Generates a piece of notes given a starting note
	:param model: trained model
	:param ascii_to_id_dict: a dictionary mapping ASCIIs to integer ids
	:param initial_note_ascii: an initial note as an ASCII character
	:param length: desired piece length
	:return: a generated piece of ASCII characters
	"""
	sample_n = 5  # The top sample_n chords are chosen from randomly when generating the next chord of the piece
	reverse_dictionary = {id: ascii for ascii, id in ascii_to_id_dict.items()}

	first_note_id = ascii_to_id_dict[initial_note_ascii]
	next_input = [[first_note_id]]
	ascii_piece = [initial_note_ascii]

	for i in range(length):
		probs = model.predict(next_input)
		probs = np.array(probs[0, -1, :])  # output of model is 3D

		top_note_ids = np.argsort(probs)[-sample_n:]
		top_probs = np.exp(probs[top_note_ids]) / sum(np.exp(probs[top_note_ids]))
		next_chord_id = np.random.choice(top_note_ids, p=top_probs)

		ascii_piece.append(reverse_dictionary[next_chord_id])
		next_input[0].append(next_chord_id)
	print(ascii_piece)
	return ascii_piece, next_input


def generate_durations_and_offsets(model, piece):
	"""

	:param model: trained duration_gen model
	:param piece: generated sequence of note ids (with an extended dim)
	:return:
	"""
	# ToDo:
	# Implement generate durations
	sample_n = 5  # The top sample_n chords are chosen from randomly when generating the next chord of the piece

	first_dot_id = START_ID
	current_piece_len = len(piece)
	n_pad_tokens = WINDOW_SIZE - current_piece_len
	encoder_input = [[START_ID] + piece + [PAD_ID] * n_pad_tokens +  [STOP_ID]]
	#print(encoder_input)
	#print(len(encoder_input[0]))
	next_input = [first_dot_id]

	for i in range(current_piece_len):
		next_input_current_len = len(next_input)
		n_decoder_pad_tokens = WINDOW_SIZE - next_input_current_len
		decoder_input = [next_input + [PAD_ID] * (n_decoder_pad_tokens+1) + [STOP_ID]]

		probs = model.call(tf.convert_to_tensor(encoder_input), tf.convert_to_tensor(decoder_input))
		probs = np.array(probs[0, -1, :])  # output of model is 3D

		top_note_ids = list(np.argsort(probs)[-sample_n:])#.remove(STOP_ID).remove(START_ID).remove(PAD_ID)

		ids_to_remove = [START_ID, STOP_ID, PAD_ID]
		for id in ids_to_remove:
			if id in top_note_ids:
				top_note_ids.remove(id)

		#print(top_note_ids)
		top_probs = np.exp(probs[top_note_ids]) / sum(np.exp(probs[top_note_ids]))
		next_dot_id = np.random.choice(top_note_ids, p=top_probs)

		next_input.append(next_dot_id)
	print(next_input)
	return [next_input]

def reverse_dictionary(dictionary: dict) -> dict:
	"""
    Reverses a bijective dictionary
    :param dictionary: a bijective dictionary
    :return: the input dictionary with keys ad values reversed
    """
	return {value: key for key, value in dictionary.items()}


def id_to_ascii(id_piece: list, id_to_ascii_dict: dict) -> list:
	"""
	Turn a generated piece of ids into a piece of ASCIIs
	:param id_piece: a piece generated by the model in id form
	:param id_to_ascii_dict: a dictionary mapping id to ASCII
	:return: a list of ascii characters
	"""
	ascii_piece = [id_to_ascii_dict[id] for id in id_piece]
	return ascii_piece


def id_to_duration_offsets(id_durations: list, id_to_dot_dict: dict) -> list:
	"""
	Turn a generated list of duratino ids into a list of durations
	:param id_durations: a list of durations by the model in id form
	:param duration_offset_to_id_dict: a dictionary mapping id to duration
	:return: a list of durations
	"""
	durations = [id_to_dot_dict[duration_offset] for duration_offset in id_durations]
	return durations

def accumulate_offset(incremental_offset: list) -> list:
	"""
	Accumulates offsets
	:param incremental_offset: a list of incremental offsets
	:return: incrementalized list of accumulated offsets
	"""
	out = [incremental_offset[0]]
	for i in range(len(incremental_offset) - 1):
		out.append(out[i]+incremental_offset[i+1])
	return out


def ascii_to_m21(ascii_notes: list, ascii_to_m21_dict: dict, durations_and_offsets=None):
	"""
	Takes a list of ASCII notes and durations and returns a music21 stream object
	:param ascii_notes: a piece of music in ascii form
	:param ascii_to_m21_dict: dictionary mapping ASCII characters to m21 objects
	:param durations: a list of durations
	:param offsets: a list of incremental offsets
	:return: music21 Stream object
	"""
	# can i assume start, stop, and pad are in neither notes nor durations?
	piece = stream.Stream()
	for chord_string in ascii_notes:
		if len(chord_string) > 1:
			m21_chord = chord.Chord()
			split = list(chord_string)
			for note_name in split:
				m21_chord.add(ascii_to_m21_dict[note_name])
			piece.append(m21_chord)
		elif chord_string == REST_ASCII:
			piece.append(note.Rest())
		else:
			piece.append(note.Note(ascii_to_m21_dict[chord_string]))

	if durations_and_offsets:
		#print(ascii_notes, durations_and_offsets)
		if durations_and_offsets[0] == START_TOKEN:
			durations_and_offsets = durations_and_offsets[1:]
		if START_ID in durations_and_offsets:
			raise Exception("there is a start token where there shouldn't be")
		assert len(ascii_notes) == len(durations_and_offsets)
		durations = [elm[0] for elm in durations_and_offsets]
		accumulated_offsets = accumulate_offset([elm[1] for elm in durations_and_offsets])
		for i in range(len(durations)):
			piece[i].duration.quarterLength = durations[i]
			piece[i].offset = accumulated_offsets[i]

	return piece


def generate_midi(note_model, ascii_id_dict: dict, id_duration_offset_dict: dict, ascii_m21_dict: dict,
                  initial_note_ascii: str, length: int, duration_model=None):# -> None:
	"""
	Does the complete postprocessing using above-defined helper functions and saves a file called "first_ever_piece.midi"
	to the current directory
	:param note_model: model that generates notes
	:param ascii_id_dict: dictionary mapping ASCII to ids
	:param id_duration_offset_dict: dictionary mapping ids to (duration, offset) tuples
	:param ascii_m21_dict: dictionary mapping ASCII to music21 objects
	:param initial_note_ascii: an initial note as an ASCII character
	:param length: desired generated piece length
	:param duration_model: model that generates durations
	:return: None
	"""
	composed_piece, composed_id_piece = generate_notes(note_model, ascii_id_dict, initial_note_ascii, length)
	#print(id_ascii_dict)
	#print(composed_piece)
	#print(composed_id_piece)

	if duration_model:
		id_durations_and_offsets = generate_durations_and_offsets(duration_model, composed_id_piece[0])
		durations_and_offsets = id_to_duration_offsets(id_durations_and_offsets[0], id_duration_offset_dict)
	else:
		durations_and_offsets = None

	piece = ascii_to_m21(composed_piece, ascii_m21_dict, durations_and_offsets)

	# Saves a midi file containing the generated piece called first_ever_piece.midi to the current directory
	current_directory = os.getcwd()
	#print(current_directory)
	separator = "\\" if os.name == 'nt' else '/'
	target_directory = current_directory + separator + "Generated Pieces"
	file_name = str(datetime.datetime.now())[:16].replace(":", "_") + ".midi"

	piece.write("midi", file_name)
	shutil.move(current_directory + separator + file_name, target_directory + separator + file_name)
	return piece
	# Opens a MusicXML reader and shows the sheet music for the generated piece
	#piece.show()  # only works if MusicXML reader like MuseScore, Finale, or Sibelius is installed



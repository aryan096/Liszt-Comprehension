from music21 import *
import numpy as np


def generate_notes(model, id_to_ascii_dict: dict, initial_note_ascii: str, length: int) -> list:
	"""
	Generates a piece of notes given a starting note
	:param model: trained model
	:param id_to_ascii_dict: a dictionary mapping integer ids to ASCII ids
	:param initial_note_ascii: an initial note as an ASCII character
	:param length: desired piece length
	:return: a generated piece of ASCII characters
	"""

	sample_n = 10
	reverse_dictionary = {ascii: id for ascii, id in id_to_ascii_dict.items()}
	previous_state = None

	first_note_index = reverse_dictionary[initial_note_ascii]
	next_input = [[first_note_index]]
	ascii_piece = [initial_note_ascii]

	for i in range(length):
		probs, previous_state = model.call(next_input, previous_state)
		probs = np.array(probs[0, 0, :])
		top_note_ids = np.argsort(probs)[-sample_n:]
		top_probs = np.exp(probs[top_note_ids]) / sum(np.exp(probs[top_note_ids]))
		next_chord_index = np.random.choice(top_note_ids, p=top_probs)

		ascii_piece.append(id_to_ascii_dict[next_chord_index])
		next_input = [[next_chord_index]]
	return ascii_piece


def generate_durations(model, piece):
	# ToDo:
	# Implement generate durations
	return []


def id_to_ascii(id_piece: list, id_to_ascii_dict: dict) -> list:
	"""
	Turn a generated piece of ids into a piece of ASCIIs
	:param id_piece: a piece generated by the model in id form
	:param id_to_ascii_dict: a dictionary mapping id to ASCII
	:return: a list of ascii characters
	"""
	ascii_piece = [id_to_ascii_dict[id] for id in id_piece]
	return ascii_piece


def id_to_duration(id_durations: list, id_to_duration_dict: dict) -> list:
	"""
	Turn a generated list of duratino ids into a list of durations
	:param id_durations: a list of durations by the model in id form
	:param id_to_duration_dict: a dictionary mapping id to duration
	:return: a list of durations
	"""
	durations = [id_to_duration_dict[id] for id in id_durations]
	return durations

def ascii_to_m21(ascii_notes: list, ascii_to_m21_dict: dict, durations=None):
	"""
	Takes a list of ASCII notes and durations and returns a music21 stream object
	:param ascii_notes: a piece of music in ascii form
	:param ascii_to_m21_dict: dictionary mapping ASCII characters to m21 objects
	:param durations: a list of durations
	:return: music21 Stream object
	"""
	# can i assume start, stop, and pad are in neither notes nor durations?
	piece = stream.Stream()
	for i, chord in enumerate(ascii_notes):
		if len(chord) > 1:
			m21_chord = chord.Chord()
			split = list(chord)
			for note in split:
				m21_chord.add(ascii_to_m21_dict[note])
				piece.append(m21_chord)
		if chord == "rest token":
			piece.append(note.Rest())
		else:
			piece.append(note.Note(ascii_to_m21_dict[chord]))
	if durations:
		assert len(ascii_notes) == len(durations)
		for i, duration in enumerate(durations):
			piece[i].duration.quarterLength = duration
	return piece


def generate_midi(note_model, id_ascii_dict: dict, id_duration_dict: dict, ascii_m21_dict: dict,
                  initial_note_ascii: str, length: int, duration_model=None) -> None:
	"""
	Does the complete postprocessing using above-defined helper functions and saves a file called "generated_piece.midi"
	to the current directory
	:param note_model: model that generates notes
	:param id_ascii_dict: dictionary mapping ids to ASCII
	:param id_duration_dict: dictionary mapping ids to durations
	:param ascii_m21_dict: dictionary mapping ASCII to music21 objects
	:param initial_note_ascii: an initial note as an ASCII character
	:param length: desired generated piece length
	:param duration_model: model that generates durations
	:return: None
	"""
	composed_piece = generate_notes(note_model, id_ascii_dict, initial_note_ascii, length)
	if duration_model:
		id_durations = generate_durations(duration_model, composed_piece)
		durations = id_to_duration(id_durations, id_duration_dict)
	else:
		durations = None
	ascii_notes = id_to_ascii(composed_piece, id_ascii_dict)
	piece = ascii_to_m21(ascii_notes, ascii_m21_dict, durations)
	piece.write("midi", "generated_music.midi")


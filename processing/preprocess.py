from music21 import *
import os
import random
import tensorflow as tf
import re
# ToDo: (general)
# 2. Find way to store data (ary)


PAD_TOKEN = "**PAD**"
PAD_ASCII = chr(35)
STOP_TOKEN = "**STOP**"
STOP_ASCII = chr(34)
START_TOKEN = "**START**"
START_ASCII = chr(33)
REST_TOKEN = "rest"
REST_ASCII = chr(36)


def midi_to_m21(file_path: str):
	"""
	This function takes in a file_path to a midi file and returns the m21 score object
	for that file
	:param file_path: global file path for a single midi file
	:return: a music21 object
	"""
	file_path_split = file_path.split('/')
	print('parsing ' + file_path_split[len(file_path_split) - 1] + ' ...')
	m21_midi = converter.parse(file_path)  # This will return a score object
	return m21_midi


def get_notes_and_durations(score) -> (list, list, list):
	"""
	Converts a music21 object to list of chords(notes, chords, rests) and list of durations
	:param score: a piece of music as a music21 object
	:return: a list of chords, a list of durations, and a list of offsets of length number_of_chords_in_piece
	"""
	durations = []
	offset = []
	# This loop goes through everything in the score, adds notes, chords, and
	# rests to the sounds list, and durations to the durations list
	try:  # file has instrument parts
		sounds = instrument.partitionByInstrument(score).parts[0].recurse()
	except:  # file has notes in a flat structure
		sounds = score.flat.notesAndRests

	for sound in sounds:
		# add durations
		durations.append(sound.duration.quarterLength)
		offset.append(sound.offset)

	return sounds, durations, offset


def incrementalize_offset(offset: list) -> list:
	"""
	Incrementalizes offsets
	:param offset: a list of offsets
	:return: incrementalized list of offsets
	"""
	offset = [0] + offset
	return [x-offset[i] for i, x in enumerate(offset[1:])]


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


def note_pitchify(score: list) -> list:
	"""
	Takes a sequence of music21 objects and converts it to a list of lists containing pitch names with octaves
	:param score: a list of music21 objects
	:return: a list of lists containing note names with octaves
	"""
	pitches = []
	for thing in score:
		if isinstance(thing, note.Note):
			# if thing is a note
			pitch_thing = [thing.nameWithOctave]

		elif isinstance(thing, chord.Chord):
			# if thing is a chord
			pitch_thing = [note_obj.nameWithOctave for note_obj in thing.pitches]

		elif isinstance(thing, note.Rest):
			# if thing is a rest
			pitch_thing = [REST_TOKEN]

		else:
			# if thing is magically something else
			pitch_thing = [REST_TOKEN]

		pitches.append(pitch_thing)
	return pitches


def amend_duration_dictionary(duration_dictionary: dict, durations: list):
	"""
	Give each duration encountered a unique integer id
	:param durations: a list of all durations encountered in preprocessing
	:return: None
	"""

	# each duration is keyed with an integer starting from
	for duration in durations:
		# generate random key between 1000 and 100000
		# this range should be more than good enough
		curr = random.randint(1000, 100000)
		while curr in duration_dictionary:
			curr = random.randint(1000, 100000)

		if duration not in duration_dictionary.values():
			# add key of duration and map it to the value
			duration_dictionary[duration] = curr

	return duration_dictionary


def pad_and_token(max_length: int, stripped_piece: list) -> list:
	"""
	Pad each piece, now in ASCII form, to fit length of longest piece and add a start and stop token
	:param max_length: length to which each piece should be padded
	:param stripped_piece: either the notes or durations of a piece in ASCII form
	:return: padded, start tokened, and stop tokened list of ASCII characters
	"""
	# ToDo:
	# add start token
	# add stop token
	# pad to correct max length
	padded = []
	return padded


def duration_to_id(durations: list, duration_dictionary: dict) -> list:
	"""
	Turn each duration in durations into its unique id
	:param durations: a list of durations of length length_of_longest_piece
	:param duration_dictionary: a dictionary mapping durations to integer ids
	:return: a list of integers of length length_of_longest_piece
	"""
	durations_unique_ids = []
	for duration_length in durations:
		durations_unique_ids.append(duration_dictionary[duration_length])

	return durations_unique_ids


def note_asciify(chords: list, ascii_dict: dict) -> list:
	"""
	Turns strings of note names and rests into ASCII characters
	:param chords: a list of lists of note names
	:param ascii_dict: a dictionary mapping note name to ASCII
	:return: a list of ascii characters
	"""
	ascii_piece = []
	for chord in chords:
		ascii_chord = []
		for pitch in chord:
			if pitch not in ascii_dict:
				ascii_dict[pitch] = chr(len(ascii_dict) + 33)

			ascii_chord.append(ascii_dict[pitch])
		ascii_chord.sort()  # Takes care of chord permutations
		ascii_piece.append("".join(ascii_chord))

	return ascii_piece


def note_idify(asciis: list, id_dict):
	"""
	Turns ascii characters into unique IDs
	:param asciis: a list of ASCII characters
	:param id_dict: a dictionary mapping ASCII characters to IDs
	:return:
	"""
	id_piece = []
	for ascii in asciis:
		if ascii not in id_dict:
			id_dict[ascii] = len(id_dict)

		id_piece.append(id_dict[ascii])

	return id_piece


def get_inputs_and_labels(data):
	"""
	Produces labels and inputs for given data
	:param data: tensor or array of size (batch_size, window_size)
	:return: two tensors of size (batch_size, window_size - 1)
	"""
	inputs = [data[i][:-1] for i in range(len(data))]
	labels = [data[i][1:] for i in range(len(data))]
	return tf.convert_to_tensor(inputs), tf.convert_to_tensor(labels)


def get_data(midi_folder, window_size: int):
	"""
	Does all the preprocessing
	:param midi_folder: a directory of all midi files
	:param window_size: window size for data
	:return: notes in pieces as an id array of shape [num_pieces, max_piece_length],
			durations in pieces as an id array of shape [num_pieces, max_piece_length],
			dictionary mapping id's to ASCII characters,
			dictionary mapping id's to durations,
			pad_token_id
	"""
	pitch_to_ascii = {START_TOKEN: chr(33),
	                  STOP_TOKEN: chr(34),
	                  PAD_TOKEN: chr(35),
	                  REST_TOKEN: chr(36)}
	ascii_to_id = {}
	corpus_note_id_batches = []
	corpus_durations_batches = []
	corpus_offsets_batches = []

	# list of files in midi_folder
	midi_files = os.listdir(midi_folder)[:50] # TODO - use this to only get some files if necessary

	for elm in midi_files:
		if re.match('[a-z0-9_]*\.mid[i]?', elm) is not None:
			m21_score = midi_to_m21(midi_folder + "/" + elm)  # this returns the m21 score object
			# this gets the list of notes/chords/rests, the list of durations, and the list of offsets
			score, durations, offsets = get_notes_and_durations(m21_score)
			pitch_score = note_pitchify(score)
			ascii_score = note_asciify(pitch_score, pitch_to_ascii)
			id_score = note_idify(ascii_score, ascii_to_id)

			# batches pieces
			piece_len = len(id_score)
			num_batches = piece_len // window_size
			ascii_score_batches = tf.reshape(id_score[:num_batches*window_size], [num_batches, -1])
			corpus_note_id_batches.extend(ascii_score_batches)

	corpus_note_id_batches = tf.convert_to_tensor(corpus_note_id_batches)
	note_id_inputs, note_id_labels = get_inputs_and_labels(corpus_note_id_batches)
	return note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii

#print(get_data(r"C:\Users\dhruv\PycharmProjects\CSCI1470\Liszt_Comprehension\data\Scarlatti", 250))

from music21 import *
import os
import tensorflow as tf
import re
import pickle

PAD_TOKEN = "**PAD**"
PAD_ID = 2
STOP_TOKEN = "**STOP**"
STOP_ID = 1
START_TOKEN = "**START**"
START_ID = 0
REST_TOKEN = "rest"
REST_ASCII = chr(33)
WINDOW_SIZE = 250


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


def incrementalize_offset(offset: list) -> list:
	"""
	Incrementalizes offsets
	:param offset: a list of offsets
	:return: incrementalized list of offsets
	"""
	offset = [0] + offset
	return [x-offset[i] for i, x in enumerate(offset[1:])]


def get_notes_and_durations(score) -> (list, list, list):
	"""
	Converts a music21 object to list of chords(notes, chords, rests) and list of durations
	:param score: a piece of music as a music21 object
	:return: a list of chords, a list of durations, and a list of offsets of length number_of_chords_in_piece
	"""
	durations = []
	offsets = []
	notes_and_rests = list(score.flat.notesAndRests)
	sounds = []
	no_rest_offsets = []
	out_durations = []
	out_offsets = []
	out_sounds = []
	actual_durations = []
	actual_offsets = []
	actual_sounds = []

	# This loop goes through everything in the score, adds notes, chords, and rests to the sounds list,
	# and durations to the durations list
	for sound in notes_and_rests:
		if not (isinstance(sound, note.Rest) and sound.duration.quarterLength > 4):
			sounds.append(sound)
			durations.append(sound.duration.quarterLength)
			offsets.append(sound.offset)
			if not isinstance(sound, note.Rest):
				no_rest_offsets.append(sound.offset)

	for i, sound in enumerate(sounds):
		if not (isinstance(sound, note.Rest) and sound.offset in no_rest_offsets):
			out_sounds.append(sounds[i])
			out_offsets.append(offsets[i])
			out_durations.append(durations[i])

	incremented_offsets = incrementalize_offset(out_offsets)

	for i, offset in enumerate(incremented_offsets):
		if not(isinstance(out_sounds[i], note.Rest) and offset == 0):
			actual_sounds.append(out_sounds[i])
			actual_offsets.append(out_offsets[i])
			actual_durations.append(out_durations[i])

	duration_offset_tuples = list(zip(actual_durations, incremented_offsets))
	return actual_sounds, duration_offset_tuples


def note_pitchify(score: list) -> list:
	"""
	Takes a sequence of music21 objects and converts it to a list of lists containing pitch names with octaves
	:param score: a list of music21 objects
	:return: a list of lists containing note names with octaves
	"""
	pitches = []
	for element in score:
		if isinstance(element, note.Note):
			# if element is a note
			pitch_thing = [element.nameWithOctave]

		elif isinstance(element, chord.Chord):
			# if element is a chord
			pitch_thing = [note_obj.nameWithOctave for note_obj in element.pitches]

		elif isinstance(element, note.Rest):
			# if element is a rest
			pitch_thing = [REST_TOKEN]

		else:
			# if element is magically something else
			pitch_thing = [REST_TOKEN]

		pitches.append(pitch_thing)
	return pitches


def duration_offset_idify(duration_offsets: list, duration_id_dict) -> list:
	"""
	Turn each duration_offset_tuple (dot) into its unique id
	:param duration_offsets: a list of dots
	:param duration_id_dict: a dictionary mapping dots to integer ids
	:return: a list of integers of length length_of_longest_piece
	"""
	duration_offset_id_piece = []
	for tuple in duration_offsets:
		if tuple not in duration_id_dict:
			duration_id_dict[tuple] = len(duration_id_dict)

		duration_offset_id_piece.append(duration_id_dict[tuple])

	return duration_offset_id_piece


def note_asciify(chords: list, ascii_dict: dict) -> list:
	"""
	Turns strings of note names and rests into ASCII characters
	:param chords: a list of lists of note names
	:param ascii_dict: a dictionary mapping note name to ASCII
	:return: a list of ASCII characters
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


def note_idify(asciis: list, id_dict) -> list:
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


def read_dicts_from_file(file_path):
	"""
	Reads everything from the db_dict file
	:return: note_id_input, note_id_labels, pitch_to_ascii and ascii_to_id and dot_to_id
	"""
	# for reading also binary mode is important
	dict_db_file = open(file_path, 'rb')
	dict_db = pickle.load(dict_db_file)
	return dict_db['corpus_note_id_batches'], dict_db['note_id_inputs'], dict_db['note_id_labels'], dict_db['ascii_to_id'], dict_db['pitch_to_ascii'], dict_db['dot_to_id'], dict_db['corpus_duration_offset_batches']


def write_dicts_to_file(file_path, corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches):
	"""
	Writes the dicts to a file
	"""
	# pickle code to write the dictionaries to a file
	dict_db = {}
	dict_db['corpus_note_id_batches'] = corpus_note_id_batches
	dict_db['pitch_to_ascii'] = pitch_to_ascii
	dict_db['ascii_to_id'] = ascii_to_id
	dict_db['note_id_inputs'] = note_id_inputs
	dict_db['note_id_labels'] = note_id_labels
	dict_db['dot_to_id'] = dot_to_id
	dict_db['corpus_duration_offset_batches'] = corpus_duration_offset_batches
	dict_db_file = open(file_path, 'wb')
	# source, destination
	pickle.dump(dict_db, dict_db_file)
	dict_db_file.close()


def split_train_and_test_data(inputs, labels):
	n = len(inputs)
	inputs_train = inputs[:int(n * 9/10)]
	inputs_test = inputs[int(n * 9/10):]
	labels_train = labels[:int(n * 9 / 10)]
	labels_test = labels[int(n * 9 / 10):]

	return inputs_train, labels_train, inputs_test,  labels_test


def get_data(file_path_to_save_data, midi_folder, window_size: int):
	"""
	Does all the preprocessing for NoteGen and the prepreprocessing for DurationGen
	:param file_path_to_save_data: where the processed data gets stored for easy retrieval
	:param midi_folder: a directory of all midi files
	:param window_size: window size for data
	:return: notes in pieces as an id array of shape [num_pieces, window_size],
			note inputs as an id array,
			note labels as an id array,
			dictionary mapping ASCII to unique id,
			dictionary mapping pitch to ASCII,
			dictionary mapping dot to unique id,
			durations in pieces as an id array of shape [num_pieces, window_size],
	"""
	# initialize the dicts
	pitch_to_ascii = {}
	ascii_to_id = {}
	dot_to_id = {START_TOKEN: START_ID, STOP_TOKEN: STOP_ID, PAD_TOKEN: PAD_ID}
	corpus_note_id_batches = []
	corpus_duration_offset_batches = []

	# add the necessary token stuff to the dict (although it is probably in it anyway)
	pitch_to_ascii[REST_TOKEN] = REST_ASCII

	# list of files in midi_folder
	midi_files = os.listdir(midi_folder)[:]  # use this to only get some files if necessary
	separator = "\\" if os.name == 'nt' else '/'

	# for each file in the directory
	for elm in midi_files:
		if re.match('.*\.mid[i]?', elm) is not None:
			# get music21 representation
			m21_score = midi_to_m21(midi_folder + separator + elm)  # this returns the m21 score object

			# this gets the list of notes/chords/rests, the list of durations, and the list of offsets
			score, duration_offset_tuples = get_notes_and_durations(m21_score)

			# converting the piece to an id reprentation
			id_duration_offsets = duration_offset_idify(duration_offset_tuples, dot_to_id)
			pitch_score = note_pitchify(score)
			ascii_score = note_asciify(pitch_score, pitch_to_ascii)
			id_score = note_idify(ascii_score, ascii_to_id)

			# batches pieces
			piece_len = len(id_score)
			num_batches = piece_len // window_size
			ascii_score_batches = tf.reshape(id_score[:num_batches*window_size], [num_batches, -1])
			duration_offset_batches = tf.reshape(id_duration_offsets[:num_batches*window_size], [num_batches, -1])
			corpus_note_id_batches.extend(ascii_score_batches)
			corpus_duration_offset_batches.extend(duration_offset_batches)

	corpus_note_id_batches = tf.convert_to_tensor(corpus_note_id_batches)
	note_id_inputs, note_id_labels = get_inputs_and_labels(corpus_note_id_batches)

	corpus_duration_offset_batches = tf.convert_to_tensor(corpus_duration_offset_batches)

	# function call to write the dictionaries to a file
	write_dicts_to_file(file_path_to_save_data, corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches)

	return corpus_note_id_batches, note_id_inputs, note_id_labels, ascii_to_id, pitch_to_ascii, dot_to_id, corpus_duration_offset_batches


def prep_duration_gen(corpus_note_id_batches, corpus_duration_offset_id_batches):
	"""
	Processes data for the DurationGen model
	:param corpus_note_id_batches: all note data - essentialy the language our data exisits in
	:param corpus_duration_offset_id_batches: all dot data - essentially the language we are translating to
	:return: id notes as inputs, id dots as labels
	"""
	corpus_note_id_batches = list(corpus_note_id_batches.numpy())
	corpus_duration_offset_id_batches = list(corpus_duration_offset_id_batches.numpy())

	for i in range(len(corpus_note_id_batches)):
		corpus_note_id_batches[i] = [START_ID] + list(corpus_note_id_batches[i]) + [STOP_ID]
		corpus_duration_offset_id_batches[i] = [START_ID] + list(corpus_duration_offset_id_batches[i]) + [STOP_ID]

	prepped_note_id_batches = tf.convert_to_tensor(corpus_note_id_batches)
	prepped_dot_id_batches = tf.convert_to_tensor(corpus_duration_offset_id_batches)

	return prepped_note_id_batches, prepped_dot_id_batches

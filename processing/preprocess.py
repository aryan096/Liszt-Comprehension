from music21 import *
from fractions import Fraction
import os
import random
import numpy as np
import tensorflow as tf
# ToDo: (general)
# import necessary packages
# figure out where to take care of chord permutations
#   some ideas: if pitches are ints, always sort each chord from lowest pitch to highest pitch before asciiing
#               check through each generated ascii and compare to all other asciis for permutations


PAD_TOKEN = "**PAD**"
STOP_TOKEN = "**STOP**"
START_TOKEN = "**START**"
REST_TOKEN = "rest"

def midi_to_m21(file_path: str):
	"""
	This function takes in a file_path to a midi file and returns the m21 score object
	for that file
	:param file_path: global file path for a single midi file
	:return: a music21 object
	"""
	file_path_split = file_path.split('/')
	print('parsing ' + file_path_split[len(file_path_split) - 1] + ' ...')
	m21_midi = converter.parse(file_path) # This will return a score object
	return m21_midi


def get_notes_and_durations(score) -> (list, list, list):
	"""
	Converts a music21 object to list of chords(notes, chords, rests) and list of durations
	:param piece: a piece of music as a music21 object
	:return: a list of chords, a list of durations, and a list of offsets of length number_of_chords_in_piece
	"""
	sounds = []
	durations = []
	offset = []
	chords = []
	# This loop goes through everything in the score, adds notes, chords, and
	# rests to the sounds list, and durations to the durations list
	for sound in score.flat.elements:
		# add durations
		durations.append(sound.duration.quarterLength)
		offset.append(sound.offset)

	try: # file has instrument parts
		sounds = instrument.partitionByInstrument(score).parts[0].recurse()
	except: # file has notes in a flat structure
		sounds = score.flat.notesAndRests

	return sounds, durations, offset


def incrementalize_offset(offset: list) -> list:
	offset = [0] + offset
	return [x-offset[i] for i, x in enumerate(offset[1:])]


def accumulate_offset(incremental_offset: list) -> list:
	out = [incremental_offset[0]]
	for i in range(len(incremental_offset) - 1):
		out.append(out[i]+incremental_offset[i+1])
	return out

def ammend_ascii_pitch_dict(ascii_dict, pitches):
	for note in pitches:
		if note not in ascii_dict:
			ascii_dict[pitch] = chr(len(ascii_dict) + 33)

def construct_vocab(ascii_corpus: list):
	ascii_corpus



def amend_pitch_dictionary(pitch_dict: dict, pitch_string_dict: dict, pitch: float) -> (dict, dict):
	"""
	Given the current dictionary and pitches, update it
	:return: dictionary mapping pitch to a unique integer identifier
	"""

	# for each element in pitches, make a unique key mapped to it


	for thing in pitches:

		unique_id = ""

		curr = random.randint(100, 900)
		while curr in pitch_dict:
			curr = random.randint(100, 900)

		if isinstance(thing, note.Note):
			# if thing is a note
			unique_id = str(thing.pitch)

		elif isinstance(thing, chord.Chord):
			# if thing is a chord
			chord_pitches = thing.pitches
			unique_id = '.'.join(str(pitch) for pitch in chord_pitches)

		elif isinstance(thing, note.Rest):
			# if thing is a rest
			unique_id = 'rest'

		pitch_dict[unique_id] = curr
		pitch_string_dict[str(thing)] = unique_id

	return pitch_dict, pitch_string_dict


def pitchify(score: list):
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


def pitches_to_id(pitches: list, pitch_dictionary: dict, pitch_string_dict: dict) -> list:
	"""
	Turn each ASCII character in ascii_chords into its unique id
	:param ascii_chords: a list of ASCII characters of length length_of_longest_piece
	:param dictionary: a dictionary mapping integer ids to ASCII ids from generate_ascii_dictionary
	:return: a list of integers of length length_of_longest_piece
	"""
	pitches_unique_ids = []

	for pitch in pitches:
		pitches_unique_ids.append(pitch_dictionary[pitch_string_dict[str(pitch)]])

	return pitches_unique_ids


def duration_to_id(durations: list, duration_dictionary: dict) -> list:
	"""
	Turn each duration in durations into its unique id
	:param durations: a list of durations of length length_of_longest_piece
	:param duration_dictionary: a dictionary mapping durations to integer ids
	:return: a list of integers of length length_of_longest_piece
	"""

	durations_unique_ids = []

	for duration in durations:
		durations_unique_ids.append(duration_dictionary[duration])

	return durations_unique_ids


def asciify(chords: list, ascii_dict):
	ascii_piece = []
	for chord in chords:
		ascii_chord = []
		for pitch in chord:
			if pitch not in ascii_dict:
				ascii_dict[pitch] = chr(len(ascii_dict) + 33)

			ascii_chord.append(ascii_dict[pitch])
		ascii_piece.append("".join(ascii_chord))

	return ascii_piece


def idfy(asciis: list, id_dict):
	id_piece = []
	for ascii in asciis:
		if ascii not in id_dict:
			id_dict[ascii] = len(id_dict)

		id_piece.append(id_dict[ascii])

	return id_piece




def get_data(midi_folder, batch_size):
	"""
	Herbert
	Does all the preprocessing
	:param midi_folder: a directory of all midi files
	:return: notes in pieces as an id array of shape [num_pieces, max_piece_length],
			durations in pieces as an id array of shape [num_pieces, max_piece_length],
			dictionary mapping id's to ASCII characters,
			dictionary mapping id's to durations,
			pad_token_id
	"""

	# pad_token_id = 0 # this is a placeholder
	# duration_dictionary = {}
	# pieces = []
	# durations = []
	# max_length = 0
	# pitch_dictionary = {}
	# pitch_string_dict = {}
	# ascii_to_id_dict = {}
	#

	pitch_to_ascii = {START_TOKEN: chr(33),
	                  STOP_TOKEN: chr(34),
	                  PAD_TOKEN: chr(35),
	                  REST_TOKEN: chr(36)}
	ascii_to_id = {}
	corpus_ascii_batches = []
	corpus_durations_batches = []
	corpus_offsets_batches = []


	# list of files in midi_folder
	midi_files = os.listdir(midi_folder)[105:106] # TODO - use this to only get some files if necessary

	for elm in midi_files:
		m21_score = midi_to_m21(midi_folder + "\\" + elm) # this returns the m21 score object
		# this gets the list of notes,chords, rests, and the list of durations
		score, durations, offsets = get_notes_and_durations(m21_score)
		pitch_score = pitchify(score)
		ascii_score = asciify(pitch_score, pitch_to_ascii)
		id_score = idfy(ascii_score, ascii_to_id)


		piece_len = len(id_score)
		num_batches = piece_len // batch_size
		ascii_score_batches = tf.reshape(id_score[:num_batches*batch_size], [num_batches, -1])

		# # this should get a dict of unique_ids mapped to durations
		# duration_dictionary = amend_duration_dictionary(duration_dictionary, durations)
		# durations_unique_ids = duration_to_id(durations, duration_dictionary)
		#
		# # this should get a dict of unique_ids mapped to a pitch
		# pitch_dictionary, pitch_string_dict = amend_pitch_dictionary(pitch_dictionary, pitch_string_dict, score)
		# pitches_unique_ids = pitches_to_id(score, pitch_dictionary, pitch_string_dict)
		corpus_ascii_batches.extend(ascii_score_batches)
	#return pieces, durations, pitch_dictionary, duration_dictionary, pad_token_id
	return corpus_ascii_batches, ascii_to_id

# IDs allocation
# 1000 - 100000: reserved for durations
# 100 - 900: reserved for pitches
print(get_data(r"C:\Users\dhruv\PycharmProjects\CSCI1470\Liszt_Comprehension\data\Scarlatti", 250))

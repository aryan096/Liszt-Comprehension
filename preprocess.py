def midi_to_m21(file_path: str):
	"""Converts midi file into music 21 thing"""
	# open file
	# converter.parse(file_path)
	pass


def strip_durations(piece):
	"""Converts m21 thing to list of chords(notes, chords, rests) and list of durations"""
	chords = [] #pitches
	durations = []
	return chords, durations


def chord_to_ascii(chords: list) -> list:
	ascii_chords = []
	return ascii_chords


def ascii_to_id(ascii_chords: list):
	# check permutations
	id_ascii = {} #maps id to ascii
	id_chords = []
	return id_ascii, id_chords


def pad_and_token(max_length: int, stripped_piece: list) -> list:
	# add start token
	# add stop token
	# pad to correct max length
	pass


def get_data(midi_folder):
	pieces = []
	durations = []
	max_length = 0
	for elm in midi_folder:
		midi_to_m21(midi_folder)
		strip_durations()
		# get length
		chord_to_ascii()
		ascii_to_id()
		pad_and_token()
		# take final padded chords and durations
	# pieces, durations, id->ascii dict
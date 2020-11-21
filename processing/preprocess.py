# ToDo: (general)
# import necessary packages
# figure out where to take care of chord permutations
#   some ideas: if pitches are ints, always sort each chord from lowest pitch to highest pitch before asciiing
#               check through each generated ascii and compare to all other asciis for permutations


PAD_TOKEN = "**PAD**"
STOP_TOKEN = "**STOP**"
START_TOKEN = "**START**"


def midi_to_m21(file_path: str):
	"""
	Converts midi file into music21 objects
	:param file_path: global file path for a single midi file
	:return: a music21 object
	"""
	# ToDo:
	# open file
	# converter.parse(file_path)
	thing = "music 21 object" # this is a placeholder
	return thing


def strip_durations(piece) -> (list, list):
	"""
	Converts a music21 object to list of chords(notes, chords, rests) and list of durations
	:param piece: a piece of music as a music21 object
	:return: a list of chords and a list of durations of length number_of_chords_in_piece
	"""
	chords = []
	durations = []
	# ToDo:
	# add pitches from each chord/rest in piece to chords
	# add durations of each chord/rest in piece to durations
	return chords, durations


def generate_pitch_dictionary() -> dict:
	"""
	Give each pitch on a piano, rest, start token, stop token, and pad token a unique ASCII id
	:return: dictionary mapping pitch to ASCII character
	"""
	pitch_to_ascii = {}
	# ToDo:
	# give each possible pitch, rest, pad token, start token, stop token one of 92 ascii characters
	return pitch_to_ascii


def amend_duration_dictionary(duration_dictionary: dict, durations: list):
	"""
	Give each duration encountered a unique integer id
	:param durations: a list of all durations encountered in preprocessing
	:return: None
	"""
	id_to_duration = {}
	# ToDo:
	# give each duration an id
	# make sure the duration ids are not the ids for pad, start, and stop. We could just make them very large numbers
	# if duration not in duration_dictionary.values(), add key of duration and value of id
	return None


def chord_to_ascii(chords: list, dictionary: dict) -> list:
	"""
	Turn each chord in chords into a unique ASCII string
	:param chords: a list of pitches of length number_of_chords_in_piece
	:param dictionary: a dictionary mapping a pitch to an ASCII character from generate_pitch_dictionary
	:return: a list of ASCII characters of length number_of_chords_in_piece
	"""
	ascii_chords = []
	# ToDo:
	# turn each chord into a unique ascii string
	return ascii_chords


def generate_ascii_dictionary() -> dict:
	"""
	Give each ASCII string on a unique integer id
	:return: dictionary mapping id to ASCII string
	"""
	id_to_ascii = {}
	# ToDo:
	# give each possible chord, permutation invariant, a unique integer id
	return id_to_ascii


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


def ascii_to_id(ascii_chords: list, dictionary: dict) -> list:
	"""
	Turn each ASCII character in ascii_chords into its unique id
	:param ascii_chords: a list of ASCII characters of length length_of_longest_piece
	:param dictionary: a dictionary mapping integer ids to ASCII ids from generate_ascii_dictionary
	:return: a list of integers of length length_of_longest_piece
	"""
	id_chords = []
	# ToDo:
	# turn each ASCII string into its unique ID
	return id_chords


def duration_to_id(durations: list, duration_dictionary: dict, ascii_dictionary) -> list:
	"""
	Turn each duration in durations into its unique id
	:param durations: a list of durations of length length_of_longest_piece
	:param duration_dictionary: a dictionary mapping durations to integer ids
	:param ascii_dictionary: a dictionary mapping ascii characters to integer ids
	:return: a list of integers of length length_of_longest_piece
	"""
	id_durations = []
	# ToDo:
	# turn each duration and ASCII pad, start, and stop string into its unique ID
	return id_durations


def get_data(midi_folder):
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
	# ToDo:
	# use all functions above
	pad_token_id = 0 # this is a placeholder
	duration_dictionary = {}
	pieces = []
	durations = []
	max_length = 0
	pitch_dictionary = generate_pitch_dictionary()
	ascii_to_id_dict = generate_ascii_dictionary()
	for elm in midi_folder:
		m21_piece = midi_to_m21(midi_folder)
		chords, durations = strip_durations(m21_piece)
		if len(durations) > max_length:
			max_length = len(durations)
		amend_duration_dictionary(duration_dictionary, durations)
		ascii_chords = chord_to_ascii(chords, pitch_dictionary)
		chord_to_ascii()
		ascii_to_id()
		pad_and_token()
		# take final padded chords and durations
	return pieces, durations, ascii_to_id_dict, duration_dictionary, pad_token_id
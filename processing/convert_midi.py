import mido
import os
import music21
import shutil

def convert(midi_folder, out_folder):
    midi_files = os.listdir(midi_folder)[:1]
    for elm in midi_files:
        m = mido.MidiFile(midi_folder + "\\" + elm)
        print(m.tracks)
        m = mido.merge_tracks(m.tracks)
        print(m)
        new_piece = mido.MidiFile(type=0)
        new_piece.tracks.append(m)
        print(new_piece.tracks)

        new_piece.save(out_folder + "\\" + elm)

#convert(r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\Beethoven",
#        r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\converted_pieces")

def midi_to_m21(file_path: str):
	"""
	This function takes in a file_path to a midi file and returns the m21 score object
	for that file
	:param file_path: global file path for a single midi file
	:return: a music21 object
	"""
	file_path_split = file_path.split('/')
	print('parsing ' + file_path_split[len(file_path_split) - 1] + ' ...')
	m21_midi = music21.converter.parse(file_path)  # This will return a score object
	return m21_midi


def move_one_trackers(midi_folder, target_folder):
    composer_folders = os.listdir(midi_folder)

    for composer in composer_folders:
        midi_files = os.listdir(midi_folder + '\\' + composer)
        counter = 0
        for elm in midi_files:
            piece = midi_to_m21(midi_folder + '\\' + composer + '\\' + elm)
            if len(piece.elements) == 1:
                print("yes")
                counter += 1
                shutil.copy2(midi_folder + '\\' + composer + '\\' + elm, target_folder + '\\' + composer + '\\' + elm)
        print(composer + ": {}".format(counter))

move_one_trackers(r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data",
                  r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\OneTrackData")


def move_one_trackers_mido(midi_folder, target_folder):
    # composer_folders = os.listdir(midi_folder)
    #
    # for composer in composer_folders:
    composer = "Beethoven"
    midi_files = os.listdir(midi_folder + '\\' + composer)
    counter = 0
    for elm in midi_files:
        print("parsing {}".format(composer + '\\' + elm))
        piece = mido.MidiFile(midi_folder + '\\' + composer + '\\' + elm)
        if len(piece.tracks) == 1:
            print("yes")
            counter += 1
            #shutil.copy2(midi_folder + '\\' + composer + '\\' + elm, target_folder + '\\' + composer + '\\' + elm)
    print(composer + ": {}".format(counter))

#move_one_trackers_mido(r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data",
#                  r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\OneTrackData")



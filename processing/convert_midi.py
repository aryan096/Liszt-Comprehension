import os
import music21
import shutil
import re


# This is a miscellaneous file we used to process midi files in various ways

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
        if composer == "Mozart":
            midi_files = os.listdir(midi_folder + '/' + composer)
            counter = 0
            for elm in midi_files:
                if re.match('.*\.mid[i]?', elm) is not None:  # TODO - fix if wrong
                    piece = midi_to_m21(midi_folder + '/' + composer + '/' + elm)
                    if len(piece.elements) == 1:
                        print("yes")
                        counter += 1
                        shutil.copy2(midi_folder + '/' + composer + '/' + elm, target_folder + '/' + composer + '/' + elm)
            print(composer + ": {}".format(counter))


def transpose(midi_folder):
    """
    This function transposes all of Mozart's pieces
    :param midi_folder: folder of midis to transpose
    :return: None
    """
    composer_folders = os.listdir(midi_folder)

    for composer in composer_folders:
        if composer == "Mozart":
            if re.match('[\._]', composer) is None:  # TODO - fix if wrong
                midi_files = os.listdir(midi_folder + '/' + composer)
                for elm in midi_files:
                    if re.match('.*\.mid[i]?', elm) is not None:  # TODO - fix if wrong
                        piece = midi_to_m21(midi_folder + '/' + composer + '/' + elm)
                        for i in range(1, 4):
                            new_piece = piece.transpose(i)
                            new_file_name = "transposed_" + str(i) + "_" + elm + "i"
                            new_piece.write("midi", new_file_name)
                            current_directory = os.getcwd()
                            separator = "\\" if os.name == 'nt' else '/'
                            target_directory = midi_folder + separator + composer + separator + new_file_name
                            shutil.move(current_directory + separator + new_file_name, target_directory)
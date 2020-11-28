import mido
import os

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

convert(r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\Beethoven",
        r"C:\Users\dhruv\PycharmProjects\Liszt-Comprehension\data\converted_pieces")
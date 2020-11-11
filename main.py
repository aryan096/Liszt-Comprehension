import py_midicsv as pm
import csv

# Load the MIDI file and parse it into CSV format
csv_string = pm.midi_to_csv("bohemian.mid")

with open('bohemian_converted.csv', mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    csv_writer.writerow(csv_string)
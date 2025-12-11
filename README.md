# Liszt-Comprehension
Made by Dhruv Bhatia, Noah Medina, Herbert Traub, and Aryan Srivastava.

## Installation Instructions 

1. Clone the repo and run create_env. Alternatively, set up a virtual environment and install the requirements from requirements.txt.

2. Just run `python assignment.py`! The program should prompt you for some inputs to determine the kind of learning and generation you want. 

3. If you generated music, it will be saved in the Generated Pieces folder under a file name of the current date and time.

4. Have fun! 

### An explanation of the repo structure 

Here is a map of what directory holds what! 

1. processing - this directory has the files we use for preprocessing (preprocess.py) and postprocessing (generate_midi.py). 
convert_midi has some helper functions we used during programming and testing. 

2. Models - this directory has the models we use to train (both note generation and duration generation). The files we use are 
duration_gen.py, note_gen_functional.py, and transformer_funcs.py. 

3. Generated Pieces - all generated pieces are stored here 

4. data - All the midi files sorted by composers.

5. AllOneTrack - all the midi files that only have one track!

6. OneTrackData - one track midi files sorted by composers. 

7. Trained Weights - Stored trained weights so you don't have to train everytime you want to make music!

8. Dict Data - Stored data from preprocessing to make generation based on already trained models more efficient.

### Explanation video and samples

[https://youtu.be/TBM_w61D3gk?si=fU_i_nk93mcGJuYW](url)

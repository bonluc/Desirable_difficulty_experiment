# 1. Download the repo 
Download the repository using the zip file or the following git commands in a terminal: 
* git clone https://github.com/bonluc/Desirable_difficulty_experiment.git

# 2. Create a Virtual Environment

Create and activate a virtual environment.
**On Windows use**:
* python -m venv name_venv
* name_venv\Scripts\activate

**On macOS / Linux**:
* python3 -m venv name_venv
* source name_venv/bin/activate

# 3. Install required packages
After having activating the environment, make sure you have pip updated:

* python -m pip install --upgrade pip
  
Then install all required dependencies:

* pip install pandas psychopy screeninfo

# 4. Run the program
Make sure you have the venv activated and are currently in directory cloned from github then use in the terminal:
* python testing_import.py

If the program is running the rest should be intuitive :D

#from psychopy import prefs
#prefs.hardware['audioLib'] = ['sounddevice']
from psychopy import visual, event, core, sound
import screeninfo
import os
import random
import pandas as pd
#import sounddevice as sd

# === INITIALIZATION FUNCTIONS ===
def initialize_screen():
    """Initialize PsychoPy window."""
    screen = screeninfo.get_monitors()[0]
    screen_width, screen_height = screen.width, screen.height

    win = visual.Window(
        size=(int(screen_width * 0.99), int(screen_height * 0.95)),
        fullscr=False,
        allowGUI=True,
        color="black",
        units="pix"
    )
    win.winHandle.set_fullscreen(False)
    win.winHandle.maximize()
    win.flip()
    return win


def initialize_beep():
    """Return a pleasant beep sound routed to the active default output device."""

    # Create the beep sound (pleasant C tone)
    beep = sound.Sound(value='C', secs=0.3, stereo=True, sampleRate=44100)
    return beep

def create_main_folder():
    """Ensure results folder exists."""
    os.makedirs("participants_results", exist_ok=True)

def create_participant_folder():
    """
    Creates a new folder for the next participant inside 'participants_results'.
    Returns the folder path and participant number.
    """
    participant_num = 1
    # Find the next available participant number
    while os.path.exists(f"participants_results/participant_{participant_num}"):
        participant_num += 1

    participant_folder = f"participants_results/participant_{participant_num}"
    os.makedirs(participant_folder)
    return participant_folder, participant_num

def get_word_sets(number_of_words=5, number_of_list=6):
    """Generate two unique word lists (round 1 & round 2)."""
    #random.seed(42)
    # Living room
    list1 = load_words('wordlist_gpt_nonsense.txt')

    # Draw first 15 words (5 from each list)
    random_sampling = random.sample(list1, number_of_words*number_of_list)
    random_list1 = random_sampling[0:number_of_words]
    random_list2 = random_sampling[number_of_words:2*number_of_words]
    random_list3 = random_sampling[2*number_of_words:3*number_of_words]
    random_list4 = random_sampling[3*number_of_words:4*number_of_words]
    random_list5 = random_sampling[4*number_of_words:5*number_of_words]
    random_list6 = random_sampling[5*number_of_words:6*number_of_words]
                                   

    # Remove the seed
    #random.seed()
    
    # Shuffle the internal order of both lists
    random.shuffle(random_list1)
    random.shuffle(random_list2)
    random.shuffle(random_list3)
    random.shuffle(random_list4)
    random.shuffle(random_list5)
    random.shuffle(random_list6)
    return random_list1, random_list2, random_list3, random_list4, random_list5, random_list6

def load_words(filename, both_words=False):
    """
    Load words from a text file.
    
    Each line in the file can contain either one word or two words separated by a space.
    If both_words=True → load the entire line (both words).
    If both_words=False → only load the first word on each line.

    All words are converted to lowercase, and blank lines are ignored.
    """
    words = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()
            if not line:
                continue
            if both_words:
                words.append(line)
            else:
                words.append(line.split()[0])  # take only the first word
    return words

def get_instructions(participant_num):
    """Order conditions based on participant number (counterbalancing)."""
    if participant_num % 2 == 0:
        return {"mirrored": "Write mirrored the word",
                "normal": "Write normally the word"}
    else:
        return {"normal": "Write normally the word",
                "mirrored": "Write mirrored the word"}

# === MAIN TASK FUNCTIONS ===

def begin_practice(win):
    start_text = visual.TextStim(win, text="Press SPACE to start practice before experiment.",
                                 color="white", height=40)
    start_text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])


def run_test(win, beep, condition_key, words, timings, instructions):
    """Run a short practice phase (no logging)."""
    time_per_word, time_per_break, time_for_filler_task, time_for_recall = timings
    condition_text = instructions[condition_key]

    # Bottom hint text
    hint_text = visual.TextStim(
        win,
        text="If you are done writing the word, press SPACE to skip to the next word.",
        color="white",
        height=25,
        pos=(0, -300)
    )

    for word in words:
        event.clearEvents(eventType='keyboard')
        win.flip()

        # Display instruction, word, and hint
        instr_text = visual.TextStim(win, text=condition_text, color="white", height=40, pos=(0, 80))
        word_text = visual.TextStim(win, text=word.lower(), color="white", height=100, bold=True, pos=(0, -40))

        instr_text.draw()
        word_text.draw()
        hint_text.draw()
        win.flip()

        # Timer for this word
        trial_timer = core.Clock()
        skipped = False

        # Wait for SPACE or timeout
        while trial_timer.getTime() < time_per_word:
            keys = event.getKeys(keyList=["space", "escape"])
            if "escape" in keys:
                win.close()
                core.quit()
            if "space" in keys:
                skipped = True
                break
            core.wait(0.05)

        # Beep plays only if the participant did NOT skip
        if not skipped:
            beep.play()
            core.wait(0.4)

        # Clear accidental keypresses before next word
        event.clearEvents(eventType='keyboard')

        # Show fixation cross
        fixation = visual.TextStim(win, text="+", color="white", height=60)
        fixation.draw()
        win.flip()
        core.wait(time_per_break)

    # Clear after practice
    win.flip()

def begin_experiment(win, round):
    event.clearEvents(eventType='keyboard')
    start_text = visual.TextStim(win, text=f"Press SPACE to start experiment round {round}.",
                                 color="white", height=40)
    start_text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])


def run_experiment(win, beep, condition_key, words, timings, instructions):
    """
    Run one full experimental round and return trial logs.
    Logs: word, condition, skipped (bool), and time_spent (seconds).
    Participant can press SPACE to skip early (no beep).
    If they wait for the full time_per_word, a beep plays automatically.
    """
    event.clearEvents(eventType='keyboard')
    time_per_word, time_per_break, time_for_filler_task, time_for_recall_test = timings
    results = []
    condition_text = instructions[condition_key]

    # Persistent bottom hint text
    hint_text = visual.TextStim(
        win,
        text="If you are done writing the word, press SPACE to skip to the next word.",
        color="white",
        height=25,
        pos=(0, -300)  # near the bottom of the screen
    )

    for word in words:
        event.clearEvents(eventType='keyboard')
        win.flip()

        # Display instruction + word + hint
        instr_text = visual.TextStim(win, text=condition_text, color="white", height=40, pos=(0, 80))
        word_text = visual.TextStim(win, text=word.lower(), color="white", height=100, bold=True, pos=(0, -40))

        instr_text.draw()
        word_text.draw()
        hint_text.draw()
        win.flip()

        # Timer for current word
        trial_timer = core.Clock()
        skipped = False

        # Wait for SPACE or timeout
        while trial_timer.getTime() < time_per_word:
            keys = event.getKeys(keyList=["space", "escape"])
            if "escape" in keys:
                win.close()
                core.quit()
            if "space" in keys:
                skipped = True
                break
            core.wait(0.05)

        # Record the time spent
        time_spent = trial_timer.getTime()

        # Beep plays ONLY if participant waited full duration
        if not skipped:
            beep.play()
            core.wait(0.4)

        # Clear extra keypresses
        event.clearEvents(eventType='keyboard')

        # Fixation cross before next word
        fixation = visual.TextStim(win, text="+", color="white", height=60)
        fixation.draw()
        win.flip()

        # Log trial
        results.append({
            "word": word,
            "condition": condition_key,
            "skipped": skipped,
            "time_spent": round(time_spent, 3)
        })

        core.wait(time_per_break)

    # Clear after all trials
    win.flip()

    return results


def run_filler_task(win, time_for_filler_task):
    """
    Run the filler task where the participant presses SPACE only when a circle appears.
    A live score is shown at the top (only number updates). +1 for correct, -1 for incorrect.
    """
    # --- Instructions ---
    filler_instr = visual.TextStim(
        win,
        text=("TASK:\n\nPress SPACE only when you see a CIRCLE!\n"
              "Ignore squares and triangles.\n\n(Press SPACE to start)"),
        color="white", height=40, wrapWidth=1200
    )

    filler_instr.draw()
    win.flip()
    event.waitKeys(keyList=["space"])

    # --- Shapes ---
    circle = visual.Circle(win, radius=60, fillColor="white", lineColor="white", pos=(0, 0))
    square = visual.Rect(win, width=120, height=120, fillColor="white", lineColor="white", pos=(0, 0))
    triangle = visual.ShapeStim(win, vertices=[(-60, -60), (60, -60), (0, 60)],
                                fillColor="white", lineColor="white", pos=(0, 0))
    shapes = [("circle", circle), ("square", square), ("triangle", triangle)]

    # --- Initialize timer and score ---
    timer = core.Clock()
    score = 0

    # Static “Score:” label (stays fixed)
    score_label = visual.TextStim(win, text="Score:", color="white", height=30, pos=(-100, 330))
    score_value = visual.TextStim(win, text=str(score), color="white", height=30, pos=(50, 330))

    # --- Task Loop ---
    while timer.getTime() < time_for_filler_task:
        # brief pause before next shape
        win.flip()
        core.wait(random.uniform(0.01, 0.03))

        # select random shape and randomize its position (but keep clear of top area)
        shape_name, shape = random.choice(shapes)
        shape.pos = (random.randint(-600, 600), random.randint(-250, 150))  # avoids top area

        # draw shape + score at the same time
        score_label.draw()
        score_value.draw()
        shape.draw()
        win.flip()

        # wait for response
        response_timer = core.Clock()
        response_made = False
        while response_timer.getTime() < 0.4:
            keys = event.getKeys(keyList=["space", "escape"])
            if "escape" in keys:
                win.close()
                core.quit()
            if "space" in keys:
                response_made = True
                break

        # evaluate response
        if response_made:
            if shape_name == "circle":
                score += 1  # correct
            else:
                score -= 1  # incorrect

        # update score display (just the number)
        score_value.text = str(score)

        # redraw only score after each shape
        score_label.draw()
        score_value.draw()
        win.flip()
        core.wait(0.05)

    # --- End filler ---
    end_text = visual.TextStim(
        win, text=f"Task complete!\nFinal Score: {score}", color="white", height=40
    )
    end_text.draw()
    win.flip()
    core.wait(3)


def recall_phase(win, beep, time_for_recall_test):
    """
    Run the recall phase where participants recall as many words as possible.
    Displays a live countdown timer.
    """

    # --- Prompt to start recall ---
    recall_text = visual.TextStim(
        win,
        text=(
            "Have pen and paper ready to write down as many words as you can remember.\n\n"
            "When ready press SPACE to begin the RECALL TEST."
        ),
        color="white",
        height=40,
        wrapWidth=1200
    )
    recall_text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
    core.wait(0.2)
    event.clearEvents(eventType='keyboard')

    # --- Recall message and timer setup ---
    recall_message = visual.TextStim(
        win, text="Write down as many words as you can remember!", color="white", height=50, pos=(0, 0)
    )
    timer_text = visual.TextStim(
        win, text="", color="white", height=30, pos=(0, 320)  # top center
    )

    # --- Start recall timer ---
    timer = core.Clock()

    while timer.getTime() < time_for_recall_test:
        # Calculate remaining time
        remaining = int(time_for_recall_test - timer.getTime())
        minutes, seconds = divmod(remaining, 60)
        timer_display = f"Time left: {minutes:02d}:{seconds:02d}"

        # Update timer text
        timer_text.text = timer_display

        # Draw both elements
        recall_message.draw()
        timer_text.draw()
        win.flip()

        # Check for ESCAPE to exit early
        keys = event.getKeys(keyList=["escape"])
        if "escape" in keys:
            win.close()
            core.quit()

        core.wait(0.5)  # update roughly every half second

    # --- End recall with beep ---
    beep.play()
    core.wait(1)

    # --- Clear the screen after recall ---
    win.flip()


# === RUN EXPERIMENT ===

def main():
    
    # Create the window
    win = initialize_screen()
    
    # Create the beep tone
    beep = initialize_beep()

    # Create main folder
    create_main_folder()
    
    # Create folder and participant folder
    participant_folder, participant_num = create_participant_folder()


    # Instructions in an order depending on 
    instructions = get_instructions(participant_num)

    # Timings (seconds)
    time_per_word = 28 # 28 
    time_per_break = 1.5
    time_for_filler_task = 3 #60
    time_for_recall = 10 #60
    timings = (time_per_word, time_per_break, time_for_filler_task, time_for_recall)
    #timings = (min(time_per_word, 5), min(time_per_break,1), min(time_for_filler_task,10), min(time_for_recall,10))

    # Shorter timings for practice
    #timings_test = (min(time_per_word, 5), min(time_per_break, 1.0), min(time_for_filler_task, 10), min(time_for_recall, 10))
    timings_test = (time_per_word, time_per_break, time_for_filler_task, time_for_recall)
    
    begin_practice(win)
    # Practice (use a tiny clean list)
    practice_words = ['sam']
    for condition in instructions.keys():
        run_test(win, beep, condition, practice_words, timings, instructions)
        #run_filler_task(win, time_for_filler_task=30)
        #recall_phase(win, beep, time_for_recall=10)

    # Word sets for the two rounds
    words_round1, words_round2, words_round3, words_round4, words_round5, words_round6 = get_word_sets()
    
    # Run the two real rounds (use list() for indexing)
    all_results = []
    conditions = list(instructions.keys())
    round = 1
    begin_experiment(win, round)
    # 1st Round
    all_results = run_experiment(win, beep, conditions[0], words_round1, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)

    round +=1
    begin_experiment(win, round)
    # 2nd Round
    all_results = run_experiment(win, beep, conditions[1], words_round2, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)

    round +=1
    begin_experiment(win, round)
    # 3rd Round
    all_results = run_experiment(win, beep, conditions[0], words_round3, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)
    round += 1
    begin_experiment(win, round)
    # 4th Round
    all_results = run_experiment(win, beep, conditions[1], words_round4, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)

    round +=1
    begin_experiment(win, round)
    # 5th Round
    all_results = run_experiment(win, beep, conditions[0], words_round5, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)

    round += 1
    begin_experiment(win, round)
    # 6th Round
    all_results = run_experiment(win, beep, conditions[1], words_round6, timings, instructions)
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(participant_folder, f"round_{round}.csv"), index=False)
    run_filler_task(win, time_for_filler_task)
    recall_phase(win, beep, time_for_recall)

    # End screen
    end_text = visual.TextStim(win, text="The experiment is over.\n\nThank you for participating!",
                               color="white", height=40)
    end_text.draw()
    win.flip()
    event.waitKeys(keyList=["escape"])
    win.close()
    core.quit()


if __name__ == "__main__":
    main()
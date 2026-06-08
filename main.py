import string
from psychopy import visual, core, event

# --- 1. Initialize Window & Mouse ---
win = visual.Window(size=(1024, 768), color='black', units='pix')
mouse = event.Mouse(visible=True, win=win) 

fixation = visual.TextStim(win, text='+', color='white', height=40)
prime_text = visual.TextStim(win, text='', color='white', height=50)

# --- 2. Trial Parameters & Experimental Conditions ---
grid_size = 12
spacing = 35 

start_x = -(grid_size * spacing) / 2 + (spacing / 2)
start_y = (grid_size * spacing) / 2 - (spacing / 2)

# 10 Trials manually ordered: Primed -> Distracted -> Blank loop
trials = [
    # Loop 1
    ("Primed", "DOCTOR", "NURSE"),
    ("Distracted", "ANGER", "SNOW"),
    ("Blank", "", "APPLE"),
    
    # Loop 2
    ("Primed", "BREAD", "BUTTER"),
    ("Distracted", "HOUSE", "FOREST"),
    ("Blank", "", "CHAIR"),
    
#    # Loop 3
#    ("Primed", "KING", "QUEEN"),
#    ("Distracted", "CHAIR", "SLEEP"),
#    ("Blank", "XXXXXX", "TRAIN"),
    
#    # Leftover 4th Primer
#    ("Primed", "STORM", "RAIN")
]

# Three lists to separate our data for the final comparison
primed_rts = []
blank_rts = []
distracted_rts = []

quit_experiment = False 

try:
    # --- INSTRUCTION SCREEN LOGIC ---
    instruction_text = visual.TextStim(win, text=(
        "Welcome to the Word Search Experiment!\n\n"
        "You will see a series of letter grids. In each grid, a target word is hidden.\n\n"
        "Before each grid, you will see a cue:\n"
        "1. A HELPFUL word related to the target.\n"
        "2. A DISTRACTION word to trick you.\n"
        "3. A BLANK screen with no hint.\n\n"
        "Your task is to find and CLICK the hidden target word as FAST as possible.\n\n"
        "Press the SPACEBAR when you are ready to start."
    ), color='white', height=24, wrapWidth=800)
    
    instruction_text.draw()
    win.flip()
    
    # Wait indefinitely until the participant presses the spacebar
    event.waitKeys(keyList=['space'])
    # --------------------------------

    # --- 3. The Main Trial Loop ---
    for condition, cue, target in trials:
        if quit_experiment:
            break
            
        # A. Show Fixation (500ms)
        fixation.draw()
        win.flip()
        core.wait(1)

        # B. Show Cue Word (200ms)
        # --> NEW LOGIC: Check if it is a distraction trial and update the text
        if condition == "Distracted":
            prime_text.text = f"DISTRACTION: {cue}"
        else:
            prime_text.text = cue
            
        prime_text.draw()
        win.flip()
        core.wait(1)
        
        # C. Generate the Grid Logic 
        import random 
        t_row = random.randint(0, grid_size - 1)
        t_col = random.randint(0, grid_size - len(target))
        
        all_letter_stims = [] 
        target_stims = []     

        # Build the grid
        for r in range(grid_size):
            for c in range(grid_size):
                x = start_x + (c * spacing)
                y = start_y - (r * spacing)
                
                if r == t_row and t_col <= c < t_col + len(target):
                    letter = target[c - t_col]
                    stim = visual.TextStim(win, text=letter, pos=(x, y), height=30, font='Courier', color='white')
                    target_stims.append(stim) 
                else:
                    letter = random.choice(string.ascii_uppercase)
                    stim = visual.TextStim(win, text=letter, pos=(x, y), height=30, font='Courier', color='white') 
                
                all_letter_stims.append(stim)

        # D. Draw the initial grid and start the clock
        for stim in all_letter_stims:
            stim.draw()
        win.flip() 
        
        rt_clock = core.Clock() 
        mouse.clickReset() 
        event.clearEvents()
        
        found = False

        # E. The "Wait for Click" Loop
        while not found:
            if 'escape' in event.getKeys():
                quit_experiment = True
                break

            buttons = mouse.getPressed()
            
            if buttons[0]: 
                for t_stim in target_stims:
                    if mouse.isPressedIn(t_stim):
                        # Grab the time
                        rt = rt_clock.getTime() 
                        
                        # SORT THE DATA into the three new buckets
                        if condition == "Primed":
                            primed_rts.append(rt)
                        elif condition == "Blank":
                            blank_rts.append(rt)
                        elif condition == "Distracted":
                            distracted_rts.append(rt)
                            
                        found = True
                        
                        # Visual Feedback
                        for ts in target_stims:
                            ts.color = 'green'
                        for stim in all_letter_stims:
                            stim.draw()
                        win.flip()
                        core.wait(1) 
                        break 
                
                if not found:
                    core.wait(0.1) 
                    mouse.clickReset()
                    
        # F. Blank screen inter-trial interval
        win.flip()
        core.wait(1)

    # --- 4. Final Math and Comparison Output ---
    print("\n" + "="*40)
    print(" EXPERIMENT RESULTS: INTERFERENCE TASK")
    print("="*40)
    
    # 1. Calculate Primed Average
    avg_primed = sum(primed_rts) / len(primed_rts) if primed_rts else 0
    if avg_primed:
        print(f"Average PRIMED Reaction Time:     {avg_primed:.3f} seconds")
        
    # 2. Calculate Blank Average (Baseline)
    avg_blank = sum(blank_rts) / len(blank_rts) if blank_rts else 0
    if avg_blank:
        print(f"Average BLANK Reaction Time:      {avg_blank:.3f} seconds (BASELINE)")

    # 3. Calculate Distracted Average
    avg_distracted = sum(distracted_rts) / len(distracted_rts) if distracted_rts else 0
    if avg_distracted:
        print(f"Average DISTRACTED Reaction Time: {avg_distracted:.3f} seconds")

    # 4. Print the final conclusions
    print("-" * 40)
    if avg_blank and avg_primed:
        print(f"Priming impact: {avg_blank - avg_primed:.3f} seconds (Positive means faster)")
    if avg_blank and avg_distracted:
        print(f"Distraction impact: {avg_blank - avg_distracted:.3f} seconds (Negative means slower)")
            
finally:
    win.close()
    core.quit()
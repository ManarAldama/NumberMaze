import tkinter as tk
from random import randint, choice
from PIL import Image, ImageTk  #(Python Imaging Library) for image-related tasks.
import pygame

class GameApp:
    def __init__(self, root):
        self.root = root #window
        self.root.title("NumberMaze")
        self.root.geometry("800x600")

        # Initialize pygame for sound effects
        pygame.init()
        pygame.mixer.init()
        self.countdown_sound = pygame.mixer.Sound('sound/countdown.mp3')
        self.background_sound = pygame.mixer.Sound('sound/background.mp3')
        self.timeout_sound = pygame.mixer.Sound('sound/free_timer.mp3')
        self.wrong_answer_sound = pygame.mixer.Sound('sound/wrong_answer.mp3')
        self.game_end_sound = pygame.mixer.Sound('sound/game_end.mp3')

        # Set initial game variables
        self.time_left = 30
        self.difficulty_level = None
        self.error_label_shown = False
        self.timer_running = False
        self.question_counter = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.available_hints = 3
        self.questions_and_answers = []
        self.setBackground("images/background.png")
        self.username = ""
        self.setup_welcome_screen()

    def setBackground(self, image_path):
        # Set background image
        self.background_image = tk.PhotoImage(file=image_path)
        self.background_label = tk.Label(self.root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

    def setLogo(self, image_path):
        # Load and set the logo image
        img = Image.open(image_path) #using PIL library.
        width, height = 500, 500
        img = img.resize((width, height))
        self.logo_image = ImageTk.PhotoImage(img)
        logo_label = tk.Label(self.welcome_frame, image=self.logo_image)
        logo_label.pack(pady=10) #its apperance inside its parent

    def setup_welcome_screen(self):
        # Create and display the welcome screen
        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(expand=True)

        # Add welcome text
        welcome_label = tk.Label(self.welcome_frame,
                                 text="Welcome to the game😊! Before we dive in, please enter your name🎮",
                                 font=('Comic Sans MS', 18))
        welcome_label.pack(pady=10)

        # Username entry field
        self.username_entry = tk.Entry(self.welcome_frame, font=('Helvetica', 14))
        self.username_entry.pack(pady=20)

        # Start game button
        start_button = tk.Button(self.welcome_frame, text="Play", command=self.start_game, font=('Helvetica', 14),
                                 width=10)
        start_button.pack(pady=20)

        # Error label for empty username (hidden initially)
        self.error_label = tk.Label(self.welcome_frame, text="Username is mandatory!", font=('Helvetica', 12), fg='red')


        self.setLogo("images/logo.png")

        self.muted = False
        self.create_mute_button()
        self.sounds = [
            self.countdown_sound,
            self.background_sound,
            self.timeout_sound,
            self.wrong_answer_sound,
            self.game_end_sound
        ]
        self.initial_volume = 0.5
        self.update_sound_state()

    def create_mute_button(self):
        # Create a circular button with a speaker emoji
        self.mute_button_var = tk.StringVar()
        self.mute_button_var.set("🔈")  # Set initial emoji (unmuted state)
        self.mute_button = tk.Button(self.root, textvariable=self.mute_button_var, command=self.toggle_mute,
                                     font=('Helvetica', 14))
        self.mute_button.pack(side='top', pady=10, anchor='ne')

    def toggle_mute(self):
        # Toggle between muting and unmuting the sound
        self.muted = not self.muted
        self.update_sound_state()

    def update_sound_state(self):
        # Set the volume for each sound object based on the mute state
        for sound in self.sounds:
            if self.muted:
                sound.set_volume(0)
            else:
                sound.set_volume(self.initial_volume)
            emoji = "🔇" if self.muted else "🔈"
            self.mute_button_var.set(emoji)

    def start_game(self):
        self.username = self.username_entry.get().strip()

        if not self.username:
            # Show the error message if the username field is empty
            self.error_label.pack()
            return

        else:
            # Hide the error message if the username is entered
            self.error_label.pack_forget()

        # Proceed to the difficulty selection screen
        self.welcome_frame.pack_forget()
        self.setup_difficulty_selection_screen()

    def setup_game_screen(self):
        # Set up the main game screen
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(expand=True)
        self.game_frame.pack_propagate(0)
        self.game_frame.config(width=500, height=500)

        # Display player's username
        user_label = tk.Label(self.game_frame, text=f"Player: {self.username}", font=('Helvetica', 14))
        user_label.pack(pady=10)

        # Score label
        self.score_label = tk.Label(self.game_frame, text="Correct: 0, Wrong: 0", font=('Helvetica', 14))
        self.score_label.pack(pady=10)

        # Label for displaying questions
        self.question_label = tk.Label(self.game_frame, font=('Helvetica', 16))
        self.question_label.pack(pady=20)

        # Timer label
        self.timer_label = tk.Label(self.game_frame, text=f"Time Left: {self.time_left}", font=('Helvetica', 14))
        self.timer_label.pack(pady=10)

        # Set up answer option buttons and difficulty menu
        self.setup_option_buttons()
        self.setup_difficulty_menu()

        # Create a frame for hint and close buttons
        buttons_frame = tk.Frame(self.game_frame)
        buttons_frame.pack(pady=10)

        # Add hint button
        self.hint_button = tk.Button(buttons_frame, text="Hint", command=self.show_hint, font=('Helvetica', 14))
        self.hint_button.pack(side='left', padx=5)

        # Add close button
        self.close_button = tk.Button(buttons_frame, text="Close", command=self.exit_game, font=('Helvetica', 14))
        self.close_button.pack(side='right', padx=5)

        # Add hint label
        self.hint_label = tk.Label(self.game_frame, text="", font=('Helvetica', 12))
        self.hint_label.pack(side='bottom')

        # Add questions left label
        self.questions_left_label = tk.Label(self.game_frame, text="", font=('Helvetica', 14))
        self.questions_left_label.pack(pady=10)

    def start_countdown(self):
        # Check if a difficulty level has been selected
        if self.difficulty_level not in ["Easy", "Medium", "Hard"]:
            if not self.error_label_shown:
                self.error_label = tk.Label(self.difficulty_frame, text="Please select a difficulty level!",
                                            font=('Helvetica', 12), fg='red')
                self.error_label.pack()
                self.error_label_shown = True
            return

        # If a difficulty level is selected, proceed with the countdown
        countdown_label = tk.Label(self.root, text="3", font=("Helvetica", 150), bg='#B9E1EF')
        countdown_label.place(relx=0.5, rely=0.5, anchor='center')
        countdown_label.pack(pady=20)
        self.countdown(3, countdown_label)
        self.difficulty_frame.pack_forget()

    def countdown(self, time, label):
        # Countdown timer function
        if time >= 0:
            self.countdown_sound.play()  # Play countdown sound
            label.configure(text=str(time))
            self.root.after(500, lambda: self.countdown(time - 1, label))
        else:
            self.countdown_sound.stop()
            label.destroy()
            self.setup_game_screen()
            self.display_question()

    def setup_option_buttons(self):
        # Create and place option buttons for answers
        self.options_frame = tk.Frame(self.game_frame)
        self.options_frame.pack(pady=20)

        self.option_buttons = []
        for i in range(4):
            button = tk.Button(self.options_frame, font=('Helvetica', 14), width=15, command=lambda i=i: self.check_answer(i))
            button.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.option_buttons.append(button)

    def show_hint(self):
        if self.available_hints > 0:
            # Logic to display a specific hint based on the current question
            hint_text = f"The answer is around {self.correct_answer + randint(-1, 1)}"
            self.hint_label.config(text=hint_text)
            self.available_hints -= 1
            print("A hint was used")

        else:
            # When no hints are available
            self.hint_label.config(text="No more hints available!")

            # This line will automatically hide the hint message after 2 seconds
            self.root.after(2000, lambda: self.hint_label.config(text=""))

    def setup_difficulty_menu(self):
        # Create a menu for selecting game difficulty
        difficulty_menu = tk.Menu(self.root)
        self.root.config(menu=difficulty_menu)

        difficulty_sub_menu = tk.Menu(difficulty_menu)
        difficulty_menu.add_cascade(label="Difficulty", menu=difficulty_sub_menu)
        difficulty_sub_menu.add_command(label="Easy", command=lambda: self.set_difficulty("Easy"))
        difficulty_sub_menu.add_command(label="Medium", command=lambda: self.set_difficulty("Medium"))
        difficulty_sub_menu.add_command(label="Hard", command=lambda: self.set_difficulty("Hard"))

    def setup_difficulty_selection_screen(self):
        # Create and display the difficulty selection screen
        self.difficulty_frame = tk.Frame(self.root)
        self.difficulty_frame.pack(expand=True)

        self.difficulty_buttons = {}

        # Frame for difficulty buttons
        difficulty_buttons_frame = tk.Frame(self.difficulty_frame)
        difficulty_buttons_frame.pack(pady=20)

        for difficulty in ["Easy", "Medium", "Hard"]:
            button = tk.Button(difficulty_buttons_frame, text=difficulty, font=('Helvetica', 14), width=10,
                               command=lambda d=difficulty: self.select_difficulty(d))
            button.pack(side='left', padx=10)
            self.difficulty_buttons[difficulty] = button

        # Start button below the difficulty buttons
        start_button = tk.Button(self.difficulty_frame, text="Start", command=self.start_countdown,
                                 font=('Helvetica', 14), width=10)
        start_button.pack(pady=20)

    def select_difficulty(self, level):
        # Check if the selected level is the same as the current level
        if self.difficulty_level == level:
            # If so, deselect the level
            self.difficulty_level = None
            self.difficulty_buttons[level].config(bg='white')
        else:
            # If a new level is selected, update the selection and the button color
            self.difficulty_level = level
            for difficulty, button in self.difficulty_buttons.items():
                button.config(bg='green' if difficulty == level else 'white')

    def set_difficulty(self, level):
        # Set the game difficulty level
        self.difficulty_level = level
        print(f"Difficulty level changed to: {level}")
        self.display_question()

    def display_question(self):
        # Clear the hint label at the beginning of each question
        self.hint_label.config(text="")

        # Display a new question
        for button in self.option_buttons:
            button.config(bg='SystemButtonFace')

        # Generate random numbers and operation for the question
        num1, num2 = randint(1, 10), randint(1, 10)
        operation = choice(["+", "-", "*"])
        self.correct_answer = eval(f"{num1} {operation} {num2}")

        # Update question label
        question = f"What is {num1} {operation} {num2}?"
        self.question_label.config(text=question)
        self.background_sound.play()
        self.question_counter += 1

        # Check if it's time to add a hint
        if self.question_counter % 10 == 0:
            self.available_hints = 3  # Reset available hints every 10 questions
            self.hint_label.config(text="Hints refreshed!")

        # Check difficulty level and set the maximum number of questions
        max_questions = 0
        if self.difficulty_level == "Easy":
            max_questions = 10
        elif self.difficulty_level == "Medium":
            max_questions = 20
        elif self.difficulty_level == "Hard":
            max_questions = 30

        questions_left = max(0, max_questions - self.question_counter)
        self.questions_left_label.config(text=f"Questions Left: {questions_left}")
        if self.question_counter > max_questions:
            self.show_final_score()
            return

        self.set_option_buttons()
        self.reset_timer()

    def set_option_buttons(self):
        # Set text for option buttons with one correct and three wrong answers
        options = [self.correct_answer, randint(1, 20), randint(1, 20), randint(1, 20)]
        while len(set(options)) < 4:
            options.append(randint(1, 20))

        options = list(set(options))

        for button, option in zip(self.option_buttons, options):
            button.config(text=str(option))

    def check_answer(self, index):

        selected_answer = int(self.option_buttons[index].cget("text"))
        self.background_sound.stop()  # Stop the background sound

        # Disable all answer buttons to prevent multiple submissions
        for button in self.option_buttons:
            button.config(state=tk.DISABLED)

        # Check if the selected answer is correct
        if selected_answer == self.correct_answer:
            self.correct_answers += 1
            self.option_buttons[index].config(bg='green')
            self.timeout_sound.play()
        else:
            self.wrong_answers += 1
            self.option_buttons[index].config(bg='red')
            self.wrong_answer_sound.play()

        # Update the score display
        self.update_score()

        # Re-enable all buttons after a short delay and move to the next question
        self.root.after(1000, self.enable_option_buttons)

        # Check if it's time to add a hint
        if self.question_counter % 3 == 0:
            self.available_hints += 1

    def enable_option_buttons(self):
        # Re-enable the buttons
        for button in self.option_buttons:
            button.config(state=tk.NORMAL, bg='SystemButtonFace')
        # Proceed to the next question
        self.display_question()

    def resume_background_sound(self):
        self.background_sound.play()
        self.display_question()

    def update_score(self):
        # Update the score display
        score_text = f"Correct: {self.correct_answers}, Wrong: {self.wrong_answers}"
        self.score_label.config(text=score_text)

    def reset_timer(self):
        # Reset the timer for each question
        self.time_left = 30
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        # Update the countdown timer for each question
        if not self.timer_running:
            return
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time Left: {self.time_left}")
            self.root.after(1000, self.update_timer)
        else:
            self.handle_timeout()

    def handle_timeout(self):
        # Handle what happens when the timer runs out
        if self.timer_running:
            self.wrong_answers += 1
            self.update_score()
            # Display the next question after a delay
            self.root.after(1000, self.display_question)
            self.timer_running = False

    def show_final_score(self):
        # Stop sounds and game logic
        self.background_sound.stop()
        self.game_end_sound.play()
        self.timer_running = False

        # Clear the game frame if it exists
        if self.game_frame.winfo_exists():
            self.game_frame.pack_forget()

        # Create a frame for the final score and buttons
        self.final_score_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.final_score_frame.pack(expand=True)

        # Final score label with bold and larger font
        final_score_label = tk.Label(self.final_score_frame,
                                     text="FINAL SCORE",
                                     font=('Helvetica', 30, 'bold'), bg="#f7f7f7")
        final_score_label.pack(pady=(20, 5))

        # Correct answers label 
        correct_label = tk.Label(self.final_score_frame,
                                 text=f"Correct: {self.correct_answers}",
                                 font=('Helvetica', 22, 'bold'), bg="#f7f7f7", fg="#4CAF50")
        correct_label.pack()


        # Wrong answers label
        wrong_label = tk.Label(self.final_score_frame,
                               text=f"Wrong: {self.wrong_answers}",
                               font=('Helvetica', 22, 'bold'), bg="#f7f7f7", fg="#f44336")
        wrong_label.pack()


        # Restart and Exit buttons
        restart_button = tk.Button(self.final_score_frame, text="Restart", command=self.restart_game,
                                   font=('Helvetica', 20), bg="#4CAF50", fg="white")
        restart_button.pack(side='left', padx=50, pady=20)

        exit_button = tk.Button(self.final_score_frame, text="Exit", command=self.exit_game,
                                font=('Helvetica', 20), bg="#f44336", fg="white")
        exit_button.pack(side='right', padx=50, pady=20)



    def restart_game(self):
        # Reset game variables
        self.correct_answers = 0
        self.wrong_answers = 0
        self.available_hints = 3
        self.question_counter = 0
        self.time_left = 30
        self.timer_running = False
        self.difficulty_level = None
        self.error_label_shown = False

        # Stop any sounds that may be playing
        self.background_sound.stop()
        self.game_end_sound.stop()

        # Destroy the final score and game frames if they exist
        if hasattr(self, 'final_score_frame') and self.final_score_frame.winfo_exists():
            self.final_score_frame.destroy()
        if hasattr(self, 'game_frame') and self.game_frame.winfo_exists():
            self.game_frame.destroy()

        # Show the difficulty selection screen
        self.setup_difficulty_selection_screen()

    def exit_game(self):
        self.root.destroy()

# Initialize and run the application
root = tk.Tk()
app = GameApp(root)
root.mainloop()

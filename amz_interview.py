import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from typing import Dict, List
import os
import random
import threading
import pyaudio
import wave

class LPMatrixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Leadership Principles Story Matrix")
        self.root.geometry("1000x700")

        # Full list of Amazon Leadership Principles
        self.leadership_principles = [
            "Customer Obsession",
            "Ownership",
            "Invent and Simplify",
            "Are Right, A Lot",
            "Learn and Be Curious",
            "Hire and Develop the Best",
            "Insist on the Highest Standards",
            "Think Big",
            "Bias for Action",
            "Frugality",
            "Earn Trust",
            "Dive Deep",
            "Have Backbone; Disagree and Commit",
            "Deliver Results",
            "Strive to be Earth's Best Employer",
            "Success and Scale Bring Broad Responsibility"
        ]

        self.experiences = [
            "RPA Project",
            "Amazon Investigation",
            "Mercari Risk Control",
            "Rusutsu System"
        ]

        # Initialize data structure
        self.matrix_data = {}
        self.lp_questions = self.load_lp_questions()
        self.practice_history = self.load_practice_history()

        self.create_gui()
        self.load_data()

    def create_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)

        # Matrix View Tab
        self.matrix_frame = ttk.Frame(self.notebook)
        self.create_matrix_view(self.matrix_frame)

        # Story Editor Tab
        self.editor_frame = ttk.Frame(self.notebook)
        self.create_story_editor(self.editor_frame)

        # Practice Tab
        self.practice_frame = ttk.Frame(self.notebook)
        self.create_practice_tab(self.practice_frame)

        # Add tabs to notebook
        self.notebook.add(self.matrix_frame, text="Matrix View")
        self.notebook.add(self.editor_frame, text="Story Editor")
        self.notebook.add(self.practice_frame, text="Practice")

        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

    def create_matrix_view(self, parent):
        # Create matrix table
        self.matrix_tree = ttk.Treeview(parent, columns=['Experience'] + self.leadership_principles)

        # Configure columns
        self.matrix_tree.heading('#0', text='')
        self.matrix_tree.column('#0', width=0, stretch=tk.NO)

        self.matrix_tree.heading('Experience', text='Experience')
        self.matrix_tree.column('Experience', width=150, stretch=tk.NO)

        for lp in self.leadership_principles:
            self.matrix_tree.heading(lp, text=lp, anchor='center')
            self.matrix_tree.column(lp, width=80, anchor='center')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.matrix_tree.yview)
        self.matrix_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements using grid
        self.matrix_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Bind double-click event
        self.matrix_tree.bind("<Double-1>", self.on_matrix_item_double_click)

    def create_story_editor(self, parent):
        # Use grid layout
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Experience selection
        ttk.Label(input_frame, text="Experience:").grid(row=0, column=0, sticky='w')
        self.experience_var = tk.StringVar()
        self.experience_combo = ttk.Combobox(input_frame, textvariable=self.experience_var, values=self.experiences)
        self.experience_combo.grid(row=0, column=1, sticky='ew', pady=2)

        # LP selection
        ttk.Label(input_frame, text="Leadership Principle:").grid(row=1, column=0, sticky='w')
        self.lp_var = tk.StringVar()
        self.lp_combo = ttk.Combobox(input_frame, textvariable=self.lp_var, values=self.leadership_principles)
        self.lp_combo.grid(row=1, column=1, sticky='ew', pady=2)

        # Score selection
        ttk.Label(input_frame, text="Score (1-4):").grid(row=2, column=0, sticky='w')
        self.score_var = tk.StringVar()
        self.score_combo = ttk.Combobox(input_frame, textvariable=self.score_var, values=['1', '2', '3', '4'])
        self.score_combo.grid(row=2, column=1, sticky='ew', pady=2)

        # Key points
        ttk.Label(input_frame, text="Key Points (one per line):").grid(row=3, column=0, sticky='nw')
        self.points_text = scrolledtext.ScrolledText(input_frame, height=5)
        self.points_text.grid(row=3, column=1, sticky='ew', pady=2)

        # STAR Story
        ttk.Label(input_frame, text="STAR Story:").grid(row=4, column=0, sticky='nw')
        self.story_text = scrolledtext.ScrolledText(input_frame, height=10)
        self.story_text.grid(row=4, column=1, sticky='ew', pady=2)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=1, sticky='e', pady=5)

        ttk.Button(button_frame, text="Save Story", command=self.save_story).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        input_frame.grid_columnconfigure(1, weight=1)

    def create_practice_tab(self, parent):
        practice_frame = ttk.Frame(parent)
        practice_frame.pack(expand=True, fill='both', padx=10, pady=10)

        ttk.Label(practice_frame, text="Practice with Recording", font=("Helvetica", 16)).pack(pady=10)

        # LP selection buttons
        self.lp_button_frame = ttk.Frame(practice_frame)
        self.lp_button_frame.pack(fill='x', pady=5)

        self.create_lp_buttons(self.lp_button_frame)

        # Flashcard Display
        self.flashcard_label = ttk.Label(practice_frame, text="", wraplength=800, font=("Helvetica", 14), justify='center')
        self.flashcard_label.pack(expand=True)

        # Record and Play Buttons
        control_frame = ttk.Frame(practice_frame)
        control_frame.pack(pady=10)

        self.record_button = ttk.Button(control_frame, text="Start Recording", command=self.start_recording, state='disabled')
        self.record_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop Recording", command=self.stop_recording, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        self.play_button = ttk.Button(control_frame, text="Play Recording", command=self.play_recording, state='disabled')
        self.play_button.pack(side='left', padx=5)

        # Spaced Repetition Info
        self.spaced_repetition_label = ttk.Label(practice_frame, text="")
        self.spaced_repetition_label.pack(pady=5)

        # Bind spacebar
        self.root.bind('<space>', self.next_flashcard_content)

        self.flashcard_state = 0  # 0: question, 1: answer, 2: key points
        self.current_flashcard = None

        # Audio recording variables
        self.is_recording = False
        self.record_frames = []
        self.audio_filename = "recording.wav"

    def create_lp_buttons(self, parent):
        # Create a canvas for scrollable buttons
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='horizontal', command=canvas.xview)
        self.lp_buttons_frame = ttk.Frame(canvas)

        self.lp_buttons_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.lp_buttons_frame, anchor='nw')
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side='top', fill='x', expand=True)
        scrollbar.pack(side='bottom', fill='x')

        # Create buttons for each leadership principle
        for lp in self.leadership_principles:
            button = ttk.Button(self.lp_buttons_frame, text=lp, command=lambda lp=lp: self.start_practice(lp))
            button.pack(side='left', padx=5, pady=5)

    def start_practice(self, lp=None):
        if lp is None:
            lp = random.choice(self.leadership_principles)
        flashcards = self.lp_questions.get(lp, [])
        if not flashcards:
            messagebox.showinfo("Info", f"No questions available for {lp}")
            return

        # Use spaced repetition to select the next question
        flashcard = self.select_flashcard(lp, flashcards)
        self.current_practice_lp = lp
        self.current_flashcard = flashcard
        self.flashcard_state = 0
        self.update_flashcard_display()

    def select_flashcard(self, lp, flashcards):
        # Simple spaced repetition implementation
        history = self.practice_history.get(lp, {})
        # Sort flashcards by last practiced date
        flashcards.sort(key=lambda x: history.get(x['id'], 0))
        return flashcards[0]

    def next_flashcard_content(self, event):
        if self.current_flashcard is None:
            return
        self.flashcard_state = (self.flashcard_state + 1) % 3
        self.update_flashcard_display()
        if self.flashcard_state == 0:
            # Update practice history
            lp = self.current_practice_lp
            flashcard_id = self.current_flashcard['id']
            self.practice_history.setdefault(lp, {})[flashcard_id] = self.get_current_timestamp()
            self.save_practice_history()

    def update_flashcard_display(self):
        if self.flashcard_state == 0:
            # Display question
            text = f"Leadership Principle: {self.current_practice_lp}\n\nQuestion:\n{self.current_flashcard['question']}\n\n(Press Space to see the answer)"
            self.record_button.config(state='normal')
            self.play_button.config(state='disabled')
        elif self.flashcard_state == 1:
            # Display answer
            text = f"Leadership Principle: {self.current_practice_lp}\n\nAnswer:\n{self.current_flashcard['answer']}\n\n(Press Space to see key points)"
            self.record_button.config(state='disabled')
            self.play_button.config(state='normal')
        else:
            # Display key points
            key_points = '\n'.join(self.current_flashcard['key_points'])
            text = f"Leadership Principle: {self.current_practice_lp}\n\nKey Points:\n{key_points}\n\n(Press Space to see next question)"
            self.record_button.config(state='disabled')
            self.play_button.config(state='normal')
        self.flashcard_label.config(text=text)
        # Update spaced repetition info
        lp = self.current_practice_lp
        flashcard_id = self.current_flashcard['id']
        last_practiced = self.practice_history.get(lp, {}).get(flashcard_id, None)
        if last_practiced:
            self.spaced_repetition_label.config(text=f"Last practiced on: {last_practiced}")
        else:
            self.spaced_repetition_label.config(text="This is your first time practicing this question.")

    def start_recording(self):
        self.is_recording = True
        self.record_frames = []
        self.record_button.config(state='disabled')
        self.stop_button.config(state='normal')
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.is_recording = False
        self.stop_button.config(state='disabled')
        self.play_button.config(state='normal')

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        while self.is_recording:
            data = stream.read(1024)
            self.record_frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        # Save recording
        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.record_frames))
        wf.close()

    def play_recording(self):
        if not os.path.exists(self.audio_filename):
            messagebox.showerror("Error", "No recording found.")
            return
        threading.Thread(target=self.play_audio).start()

    def play_audio(self):
        wf = wave.open(self.audio_filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                        rate=wf.getframerate(), output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def load_lp_questions(self):
        # Sample questions for each leadership principle with answers and key points
        lp_questions = {
            "Customer Obsession": [
                {
                    "id": "CO1",
                    "question": "Tell me about a time you went above and beyond for a customer.",
                    "answer": "In my previous role, I noticed a customer's recurring issue with our software. I proactively reached out, gathered their feedback, and worked with the development team to implement a solution that improved their experience.",
                    "key_points": [
                        "Proactive engagement",
                        "Collaboration with team",
                        "Improved customer satisfaction"
                    ]
                },
                # Add more questions...
            ],
            "Ownership": [
                {
                    "id": "OW1",
                    "question": "Describe a time you took ownership of a project.",
                    "answer": "When our team leader left unexpectedly, I stepped up to lead the project. I coordinated tasks, communicated with stakeholders, and ensured we met our deadlines successfully.",
                    "key_points": [
                        "Stepping up in challenging times",
                        "Leadership and coordination",
                        "Successful project delivery"
                    ]
                },
                # Add more questions...
            ],
            # Add questions for other leadership principles...
        }
        # Ensure all LPs have at least one question
        for lp in self.leadership_principles:
            if lp not in lp_questions:
                lp_questions[lp] = [{
                    "id": lp.replace(' ', '') + "1",
                    "question": f"Describe how you embody the '{lp}' principle.",
                    "answer": "Provide a specific example from your experience.",
                    "key_points": ["Specific example", "Demonstrate the principle", "Reflect on outcomes"]
                }]
        return lp_questions

    def save_story(self):
        experience = self.experience_var.get()
        lp = self.lp_var.get()

        if not experience or not lp:
            messagebox.showerror("Error", "Please select both Experience and Leadership Principle")
            return

        points = [p.strip() for p in self.points_text.get("1.0", tk.END).split('\n') if p.strip()]

        story_data = {
            "points": points,
            "score": int(self.score_var.get() or "0"),
            "story": self.story_text.get("1.0", tk.END).strip()
        }

        if experience not in self.matrix_data:
            self.matrix_data[experience] = {}

        self.matrix_data[experience][lp] = story_data

        self.update_matrix_view()
        self.save_data()
        messagebox.showinfo("Success", "Story saved successfully!")

    def clear_form(self):
        self.experience_var.set("")
        self.lp_var.set("")
        self.score_var.set("")
        self.points_text.delete("1.0", tk.END)
        self.story_text.delete("1.0", tk.END)

    def update_matrix_view(self):
        # Clear existing items
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)

        # Add rows
        for exp in self.experiences:
            values = [exp]
            for lp in self.leadership_principles:
                if exp in self.matrix_data and lp in self.matrix_data[exp]:
                    score = self.matrix_data[exp][lp]["score"]
                    values.append("★" * score)
                else:
                    values.append("")
            self.matrix_tree.insert("", "end", values=values)

    def on_matrix_item_double_click(self, event):
        item = self.matrix_tree.selection()[0]
        col = self.matrix_tree.identify_column(event.x)
        col_num = int(col[1:]) - 1

        if col_num == 0:  # Experience column
            return

        experience = self.matrix_tree.item(item)["values"][0]
        lp = self.leadership_principles[col_num - 1]

        if experience in self.matrix_data and lp in self.matrix_data[experience]:
            self.load_story_to_editor(experience, lp)
            self.notebook.select(1)  # Switch to editor tab

    def load_story_to_editor(self, experience, lp):
        story_data = self.matrix_data[experience][lp]

        self.experience_var.set(experience)
        self.lp_var.set(lp)
        self.score_var.set(str(story_data["score"]))

        self.points_text.delete("1.0", tk.END)
        self.points_text.insert("1.0", "\n".join(story_data["points"]))

        self.story_text.delete("1.0", tk.END)
        self.story_text.insert("1.0", story_data["story"])

    def save_data(self):
        with open("lp_matrix_data.json", "w", encoding='utf-8') as f:
            json.dump(self.matrix_data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            if os.path.exists("lp_matrix_data.json"):
                with open("lp_matrix_data.json", "r", encoding='utf-8') as f:
                    self.matrix_data = json.load(f)
                self.update_matrix_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def get_current_timestamp(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_practice_history(self):
        with open("practice_history.json", "w", encoding='utf-8') as f:
            json.dump(self.practice_history, f, ensure_ascii=False, indent=2)

    def load_practice_history(self):
        try:
            if os.path.exists("practice_history.json"):
                with open("practice_history.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load practice history: {str(e)}")
            return {}

def main():
    root = tk.Tk()
    app = LPMatrixGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

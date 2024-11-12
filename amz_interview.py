import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import random
import threading
import pyaudio
import wave
import datetime

class AmazonInterviewPrep:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Interview Preparation Tool")
        self.root.geometry("1200x1000")

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

        # Initialize data structures
        self.experiences = []
        self.questions = []
        self.practice_history = {}
        self.lp_matrix_data = {}
        self.interview_framework = {}

        self.load_experiences()
        self.load_questions()
        self.load_practice_history()
        self.load_lp_matrix_data()
        self.load_interview_framework()

        self.create_gui()

    def create_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)

        # Question Bank Tab
        self.question_bank_frame = ttk.Frame(self.notebook)
        self.create_question_bank(self.question_bank_frame)

        # Experience Library Tab
        self.experience_frame = ttk.Frame(self.notebook)
        self.create_experience_library(self.experience_frame)

        # LP Story Matrix Tab
        self.lp_matrix_frame = ttk.Frame(self.notebook)
        self.create_lp_matrix(self.lp_matrix_frame)

        # Interview Framework Tab
        self.interview_framework_frame = ttk.Frame(self.notebook)
        self.create_interview_framework(self.interview_framework_frame)

        # Practice Tab
        self.practice_frame = ttk.Frame(self.notebook)
        self.create_practice_tab(self.practice_frame)

        # Progress Tracking Tab
        self.progress_frame = ttk.Frame(self.notebook)
        self.create_progress_tracking(self.progress_frame)

        # Add tabs to notebook
        self.notebook.add(self.question_bank_frame, text="Question Bank")
        self.notebook.add(self.experience_frame, text="Experience Library")
        self.notebook.add(self.lp_matrix_frame, text="LP Story Matrix")
        self.notebook.add(self.interview_framework_frame, text="Interview Framework")
        self.notebook.add(self.practice_frame, text="Practice")
        self.notebook.add(self.progress_frame, text="Progress Tracking")

        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

    # ----------------------- Question Bank -----------------------
    def create_question_bank(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Question List
        ttk.Label(main_frame, text="Question Bank", font=('Helvetica', 16)).pack(pady=10)

        self.question_tree = ttk.Treeview(main_frame, columns=('Question', 'LPs'), show='headings')
        self.question_tree.heading('Question', text='Question')
        self.question_tree.heading('LPs', text='Leadership Principles')
        self.question_tree.pack(fill='both', expand=True)
        self.question_tree.bind('<<TreeviewSelect>>', self.on_question_select)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Add Question", command=self.add_question).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Question", command=self.edit_question).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Question", command=self.delete_question).pack(side='left', padx=5)

        # Load questions
        self.update_question_tree()

    def update_question_tree(self):
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        for idx, question in enumerate(self.questions):
            lp_str = ", ".join(question.get('leadership_principles', []))
            self.question_tree.insert('', 'end', iid=idx, values=(question['question'], lp_str))

    def on_question_select(self, event):
        selected = self.question_tree.focus()
        if selected:
            self.current_question_index = int(selected)

    def add_question(self):
        self.open_question_editor()

    def edit_question(self):
        selected = self.question_tree.focus()
        if selected:
            idx = int(selected)
            question = self.questions[idx]
            self.open_question_editor(question, idx)
        else:
            messagebox.showerror("Error", "Please select a question to edit.")

    def delete_question(self):
        selected = self.question_tree.focus()
        if selected:
            idx = int(selected)
            del self.questions[idx]
            self.save_questions()
            self.update_question_tree()
        else:
            messagebox.showerror("Error", "Please select a question to delete.")

    def open_question_editor(self, question=None, idx=None):
        # Create a new window for question editing
        self.question_editor_window = tk.Toplevel(self.root)
        self.question_editor_window.title("Question Editor")
        self.question_editor_window.geometry("800x1000")

        ttk.Label(self.question_editor_window, text="Question Details", font=('Helvetica', 14)).pack(pady=10)

        # Question
        ttk.Label(self.question_editor_window, text="Question:").pack(anchor='nw', padx=10)
        self.question_var = tk.StringVar()
        self.question_entry = ttk.Entry(self.question_editor_window, textvariable=self.question_var, width=100)
        self.question_entry.pack(fill='x', padx=10, pady=5)

        # Answer
        ttk.Label(self.question_editor_window, text="Answer:").pack(anchor='nw', padx=10)
        self.answer_text = scrolledtext.ScrolledText(self.question_editor_window, height=8)
        self.answer_text.pack(fill='both', expand=True, padx=10, pady=5)

        # Key Points
        ttk.Label(self.question_editor_window, text="Key Points:").pack(anchor='nw', padx=10)
        self.keypoints_text = scrolledtext.ScrolledText(self.question_editor_window, height=5)
        self.keypoints_text.pack(fill='both', expand=True, padx=10, pady=5)

        # Associated Experiences
        ttk.Label(self.question_editor_window, text="Associated Experiences:").pack(anchor='nw', padx=10)
        self.experience_vars = {}
        exp_frame = ttk.Frame(self.question_editor_window)
        exp_frame.pack(fill='both', expand=True, padx=10, pady=5)
        for exp in self.experiences:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(exp_frame, text=exp['title'], variable=var)
            cb.pack(anchor='w')
            self.experience_vars[exp['title']] = var

        # Leadership Principles
        ttk.Label(self.question_editor_window, text="Leadership Principles:").pack(anchor='nw', padx=10)
        self.lp_vars = {}
        lp_frame = ttk.Frame(self.question_editor_window)
        lp_frame.pack(fill='both', expand=True, padx=10, pady=5)
        for lp in self.leadership_principles:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(lp_frame, text=lp, variable=var)
            cb.pack(anchor='w')
            self.lp_vars[lp] = var

        # Buttons
        button_frame = ttk.Frame(self.question_editor_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save", command=lambda: self.save_question(idx)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.question_editor_window.destroy).pack(side='left', padx=5)

        # Load question data if editing
        if question:
            self.question_var.set(question['question'])
            self.answer_text.insert('1.0', question.get('answer', ''))
            self.keypoints_text.insert('1.0', '\n'.join(question.get('key_points', [])))
            for exp_title in question.get('experiences', []):
                if exp_title in self.experience_vars:
                    self.experience_vars[exp_title].set(True)
            for lp in question.get('leadership_principles', []):
                if lp in self.lp_vars:
                    self.lp_vars[lp].set(True)
        else:
            # Clear fields for new question
            self.question_var.set("")
            self.answer_text.delete('1.0', tk.END)
            self.keypoints_text.delete('1.0', tk.END)
            for var in self.experience_vars.values():
                var.set(False)
            for var in self.lp_vars.values():
                var.set(False)

    def save_question(self, idx=None):
        question_text = self.question_var.get().strip()
        answer_text = self.answer_text.get('1.0', tk.END).strip()
        key_points = [kp.strip() for kp in self.keypoints_text.get('1.0', tk.END).strip().split('\n') if kp.strip()]
        experiences = [title for title, var in self.experience_vars.items() if var.get()]
        leadership_principles = [lp for lp, var in self.lp_vars.items() if var.get()]

        if not question_text:
            messagebox.showerror("Error", "Please enter a question.")
            return

        question_data = {
            'question': question_text,
            'answer': answer_text,
            'key_points': key_points,
            'experiences': experiences,
            'leadership_principles': leadership_principles
        }

        if idx is not None:
            self.questions[idx] = question_data
        else:
            self.questions.append(question_data)

        self.save_questions()
        self.update_question_tree()
        self.question_editor_window.destroy()

    def load_questions(self):
        try:
            if os.path.exists("questions.json"):
                with open("questions.json", "r", encoding='utf-8') as f:
                    self.questions = json.load(f)
            else:
                self.questions = []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
            self.questions = []

    def save_questions(self):
        with open("questions.json", "w", encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)

    # ----------------------- Experience Library -----------------------
    def create_experience_library(self, parent):
        # Frame for experience list and details
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Experience List
        exp_list_frame = ttk.Frame(main_frame)
        exp_list_frame.pack(side='left', fill='y')

        ttk.Label(exp_list_frame, text="Experiences", font=('Helvetica', 14)).pack(pady=5)

        self.exp_listbox = tk.Listbox(exp_list_frame)
        self.exp_listbox.pack(fill='y', expand=True)
        self.exp_listbox.bind('<<ListboxSelect>>', self.on_experience_select)

        # Add experiences to listbox
        self.update_experience_listbox()

        # Experience Details
        exp_details_frame = ttk.Frame(main_frame)
        exp_details_frame.pack(side='right', fill='both', expand=True)

        ttk.Label(exp_details_frame, text="Experience Details", font=('Helvetica', 14)).grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(exp_details_frame, text="Title:").grid(row=1, column=0, sticky='w')
        self.exp_title_var = tk.StringVar()
        self.exp_title_entry = ttk.Entry(exp_details_frame, textvariable=self.exp_title_var)
        self.exp_title_entry.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(exp_details_frame, text="Description:").grid(row=2, column=0, sticky='nw')
        self.exp_desc_text = scrolledtext.ScrolledText(exp_details_frame, height=15)
        self.exp_desc_text.grid(row=2, column=1, sticky='nsew', pady=2)

        # Buttons
        button_frame = ttk.Frame(exp_details_frame)
        button_frame.grid(row=3, column=1, sticky='e', pady=5)

        ttk.Button(button_frame, text="Save Experience", command=self.save_experience).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Experience", command=self.delete_experience).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_experience_form).pack(side="left", padx=5)

        exp_details_frame.columnconfigure(1, weight=1)
        exp_details_frame.rowconfigure(2, weight=1)

    def update_experience_listbox(self):
        self.exp_listbox.delete(0, tk.END)
        for exp in self.experiences:
            self.exp_listbox.insert(tk.END, exp['title'])

    def on_experience_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_exp_index = selection[0]
            experience = self.experiences[self.current_exp_index]
            self.load_experience_details(experience)
        else:
            self.clear_experience_form()

    def load_experience_details(self, experience):
        self.exp_title_var.set(experience['title'])
        self.exp_desc_text.delete('1.0', tk.END)
        self.exp_desc_text.insert('1.0', experience['description'])

    def save_experience(self):
        title = self.exp_title_var.get().strip()
        description = self.exp_desc_text.get('1.0', tk.END).strip()

        if not title:
            messagebox.showerror("Error", "Please enter a title for the experience.")
            return

        experience = {
            'title': title,
            'description': description
        }

        # Check if updating existing experience
        for idx, exp in enumerate(self.experiences):
            if exp['title'] == title:
                self.experiences[idx] = experience
                break
        else:
            self.experiences.append(experience)

        self.save_experiences()
        self.update_experience_listbox()
        messagebox.showinfo("Success", "Experience saved successfully!")

    def delete_experience(self):
        title = self.exp_title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please select an experience to delete.")
            return

        self.experiences = [exp for exp in self.experiences if exp['title'] != title]
        self.save_experiences()
        self.update_experience_listbox()
        self.clear_experience_form()
        messagebox.showinfo("Success", "Experience deleted successfully!")

    def clear_experience_form(self):
        self.exp_title_var.set("")
        self.exp_desc_text.delete('1.0', tk.END)

    def load_experiences(self):
        try:
            if os.path.exists("experiences.json"):
                with open("experiences.json", "r", encoding='utf-8') as f:
                    self.experiences = json.load(f)
                # Ensure experiences are a list
                if not isinstance(self.experiences, list):
                    self.experiences = []
            else:
                self.experiences = []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load experiences: {str(e)}")
            self.experiences = []

    def save_experiences(self):
        with open("experiences.json", "w", encoding='utf-8') as f:
            json.dump(self.experiences, f, ensure_ascii=False, indent=2)

    # ----------------------- LP Story Matrix -----------------------
    def create_lp_matrix(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="LP Story Matrix", font=('Helvetica', 16)).pack(pady=10)

        # Create matrix table
        columns = ['Experience'] + self.leadership_principles
        self.matrix_tree = ttk.Treeview(main_frame, columns=columns, show='headings')

        for col in columns:
            self.matrix_tree.heading(col, text=col)
            self.matrix_tree.column(col, width=100, anchor='center')

        self.matrix_tree.pack(fill='both', expand=True)

        # Load data
        self.update_lp_matrix_tree()

    def update_lp_matrix_tree(self):
        # Clear existing items
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)

        # Populate the matrix
        for exp in self.experiences:
            exp_title = exp['title']
            row = [exp_title]
            for lp in self.leadership_principles:
                # Check if there is a story for this experience and LP
                key = f"{exp_title}-{lp}"
                if key in self.lp_matrix_data:
                    row.append("✓")
                else:
                    row.append("")
            self.matrix_tree.insert('', 'end', values=row)

        # Bind double-click event
        self.matrix_tree.bind("<Double-1>", self.on_lp_matrix_double_click)

    def on_lp_matrix_double_click(self, event):
        item = self.matrix_tree.selection()[0]
        col = self.matrix_tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1  # Adjust for Treeview indexing
        if col_index == 0:
            return  # Ignore if clicked on the Experience column

        exp_title = self.matrix_tree.item(item)['values'][0]
        lp = self.leadership_principles[col_index - 1]

        self.open_lp_story_editor(exp_title, lp)

    def open_lp_story_editor(self, exp_title, lp):
        # Open a new window to edit the story
        self.lp_story_window = tk.Toplevel(self.root)
        self.lp_story_window.title(f"Edit Story - {exp_title} - {lp}")
        self.lp_story_window.geometry("800x1000")

        ttk.Label(self.lp_story_window, text=f"Experience: {exp_title}", font=('Helvetica', 14)).pack(pady=5)
        ttk.Label(self.lp_story_window, text=f"Leadership Principle: {lp}", font=('Helvetica', 14)).pack(pady=5)

        # Story Text
        ttk.Label(self.lp_story_window, text="Story:").pack(anchor='nw', padx=10)
        self.lp_story_text = scrolledtext.ScrolledText(self.lp_story_window, height=20)
        self.lp_story_text.pack(fill='both', expand=True, padx=10, pady=5)

        # Load existing story if any
        key = f"{exp_title}-{lp}"
        if key in self.lp_matrix_data:
            self.lp_story_text.insert('1.0', self.lp_matrix_data[key]['story'])

        # Buttons
        button_frame = ttk.Frame(self.lp_story_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save", command=lambda: self.save_lp_story(exp_title, lp)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.lp_story_window.destroy).pack(side='left', padx=5)

    def save_lp_story(self, exp_title, lp):
        story_text = self.lp_story_text.get('1.0', tk.END).strip()
        key = f"{exp_title}-{lp}"
        self.lp_matrix_data[key] = {'story': story_text}
        self.save_lp_matrix_data()
        self.update_lp_matrix_tree()
        self.lp_story_window.destroy()
        messagebox.showinfo("Success", "Story saved successfully!")

    def load_lp_matrix_data(self):
        try:
            if os.path.exists("lp_matrix_data.json"):
                with open("lp_matrix_data.json", "r", encoding='utf-8') as f:
                    self.lp_matrix_data = json.load(f)
                if not isinstance(self.lp_matrix_data, dict):
                    self.lp_matrix_data = {}
            else:
                self.lp_matrix_data = {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load LP matrix data: {str(e)}")
            self.lp_matrix_data = {}

    def save_lp_matrix_data(self):
        with open("lp_matrix_data.json", "w", encoding='utf-8') as f:
            json.dump(self.lp_matrix_data, f, ensure_ascii=False, indent=2)

    # ----------------------- Interview Framework -----------------------
    def create_interview_framework(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Interview Framework", font=('Helvetica', 16)).pack(pady=10)

        # Sections
        sections = [
            ("Self Introduction", "self_introduction"),
            ("Career Storyline", "career_storyline"),
            ("Key Achievements", "key_achievements"),
            ("Understanding of the Role", "role_understanding")
        ]

        self.framework_texts = {}

        for idx, (label_text, key) in enumerate(sections):
            ttk.Label(main_frame, text=label_text + ":").pack(anchor='nw', pady=5)
            text_widget = scrolledtext.ScrolledText(main_frame, height=5)
            text_widget.pack(fill='both', expand=True)
            self.framework_texts[key] = text_widget

            # Load existing content
            if key in self.interview_framework:
                text_widget.insert('1.0', self.interview_framework[key])

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save Framework", command=self.save_interview_framework).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_interview_framework).pack(side='left', padx=5)

    def save_interview_framework(self):
        for key, text_widget in self.framework_texts.items():
            self.interview_framework[key] = text_widget.get('1.0', tk.END).strip()
        self.save_framework_data()
        messagebox.showinfo("Success", "Interview framework saved successfully!")

    def clear_interview_framework(self):
        for text_widget in self.framework_texts.values():
            text_widget.delete('1.0', tk.END)

    def load_interview_framework(self):
        try:
            if os.path.exists("interview_framework.json"):
                with open("interview_framework.json", "r", encoding='utf-8') as f:
                    self.interview_framework = json.load(f)
                if not isinstance(self.interview_framework, dict):
                    self.interview_framework = {}
            else:
                self.interview_framework = {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load interview framework: {str(e)}")
            self.interview_framework = {}

    def save_framework_data(self):
        with open("interview_framework.json", "w", encoding='utf-8') as f:
            json.dump(self.interview_framework, f, ensure_ascii=False, indent=2)

    # ----------------------- Practice -----------------------
    def create_practice_tab(self, parent):
        practice_frame = ttk.Frame(parent)
        practice_frame.pack(expand=True, fill='both', padx=10, pady=10)

        ttk.Label(practice_frame, text="Practice", font=("Helvetica", 16)).pack(pady=10)

        # LP Selection
        lp_frame = ttk.Frame(practice_frame)
        lp_frame.pack(pady=5)

        ttk.Label(lp_frame, text="Select Leadership Principle:").pack(side='left', padx=5)
        self.practice_lp_var = tk.StringVar()
        lp_options = ['All'] + self.leadership_principles
        self.practice_lp_var.set('All')
        self.practice_lp_combo = ttk.Combobox(lp_frame, textvariable=self.practice_lp_var, values=lp_options, state='readonly')
        self.practice_lp_combo.pack(side='left', padx=5)

        # Start Practice Button
        ttk.Button(lp_frame, text="Start Practice", command=self.start_practice).pack(side='left', padx=5)

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

    def start_practice(self):
        lp_selected = self.practice_lp_var.get()
        if lp_selected == 'All':
            questions_pool = self.questions
        else:
            questions_pool = [q for q in self.questions if lp_selected in q.get('leadership_principles', [])]

        if not questions_pool:
            messagebox.showinfo("Info", "No questions available for the selected Leadership Principle.")
            return

        # Use spaced repetition to select the next question
        question = self.select_flashcard(questions_pool)
        self.current_flashcard = question
        self.flashcard_state = 0
        self.update_flashcard_display()

    def select_flashcard(self, questions_pool):
        # Simple spaced repetition implementation
        history = self.practice_history
        # Assign IDs if not present
        for idx, q in enumerate(questions_pool):
            if 'id' not in q:
                q['id'] = f"Q{idx}"
        # Sort questions by last practiced date
        questions_pool.sort(key=lambda x: history.get(x['id'], 0))
        return questions_pool[0]

    def next_flashcard_content(self, event):
        if self.current_flashcard is None:
            return
        self.flashcard_state = (self.flashcard_state + 1) % 3  # 0: question, 1: answer, 2: key points
        self.update_flashcard_display()
        if self.flashcard_state == 0:
            # Update practice history
            flashcard_id = self.current_flashcard['id']
            self.practice_history[flashcard_id] = self.get_current_timestamp()
            self.save_practice_history()

    def update_flashcard_display(self):
        if self.flashcard_state == 0:
            # Display question
            text = f"Question:\n{self.current_flashcard['question']}\n\n(Press Space to see the answer)"
            self.record_button.config(state='normal')
            self.play_button.config(state='disabled')
        elif self.flashcard_state == 1:
            # Display answer
            text = f"Answer:\n{self.current_flashcard.get('answer', 'No answer provided.')}\n\n(Press Space to see key points)"
            self.record_button.config(state='disabled')
            self.play_button.config(state='normal')
        else:
            # Display key points
            key_points = '\n'.join(self.current_flashcard.get('key_points', []))
            text = f"Key Points:\n{key_points}\n\n(Press Space for next question)"
            self.record_button.config(state='disabled')
            self.play_button.config(state='normal')
        self.flashcard_label.config(text=text)
        # Update spaced repetition info
        flashcard_id = self.current_flashcard['id']
        last_practiced = self.practice_history.get(flashcard_id, None)
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
        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access microphone: {str(e)}")
            return
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
        try:
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                            rate=wf.getframerate(), output=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")
            return
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def get_current_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_practice_history(self):
        with open("practice_history.json", "w", encoding='utf-8') as f:
            json.dump(self.practice_history, f, ensure_ascii=False, indent=2)

    def load_practice_history(self):
        try:
            if os.path.exists("practice_history.json"):
                with open("practice_history.json", "r", encoding='utf-8') as f:
                    self.practice_history = json.load(f)
                # Ensure practice_history is a dict
                if not isinstance(self.practice_history, dict):
                    self.practice_history = {}
            else:
                self.practice_history = {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load practice history: {str(e)}")
            self.practice_history = {}

    # ----------------------- Progress Tracking -----------------------
    def create_progress_tracking(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Progress Tracking", font=('Helvetica', 16)).pack(pady=10)

        # For simplicity, we will just show a list of last practiced dates
        tree = ttk.Treeview(main_frame, columns=('Question', 'Last Practiced'), show='headings')
        tree.heading('Question', text='Question')
        tree.heading('Last Practiced', text='Last Practiced')
        tree.pack(fill='both', expand=True)

        # Load data
        for q in self.questions:
            qid = q.get('id')
            last_practiced = self.practice_history.get(qid, 'Never')
            tree.insert('', 'end', values=(q['question'], last_practiced))

    # 程序入口
def main():
    root = tk.Tk()
    app = AmazonInterviewPrep(root)
    root.mainloop()

if __name__ == "__main__":
    main()

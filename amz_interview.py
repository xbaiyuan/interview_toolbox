import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import random
import threading
import pyaudio
import wave
import datetime

class LPMatrixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Interview Preparation Tool")
        self.root.geometry("1200x800")

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
        self.experiences = self.load_experiences()
        self.common_questions = self.load_common_questions()
        self.matrix_data = self.load_matrix_data()
        self.lp_questions = self.load_lp_questions()
        self.practice_history = self.load_practice_history()
        self.interview_framework = self.load_interview_framework()

        self.create_gui()

    def create_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)

        # Experience Library Tab
        self.experience_frame = ttk.Frame(self.notebook)
        self.create_experience_library(self.experience_frame)

        # Common Questions Tab
        self.common_questions_frame = ttk.Frame(self.notebook)
        self.create_common_questions(self.common_questions_frame)

        # LP Story Matrix Tab
        self.matrix_frame = ttk.Frame(self.notebook)
        self.create_matrix_view(self.matrix_frame)

        # Interview Framework Tab
        self.framework_frame = ttk.Frame(self.notebook)
        self.create_interview_framework(self.framework_frame)

        # Practice Tab
        self.practice_frame = ttk.Frame(self.notebook)
        self.create_practice_tab(self.practice_frame)

        # Progress Tracking Tab
        self.progress_frame = ttk.Frame(self.notebook)
        self.create_progress_tracking(self.progress_frame)

        # Add tabs to notebook
        self.notebook.add(self.experience_frame, text="Experience Library")
        self.notebook.add(self.common_questions_frame, text="Common Questions")
        self.notebook.add(self.matrix_frame, text="LP Story Matrix")
        self.notebook.add(self.framework_frame, text="Interview Framework")
        self.notebook.add(self.practice_frame, text="Practice")
        self.notebook.add(self.progress_frame, text="Progress Tracking")

        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

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
        self.exp_desc_text = scrolledtext.ScrolledText(exp_details_frame, height=10)
        self.exp_desc_text.grid(row=2, column=1, sticky='nsew', pady=2)

        ttk.Label(exp_details_frame, text="Leadership Principles:").grid(row=3, column=0, sticky='nw')
        self.exp_lp_frame = ttk.Frame(exp_details_frame)
        self.exp_lp_frame.grid(row=3, column=1, sticky='nw')

        # LP Checkboxes
        self.exp_lp_vars = {}
        for lp in self.leadership_principles:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.exp_lp_frame, text=lp, variable=var)
            cb.pack(anchor='w')
            self.exp_lp_vars[lp] = var

        # Buttons
        button_frame = ttk.Frame(exp_details_frame)
        button_frame.grid(row=4, column=1, sticky='e', pady=5)

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
            index = selection[0]
            experience = self.experiences[index]
            self.load_experience_details(experience)

    def load_experience_details(self, experience):
        self.exp_title_var.set(experience['title'])
        self.exp_desc_text.delete('1.0', tk.END)
        self.exp_desc_text.insert('1.0', experience['description'])
        for lp in self.leadership_principles:
            self.exp_lp_vars[lp].set(lp in experience['leadership_principles'])

    def save_experience(self):
        title = self.exp_title_var.get().strip()
        description = self.exp_desc_text.get('1.0', tk.END).strip()
        leadership_principles = [lp for lp in self.leadership_principles if self.exp_lp_vars[lp].get()]

        if not title:
            messagebox.showerror("Error", "Please enter a title for the experience.")
            return

        experience = {
            'title': title,
            'description': description,
            'leadership_principles': leadership_principles
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
        for var in self.exp_lp_vars.values():
            var.set(False)

    def load_experiences(self):
        try:
            if os.path.exists("experiences.json"):
                with open("experiences.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load experiences: {str(e)}")
            return []

    def save_experiences(self):
        with open("experiences.json", "w", encoding='utf-8') as f:
            json.dump(self.experiences, f, ensure_ascii=False, indent=2)

    # ----------------------- Common Questions -----------------------
    def create_common_questions(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Questions List
        question_list_frame = ttk.Frame(main_frame)
        question_list_frame.pack(side='left', fill='y')

        ttk.Label(question_list_frame, text="Common Questions", font=('Helvetica', 14)).pack(pady=5)

        self.question_listbox = tk.Listbox(question_list_frame)
        self.question_listbox.pack(fill='y', expand=True)
        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)

        # Add questions to listbox
        self.update_question_listbox()

        # Question Details
        question_details_frame = ttk.Frame(main_frame)
        question_details_frame.pack(side='right', fill='both', expand=True)

        ttk.Label(question_details_frame, text="Question Details", font=('Helvetica', 14)).grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(question_details_frame, text="Question:").grid(row=1, column=0, sticky='nw')
        self.question_text = scrolledtext.ScrolledText(question_details_frame, height=5)
        self.question_text.grid(row=1, column=1, sticky='nsew', pady=2)

        ttk.Label(question_details_frame, text="Your Answer:").grid(row=2, column=0, sticky='nw')
        self.answer_text = scrolledtext.ScrolledText(question_details_frame, height=10)
        self.answer_text.grid(row=2, column=1, sticky='nsew', pady=2)

        # Buttons
        button_frame = ttk.Frame(question_details_frame)
        button_frame.grid(row=3, column=1, sticky='e', pady=5)

        ttk.Button(button_frame, text="Save Answer", command=self.save_answer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_answer_form).pack(side="left", padx=5)

        question_details_frame.columnconfigure(1, weight=1)
        question_details_frame.rowconfigure(2, weight=1)

    def update_question_listbox(self):
        self.question_listbox.delete(0, tk.END)
        for q in self.common_questions:
            self.question_listbox.insert(tk.END, q['question'])

    def on_question_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            question = self.common_questions[index]
            self.load_question_details(question)

    def load_question_details(self, question):
        self.question_text.delete('1.0', tk.END)
        self.question_text.insert('1.0', question['question'])
        self.answer_text.delete('1.0', tk.END)
        self.answer_text.insert('1.0', question.get('answer', ''))

    def save_answer(self):
        question_text = self.question_text.get('1.0', tk.END).strip()
        answer_text = self.answer_text.get('1.0', tk.END).strip()

        if not question_text:
            messagebox.showerror("Error", "Please select or enter a question.")
            return

        # Check if updating existing question
        for idx, q in enumerate(self.common_questions):
            if q['question'] == question_text:
                self.common_questions[idx]['answer'] = answer_text
                break
        else:
            self.common_questions.append({'question': question_text, 'answer': answer_text})

        self.save_common_questions()
        self.update_question_listbox()
        messagebox.showinfo("Success", "Answer saved successfully!")

    def clear_answer_form(self):
        self.question_text.delete('1.0', tk.END)
        self.answer_text.delete('1.0', tk.END)

    def load_common_questions(self):
        try:
            if os.path.exists("common_questions.json"):
                with open("common_questions.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default common questions
                return [
                    {'question': 'Tell me about yourself.', 'answer': ''},
                    {'question': 'Why do you want to work at Amazon?', 'answer': ''},
                    {'question': 'Why are you interested in this role?', 'answer': ''}
                ]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load common questions: {str(e)}")
            return []

    def save_common_questions(self):
        with open("common_questions.json", "w", encoding='utf-8') as f:
            json.dump(self.common_questions, f, ensure_ascii=False, indent=2)

    # ----------------------- LP Story Matrix -----------------------
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

        # Update matrix view
        self.update_matrix_view()

    def update_matrix_view(self):
        # Clear existing items
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)

        # Add rows
        for exp in self.experiences:
            exp_title = exp['title']
            values = [exp_title]
            for lp in self.leadership_principles:
                if exp_title in self.matrix_data and lp in self.matrix_data[exp_title]:
                    score = self.matrix_data[exp_title][lp]["score"]
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

        self.open_story_editor(experience, lp)

    def open_story_editor(self, experience, lp):
        # Open a new window for story editing
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit Story - {experience} - {lp}")
        editor_window.geometry("800x600")

        ttk.Label(editor_window, text=f"Experience: {experience}", font=('Helvetica', 14)).pack(pady=5)
        ttk.Label(editor_window, text=f"Leadership Principle: {lp}", font=('Helvetica', 14)).pack(pady=5)

        # Score selection
        score_frame = ttk.Frame(editor_window)
        score_frame.pack(pady=5)
        ttk.Label(score_frame, text="Score (1-4):").pack(side='left')
        score_var = tk.StringVar()
        score_combo = ttk.Combobox(score_frame, textvariable=score_var, values=['1', '2', '3', '4'])
        score_combo.pack(side='left', padx=5)

        # Key points
        ttk.Label(editor_window, text="Key Points (one per line):").pack(anchor='nw')
        points_text = scrolledtext.ScrolledText(editor_window, height=5)
        points_text.pack(fill='both', expand=True, pady=2)

        # STAR Story
        ttk.Label(editor_window, text="STAR Story:").pack(anchor='nw')
        story_text = scrolledtext.ScrolledText(editor_window, height=10)
        story_text.pack(fill='both', expand=True, pady=2)

        # Load existing data if any
        if experience in self.matrix_data and lp in self.matrix_data[experience]:
            story_data = self.matrix_data[experience][lp]
            score_var.set(str(story_data["score"]))
            points_text.insert('1.0', '\n'.join(story_data["points"]))
            story_text.insert('1.0', story_data["story"])

        # Buttons
        button_frame = ttk.Frame(editor_window)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Save Story", command=lambda: self.save_story(experience, lp, score_var.get(), points_text.get('1.0', tk.END), story_text.get('1.0', tk.END), editor_window)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=editor_window.destroy).pack(side="left", padx=5)

    def save_story(self, experience, lp, score, points, story, window):
        points_list = [p.strip() for p in points.strip().split('\n') if p.strip()]
        story_data = {
            "points": points_list,
            "score": int(score or "0"),
            "story": story.strip()
        }

        if experience not in self.matrix_data:
            self.matrix_data[experience] = {}

        self.matrix_data[experience][lp] = story_data

        self.save_matrix_data()
        self.update_matrix_view()
        messagebox.showinfo("Success", "Story saved successfully!", parent=window)

    def load_matrix_data(self):
        try:
            if os.path.exists("lp_matrix_data.json"):
                with open("lp_matrix_data.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load LP matrix data: {str(e)}")
            return {}

    def save_matrix_data(self):
        with open("lp_matrix_data.json", "w", encoding='utf-8') as f:
            json.dump(self.matrix_data, f, ensure_ascii=False, indent=2)

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
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load interview framework: {str(e)}")
            return {}

    def save_framework_data(self):
        with open("interview_framework.json", "w", encoding='utf-8') as f:
            json.dump(self.interview_framework, f, ensure_ascii=False, indent=2)

    # ----------------------- Practice -----------------------
    def create_practice_tab(self, parent):
        practice_frame = ttk.Frame(parent)
        practice_frame.pack(expand=True, fill='both', padx=10, pady=10)

        ttk.Label(practice_frame, text="Integrated Practice Mode", font=("Helvetica", 16)).pack(pady=10)

        # Mode selection
        mode_frame = ttk.Frame(practice_frame)
        mode_frame.pack(pady=5)

        ttk.Label(mode_frame, text="Select Practice Mode:").pack(side='left', padx=5)
        self.practice_mode_var = tk.StringVar()
        self.practice_mode_var.set('LP Questions')
        practice_modes = ['LP Questions', 'Common Questions', 'Integrated']
        self.practice_mode_combo = ttk.Combobox(mode_frame, textvariable=self.practice_mode_var, values=practice_modes, state='readonly')
        self.practice_mode_combo.pack(side='left', padx=5)

        # Start Practice Button
        ttk.Button(mode_frame, text="Start Practice", command=self.start_practice).pack(side='left', padx=5)

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
        mode = self.practice_mode_var.get()
        if mode == 'LP Questions':
            lp = random.choice(self.leadership_principles)
            flashcards = self.lp_questions.get(lp, [])
            if not flashcards:
                messagebox.showinfo("Info", f"No questions available for {lp}")
                return
            self.current_practice_lp = lp
            # Use spaced repetition to select the next question
            flashcard = self.select_flashcard(lp, flashcards)
            self.current_flashcard = flashcard
        elif mode == 'Common Questions':
            if not self.common_questions:
                messagebox.showinfo("Info", "No common questions available.")
                return
            # Use spaced repetition to select the next question
            flashcard = self.select_common_question()
            self.current_flashcard = flashcard
        else:  # Integrated mode
            all_flashcards = []
            for lp, questions in self.lp_questions.items():
                for q in questions:
                    q_copy = q.copy()
                    q_copy['lp'] = lp
                    all_flashcards.append(q_copy)
            for q in self.common_questions:
                q_copy = q.copy()
                q_copy['type'] = 'common'
                all_flashcards.append(q_copy)
            if not all_flashcards:
                messagebox.showinfo("Info", "No questions available.")
                return
            random.shuffle(all_flashcards)
            self.current_flashcard = all_flashcards[0]

        self.flashcard_state = 0
        self.update_flashcard_display()

    def select_flashcard(self, lp, flashcards):
        # Simple spaced repetition implementation
        history = self.practice_history.get(lp, {})
        # Sort flashcards by last practiced date
        flashcards.sort(key=lambda x: history.get(x['id'], 0))
        return flashcards[0]

    def select_common_question(self):
        # Simple spaced repetition implementation
        history = self.practice_history.get('Common Questions', {})
        # Assign IDs if not present
        for idx, q in enumerate(self.common_questions):
            if 'id' not in q:
                q['id'] = f"CQ{idx}"
        # Sort questions by last practiced date
        self.common_questions.sort(key=lambda x: history.get(x['id'], 0))
        return self.common_questions[0]

    def next_flashcard_content(self, event):
        if self.current_flashcard is None:
            return
        self.flashcard_state = (self.flashcard_state + 1) % 2  # For simplicity, only question and answer
        self.update_flashcard_display()
        if self.flashcard_state == 0:
            # Update practice history
            if 'lp' in self.current_flashcard:
                lp = self.current_flashcard['lp']
                flashcard_id = self.current_flashcard['id']
            elif 'type' in self.current_flashcard and self.current_flashcard['type'] == 'common':
                lp = 'Common Questions'
                flashcard_id = self.current_flashcard['id']
            else:
                return
            self.practice_history.setdefault(lp, {})[flashcard_id] = self.get_current_timestamp()
            self.save_practice_history()

    def update_flashcard_display(self):
        mode = self.practice_mode_var.get()
        if self.flashcard_state == 0:
            # Display question
            if mode == 'LP Questions' or ('lp' in self.current_flashcard):
                text = f"Leadership Principle: {self.current_practice_lp}\n\nQuestion:\n{self.current_flashcard['question']}\n\n(Press Space to see the answer)"
            else:
                text = f"Question:\n{self.current_flashcard['question']}\n\n(Press Space to see the answer)"
            self.record_button.config(state='normal')
            self.play_button.config(state='disabled')
        else:
            # Display answer
            text = f"Answer:\n{self.current_flashcard.get('answer', 'No answer provided.')}\n\n(Press Space for next question)"
            self.record_button.config(state='disabled')
            self.play_button.config(state='normal')
        self.flashcard_label.config(text=text)
        # Update spaced repetition info
        if 'lp' in self.current_flashcard:
            lp = self.current_flashcard['lp']
            flashcard_id = self.current_flashcard['id']
        elif 'type' in self.current_flashcard and self.current_flashcard['type'] == 'common':
            lp = 'Common Questions'
            flashcard_id = self.current_flashcard['id']
        else:
            return
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

    def get_current_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_practice_history(self):
        with open("practice_history.json", "w", encoding='utf-8') as f:
            json.dump(self.practice_history, f, ensure_ascii=False, indent=2)

    def load_practice_history(self):
        try:
            if os.path.exists("practice_history.json"):
                with open("practice_history.json", "r", encoding='utf-8') as f:
                    return json.load(f)
                return {}
            else:
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load practice history: {str(e)}")
            return {}

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
        for lp, history in self.practice_history.items():
            for qid, date in history.items():
                # Find the question text
                question_text = ''
                if lp == 'Common Questions':
                    for q in self.common_questions:
                        if q.get('id') == qid:
                            question_text = q['question']
                            break
                else:
                    for q in self.lp_questions.get(lp, []):
                        if q['id'] == qid:
                            question_text = q['question']
                            break
                tree.insert('', 'end', values=(question_text, date))

    # -----------------------------------------------------------------

def main():
    root = tk.Tk()
    app = LPMatrixGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

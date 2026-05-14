import tkinter as tk
from tkinter import filedialog


class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, blank_symbol,
                 start_state, accept_state, reject_state, transitions):
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.blank_symbol = blank_symbol
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.transitions = transitions

    def get_simulation_steps(self, input_string, max_steps=1000):
        steps = []

        tape = list(input_string)

        if len(tape) == 0:
            tape.append(self.blank_symbol)

        head = 0
        current_state = self.start_state
        step = 0

        while step <= max_steps:
            steps.append({
                "step": step,
                "state": current_state,
                "tape": tape.copy(),
                "head": head,
                "message": ""
            })

            if current_state == self.accept_state:
                return True, steps, "String Accepted"

            if current_state == self.reject_state:
                return False, steps, "String Rejected"

            if head < 0:
                tape.insert(0, self.blank_symbol)
                head = 0

            if head >= len(tape):
                tape.append(self.blank_symbol)

            read_symbol = tape[head]
            key = (current_state, read_symbol)

            if key not in self.transitions:
                steps.append({
                    "step": step + 1,
                    "state": current_state,
                    "tape": tape.copy(),
                    "head": head,
                    "message": "No transition found for " + str(key)
                })
                return False, steps, "String Rejected"

            new_state, write_symbol, direction = self.transitions[key]

            tape[head] = write_symbol
            current_state = new_state

            if direction == "R":
                head += 1
            elif direction == "L":
                head -= 1
            elif direction == "S":
                pass
            else:
                steps.append({
                    "step": step + 1,
                    "state": current_state,
                    "tape": tape.copy(),
                    "head": head,
                    "message": "Invalid direction: " + direction
                })
                return False, steps, "String Rejected"

            step += 1

        return False, steps, "Maximum number of steps reached"


def read_tm_from_file(filename):
    states = []
    input_alphabet = []
    tape_alphabet = []
    blank_symbol = ""
    start_state = ""
    accept_state = ""
    reject_state = ""
    test_string = ""
    transitions = {}

    reading_transitions = False

    try:
        file = open(filename, "r")
    except FileNotFoundError:
        return None, None, "File not found."

    for line in file:
        line = line.strip()

        if line == "" or line.startswith("#"):
            continue

        if line == "transitions:":
            reading_transitions = True
            continue

        if reading_transitions:
            parts = line.split()

            if len(parts) != 5:
                file.close()
                return None, None, "Invalid transition line: " + line

            current_state = parts[0]
            read_symbol = parts[1]
            new_state = parts[2]
            write_symbol = parts[3]
            direction = parts[4]

            transitions[(current_state, read_symbol)] = (
                new_state,
                write_symbol,
                direction
            )

        else:
            if ":" not in line:
                file.close()
                return None, None, "Invalid line: " + line

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "states":
                states = value.split()
            elif key == "input_alphabet":
                input_alphabet = value.split()
            elif key == "tape_alphabet":
                tape_alphabet = value.split()
            elif key == "blank":
                blank_symbol = value
            elif key == "start":
                start_state = value
            elif key == "accept":
                accept_state = value
            elif key == "reject":
                reject_state = value
            elif key == "test_string":
                test_string = value
            else:
                file.close()
                return None, None, "Unknown key: " + key

    file.close()

    tm = TuringMachine(
        states,
        input_alphabet,
        tape_alphabet,
        blank_symbol,
        start_state,
        accept_state,
        reject_state,
        transitions
    )

    return tm, test_string, ""


def validate_input_string(input_string, input_alphabet):
    for symbol in input_string:
        if symbol not in input_alphabet:
            return False, symbol
    return True, ""


class TuringMachineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Turing Machine Simulator")
        self.root.geometry("950x700")
        self.root.configure(bg="#1e1e2e")

        self.filename = ""
        self.steps = []
        self.current_step_index = 0
        self.final_result = ""
        self.animation_running = False

        title = tk.Label(
            root,
            text="Turing Machine Simulator",
            font=("Arial", 26, "bold"),
            bg="#1e1e2e",
            fg="#ffffff"
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            root,
            text="Animated tape simulation with moving head",
            font=("Arial", 13),
            bg="#1e1e2e",
            fg="#cdd6f4"
        )
        subtitle.pack(pady=5)

        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=15)

        choose_button = tk.Button(
            button_frame,
            text="Choose TM File",
            font=("Arial", 12, "bold"),
            bg="#89b4fa",
            fg="#000000",
            width=18,
            command=self.choose_file
        )
        choose_button.grid(row=0, column=0, padx=8)

        load_button = tk.Button(
            button_frame,
            text="Load Simulation",
            font=("Arial", 12, "bold"),
            bg="#f9e2af",
            fg="#000000",
            width=18,
            command=self.load_simulation
        )
        load_button.grid(row=0, column=1, padx=8)

        start_button = tk.Button(
            button_frame,
            text="Start Animation",
            font=("Arial", 12, "bold"),
            bg="#a6e3a1",
            fg="#000000",
            width=18,
            command=self.start_animation
        )
        start_button.grid(row=0, column=2, padx=8)

        reset_button = tk.Button(
            button_frame,
            text="Reset",
            font=("Arial", 12, "bold"),
            bg="#f38ba8",
            fg="#000000",
            width=18,
            command=self.reset_simulation
        )
        reset_button.grid(row=0, column=3, padx=8)

        self.file_label = tk.Label(
            root,
            text="No file selected",
            font=("Arial", 11),
            bg="#1e1e2e",
            fg="#bac2de"
        )
        self.file_label.pack(pady=5)

        self.info_label = tk.Label(
            root,
            text="Step: -    State: -",
            font=("Arial", 16, "bold"),
            bg="#1e1e2e",
            fg="#ffffff"
        )
        self.info_label.pack(pady=15)

        self.tape_frame = tk.Frame(root, bg="#1e1e2e")
        self.tape_frame.pack(pady=10)

        self.head_label = tk.Label(
            root,
            text="Head",
            font=("Arial", 15, "bold"),
            bg="#1e1e2e",
            fg="#f9e2af"
        )
        self.head_label.pack(pady=5)

        self.result_label = tk.Label(
            root,
            text="Result will appear here",
            font=("Arial", 18, "bold"),
            bg="#1e1e2e",
            fg="#ffffff"
        )
        self.result_label.pack(pady=15)

        output_title = tk.Label(
            root,
            text="Simulation Log",
            font=("Arial", 14, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        )
        output_title.pack(pady=5)

        output_frame = tk.Frame(root, bg="#313244")
        output_frame.pack(padx=25, pady=10, fill="both", expand=True)

        self.output_text = tk.Text(
            output_frame,
            font=("Consolas", 11),
            bg="#11111b",
            fg="#cdd6f4",
            insertbackground="#ffffff",
            wrap="none",
            height=10
        )
        self.output_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Turing Machine File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )

        if file_path:
            self.filename = file_path
            self.file_label.config(text="Selected file: " + file_path)

    def load_simulation(self):
        self.output_text.delete("1.0", tk.END)
        self.result_label.config(text="Result will appear here", fg="#ffffff")
        self.clear_tape_display()

        if self.filename == "":
            self.result_label.config(text="Please choose a file first", fg="#f38ba8")
            return

        tm, test_string, error = read_tm_from_file(self.filename)

        if tm is None:
            self.result_label.config(text="Error loading machine", fg="#f38ba8")
            self.output_text.insert(tk.END, error)
            return

        valid, invalid_symbol = validate_input_string(test_string, tm.input_alphabet)

        if not valid:
            self.result_label.config(text="Rejected", fg="#f38ba8")
            self.output_text.insert(
                tk.END,
                "Invalid input symbol: " + invalid_symbol + "\nResult: String Rejected"
            )
            return

        accepted, steps, final_result = tm.get_simulation_steps(test_string)

        self.steps = steps
        self.current_step_index = 0
        self.final_result = final_result
        self.animation_running = False

        self.output_text.insert(tk.END, "Machine loaded successfully.\n")
        self.output_text.insert(tk.END, "Test string: " + test_string + "\n")
        self.output_text.insert(tk.END, "Total steps: " + str(len(steps)) + "\n\n")

        if len(self.steps) > 0:
            self.show_step(0)

    def start_animation(self):
        if len(self.steps) == 0:
            self.result_label.config(text="Load a simulation first", fg="#f38ba8")
            return

        if self.animation_running:
            return

        self.animation_running = True
        self.animate_next_step()

    def animate_next_step(self):
        if not self.animation_running:
            return

        if self.current_step_index >= len(self.steps):
            self.animation_running = False

            if self.final_result == "String Accepted":
                self.result_label.config(text="Accepted", fg="#a6e3a1")
            else:
                self.result_label.config(text="Rejected", fg="#f38ba8")

            return

        self.show_step(self.current_step_index)
        self.current_step_index += 1

        self.root.after(2000, self.animate_next_step)

    def show_step(self, index):
        step_data = self.steps[index]

        step_number = step_data["step"]
        state = step_data["state"]
        tape = step_data["tape"]
        head = step_data["head"]
        message = step_data["message"]

        self.info_label.config(
            text="Step: " + str(step_number) + "    State: " + state
        )

        self.draw_tape(tape, head)

        log = "Step " + str(step_number) + " | State: " + state + " | Tape: " + "".join(tape)

        if message != "":
            log += " | " + message

        log += "\n"

        self.output_text.insert(tk.END, log)
        self.output_text.see(tk.END)

    def draw_tape(self, tape, head):
        self.clear_tape_display()

        for i in range(len(tape)):
            if i == head:
                bg_color = "#f9e2af"
                fg_color = "#000000"
            else:
                bg_color = "#313244"
                fg_color = "#ffffff"

            cell = tk.Label(
                self.tape_frame,
                text=tape[i],
                font=("Arial", 18, "bold"),
                width=4,
                height=2,
                bg=bg_color,
                fg=fg_color,
                relief="solid",
                borderwidth=2
            )
            cell.grid(row=0, column=i, padx=3)

        arrow_row = tk.Frame(self.tape_frame, bg="#1e1e2e")
        arrow_row.grid(row=1, column=0, columnspan=len(tape), pady=5)

        for i in range(len(tape)):
            arrow = "▲" if i == head else " "
            arrow_label = tk.Label(
                arrow_row,
                text=arrow,
                font=("Arial", 16, "bold"),
                width=4,
                bg="#1e1e2e",
                fg="#f9e2af"
            )
            arrow_label.grid(row=0, column=i, padx=3)

    def clear_tape_display(self):
        for widget in self.tape_frame.winfo_children():
            widget.destroy()

    def reset_simulation(self):
        self.animation_running = False
        self.current_step_index = 0
        self.output_text.delete("1.0", tk.END)
        self.result_label.config(text="Result will appear here", fg="#ffffff")
        self.info_label.config(text="Step: -    State: -")
        self.clear_tape_display()

        if len(self.steps) > 0:
            self.show_step(0)

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    app = TuringMachineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
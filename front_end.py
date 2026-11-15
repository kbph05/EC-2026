import json
import os
import re
import webbrowser
import map_drawer
import tkinter as tk
from tkinter import ttk, messagebox
from transport import find_route
import dom_lib_of_greatness

MAP_IMG_PATH = r"temp/map.png"
RESULTS_PATH = r"temp/result"
POSSIBLE_LOCATION = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'J1', 'J2', 'J3', 'J4']
START_LOCATIONS = POSSIBLE_LOCATION
TRANSPORT_OPTIONS = ["Car", "Walk", "Walking with A Child", "Wheelchair", "Bicycle", "Wheelchair (stolen)"]
CLOSED_PATH_PATTERN = re.compile(r"^([A-Za-z]\d?)-?([A-Za-z]\d?)$")

with open(map_drawer.EDGE_POS_FILE_PATH) as f:
    VALID_EDGES = set(json.load(f).keys())

class MapApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Map Route Planner")
        self.root.resizable(False, False)

        root.lift()
        root.focus_force()

        #Display Map
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=(10, 5), padx=15)

        self.map_photo = None
        self.img_label = None
        self.display_map()

        #Set Input Options
        self.controls_frame = tk.LabelFrame(self.root, text="Current Status", padx=10, pady=10)
        self.controls_frame.pack(padx=15, pady=5, fill="x")

        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.columnconfigure(1, weight=1)

        #Start Location
        tk.Label(self.controls_frame, text="Start Location:").grid(row=0, column=0, sticky="w", padx=10)

        locations = START_LOCATIONS
        self.start_var = tk.StringVar(value=locations[0])

        self.start_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.start_var, values=locations, state="readonly", width=10)
        self.start_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        #Transport Options
        tk.Label(self.controls_frame, text="Method of Transport:").grid(row=0, column=1, sticky="w", padx=10)
        transports = TRANSPORT_OPTIONS
        self.transport_var = tk.StringVar(value=transports[0])

        self.transport_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.transport_var, values=transports, state="readonly", width=10)
        self.transport_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        #Flooded Regions & Closed Paths Option
        self.lists_frame = tk.Frame(self.root)
        self.lists_frame.pack(padx=15, fill="x")
        self.lists_frame.columnconfigure(0, weight=1, uniform="lists")
        self.lists_frame.columnconfigure(1, weight=1, uniform="lists")

        self.flooded_listbox = self.build_list_frame(self.lists_frame, "Flooded Regions", column=0, validator=self.validate_flooded, hint="e.g. A or J1")
        self.closed_listbox = self.build_list_frame(self.lists_frame, "Closed Paths", column=1, validator=self.validate_closed_path, hint="e.g. A-B")

        #Advanced Options (custom path weights) - stored here so they persist when the window closes
        self.changed_weights = {}
        self.advanced_win = None

        #Buttons
        btn_row = tk.Frame(self.root)
        btn_row.pack(pady=10)
        ttk.Button(btn_row, text="Advanced Options", command=self.open_advanced_options).pack(side="left", padx=5)
        self.submit_btn = ttk.Button(btn_row, text="Calculate", command=self.on_submit)
        self.submit_btn.pack(side="left", padx=5)

        # Redraw the map whenever the start location changes
        self.start_var.trace_add("write", lambda *args: self.update_map())
        self.update_map()

    def update_map(self):
        vals = self.get_input_vals()
        try:
            map_drawer.draw_map_img(user_pos=vals["start_pos"], nodes=vals["flooded"], edges=vals["closed"])
        except KeyError as e:
            messagebox.showerror("Map Error", f"Can't draw {e} on the map.")
            return
        self.display_map()

    def display_map(self):
        self.map_photo = tk.PhotoImage(file=MAP_IMG_PATH)
        if self.img_label is None:
            self.img_label = tk.Label(self.image_frame, image=self.map_photo)
            self.img_label.pack()
        else:
            self.img_label.config(image=self.map_photo)
        self.img_label.image = self.map_photo

        #Template for the listboxes
    def build_list_frame(self, parent, title, column, validator, hint=""):
        frame = tk.LabelFrame(parent, text=title, padx=8, pady=8)
        frame.grid(row=0, column=column, sticky="nsew", padx=(0, 5) if column == 0 else (5, 0))
        frame.columnconfigure(0, weight=1)

        entry = ttk.Entry(frame, width=6)
        entry.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        listbox = tk.Listbox(frame, height=3, width=8, selectmode="extended")
        listbox.grid(row=1, column=0, columnspan=2, sticky="ew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        listbox.config(yscrollcommand=scrollbar.set)

        tk.Label(frame, text=hint, fg="gray", font=("Helvetica", 10)).grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))

        add = lambda event=None: self.add_item(entry, listbox, validator)
        ttk.Button(frame, text="Add", width=5, command=add).grid(row=0, column=1, columnspan=2, padx=(5, 0), pady=(0, 5))

        remove = lambda event=None: self.remove_selected(listbox)
        ttk.Button(frame, text="Remove", command=remove).grid(row=3, column=0, columnspan=3, sticky="ew", pady=(5, 0))

        return listbox

    def validate_flooded(self, text):
        letter = text.strip().upper()
        if letter in POSSIBLE_LOCATION:
            return letter
        messagebox.showerror("Invalid Region", f"Flooded region must be one of: {', '.join(POSSIBLE_LOCATION)}.")
        return None

    def validate_closed_path(self, text):
        match = CLOSED_PATH_PATTERN.match(text.strip())
        if match:
            a, b = match.group(1).upper(), match.group(2).upper()
            if a in POSSIBLE_LOCATION and b in POSSIBLE_LOCATION and a != b:
                if "-".join(sorted([a, b])) in VALID_EDGES:
                    return f"{a}-{b}"
                messagebox.showerror("Invalid Path", f"There is no road between {a} and {b}.")
                return None
        messagebox.showerror("Invalid Path", "Closed path must be two different locations, e.g. AB, A-B, or A-J1.")
        return None

    def add_item(self, entry, listbox, validator):
        value = validator(entry.get())
        if value is None:
            return
        if value in listbox.get(0, "end"):
            messagebox.showinfo("Duplicate", f"{value} is already in the list.")
            return
        listbox.insert("end", value)
        entry.delete(0, "end")
        self.update_map()

    def remove_selected(self, listbox):
        for index in reversed(listbox.curselection()):
            listbox.delete(index)
        self.update_map()

    def open_advanced_options(self):
        if self.advanced_win is not None and self.advanced_win.winfo_exists():
            self.advanced_win.lift()
            self.advanced_win.focus_force()
            return

        win = tk.Toplevel(self.root)
        win.title("Advanced Options")
        win.resizable(False, False)
        self.advanced_win = win

        frame = tk.LabelFrame(win, text="Custom Path Weights", padx=8, pady=8)
        frame.pack(padx=15, pady=15, fill="both")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="Path (e.g. A-B):").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="New Weight:").grid(row=0, column=1, sticky="w", padx=(5, 0))

        path_entry = ttk.Entry(frame, width=10)
        path_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        weight_entry = ttk.Entry(frame, width=10)
        weight_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))

        listbox = tk.Listbox(frame, height=5, width=20, selectmode="extended")
        listbox.grid(row=2, column=0, columnspan=3, sticky="ew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=2, column=3, sticky="ns")
        listbox.config(yscrollcommand=scrollbar.set)

        def refresh():
            listbox.delete(0, "end")
            for path, weight in self.changed_weights.items():
                listbox.insert("end", f"{path}: {weight:g}")

        def add(event=None):
            path = self.validate_closed_path(path_entry.get())
            if path is None:
                return
            try:
                weight = float(weight_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Weight", "Weight must be a number.", parent=win)
                return
            if weight <= 0:
                messagebox.showerror("Invalid Weight", "Weight must be greater than 0.", parent=win)
                return
            
            # Treat A-B and B-A as the same path
            a, b = path.split("-")
            reverse = f"{b}-{a}"
            if reverse in self.changed_weights:
                del self.changed_weights[reverse]
            self.changed_weights[path] = weight
            refresh()
            path_entry.delete(0, "end")
            weight_entry.delete(0, "end")
            path_entry.focus_set()

        def remove(event=None):
            keys = list(self.changed_weights.keys())
            for index in reversed(listbox.curselection()):
                del self.changed_weights[keys[index]]
            refresh()

        ttk.Button(frame, text="Add", width=5, command=add).grid(row=1, column=2, columnspan=2, padx=(5, 0), pady=(0, 5))
        ttk.Button(frame, text="Remove", command=remove).grid(row=3, column=0, columnspan=4, sticky="ew", pady=(5, 0))
        path_entry.bind("<Return>", lambda e: weight_entry.focus_set())
        weight_entry.bind("<Return>", add)

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))

        refresh()
        path_entry.focus_set()

    def get_input_vals(self):
        start = self.start_var.get()
        transport = self.transport_var.get()
        flooded = list(self.flooded_listbox.get(0, "end"))
        closed = list(self.closed_listbox.get(0, "end"))
        changed_weights = dict(self.changed_weights)
        return {"start_pos":start, "transport":transport, "flooded":flooded, "closed":closed, "changed_weights":changed_weights}

    def on_submit(self, not_a_stop=None):
        if not_a_stop is None:
            not_a_stop = []

        input_vals = self.get_input_vals()
        results = find_route(input_vals["start_pos"], input_vals["transport"], input_vals["flooded"], input_vals["closed"], not_a_stop, input_vals["changed_weights"])

        if not results:
            self.show_results(None)
            return

        map_drawer.draw_route(results["route"], output_folder=RESULTS_PATH)
        self.show_results(results, not_a_stop)

    def find_alternative(self, win, results, not_a_stop):
        win.destroy()
        self.on_submit(not_a_stop + [results["route"][-1]])

    def save_instructions(self, instructions):
        dom_lib_of_greatness.print_results(instructions)

    def show_results(self, results, not_a_stop=None):
        if not_a_stop is None:
            not_a_stop = []

        if results is None:
            win = tk.Toplevel(self.root)
            win.title("No Route")
            win.resizable(False, False)

            tk.Label(win, text="No safe path found.\nYou're cooked...", font=("Helvetica", 16, "bold")).pack(padx=20, pady=(15, 5))
            tk.Label(win, text="💀", font=("Helvetica", 360)).pack(padx=20, pady=(0, 15))
            return

        win = tk.Toplevel(self.root)
        win.title("Route Result")
        win.resizable(False, False)

        istructions = dom_lib_of_greatness.print_instructions_v2(results)
        tk.Label(win, text=istructions, justify="left").pack(pady=(0, 8))

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=(0, 8))
        ttk.Button(btn_frame, text="Find Alternative Destination", command=lambda: self.find_alternative(win, results, not_a_stop)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Instructions to File", command=lambda: self.save_instructions(istructions)).pack(side="left", padx=5)

        files = [f for f in os.listdir(RESULTS_PATH) if f.startswith("step") and f.endswith(".png")]
        files.sort(key=lambda f: int(f[4:-4]))
        frames = [tk.PhotoImage(file=os.path.join(RESULTS_PATH, f)) for f in files]

        img_label = tk.Label(win)
        img_label.pack(padx=15, pady=(0, 15))
        img_label.frames = frames

        def cycle(i=0):
            if not win.winfo_exists():
                return
            img_label.config(image=frames[i])
            delay = 1500 if i == len(frames) - 1 else 500
            win.after(delay, cycle, (i + 1) % len(frames))

        if frames:
            cycle()
    

if __name__ == "__main__":
    root = tk.Tk()
    app = MapApp(root)
    root.mainloop()

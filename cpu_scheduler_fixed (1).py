import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import statistics

class CPUSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Visualizer")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)

        self.colors = ["#4F8EF7", "#20A39E", "#F4A261", "#9B5DE5",
                       "#E76F51", "#577590", "#90BE6D", "#F15BB5"]
        self.processes = []
        self.results = []
        self.timeline = []
        self.comparison = []

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", rowheight=27, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=7)
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#526174")

        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#102A43", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="CPU SCHEDULING VISUALIZER",
                 bg="#102A43", fg="white",
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=25, pady=(13, 0))
        tk.Label(header, text="FCFS  •  SJF  •  Priority  •  Round Robin",
                 bg="#102A43", fg="#B8D8F0",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=27)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=14)

        self.dashboard_tab = ttk.Frame(self.notebook, padding=14)
        self.details_tab = ttk.Frame(self.notebook, padding=14)
        self.analysis_tab = ttk.Frame(self.notebook, padding=14)
        self.compare_tab = ttk.Frame(self.notebook, padding=14)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.details_tab, text="Process Details")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.compare_tab, text="Algorithm Comparison")

        self.build_dashboard()
        self.build_details()
        self.build_analysis()
        self.build_comparison()

    def build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="Process Management",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.dashboard_tab, text="Add processes and run a scheduling algorithm.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 12))

        form = ttk.LabelFrame(self.dashboard_tab, text="Add New Process", padding=12)
        form.pack(fill="x", pady=(0, 12))
        self.pid_entry = self.make_field(form, "Process ID", "P1", 0)
        self.at_entry = self.make_field(form, "Arrival Time", "0", 1)
        self.bt_entry = self.make_field(form, "Burst Time", "5", 2)
        self.prio_entry = self.make_field(form, "Priority (lower = higher)", "1", 3)

        ttk.Button(form, text="Add Process", command=self.add_process).grid(
            row=1, column=4, padx=10, sticky="ew")
        ttk.Button(form, text="Remove Selected", command=self.remove_process).grid(
            row=1, column=5, padx=5, sticky="ew")
        ttk.Button(form, text="Clear All", command=self.clear_processes).grid(
            row=1, column=6, padx=5, sticky="ew")

        controls = ttk.LabelFrame(self.dashboard_tab, text="Run Scheduler", padding=12)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Label(controls, text="Algorithm").grid(row=0, column=0, padx=5, sticky="w")
        self.algorithm_var = tk.StringVar(value="FCFS")
        self.algorithm_box = ttk.Combobox(
            controls, textvariable=self.algorithm_var, state="readonly",
            values=["FCFS", "SJF", "Priority", "Round Robin"], width=18)
        self.algorithm_box.grid(row=0, column=1, padx=5)
        ttk.Label(controls, text="Time Quantum").grid(row=0, column=2, padx=(18, 5))
        self.quantum_entry = ttk.Entry(controls, width=8)
        self.quantum_entry.insert(0, "2")
        self.quantum_entry.grid(row=0, column=3, padx=5)
        ttk.Button(controls, text="Run Scheduling", command=self.run_scheduler).grid(
            row=0, column=4, padx=15)
        ttk.Button(controls, text="Open Gantt Chart", command=self.open_gantt).grid(
            row=0, column=5, padx=5)
        ttk.Button(controls, text="Compare All", command=self.compare_algorithms).grid(
            row=0, column=6, padx=5)

        table_frame = ttk.LabelFrame(self.dashboard_tab, text="Process Information", padding=8)
        table_frame.pack(fill="both", expand=True)
        cols = ("pid", "at", "bt", "priority", "color")
        self.dashboard_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=9)
        for col, title, width in [
            ("pid", "Process ID", 150), ("at", "Arrival Time", 150),
            ("bt", "Burst Time", 150), ("priority", "Priority", 150),
            ("color", "Chart Color", 180)
        ]:
            self.dashboard_tree.heading(col, text=title)
            self.dashboard_tree.column(col, width=width, anchor="center")
        self.dashboard_tree.pack(fill="both", expand=True)

        self.status_label = ttk.Label(self.dashboard_tab, text="Add processes to begin.",
                                      style="Sub.TLabel")
        self.status_label.pack(anchor="w", pady=(8, 0))

    def make_field(self, parent, label, default, column):
        ttk.Label(parent, text=label).grid(row=0, column=column, padx=7, sticky="w")
        entry = ttk.Entry(parent, width=17)
        entry.insert(0, default)
        entry.grid(row=1, column=column, padx=7, pady=(5, 0), sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        return entry

    def build_details(self):
        ttk.Label(self.details_tab, text="Scheduling Results",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.details_tab, text="Completion, turnaround, waiting and response times.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 12))
        cols = ("pid", "at", "bt", "priority", "ct", "tat", "wt", "rt")
        self.details_tree = ttk.Treeview(self.details_tab, columns=cols, show="headings")
        headings = [("pid", "Process"), ("at", "Arrival"), ("bt", "Burst"),
                    ("priority", "Priority"), ("ct", "Completion"),
                    ("tat", "Turnaround"), ("wt", "Waiting"), ("rt", "Response")]
        for c, title in headings:
            self.details_tree.heading(c, text=title)
            self.details_tree.column(c, width=115, anchor="center")
        self.details_tree.pack(fill="both", expand=True)
        self.metrics_label = ttk.Label(self.details_tab, text="Run an algorithm to view metrics.",
                                       font=("Segoe UI", 11, "bold"))
        self.metrics_label.pack(anchor="w", pady=12)

    def build_analysis(self):
        ttk.Label(self.analysis_tab, text="Scheduling Analysis",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.analysis_tab, text="A readable explanation of the selected algorithm's result.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 12))
        self.analysis_text = tk.Text(self.analysis_tab, wrap="word", font=("Consolas", 11),
                                     bg="#F7FAFC", fg="#243B53", padx=14, pady=14,
                                     relief="flat")
        self.analysis_text.pack(fill="both", expand=True)
        self.analysis_text.insert("1.0", "Run a scheduling algorithm to generate the analysis.")
        self.analysis_text.config(state="disabled")

    def build_comparison(self):
        ttk.Label(self.compare_tab, text="Algorithm Comparison",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.compare_tab, text="Compare average turnaround and waiting times.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 12))
        cols = ("algorithm", "avg_tat", "avg_wt", "avg_rt")
        self.comparison_tree = ttk.Treeview(self.compare_tab, columns=cols, show="headings",
                                            height=8)
        for c, title in [("algorithm", "Algorithm"), ("avg_tat", "Average Turnaround"),
                         ("avg_wt", "Average Waiting"), ("avg_rt", "Average Response")]:
            self.comparison_tree.heading(c, text=title)
            self.comparison_tree.column(c, width=190, anchor="center")
        self.comparison_tree.pack(fill="x", pady=(0, 15))
        self.comparison_note = ttk.Label(self.compare_tab, text="Click Compare All to populate results.",
                                         font=("Segoe UI", 11, "bold"))
        self.comparison_note.pack(anchor="w")

    def add_process(self):
        pid = self.pid_entry.get().strip()
        try:
            at = int(self.at_entry.get())
            bt = int(self.bt_entry.get())
            prio = int(self.prio_entry.get())
            if not pid or at < 0 or bt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Enter a process ID, arrival time >= 0, burst time > 0, and integer priority.")
            return

        if any(p["pid"].casefold() == pid.casefold() for p in self.processes):
            messagebox.showerror("Duplicate Process", "This Process ID already exists.")
            return

        color = self.colors[len(self.processes) % len(self.colors)]
        self.processes.append({"pid": pid, "at": at, "bt": bt,
                               "prio": prio, "color": color})
        self.refresh_dashboard()
        self.invalidate_results()
        self.pid_entry.delete(0, tk.END)
        self.pid_entry.insert(0, f"P{len(self.processes) + 1}")
        self.at_entry.delete(0, tk.END)
        self.at_entry.insert(0, "0")
        self.bt_entry.delete(0, tk.END)
        self.bt_entry.insert(0, "5")

    def remove_process(self):
        selected = self.dashboard_tree.selection()
        if not selected:
            messagebox.showinfo("Select Process", "Select a process to remove.")
            return
        ids = {self.dashboard_tree.item(item, "values")[0] for item in selected}
        self.processes = [p for p in self.processes if p["pid"] not in ids]
        self.refresh_dashboard()
        self.invalidate_results()

    def clear_processes(self):
        if not self.processes:
            return
        if messagebox.askyesno("Clear All", "Remove all processes?"):
            self.processes.clear()
            self.refresh_dashboard()
            self.invalidate_results()

    def refresh_dashboard(self):
        self.dashboard_tree.delete(*self.dashboard_tree.get_children())
        for p in self.processes:
            self.dashboard_tree.insert("", "end",
                values=(p["pid"], p["at"], p["bt"], p["prio"], p["color"]))

    def invalidate_results(self):
        self.results = []
        self.timeline = []
        self.details_tree.delete(*self.details_tree.get_children())
        self.comparison_tree.delete(*self.comparison_tree.get_children())
        self.metrics_label.config(text="Process list changed. Run scheduling again.")
        self.comparison_note.config(text="Run Compare All to generate fresh comparison data.")
        self.analysis_text.config(state="normal")
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", "Process list changed. Run scheduling again.")
        self.analysis_text.config(state="disabled")
        self.status_label.config(text=f"{len(self.processes)} process(es) loaded. Results need recalculation.")

    def calculate(self, algorithm, source, quantum=2):
        if not source:
            return [], []
        procs = [dict(p) for p in source]
        n = len(procs)
        remaining = [p["bt"] for p in procs]
        first_start = [None] * n
        completion = [0] * n
        timeline = []
        time = 0
        completed = 0

        def add_segment(index, start, end):
            if end <= start:
                return
            pid = "IDLE" if index is None else procs[index]["pid"]
            color = "#CBD5E0" if index is None else procs[index]["color"]
            if timeline and timeline[-1][0] == pid and timeline[-1][2] == start:
                timeline[-1] = (pid, timeline[-1][1], end, color)
            else:
                timeline.append((pid, start, end, color))

        if algorithm in ("FCFS", "SJF", "Priority"):
            pending = set(range(n))
            while pending:
                ready = [i for i in pending if procs[i]["at"] <= time]
                if not ready:
                    next_time = min(procs[i]["at"] for i in pending)
                    add_segment(None, time, next_time)
                    time = next_time
                    ready = [i for i in pending if procs[i]["at"] <= time]

                if algorithm == "FCFS":
                    idx = min(ready, key=lambda i: (procs[i]["at"], i))
                elif algorithm == "SJF":
                    idx = min(ready, key=lambda i: (procs[i]["bt"], procs[i]["at"], i))
                else:
                    idx = min(ready, key=lambda i: (procs[i]["prio"], procs[i]["at"], i))

                start = time
                if first_start[idx] is None:
                    first_start[idx] = start
                time += procs[idx]["bt"]
                completion[idx] = time
                add_segment(idx, start, time)
                pending.remove(idx)
        else:
            if quantum <= 0:
                raise ValueError("Time quantum must be positive.")
            arrival_order = sorted(range(n), key=lambda i: (procs[i]["at"], i))
            next_arrival = 0
            ready_queue = deque()
            while completed < n:
                while next_arrival < n and procs[arrival_order[next_arrival]]["at"] <= time:
                    ready_queue.append(arrival_order[next_arrival])
                    next_arrival += 1
                if not ready_queue:
                    next_time = procs[arrival_order[next_arrival]]["at"]
                    add_segment(None, time, next_time)
                    time = next_time
                    continue
                idx = ready_queue.popleft()
                if first_start[idx] is None:
                    first_start[idx] = time
                run_for = min(quantum, remaining[idx])
                start = time
                time += run_for
                remaining[idx] -= run_for
                add_segment(idx, start, time)
                while next_arrival < n and procs[arrival_order[next_arrival]]["at"] <= time:
                    ready_queue.append(arrival_order[next_arrival])
                    next_arrival += 1
                if remaining[idx] > 0:
                    ready_queue.append(idx)
                else:
                    completion[idx] = time
                    completed += 1

        results = []
        for i, p in enumerate(procs):
            tat = completion[i] - p["at"]
            wt = tat - p["bt"]
            rt = first_start[i] - p["at"]
            results.append({**p, "ct": completion[i], "tat": tat, "wt": wt, "rt": rt})
        results.sort(key=lambda x: x["pid"])
        return timeline, results

    def run_scheduler(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Add at least one process first.")
            return
        algo = self.algorithm_var.get()
        try:
            quantum = int(self.quantum_entry.get())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            if algo == "Round Robin":
                messagebox.showerror("Invalid Quantum", "Enter a positive integer time quantum.")
                return
            quantum = 2

        try:
            self.timeline, self.results = self.calculate(algo, self.processes, quantum)
        except ValueError as exc:
            messagebox.showerror("Scheduling Error", str(exc))
            return
        self.current_algorithm = algo
        self.update_details()
        self.update_analysis()
        self.status_label.config(text=f"{algo} completed successfully.")
        self.notebook.select(self.details_tab)

    def update_details(self):
        self.details_tree.delete(*self.details_tree.get_children())
        if not self.results:
            self.metrics_label.config(text="No scheduling results available.")
            return
        for p in self.results:
            self.details_tree.insert("", "end", values=(
                p["pid"], p["at"], p["bt"], p["prio"], p["ct"],
                p["tat"], p["wt"], p["rt"]))
        avg_tat = statistics.mean(p["tat"] for p in self.results)
        avg_wt = statistics.mean(p["wt"] for p in self.results)
        avg_rt = statistics.mean(p["rt"] for p in self.results)
        self.metrics_label.config(
            text=f"Average Turnaround Time: {avg_tat:.2f}     "
                 f"Average Waiting Time: {avg_wt:.2f}     "
                 f"Average Response Time: {avg_rt:.2f}")

    def update_analysis(self):
        self.analysis_text.config(state="normal")
        self.analysis_text.delete("1.0", tk.END)
        if not self.results:
            self.analysis_text.insert("1.0", "No results available.")
            self.analysis_text.config(state="disabled")
            return
        avg_tat = statistics.mean(p["tat"] for p in self.results)
        avg_wt = statistics.mean(p["wt"] for p in self.results)
        avg_rt = statistics.mean(p["rt"] for p in self.results)
        total_burst = sum(p["bt"] for p in self.results)
        start_time = min(p["at"] for p in self.results)
        finish_time = max(p["ct"] for p in self.results)
        elapsed = finish_time - start_time
        utilization = (total_burst / elapsed * 100) if elapsed else 0

        lines = [
            f"ALGORITHM: {getattr(self, 'current_algorithm', 'Unknown')}",
            "",
            f"Number of processes: {len(self.results)}",
            f"Total CPU burst time: {total_burst}",
            f"Total elapsed scheduling time: {elapsed}",
            f"CPU utilization (excluding time before first arrival): {utilization:.2f}%",
            "",
            f"Average turnaround time: {avg_tat:.2f}",
            f"Average waiting time: {avg_wt:.2f}",
            f"Average response time: {avg_rt:.2f}",
            "",
            "PROCESS-WISE SUMMARY"
        ]
        for p in self.results:
            lines.append(
                f"{p['pid']}: CT={p['ct']}, TAT={p['tat']}, "
                f"WT={p['wt']}, RT={p['rt']}")
        lines += ["", "Metric definitions:",
                  "Completion Time (CT): time at which a process finishes.",
                  "Turnaround Time (TAT): CT - Arrival Time.",
                  "Waiting Time (WT): TAT - Burst Time.",
                  "Response Time (RT): first CPU start - Arrival Time.",
                  "", "Lower average waiting and turnaround times are generally preferable."]
        self.analysis_text.insert("1.0", "\n".join(lines))
        self.analysis_text.config(state="disabled")

    def compare_algorithms(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Add processes before comparison.")
            return
        try:
            quantum = int(self.quantum_entry.get())
            if quantum <= 0:
                quantum = 2
        except ValueError:
            quantum = 2

        self.comparison_tree.delete(*self.comparison_tree.get_children())
        comparison = []
        for algo in ["FCFS", "SJF", "Priority", "Round Robin"]:
            _, results = self.calculate(algo, [dict(p) for p in self.processes], quantum)
            if not results:
                continue
            avg_tat = statistics.mean(p["tat"] for p in results)
            avg_wt = statistics.mean(p["wt"] for p in results)
            avg_rt = statistics.mean(p["rt"] for p in results)
            self.comparison_tree.insert("", "end", values=(
                algo, f"{avg_tat:.2f}", f"{avg_wt:.2f}", f"{avg_rt:.2f}"))
            comparison.append((algo, avg_tat, avg_wt, avg_rt))

        if comparison:
            best = min(comparison, key=lambda x: x[2])
            self.comparison_note.config(
                text=f"Lowest Average Waiting Time: {best[0]} ({best[2]:.2f})")
        else:
            self.comparison_note.config(text="No comparison data available.")

    def open_gantt(self):
        if not self.timeline:
            messagebox.showinfo("No Gantt Chart", "Run an algorithm first to generate the Gantt chart.")
            return
        win = tk.Toplevel(self.root)
        win.title("Gantt Chart")
        win.geometry("1050x480")
        win.minsize(700, 350)
        ttk.Label(win, text=f"Gantt Chart — {getattr(self, 'current_algorithm', '')}",
                  style="Title.TLabel").pack(anchor="w", padx=18, pady=(15, 5))
        canvas_frame = ttk.Frame(win, padding=12)
        canvas_frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(canvas_frame, bg="white", height=220, highlightthickness=1,
                           highlightbackground="#D9E2EC")
        hbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=hbar.set)
        canvas.pack(fill="both", expand=True)
        hbar.pack(fill="x")
        self.draw_gantt(canvas)

        summary = ttk.Label(win, text=self.gantt_summary(), style="Sub.TLabel")
        summary.pack(anchor="w", padx=18, pady=(0, 15))

    def draw_gantt(self, canvas):
        canvas.delete("all")
        if not self.timeline:
            return
        left, top, block_h, scale = 45, 65, 65, 55
        total = self.timeline[-1][2]
        width = max(850, left + total * scale + 70)
        canvas.configure(scrollregion=(0, 0, width, 210))
        canvas.create_text(18, top + block_h / 2, text="CPU", anchor="w",
                           font=("Segoe UI", 10, "bold"))
        for pid, start, end, color in self.timeline:
            x1 = left + start * scale
            x2 = left + end * scale
            canvas.create_rectangle(x1, top, x2, top + block_h,
                                    fill=color, outline="#243B53", width=1)
            canvas.create_text((x1 + x2) / 2, top + block_h / 2,
                               text=pid, fill="white" if pid != "IDLE" else "#243B53",
                               font=("Segoe UI", 10, "bold"))
            canvas.create_line(x1, top + block_h, x1, top + block_h + 18,
                               fill="#243B53")
            canvas.create_text(x1, top + block_h + 22, text=str(start),
                               anchor="n", font=("Segoe UI", 9))
        end_x = left + total * scale
        canvas.create_line(end_x, top + block_h, end_x, top + block_h + 18,
                           fill="#243B53")
        canvas.create_text(end_x, top + block_h + 22, text=str(total),
                           anchor="n", font=("Segoe UI", 9))

    def gantt_summary(self):
        if not self.results:
            return ""
        return (f"Processes: {len(self.results)}   |   "
                f"Average WT: {statistics.mean(p['wt'] for p in self.results):.2f}   |   "
                f"Average TAT: {statistics.mean(p['tat'] for p in self.results):.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerApp(root)
    root.mainloop()

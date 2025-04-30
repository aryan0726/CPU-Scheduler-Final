import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from collections import deque

class Process:
    """Class to represent a Process with all necessary attributes"""
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None
        self.turnaround_time = None
        self.waiting_time = None
        self.response_time = None
        self.execution_history = []  # To store execution intervals for Gantt chart

class CPUSchedulingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("900x700")
        
        # Set up tabbed interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.input_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        self.comparison_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.input_tab, text="Process Input")
        self.notebook.add(self.results_tab, text="Results")
        self.notebook.add(self.comparison_tab, text="Algorithm Comparison")
        
        self.setup_input_tab()
        self.setup_results_tab()
        self.setup_comparison_tab()
        
        self.processes = []
        self.gantt_canvas = None
        
    def setup_input_tab(self):
        """Set up the Process Input tab"""
        # Input fields
        input_frame = ttk.LabelFrame(self.input_tab, text="Add Process")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields_frame = ttk.Frame(input_frame)
        fields_frame.pack(pady=10)
        
        labels = ["Arrival Time:", "Burst Time:", "Priority:"]
        defaults = ["0", "5", "1"]
        entries = []
        
        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(fields_frame, text=label).grid(row=0, column=i*2, padx=5)
            entry = ttk.Entry(fields_frame, width=8)
            entry.grid(row=0, column=i*2+1, padx=5)
            entry.insert(0, default)
            entries.append(entry)
        
        self.at_entry, self.bt_entry, self.pr_entry = entries
        
        # Buttons
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(pady=5)
        
        button_texts = ["Add Process", "Generate Random", "Clear All"]
        commands = [self.add_process, self.generate_random_processes, self.clear_tables]
        
        for i, (text, cmd) in enumerate(zip(button_texts, commands)):
            ttk.Button(buttons_frame, text=text, command=cmd).grid(row=0, column=i, padx=5)
        
        # Process table
        table_frame = ttk.LabelFrame(self.input_tab, text="Process List")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("PID", "Arrival", "Burst", "Priority")
        self.process_table = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=ttk.Scrollbar(table_frame, orient="vertical").set
        )
        
        for col in columns:
            self.process_table.heading(col, text=col)
            self.process_table.column(col, width=80)
        
        self.process_table.pack(fill=tk.BOTH, expand=True)
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(self.input_tab, text="Algorithm Selection")
        algo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.algo_var = tk.StringVar(value="FCFS")
        algorithms = [
            ("First Come First Serve (FCFS)", "FCFS"),
            ("Shortest Job First (SJF)", "SJF"),
            ("Shortest Remaining Time First (SRTF)", "SRTF"),
            ("Priority Scheduling", "Priority"),
            ("Round Robin", "Round Robin")
        ]
        
        for i, (text, value) in enumerate(algorithms):
            ttk.Radiobutton(
                algo_frame, text=text, variable=self.algo_var, value=value,
                command=self.toggle_time_quantum
            ).grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
        
        # Time quantum entry
        self.tq_frame = ttk.Frame(algo_frame)  
        self.tq_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(self.tq_frame, text="Time Quantum:").pack(side=tk.LEFT)
        self.tq_entry = ttk.Entry(self.tq_frame, width=5)
        self.tq_entry.pack(side=tk.LEFT, padx=5)
        self.tq_entry.insert(0, "2")
        self.tq_frame.grid_remove()  # Hide initially
        
        # Run button
        ttk.Button(self.input_tab, text="Run Simulation", command=self.run_algorithm).pack(pady=10)
        
    def setup_results_tab(self):
        """Set up the Results tab"""
        # Output table
        table_frame = ttk.LabelFrame(self.results_tab, text="Process Results")
        table_frame.pack(fill=tk.X, padx=10, pady=10)
        
        columns = ("PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response")
        self.output_table = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=ttk.Scrollbar(table_frame, orient="vertical").set
        )
        
        for col in columns:
            self.output_table.heading(col, text=col)
            self.output_table.column(col, width=80)
        
        self.output_table.pack(fill=tk.X)
        
        # Summary text
        summary_frame = ttk.LabelFrame(self.results_tab, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=5)
        self.summary_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Gantt chart placeholder
        gantt_frame = ttk.LabelFrame(self.results_tab, text="Gantt Chart")
        gantt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.gantt_placeholder = ttk.Frame(gantt_frame)
        self.gantt_placeholder.pack(fill=tk.BOTH, expand=True)
        
    def setup_comparison_tab(self):
        """Set up the Algorithm Comparison tab"""
        comparison_frame = ttk.Frame(self.comparison_tab)
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(comparison_frame, text="Compare All Algorithms", 
                  command=self.compare_algorithms).pack(pady=10)
        
        self.comparison_text = scrolledtext.ScrolledText(comparison_frame, height=10)
        self.comparison_text.pack(fill=tk.X, padx=5, pady=5)
        
        self.comparison_chart_frame = ttk.Frame(comparison_frame)
        self.comparison_chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def toggle_time_quantum(self):
        """Show/hide time quantum entry based on algorithm selection"""
        if self.algo_var.get() == "Round Robin":
            self.tq_frame.grid()
        else:
            self.tq_frame.grid_remove()
            
    def add_process(self):
        """Add a process to the process table"""
        try:
            at = int(self.at_entry.get())
            bt = int(self.bt_entry.get())
            pr = int(self.pr_entry.get())
            
            if bt <= 0 or at < 0:
                messagebox.showerror("Error", "Invalid input values")
                return
                
            pid = len(self.process_table.get_children()) + 1
            self.process_table.insert("", "end", values=(pid, at, bt, pr))
            
            # Update entry fields for next process
            self.at_entry.delete(0, tk.END)
            self.bt_entry.delete(0, tk.END)
            self.pr_entry.delete(0, tk.END)
            
            self.at_entry.insert(0, str(at + 2))
            self.bt_entry.insert(0, "5")
            self.pr_entry.insert(0, str(random.randint(1, 10)))
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
            
    def generate_random_processes(self):
        """Generate random processes for demonstration"""
        for _ in range(5):
            at = random.randint(0, 10)
            bt = random.randint(1, 15)
            pr = random.randint(1, 10)
            pid = len(self.process_table.get_children()) + 1
            self.process_table.insert("", "end", values=(pid, at, bt, pr))
            
    def clear_tables(self):
        """Clear all tables and results"""
        for table in [self.process_table, self.output_table]:
            for row in table.get_children():
                table.delete(row)
                
        self.summary_text.delete(1.0, tk.END)
        
        if self.gantt_canvas:
            self.gantt_canvas.get_tk_widget().destroy()
            self.gantt_canvas = None
            
    def get_processes_from_table(self):
        """Get processes from the process table"""
        processes = []
        for row in self.process_table.get_children():
            values = self.process_table.item(row)["values"]
            pid, at, bt, pr = values
            processes.append(Process(int(pid), int(at), int(bt), int(pr)))
        return processes
        
    def run_algorithm(self):
        """Run the selected scheduling algorithm"""
        if not self.process_table.get_children():
            messagebox.showwarning("Warning", "Please add processes first")
            return
            
        # Clear previous results
        for row in self.output_table.get_children():
            self.output_table.delete(row)
            
        self.summary_text.delete(1.0, tk.END)
        
        # Get processes from table
        self.processes = self.get_processes_from_table()
        
        # Reset all process attributes
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.start_time = p.completion_time = p.turnaround_time = p.waiting_time = p.response_time = None
            p.execution_history = []
            
        # Select and run algorithm
        algorithm = self.algo_var.get()
        algorithm_funcs = {
            "FCFS": self.fcfs,
            "SJF": self.sjf,
            "SRTF": self.srtf,
            "Priority": self.priority_scheduling,
            "Round Robin": lambda p: self.round_robin(p, int(self.tq_entry.get()))
        }
        
        try:
            result_processes = algorithm_funcs[algorithm](self.processes.copy())
            self.display_results(result_processes, algorithm)
            self.notebook.select(self.results_tab)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        
    def display_results(self, processes, algorithm):
        """Display the results in the output table and summary"""
        total_turnaround = total_waiting = total_response = 0
        
        # Sort by PID for consistent display
        processes.sort(key=lambda x: x.pid)
        
        for p in processes:
            self.output_table.insert("", "end", values=(
                p.pid, p.arrival_time, p.burst_time, p.priority,
                p.completion_time, p.turnaround_time, p.waiting_time, p.response_time
            ))
            total_turnaround += p.turnaround_time
            total_waiting += p.waiting_time
            total_response += p.response_time
        
        n = len(processes)
        avgs = {
            "turnaround": total_turnaround / n,
            "waiting": total_waiting / n,
            "response": total_response / n
        }
        
        # Display summary
        summary = f"Algorithm: {algorithm}\n"
        for metric, value in avgs.items():
            summary += f"Average {metric.title()} Time: {value:.2f}\n"
        
        self.summary_text.insert(tk.END, summary)
        
        # Draw Gantt chart
        self.draw_gantt_chart(processes, algorithm)
        
    def draw_gantt_chart(self, processes, algorithm):
        """Draw a Gantt chart showing process execution"""
        if self.gantt_canvas:
            self.gantt_canvas.get_tk_widget().destroy()
            
        fig = plt.Figure(figsize=(10, 4), tight_layout=True)
        ax = fig.add_subplot(111)
        
        # Colors for processes
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#d35400', '#c0392b', '#16a085', '#8e44ad']
        pid_to_color = {p.pid: colors[i % len(colors)] for i, p in enumerate(sorted(processes, key=lambda x: x.pid))}
        
        # Find all execution intervals
        execution_intervals = []
        for p in processes:
            for start, end in p.execution_history:
                execution_intervals.append((start, end, p.pid))
                
        execution_intervals.sort()
        
        # Draw the Gantt chart
        y_ticks = []
        y_labels = []
        for i, (start, end, pid) in enumerate(execution_intervals):
            ax.barh(i, end - start, left=start, color=pid_to_color[pid], edgecolor='white')
            ax.text((start + end) / 2, i, f"P{pid}", ha='center', va='center')
            y_ticks.append(i)
            y_labels.append(f"{start}-{end}")
            
        ax.set_xlabel("Time")
        ax.set_title(f"Gantt Chart for {algorithm} Scheduling")
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.grid(axis="x", linestyle="--", alpha=0.7)
        
        # Legend
        legend_elements = [plt.Rectangle((0, 0), 1, 1, color=pid_to_color[p.pid], label=f"P{p.pid}") 
                          for p in sorted(processes, key=lambda x: x.pid)]
        ax.legend(handles=legend_elements, loc='upper right')
        
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_placeholder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.gantt_canvas = canvas
        
    def compare_algorithms(self):
        """Compare all algorithms and show statistics"""
        if not self.process_table.get_children():
            messagebox.showwarning("Warning", "Please add processes first")
            return
            
        base_processes = self.get_processes_from_table()
        
        algorithms = [
            ("FCFS", lambda p: self.fcfs(p)),
            ("SJF", lambda p: self.sjf(p)),
            ("SRTF", lambda p: self.srtf(p)),
            ("Priority", lambda p: self.priority_scheduling(p)),
            ("Round Robin (q=2)", lambda p: self.round_robin(p, 2))
        ]
        
        results = {}
        for name, func in algorithms:
            processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in base_processes]
            result_processes = func(processes_copy)
            
            results[name] = {
                "turnaround": sum(p.turnaround_time for p in result_processes) / len(result_processes),
                "waiting": sum(p.waiting_time for p in result_processes) / len(result_processes),
                "response": sum(p.response_time for p in result_processes) / len(result_processes)
            }
        
        # Display comparison text
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, "Algorithm Comparison:\n\n")
        self.comparison_text.insert(tk.END, f"{'Algorithm':<20} {'Avg Turnaround':<20} {'Avg Waiting':<20} {'Avg Response':<20}\n")
        self.comparison_text.insert(tk.END, "-" * 80 + "\n")
        
        for algo, metrics in results.items():
            self.comparison_text.insert(tk.END, f"{algo:<20} {metrics['turnaround']:<20.2f} {metrics['waiting']:<20.2f} {metrics['response']:<20.2f}\n")
            
        # Draw comparison chart
        self.draw_comparison_chart(results)
        
    def draw_comparison_chart(self, results):
        """Draw a bar chart comparing algorithm performance"""
        for widget in self.comparison_chart_frame.winfo_children():
            widget.destroy()
            
        fig = plt.Figure(figsize=(10, 5), tight_layout=True)
        ax = fig.add_subplot(111)
        
        algorithms = list(results.keys())
        metrics = ["turnaround", "waiting", "response"]
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        
        x = range(len(algorithms))
        width = 0.25
        
        for i, metric in enumerate(metrics):
            values = [results[algo][metric] for algo in algorithms]
            ax.bar([pos + (i-1)*width for pos in x], values, width, 
                  label=f'Avg {metric.title()} Time', color=colors[i])
        
        ax.set_ylabel('Time')
        ax.set_title('Algorithm Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=self.comparison_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    # CPU Scheduling Algorithms Implementation
    def fcfs(self, processes):
        """First Come First Serve scheduling algorithm"""
        processes.sort(key=lambda x: x.arrival_time)
        current_time = 0
        
        for p in processes:
            current_time = max(current_time, p.arrival_time)
            p.start_time = current_time
            p.response_time = p.start_time - p.arrival_time
            p.completion_time = current_time + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.execution_history.append((current_time, p.completion_time))
            current_time = p.completion_time
            
        return processes
        
    def sjf(self, processes):
        """Shortest Job First (non-preemptive) scheduling algorithm"""
        processes.sort(key=lambda x: x.arrival_time)
        n = len(processes)
        current_time = 0
        completed = 0
        is_completed = [False] * n
        
        while completed != n:
            idx = -1
            shortest_burst = float('inf')
            
            for i in range(n):
                if processes[i].arrival_time <= current_time and not is_completed[i]:
                    if processes[i].burst_time < shortest_burst:
                        shortest_burst = processes[i].burst_time
                        idx = i
                        
            if idx != -1:
                p = processes[idx]
                p.start_time = current_time
                p.response_time = p.start_time - p.arrival_time
                p.completion_time = current_time + p.burst_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                p.execution_history.append((current_time, p.completion_time))
                current_time = p.completion_time
                is_completed[idx] = True
                completed += 1
            else:
                current_time += 1
                
        return processes
        
    def srtf(self, processes):
        """Shortest Remaining Time First (preemptive SJF) scheduling algorithm"""
        n = len(processes)
        completed = 0
        current_time = 0
        
        while completed != n:
            idx = -1
            shortest_remaining = float('inf')
            
            for i in range(n):
                if processes[i].arrival_time <= current_time and processes[i].remaining_time > 0:
                    if processes[i].remaining_time < shortest_remaining:
                        shortest_remaining = processes[i].remaining_time
                        idx = i
                        
            if idx != -1:
                # First execution - set response time
                if processes[idx].start_time is None:
                    processes[idx].start_time = current_time
                    processes[idx].response_time = current_time - processes[idx].arrival_time
                
                processes[idx].remaining_time -= 1
                current_time += 1
                
                # Record execution interval
                if not processes[idx].execution_history or processes[idx].execution_history[-1][1] != current_time:
                    processes[idx].execution_history.append((current_time - 1, current_time))
                else:
                    # Extend the last interval
                    processes[idx].execution_history[-1] = (processes[idx].execution_history[-1][0], current_time)
                
                if processes[idx].remaining_time == 0:
                    completed += 1
                    processes[idx].completion_time = current_time
                    processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time
                    processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time
            else:
                current_time += 1
                
        return processes
        
    def priority_scheduling(self, processes):
        """Priority Scheduling (lower number = higher priority)"""
        n = len(processes)
        current_time = 0
        completed = 0
        is_completed = [False] * n
        
        while completed != n:
            idx = -1
            highest_priority = float('inf')
            
            for i in range(n):
                if processes[i].arrival_time <= current_time and not is_completed[i]:
                    if processes[i].priority < highest_priority:
                        highest_priority = processes[i].priority
                        idx = i
                        
            if idx != -1:
                p = processes[idx]
                p.start_time = current_time
                p.response_time = p.start_time - p.arrival_time
                p.completion_time = current_time + p.burst_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                p.execution_history.append((current_time, p.completion_time))
                current_time = p.completion_time
                is_completed[idx] = True
                completed += 1
            else:
                current_time += 1
                
        return processes
        
    def round_robin(self, processes, time_quantum):
        """Round Robin scheduling algorithm"""
        if time_quantum <= 0:
            raise ValueError("Time quantum must be greater than 0")
            
        n = len(processes)
        queue = deque()
        current_time = min(p.arrival_time for p in processes) if processes else 0
        complete_count = 0
        
        # Add initial processes to queue
        for i in range(n):
            if processes[i].arrival_time <= current_time:
                queue.append(i)
                
        while complete_count < n:
            if not queue:
                # Find next arrival time
                next_arrival = min((p.arrival_time for p in processes if p.remaining_time > 0), default=current_time+1)
                current_time = next_arrival
                
                # Add newly arrived processes
                for i in range(n):
                    if processes[i].arrival_time <= current_time and processes[i].remaining_time > 0 and i not in queue:
                        queue.append(i)
                continue
            
            idx = queue.popleft()
            
            # First execution - set response time
            if processes[idx].start_time is None:
                processes[idx].start_time = current_time
                processes[idx].response_time = current_time - processes[idx].arrival_time
                
            execution_time = min(time_quantum, processes[idx].remaining_time)
            processes[idx].execution_history.append((current_time, current_time + execution_time))
            
            current_time += execution_time
            processes[idx].remaining_time -= execution_time
            
            # Add newly arrived processes
            for i in range(n):
                if processes[i].arrival_time <= current_time and processes[i].remaining_time > 0 and i != idx and i not in queue:
                    queue.append(i)
                    
            # Re-add current process if not completed
            if processes[idx].remaining_time > 0:
                queue.append(idx)
            else:
                processes[idx].completion_time = current_time
                processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time
                processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time
                complete_count += 1
                
        return processes

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulingSimulator(root)
    root.mainloop()

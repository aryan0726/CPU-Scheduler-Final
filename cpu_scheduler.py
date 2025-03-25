import matplotlib.pyplot as plt
import queue

# Class to represent a Process
class Process:
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

# First Come First Serve (FCFS) Scheduling
def fcfs(processes):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    start_times, end_times = [], []

    print("\nFCFS Scheduling:")
    print("PID | Arrival | Burst | Completion | Turnaround | Waiting")

    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.start_time = current_time
        p.completion_time = current_time + p.burst_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        current_time = p.completion_time

        print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.completion_time}\t\t{p.turnaround_time}\t\t{p.waiting_time}")

        start_times.append(p.start_time)
        end_times.append(p.completion_time)

    draw_gantt_chart(processes, "FCFS", start_times, end_times)

# Shortest Job First (SJF) Scheduling
def sjf(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time))
    ready_queue = []
    current_time = 0
    start_times, end_times, executed_processes = [], [], []

    print("\nSJF Scheduling:")
    print("PID | Arrival | Burst | Completion | Turnaround | Waiting")

    while processes or ready_queue:
        while processes and processes[0].arrival_time <= current_time:
            ready_queue.append(processes.pop(0))
        
        if ready_queue:
            ready_queue.sort(key=lambda x: x.burst_time)  # Select process with shortest burst time
            p = ready_queue.pop(0)
            p.start_time = current_time
            p.completion_time = current_time + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            current_time = p.completion_time

            print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.completion_time}\t\t{p.turnaround_time}\t\t{p.waiting_time}")

            start_times.append(p.start_time)
            end_times.append(p.completion_time)
            executed_processes.append(p)  # Store executed processes for Gantt chart

        else:
            current_time += 1

    draw_gantt_chart(executed_processes, "SJF", start_times, end_times)


# Round Robin (RR) Scheduling
def round_robin(processes, time_quantum):
    queue = []
    current_time = 0
    start_times, end_times = [], []

    print("\nRound Robin Scheduling:")
    print("PID | Arrival | Burst | Completion | Turnaround | Waiting")

    remaining_processes = processes[:]
    while remaining_processes:
        for p in remaining_processes[:]:
            if p.remaining_time > 0:
                start_times.append(current_time)
                execution_time = min(time_quantum, p.remaining_time)
                current_time += execution_time
                p.remaining_time -= execution_time
                end_times.append(current_time)
                if p.remaining_time == 0:
                    p.completion_time = current_time
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.completion_time}\t\t{p.turnaround_time}\t\t{p.waiting_time}")
                    remaining_processes.remove(p)

    draw_gantt_chart(processes, "Round Robin", start_times, end_times)

# Priority Scheduling (Non-Preemptive)
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x.priority, x.arrival_time))
    current_time = 0
    start_times, end_times = [], []

    print("\nPriority Scheduling:")
    print("PID | Arrival | Burst | Priority | Completion | Turnaround | Waiting")

    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.start_time = current_time
        p.completion_time = current_time + p.burst_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        current_time = p.completion_time

        print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.priority}\t\t{p.completion_time}\t\t{p.turnaround_time}\t\t{p.waiting_time}")

        start_times.append(p.start_time)
        end_times.append(p.completion_time)

    draw_gantt_chart(processes, "Priority", start_times, end_times)

# Gantt Chart Function
def draw_gantt_chart(processes, algorithm, start_times, end_times):
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, p in enumerate(processes):
        ax.barh(f"P{p.pid}", end_times[i] - start_times[i], left=start_times[i], color="skyblue")

    ax.set_xlabel("Time")
    ax.set_title(f"Gantt Chart for {algorithm} Scheduling")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.show()

# Main Function to Select Scheduling Algorithm
def main():
    processes = []
    num_processes = int(input("Enter the number of processes: "))

    for i in range(1, num_processes + 1):
        arrival_time = int(input(f"Enter Arrival Time for Process {i}: "))
        burst_time = int(input(f"Enter Burst Time for Process {i}: "))
        priority = int(input(f"Enter Priority for Process {i} (Lower number = Higher priority, Default=0): ") or 0)
        processes.append(Process(i, arrival_time, burst_time, priority))

    print("\nChoose Scheduling Algorithm:")
    print("1. First Come First Serve (FCFS)")
    print("2. Shortest Job First (SJF)")
    print("3. Round Robin (RR)")
    print("4. Priority Scheduling")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        fcfs(processes)
    elif choice == 2:
        sjf(processes)
    elif choice == 3:
        time_quantum = int(input("Enter Time Quantum for Round Robin: "))
        round_robin(processes, time_quantum)
    elif choice == 4:
        priority_scheduling(processes)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()

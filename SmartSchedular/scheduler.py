import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import copy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

matplotlib.use("TkAgg")
matplotlib.interactive(True)


def browse_input():
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select file", filetypes=(("txt files", "*.txt"), ("all files", "*.*")))

    # go update list
    if (filename == ''):
        filename = 'This path is not working.'
    else:
        i = 0
        data.clear()
        file = open(filename, "r")
        for line in file:
            endl = line.find('\n')
            if endl != -1:
                line = line[:endl]
            if i == 0:
                pnum = line
            else:
                line = line.split(' ')
                # Process No.  ( Arriv , Runing , Priority )
                data[int(line[0])] = [float(line[1]),
                                      float(line[2]), float(line[3])]
            i += 1
        file.close()

    path_label.config(text=filename)
    update_graph()
    return


def update_graph():
    # Figure
    figure = Figure(figsize=(13, 5), dpi=100)
    plot = figure.add_subplot(1, 1, 1)

    # Fetch selected algorithm
    ALGORITHM = algo.cget("text")
    if ALGORITHM == "HPF":
        DO_HPF()
    elif ALGORITHM == "FCFS":
        DO_FCFS()
    elif ALGORITHM == "RR":
        DO_RR()
    elif ALGORITHM == "SRTN":
        DO_SRTN()

    # Draw Output graph
    plot.set_title(algo.cget("text"), fontsize=16)
    plot.set_ylabel("Process No.", fontsize=14)
    plot.set_xlabel("Time", fontsize=14)

    x = X_time
    y = Y_prun
    plot.step(x, y, color="red", linestyle="-")
    plot.grid(visible=True, which='major', color='#AAAAAA', linestyle='-')
    plot.set_yticks(y)
    plot.set_xticks(x)
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=4, column=0, padx=5,
                                pady=5, columnspan=4, sticky="news")

    return


def DO_FCFS():
    # Clear output and time lists
    output.clear()
    X_time.clear()
    Y_prun.clear()
   
    CSTime = context_val.get()  # Get context value 

    # Sort data by arrival time
    sorted_data = sorted(data.items(), key=lambda kv: kv[1])

    AccumTime = 0  # Accumulated time
    prevX = 0  # Previous X value
    prevY = 0  # Previous Y value

    for p in sorted_data:
        # Get process info
        pno = int(p[0])  # Process number
        arrival = float(p[1][0])  # Arrival time
        burst = float(p[1][1])  # Burst time

        if arrival > prevX:
            # If there is a gap between the previous process and the current process, add idle time to the Gantt chart
            X_time.append(prevX)
            Y_prun.append(0)
            X_time.append(arrival)
            Y_prun.append(0)

            # Add the current process to the Gantt chart
            X_time.append(arrival)
            Y_prun.append(pno)
            X_time.append(burst + arrival)
            Y_prun.append(pno)

            prevX = arrival + burst  # Update the previous X value
        else:
            # If there is no gap, simply add the current process to the Gantt chart
            X_time.append(prevX)
            Y_prun.append(pno)
            X_time.append(prevX + burst)
            Y_prun.append(pno)

            prevX = prevX + burst  # Update the previous X value

        # Calculate turnaround time, waiting time, and response ratio for the current process
        output[pno] = [(prevX - arrival - burst),
                       (prevX - arrival), (prevX - arrival) / burst]

    X_time.append(prevX)
    Y_prun.append(0)

    return


def DO_HPF():
    # Clear output and time lists
    output.clear()
    X_time.clear()
    Y_prun.clear()

    CSTime = context_val.get()  # Get context value 

    # Sorting with respect to Arrival Time
    sorted_data = sorted(data.items(), key=lambda kv: kv[1][0])
    pnum = len(sorted_data)  # Number of processes

    AccumTime = sorted_data[0][1][0]  # Arrival time of first process
    prevX = 0  # Previous X value
    prevY = 0  # Previous Y value
    j = 0  # Counter for iterating through sorted_data
    i = 0  # Counter for iterating through processes
    Queue = {}  # Process queue

    for i in range(pnum):
        Queue = dict(Queue)  # Reset the queue for each process

        # Add processes with arrival time <= AccumTime to the queue
        while j < pnum and sorted_data[j][1][0] <= AccumTime:
            Queue[sorted_data[j][0]] = sorted_data[j][1]
            j += 1

        # Sort the queue by priority
        Queue = sorted(Queue.items(), key=lambda kv: kv[1][2], reverse=True)

        if len(Queue) == 0:
            # If the queue is empty, take the next process from sorted_data
            p = sorted_data[i]
        else:
            # Otherwise, take the highest priority process from the queue
            p = Queue.pop(0)

        pno = p[0]  # Process number
        arrival = p[1][0]  # Arrival time
        burst = p[1][1]  # Burst time

        if arrival > prevX:
            # If there is a gap between the previous process and the current process, add idle time to the Gantt chart
            X_time.append(prevX)
            Y_prun.append(0)
            X_time.append(arrival)
            Y_prun.append(0)

            # Add the current process to the Gantt chart
            X_time.append(arrival)
            Y_prun.append(pno)
            X_time.append(burst + arrival)
            Y_prun.append(pno)

            prevX = arrival + burst  # Update the previous X value
        else:
            # If there is no gap, simply add the current process to the Gantt chart
            X_time.append(prevX)
            Y_prun.append(pno)
            X_time.append(prevX + burst)
            Y_prun.append(pno)

            prevX = prevX + burst  # Update the previous X value

        # Calculate turnaround time, waiting time, and response ratio for the current process
        output[pno] = [(prevX - arrival - burst),
                       (prevX - arrival), (prevX - arrival) / burst]

        AccumTime = prevX  # Update the accumulated time

    X_time.append(prevX)
    Y_prun.append(0)

    return


def DO_RR():
    # Clearing the lists that will contain the output data
    output.clear()
    X_time.clear()
    Y_prun.clear()

    # Retrieving the values of context switch time and quantum time from user input
    CSTime = context_val.get()
    QUANTM = quantum_val.get()

    # Sorting the processes based on their arrival time
    datacpy = copy.deepcopy(data)
    sorted_data = sorted(datacpy.items(), key=lambda kv: kv[1][0])
    pnum = (len(sorted_data))

    # Initializing variables for the first process
    prevX = 0  # The start time of the first process is 0
    j = 1  # Index of the next process to be added to the ready queue

    # Initializing the ready queue with the first process
    RRQ = []
    RRQ.append(sorted_data[0])

    # Loop until all processes have been executed
    while (len(RRQ) != 0):
        # If the ready queue is empty and there are more processes to be added, add the next process
        if (len(RRQ) == 0 and j < pnum):
            p = sorted_data[j]
            j += 1
        else:
            # If the ready queue is not empty, select the next process to be executed from the front of the queue
            p = RRQ.pop(0)

        # Retrieving the process details from the dictionary
        pno = p[0]  # Process number
        arrival = p[1][0]  # Arrival time
        burst = p[1][1]  # Burst/execution time

        # If the current process arrived after the end of the previous process, add idle time to the output data
        if (arrival > prevX):
            X_time.append(prevX)
            Y_prun.append(0)

            X_time.append(arrival)
            Y_prun.append(0)

            X_time.append(arrival)
            Y_prun.append(pno)

            # If the process has remaining burst time greater than the quantum time, execute the process for quantum time
            if (burst > QUANTM):
                X_time.append(arrival+QUANTM)
                prevX = arrival+QUANTM
            else:
                # If the process has remaining burst time less than or equal to the quantum time, execute the process until completion
                X_time.append(arrival+burst)
                prevX = arrival+burst
            Y_prun.append(pno)

        else:
            # If the current process arrived before or at the end of the previous process, execute it for quantum time or until completion
            X_time.append(prevX)
            Y_prun.append(pno)
            if (burst >= QUANTM):
                X_time.append(prevX+QUANTM)
                prevX = prevX+QUANTM
            else:
                X_time.append(prevX+burst)
                prevX = prevX+burst
            Y_prun.append(pno)

        # Add any new processes that have arrived before or at the end of the current process to the ready queue
        while (j < pnum and sorted_data[j][1][0] <= prevX):
            RRQ.append(sorted_data[j])
            j += 1

        # If the current process has remaining burst time greater than the quantum time, add it back to the ready queue
        if (p[1][1] > QUANTM):
            p[1][1] -= QUANTM
            RRQ.append(p)
        else:
            # If the current process has remaining burst time less than or equal to the quantum time, mark it as completed and add it to the output data
            p[1][1] = 0
            p = data[int(pno)]
            arrival = p[0]
            burst = p[1]
            output[pno] = [(prevX-arrival-burst),
                           (prevX-arrival), (prevX-arrival)/burst]

        # CONTEXT SWITCHING
        # If there is a context switch and there are processes in the ready queue, add the context switch time to the output data
        if (CSTime != 0 and len(RRQ) != 0 and RRQ[0][0] != pno and RRQ[0][1][0] <= prevX):
            X_time.append(prevX)
            Y_prun.append(-1)
            X_time.append(prevX+CSTime)
            Y_prun.append(-1)
            prevX = prevX+CSTime

        # If the ready queue is empty and there are more processes to be added, add the next process
        if (len(RRQ) == 0 and j < pnum):
            RRQ.append(sorted_data[j])
            j += 1

    # Add the final idle time to the output data
    X_time.append(prevX)
    Y_prun.append(0)

    # Return the output data
    return


def DO_SRTN():
    output.clear()
    output.clear()  # Clearing any previous outputs
    X_time.clear()  # Clearing the X-axis data
    Y_prun.clear()  # Clearing the Y-axis data
    CSTime = context_val.get()  # Getting the context switching time from the GUI
    QUANTM = quantum_val.get()  # Getting the time quantum from the GUI
    # Sorting the processes by arrival time
    datacpy = copy.deepcopy(data)
    sorted_data = sorted(datacpy.items(), key=lambda kv: kv[1][0])
    pnum = (len(sorted_data))
    # Process No.  ( Arriv , Runing , Priority )
    # Setting the initial time to the arrival time of the first process
    prevX = (sorted_data[0][1][0])
    j = 1  # Initializing the index for the next process
    SRT = []  # Initializing the Round Robin Queue
    SRT.append(sorted_data[0])  # Adding the first process to the SRT
    while (len(SRT) != 0):  # Loop until the SRT is empty

        # Adding processes to the SRT that have arrived before or at the current time
        while (j < pnum and sorted_data[j][1][0] <= prevX):
            SRT.append(sorted_data[j])
            j += 1

        SRT = dict(SRT)  # Converting the SRT to a dictionary for sorting
        # Sorting the SRT by remaining burst time
        SRT = sorted(SRT.items(), key=lambda kv: kv[1][1])

        if (len(SRT) == 0 and j < pnum):  # If the SRT is empty but there are more processes to be added
            p = sorted_data[j]  # Add the next process
            j += 1
        else:
            p = SRT[0]  # Select the next process to be executed from the SRT

        pno = p[0]  # Extracting the process ID
        arrival = p[1][0]  # Extracting the arrival time
        burst = p[1][1]  # Extracting the remaining burst time

        if (arrival > prevX):  # If there is no process running at the current time
            X_time.append(prevX)
            Y_prun.append(0)

            X_time.append(arrival)
            Y_prun.append(0)

            X_time.append(arrival)
            Y_prun.append(pno)

            if (burst > QUANTM):  # If the process has remaining burst time greater than the time quantum
                X_time.append(arrival+QUANTM)
                prevX = arrival+QUANTM  # Set the current time to the end of the time quantum
            else:  # If the process has remaining burst time less than or equal to the time quantum
                X_time.append(arrival+burst)
                prevX = arrival+burst  # Set the current time to the end of the process
            Y_prun.append(pno)

        else:  # If there is a process running at the current time
            X_time.append(prevX)
            Y_prun.append(pno)
            if (burst >= QUANTM):  # If the process has remaining burst time greater than or equal to the time quantum
                X_time.append(prevX+QUANTM)
                prevX = prevX+QUANTM  # Set the current time to the end of the time quantum
            else:  # If the process has remaining burst time less than the time quantum
                X_time.append(prevX+burst)
                prevX = prevX+burst  # Set the current time to the end of the process
            Y_prun.append(pno)

        if (p[1][1] > QUANTM):  # If the process has remaining burst time greater than the time quantum
            # Decrement the remaining burst time by the time quantum
            p[1][1] -= QUANTM
        else:  # If the process has remaining burst time less than or equal to the time quantum
            SRT.pop(0)  # Remove the process from the SRT
            p[1][1] = 0  # Set the remaining burst time to zero
            p = data[int(pno)]  # Get the original process data
            # Extract the arrival time from the original process data
            arrival = p[0]
            # Extract the burst time from the original process data
            burst = p[1]
            # Calculating and storing the turnaround time, waiting time, and normalized turnaround time for the process
            output[pno] = [(prevX-arrival-burst),
                           (prevX-arrival), (prevX-arrival)/burst]

            # If the SRT is empty but there are more processes to be added
            if (len(SRT) == 0 and j < pnum):
                SRT.append(sorted_data[j])  # Add the next process to the SRT
                j += 1

        # CONTEXT SWITCHING
        if (CSTime != 0 and len(SRT) != 0 and SRT[0][0] != pno and SRT[0][1][0] <= prevX):
            # If context switching is enabled and there is a process waiting in the SRT and it has arrived before or at the current time
            X_time.append(prevX)
            # Add a data point to the plot to indicate the start of context switching
            Y_prun.append(-1)
            X_time.append(prevX+CSTime)
            # Add a data point to the plot to indicate the end of context switching
            Y_prun.append(-1)
            prevX = prevX+CSTime  # Set the current time to the end of context switching
            if SRT[0][1][1] > 0:
                # Add the preempted process back to the SRT
                SRT.append((SRT[0][0], [prevX, SRT[0][1][1]]))
                # Remove the preempted process from the SRT
                SRT.pop(0)

    X_time.append(prevX)
    # Add a data point to the plot to indicate the end of the simulation
    Y_prun.append(0)

    return


def output_write():
    output_path = output_val.get()
    file = open(output_path, "w")
    pnum = len(output)
    file.write("Process Count : "+str(pnum)+'\n')
    avg_ta = 0
    avg_wta = 0
    file.write("P. No\t\t"+"Waiting time\t"+"T.A. time\t"+"W.T.A. time"+'\n')
    for i in (output.keys()):
        # print(p[1])
        p = output[i]
        # print(p)
        avg_ta += p[1]
        avg_wta += p[2]
        file.write(str(i)+"\t\t"+str(p[0]) +
                   "\t\t"+str(p[1])+"\t\t"+str(p[2])+'\n')
    file.write("\nAvg. T.A. :" + str(avg_ta/pnum)+"\n" +
               "Avg. W.T.A. :"+str(avg_wta/pnum)+'\n')
    messagebox.showinfo("Outputfile status", "Successfully Written .")
    file.close()


# GLOBAL VARS
data = {}
output = {}

# Process Number
pnum = 0

# Time slots
X_time = []
# Runing Process No.
Y_prun = []

root = Tk(className=' OS Scheduler')
# root.geometry("860x640")
# root.resizable(width=False, height=False)

filename = ""

# Label-Input Context Switching
context_label = Label(root, text='Context Switch Time :')
context_label.grid(row=0, column=0, padx=5, pady=10, ipadx=5, sticky='w')

# context_time = StringVar(root)
context_val = IntVar(root, value=0)
context_entry = Entry(root, textvariable=context_val)  # validate='key')
context_entry.grid(row=0, column=1, ipadx=5, sticky="w")


# Label-Input Time Quantum
quantum_label = Label(root, text='Quantum Time :')
quantum_label.grid(row=1, column=0, padx=12, pady=10, ipadx=5, sticky='w')
quantum_val = IntVar(root, value=1)

quantum_entry = Entry(root, textvariable=quantum_val)
quantum_entry.grid(row=1, column=1, ipadx=5, sticky="w")


# Show/Update Btn
update_btn = Button(root, text="Show/Update Graph", command=update_graph)
update_btn.grid(row=2, column=0, padx=5, pady=10,
                ipadx=5, columnspan=1, sticky='w')


# Open file Btn
browse_btn = Button(root, text="Select Input File", command=browse_input)
browse_btn.grid(row=3, column=0, padx=5, ipadx=19, columnspan=1, sticky='w')


# Show opened file path
file_label = Label(root, text='File Path: '+filename)
file_label.grid(row=5, column=0)

path_label = Label(root, text=filename)
path_label.grid(row=5, column=1)


# Drop down list for algorithm selection
OPTIONS = ["SELECT ALGORITHM", "HPF", "FCFS", "RR", "SRTN"]

variable = StringVar(root)
variable.set(OPTIONS[0])  # default value

algo = OptionMenu(root, variable, *OPTIONS)
algo.grid(row=2, column=1, sticky='w')

# Outputfile
output_label = Label(root, text='Output file name :')
output_label.grid(row=3, column=1, sticky="w")
output_val = StringVar(root, value="Out.txt")

output_entry = Entry(root, textvariable=output_val)
output_entry.grid(row=3, column=2, sticky="w")

write_btn = Button(root, text="Wirte File", command=output_write)
write_btn.grid(row=3, column=3, padx=5, ipadx=19, columnspan=1, sticky='w')

# Graph
figure = Figure(figsize=(13, 5), dpi=100)
plot = figure.add_subplot(1, 1, 1)

plot.set_title(algo.cget("text"), fontsize=16)
plot.set_ylabel("Process No.", fontsize=14)
plot.set_xlabel("Time", fontsize=14)
x = X_time
y = Y_prun

plot.step(x, y, color="red", marker=".", linestyle="")
plot.grid(visible=True, which='major', color='#AAAAAA', linestyle='-')
plot.set_yticks(y)
plot.set_xticks(x)

canvas = FigureCanvasTkAgg(figure, root)
canvas.get_tk_widget().grid(row=4, column=0, padx=5,
                            pady=5, columnspan=4, sticky="news")

# Main loop
# Starting the simulation
root.mainloop()

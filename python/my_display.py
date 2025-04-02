import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox
from python import station_observation
from python import file_handler
from python import my_math
from python import  chart
from python import  fish_behavior as fb


def display_data(window):
    data_list = file_handler.load_latest_data()
    if not data_list:
        tk.Label(window, text="No data available.", foreground="red").pack()
        return

    columns = list(data_list[0].keys())

    # Create a frame to hold both the Treeview and scrollbars
    frame = tk.Frame(window)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    # Create vertical and horizontal scrollbars
    vsb = ttk.Scrollbar(frame, orient='vertical')
    hsb = ttk.Scrollbar(frame, orient='horizontal')

    # Create the Treeview with scroll command bindings
    tree = ttk.Treeview(
        frame,
        columns=columns,
        show='headings',
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )

    # Attach scrollbars to Treeview
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    tree.pack(side='left', fill='both', expand=True)

    # Configure Treeview columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor='center')

    # Insert data
    for row in data_list:
        values = [row[col] for col in columns]
        tree.insert('', tk.END, values=values)

def dummy_def():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("GPU Version Only")
    root.destroy()

def deploy(script_dir, dll_path, plots_dir, output_dir, date_str, time_str, csv_filename):
    try:

        # Step 7: GUI setup
        root = tk.Tk()
        root.title("Mad Angler Weather & Fishing Assistant")
        root.geometry("1600x600")

        # Left-side buttons
        left_frame = tk.Frame(root)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        # Right-side data display
        content_frame = tk.Frame(root)
        content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        title = tk.Label(content_frame, text="Latest Fishing Conditions Report", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)

        tk.Button(left_frame, text="Gather Data", width=20,
                  command=lambda: station_observation.gather_data(dll_path, plots_dir, csv_filename, output_dir)).pack(pady=5)

        tk.Button(left_frame, text="Display Data", width=20,
                  command=lambda: display_data(content_frame)).pack(pady=5)

        tk.Button(left_frame, text="Plot Weather Data", width=20,
                  command=lambda: chart.plot_weather_data(output_dir, csv_filename)).pack(pady=5)

        tk.Button(left_frame, text="Run Chaos Chart", width=20,
                  command=lambda: chart.chart_run( output_dir, date_str, time_str)).pack(pady=5)

        tk.Button(left_frame, text="Chaos Trajectory", width=20,
                  command=lambda: dummy_def()).pack(pady=5)
        
        tk.Button(left_frame, text="Get Predictions", width=20,
                  command=lambda: dummy_def()).pack(pady=5)

        tk.Button(left_frame, text="Generate Chart GIF", width=20,
                  command=lambda: chart.chart_gif(output_dir)).pack(pady=5)
        
        tk.Button(left_frame, text="Analyze Bite Patterns", width=20,
                  command=lambda: dummy_def()).pack(pady=5)

        tk.Button(left_frame, text="Generate JSON & Report", width=20,
                  command=lambda: dummy_def()).pack(pady=5)


        root.mainloop()
        print(f"END PROGRAM")

    except Exception as e:
        print(f"[ERROR] An error occurred in deploy(): {e}")

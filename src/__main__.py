import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging

# Configure logging to record all actions and errors in a log file
LOG_FILE = "spotify_data_analyzer.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Application started")

# Helper Functions for JSON Parsing and Data Analysis
def load_streaming_history_files(folder_path):
    """Load all JSON files from the given folder and combine their data."""
    logging.info("Loading streaming history files from folder: %s", folder_path)
    try:
        # Identify JSON files matching the required naming pattern
        file_list = [
            filename
            for filename in os.listdir(folder_path)
            if filename.startswith("Streaming_History_Audio_") and filename.endswith(".json")
        ]
        # Sort files based on their sequence number in the filename
        file_list.sort(
            key=lambda x: int(x.split("_")[-1].split(".")[0])
        )

        if not file_list:
            logging.warning("No valid JSON files found in the folder")
            raise FileNotFoundError("No JSON files found matching the required pattern.")

        data_list = []
        # Read and combine data from each JSON file
        for filename in file_list:
            file_path = os.path.join(folder_path, filename)
            logging.info("Reading file: %s", file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data_list.extend(data)  # Add data from the file to the combined list

        logging.info("Successfully loaded %d records from JSON files", len(data_list))
        return data_list
    except Exception as e:
        logging.error("Error while loading JSON files: %s", str(e))
        raise

def calculate_listening_time(data, key, additional_key=None):
    """Calculate total listening time in milliseconds for given key and optional additional key."""
    time_counter = defaultdict(int)
    for item in data:
        if key in item and item[key]:
            identifier = item[key]
            if additional_key and additional_key in item:
                identifier += f" by {item[additional_key]}"
            time_counter[identifier] += item["ms_played"]
    return time_counter

def analyze_streaming_data(data):
    """Analyze the streaming data to compute listening habits and preferences."""
    logging.info("Analyzing streaming data")
    try:
        # Calculate total listening time in minutes
        total_ms_played = sum(item["ms_played"] for item in data)
        total_minutes = total_ms_played / (1000 * 60)

        # Extract dates and count occurrences for most active days
        dates = [datetime.strptime(item["ts"], "%Y-%m-%dT%H:%M:%SZ").date() for item in data]
        day_counts = Counter(dates)

        # Average listening time per day
        daily_totals = [ms for date, ms in day_counts.items()]
        average_daily_minutes = sum(daily_totals) / len(daily_totals) / (1000 * 60)

        # Identify the most active hours of the day
        hours = [datetime.strptime(item["ts"], "%Y-%m-%dT%H:%M:%SZ").hour for item in data]
        most_active_hour, _ = Counter(hours).most_common(1)[0]
        time_period = ("morning" if 6 <= most_active_hour < 12 else
                       "afternoon" if 12 <= most_active_hour < 18 else
                       "evening")

        # Determine days with most listening activity and their position in the week
        most_active_days = day_counts.most_common(2)
        weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                       4: "Friday", 5: "Saturday", 6: "Sunday"}
        activity_days = []
        for date, _ in most_active_days:
            day_name = weekday_map[date.weekday()]
            position = ("start of the weekend" if date.weekday() == 4 else
                        "end of the weekend" if date.weekday() == 6 else
                        "middle of the week")
            activity_days.append(f"{day_name} ({position})")

        # Calculate top artists, tracks, and albums by total listening time
        top_artists = calculate_listening_time(data, "master_metadata_album_artist_name")
        top_tracks = calculate_listening_time(data, "master_metadata_track_name", "master_metadata_album_artist_name")
        top_albums = calculate_listening_time(data, "master_metadata_album_album_name", "master_metadata_album_artist_name")

        # Sort results by total listening time
        top_artists = sorted(top_artists.items(), key=lambda x: x[1], reverse=True)[:10]
        top_tracks = sorted(top_tracks.items(), key=lambda x: x[1], reverse=True)[:10]
        top_albums = sorted(top_albums.items(), key=lambda x: x[1], reverse=True)[:10]

        # Longest listening streak
        sorted_dates = sorted(day_counts.keys())
        streak, longest_streak = 1, 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                streak += 1
                longest_streak = max(longest_streak, streak)
            else:
                streak = 1

        # Most played day
        most_played_day, most_played_time = max(day_counts.items(), key=lambda x: x[1])

        return {
            "total_minutes": round(total_minutes, 2),
            "average_daily_minutes": round(average_daily_minutes, 2),
            "most_active_hour": most_active_hour,
            "time_period": time_period,
            "activity_days": activity_days,
            "top_artists": top_artists,
            "top_tracks": top_tracks,
            "top_albums": top_albums,
            "longest_streak": longest_streak,
            "most_played_day": most_played_day,
            "most_played_time": most_played_time / (1000 * 60 * 60),  # Convert to hours
        }
    except Exception as e:
        logging.error("Error during data analysis: %s", str(e))
        raise

# GUI Application Class
class SpotifyDataApp(tk.Tk):
    """Main application class for the Spotify Data Analyzer."""
    def __init__(self):
        super().__init__()
        self.title("Spotify Data Analyzer")
        self.attributes("-fullscreen", True)  # Start in fullscreen mode
        self.resizable(False, False)  # Make the window non-resizable
        
        # Variable to store the selected folder path
        self.folder_path = tk.StringVar()

        # Create and set up the GUI widgets
        self.create_widgets()

    def create_widgets(self):
        """Create all the widgets for the application."""
        tk.Label(self, text="Spotify Data Analyzer", font=("Helvetica", 18, "bold")).pack(pady=20)

        tk.Label(self, text="Select Folder with Spotify Data Files:").pack(pady=5)
        folder_frame = tk.Frame(self)
        folder_frame.pack(pady=10)

        # Entry widget for displaying and typing the folder path
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side="left", padx=5)

        # Button to browse and select a folder
        tk.Button(folder_frame, text="Browse", command=self.select_folder).pack(side="left")

        # Button to start the analysis process
        self.analyze_button = tk.Button(self, text="Analyze Data", command=self.analyze_data)
        self.analyze_button.pack(pady=20)

        # Label to show status updates
        self.info_label = tk.Label(self, text="", fg="blue")
        self.info_label.pack(pady=5)

        # Text widget to display the results of the analysis
        self.results_text = tk.Text(self, height=20, state="disabled")
        self.results_text.pack(padx=20, pady=10, fill="both")

        # Button to export the analysis results
        self.export_button = tk.Button(self, text="Export Results", state="disabled", command=self.export_results)
        self.export_button.pack(pady=10)

    def select_folder(self):
        """Open a dialog to select a folder and set the folder path."""
        folder = filedialog.askdirectory()
        if folder:
            logging.info("Folder selected: %s", folder)
            self.folder_path.set(folder)

    def analyze_data(self):
        """Start the analysis process in a separate thread."""
        folder = self.folder_path.get()
        if not folder:
            logging.error("No folder path provided")
            messagebox.showerror("Error", "Please select a folder first!")
            return

        self.info_label.config(text="Starting analysis...")
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")

        # Run the analysis in a separate thread to keep the GUI responsive
        thread = threading.Thread(target=self.run_analysis, args=(folder,))
        thread.start()

    def run_analysis(self, folder):
        """Perform the analysis process: load files, analyze data, and display results."""
        try:
            # Load and analyze the streaming data
            data = load_streaming_history_files(folder)
            results = analyze_streaming_data(data)

            # Display the results in the GUI
            self.display_results(results)

            # Enable the export button after successful analysis
            self.export_button.config(state="normal")
        except Exception as e:
            logging.error("Analysis failed: %s", str(e))
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.info_label.config(text="Analysis complete.")

    def display_results(self, results):
        """Display the analysis results in the text widget."""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)

        # Custom formatting for enhanced output display
        self.results_text.insert(tk.END, "[\nYour All Time History\n\n")

        # Listening Habits
        self.results_text.insert(tk.END, "Listening Habits\n")
        self.results_text.insert(tk.END, f"Total Minutes Listened: {results['total_minutes']} minutes\n")
        self.results_text.insert(tk.END, f"Average Listening Time per Day: {results['average_daily_minutes']} minutes\n")
        self.results_text.insert(tk.END, f"Most Active Listening Hours: {results['most_active_hour']} PM ({results['time_period']} jams!)\n")
        self.results_text.insert(tk.END, f"Days with Most Listening Activity: {', '.join(results['activity_days'])}\n\n")

        # Top Artists
        self.results_text.insert(tk.END, "Top Artists:\n")
        for artist, ms in results["top_artists"]:
            minutes = round(ms / (1000 * 60), 2)
            hours = round(minutes / 60, 2)
            days = round(hours / 24, 2)
            self.results_text.insert(tk.END, f"\t{artist} – {ms} ms ({minutes} minutes | {hours} hours | {days} days)\n")

        # Top Tracks
        self.results_text.insert(tk.END, "\nTop Tracks:\n")
        for track, ms in results["top_tracks"]:
            minutes = round(ms / (1000 * 60), 2)
            hours = round(minutes / 60, 2)
            days = round(hours / 24, 2)
            self.results_text.insert(tk.END, f"\t{track} – {ms} ms ({minutes} minutes | {hours} hours | {days} days)\n")

        # Top Albums
        self.results_text.insert(tk.END, "\nTop Albums:\n")
        for album, ms in results["top_albums"]:
            minutes = round(ms / (1000 * 60), 2)
            hours = round(minutes / 60, 2)
            days = round(hours / 24, 2)
            self.results_text.insert(tk.END, f"\t{album} – {ms} ms ({minutes} minutes | {hours} hours | {days} days)\n")

        # Final Milestones
        self.results_text.insert(tk.END, "\nMilestones and Achievements\n")
        self.results_text.insert(tk.END, f"Total Streams: {len(set(item['spotify_track_uri'] for item in data if 'spotify_track_uri' in item))} tracks streamed\n")
        total_hours = round(results['total_minutes'] / 60, 2)
        total_days = round(total_hours / 24, 2)
        self.results_text.insert(tk.END, f"Total Hours Listened: {total_hours} hours (that’s more than {total_days} full days of music!)\n")
        self.results_text.insert(tk.END, f"Longest Listening Streak: {results['longest_streak']} consecutive days\n")
        self.results_text.insert(tk.END, f"Most Played Day: {results['most_played_day']} with {round(results['most_played_time'], 2)} hours streamed\n")

        self.results_text.insert(tk.END, "]\n")
        self.results_text.config(state="disabled")

    def export_results(self):
        """Export the analysis results to a JSON file in the user's Documents folder."""
        try:
            # Define the folder path for exporting results
            results_folder = os.path.join(os.path.expanduser("~"), "Documents", "Spotify Listening Data")
            os.makedirs(results_folder, exist_ok=True)

            # Define the full path for the export file
            file_path = os.path.join(results_folder, "analysis_results.json")
            logging.info("Exporting results to: %s", file_path)

            # Write results to the file in JSON format
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.results_text.get("1.0", tk.END), f)

            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            logging.error("Failed to export results: %s", str(e))
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = SpotifyDataApp()
    app.mainloop()

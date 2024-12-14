# Spotify Data Analyzer

## Overview
The Spotify Data Analyzer is a Python-based application that processes your Spotify streaming history, analyzes it, and provides detailed insights into your listening habits. The results include metrics such as total listening time, top artists, tracks, and albums, along with milestones like the longest listening streak and most played day.

## Features
- **GUI Interface**: User-friendly interface for folder selection and data visualization.
- **Detailed Insights**:
  - Total minutes listened.
  - Average listening time per day.
  - Most active listening hours with personalized comments.
  - Days with most listening activity, categorized by week position.
  - Top artists, tracks, and albums by total listening time.
  - Unique tracks streamed and milestones like longest listening streak and most played day.
- **Data Export**: Export analysis results to a JSON file.

## Requirements
- Python 3.8 or higher
- Required Python libraries:
  - `tkinter`
  - `json`
  - `os`
  - `collections`
  - `datetime`
  - `logging`

## Setup Instructions

### 1. Clone the Repository
Download or clone the repository to your local machine:
```bash
git clone https://github.com/tj-batubo/spotify-data-analyzer.git
cd spotify-data-analyzer
```

### 2. Install Dependencies
Make sure you have Python installed on your system. The required libraries are part of the Python standard library, so no additional installation is needed.

### 3. Prepare Your Spotify Data
1. Log in to your Spotify account.
2. Go to **Settings > Privacy Settings > Download Your Data**.
3. Request your Spotify streaming data and download the ZIP file provided.
4. Extract the ZIP file to a folder on your computer.

### 4. Run the Application
Run the `spotify_data_analyzer.py` script:
```bash
python spotify_data_analyzer.py
```

## Usage

### Step 1: Start the Application
1. When you run the script, the application launches in fullscreen mode.
2. Use the "Browse" button to select the folder containing your Spotify JSON data files.

### Step 2: Analyze Data
1. Click the **Analyze Data** button.
2. The application processes the data and displays detailed results, including:
   - Listening habits (total minutes, most active hours, etc.).
   - Top artists, tracks, and albums by listening time.
   - Unique track count, longest listening streak, and most played day.

### Step 3: Export Results
1. After analysis, click the **Export Results** button.
2. The results will be saved as a JSON file in your system's `Documents/Spotify Listening Data` folder.

## How It Works

1. **Data Loading**:
   - The app reads all JSON files in the selected folder that match the pattern `Streaming_History_Audio_*.json`.
   - It combines and processes the data.

2. **Data Analysis**:
   - Listening metrics are calculated, including total listening time, top artists, tracks, and albums.
   - Activity streaks and most played days are determined.

3. **Results Display**:
   - Results are displayed in a formatted text area within the application.

4. **Exporting Results**:
   - Data can be exported to a JSON file for offline use.

## Example Output
```plaintext
[
Your All Time History

Listening Habits
Total Minutes Listened: 224,666.74 minutes
Average Listening Time per Day: 50 minutes
Most Active Listening Hours: 8 PM - 9 PM (You seem to love your evening jams!)
Days with Most Listening Activity: Fridays and Sundays (You’re most active at the start and end of the weekend!)

Top Artists:
	Joji – 2,000,000 ms (33,000 minutes | 550 hours | 22 days)
	Drake – 1,800,000 ms (30,000 minutes | 500 hours | 20.8 days)
	...

Top Tracks:
	"Run" by Joji – 400,000 ms (6,600 minutes | 110 hours | 4.6 days)
	"Blinding Lights" by The Weeknd – 350,000 ms (5,800 minutes | 96.7 hours | 4 days)
	...

Milestones and Achievements
	Total Streams: 3,800 tracks streamed
	Total Hours Listened: 305 hours (that’s more than 12 full days of music!)
	Longest Listening Streak: 18 consecutive days of listening (a new record!)
	Most Played Day: December 13th, with 10 hours of music streamed in a single day!
]
```

## Troubleshooting
- **No Files Detected**:
  - Ensure the folder contains JSON files named `Streaming_History_Audio_*.json`.
- **Errors During Analysis**:
  - Check the `spotify_data_analyzer.log` file in the project directory for detailed error messages.

## License
This project is licensed under my fucking ass.
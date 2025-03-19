
import speech_recognition as sr
import tkinter as tk
from textblob import TextBlob
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tkcalendar
from db_connection import DatabaseConnection
import pandas as pd
import numpy as np

class MoodAnalyzer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.setup_gui()
        self.mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
        self.weekly_mood = []

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Mood Analyzer")
        self.root.geometry("800x600")

        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input Section
        input_frame = ttk.LabelFrame(main_container, text="Input", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Calendar
        self.cal = tkcalendar.DateEntry(input_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.cal.grid(row=0, column=0, padx=5, pady=5)

        # Text Input
        self.text_input = tk.Text(input_frame, height=3, width=40)
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5)

        self.voice_button = ttk.Button(button_frame, text="Record Voice", command=self.record_voice)
        self.voice_button.grid(row=0, column=0, padx=2)

        self.analyze_button = ttk.Button(button_frame, text="Analyze Text", command=self.analyze_text)
        self.analyze_button.grid(row=0, column=1, padx=2)

        # Analysis Section
        analysis_frame = ttk.LabelFrame(main_container, text="Analysis", padding="5")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Pie Chart
        self.fig = Figure(figsize=(6, 4))
        self.pie_chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, analysis_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

        # Report Section
        report_frame = ttk.LabelFrame(main_container, text="Reports", padding="5")
        report_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Report Buttons
        # self.daily_report_button = ttk.Button(report_frame, text="Daily Report", 
        #                                     command=self.show_daily_report)
        # self.daily_report_button.grid(row=0, column=0, padx=5, pady=5)

        # self.weekly_report_button = ttk.Button(report_frame, text="Weekly Report", 
        #                                      command=self.show_weekly_report)
        # self.weekly_report_button.grid(row=0, column=1, padx=5, pady=5)

        self.date_range_button = ttk.Button(report_frame, text="Date Range Report", 
                                          command=self.show_date_range_report)
        self.date_range_button.grid(row=0, column=2, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(main_container, text="")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

    def analyze_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to analyze")
            return

        selected_date = self.cal.get_date()
        self.process_input(text, "", selected_date)

    def record_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.config(text="Adjusting for ambient noise... Please wait...")
            self.root.update()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            self.status_label.config(text="Ready! Say something about your day...")
            self.root.update()
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                self.status_label.config(text=f"You said: {text}")
                selected_date = self.cal.get_date()
                self.process_input("", text, selected_date)
            except sr.WaitTimeoutError:
                self.status_label.config(text="No speech detected within timeout period")
            except sr.UnknownValueError:
                self.status_label.config(text="Speech was not understood")
            except sr.RequestError as e:
                self.status_label.config(text=f"Could not request results; {e}")

    def process_input(self, text_input, voice_input, date):
        # Analyze sentiment
        text_to_analyze = text_input if text_input else voice_input
        analysis = TextBlob(text_to_analyze)
        sentiment = analysis.sentiment.polarity

        # Determine mood
        if sentiment > 0:
            mood = 'Happy'
        elif sentiment < 0:
            mood = 'Sad'
        else:
            mood = 'Neutral'

        # Update local data
        self.mood_data[mood] += 1
        self.weekly_mood.append(mood)

        # Save to database
        self.db.save_mood_entry(date, text_input, voice_input, sentiment, mood)

        # Update GUI
        self.update_gui()
        self.status_label.config(text=f"Analysis complete! Mood: {mood}")

    def update_gui(self):
        self.pie_chart.clear()
        self.pie_chart.pie(self.mood_data.values(), labels=self.mood_data.keys(), 
                          autopct='%1.1f%%', startangle=140)
        self.pie_chart.axis('equal')
        self.canvas.draw()

    def show_daily_report(self):
        selected_date = self.cal.get_date()
        analysis = self.db.get_daily_analysis(selected_date)
        if analysis:
            self.show_report_window("Daily Analysis", analysis)
        else:
            messagebox.showinfo("Info", "No data available for this date")

    def show_weekly_report(self):
        selected_date = self.cal.get_date()
        week_start = selected_date - timedelta(days=selected_date.weekday())
        analysis = self.db.get_weekly_analysis(week_start)
        if analysis:
            self.show_report_window("Weekly Analysis", analysis)
        else:
            messagebox.showinfo("Info", "No data available for this week")

    def show_date_range_report(self):
        # Create a new window for date range selection
        range_window = tk.Toplevel(self.root)
        range_window.title("Select Date Range")
        range_window.geometry("300x150")

        ttk.Label(range_window, text="Start Date:").pack(pady=5)
        start_cal = tkcalendar.DateEntry(range_window, width=12, background='darkblue',
                                      foreground='white', borderwidth=2)
        start_cal.pack(pady=5)

        ttk.Label(range_window, text="End Date:").pack(pady=5)
        end_cal = tkcalendar.DateEntry(range_window, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        end_cal.pack(pady=5)

        def generate_report():
            entries = self.db.get_mood_entries_by_date_range(start_cal.get_date(), 
                                                           end_cal.get_date())
            if entries:
                self.show_report_window("Date Range Analysis", entries)
            else:
                messagebox.showinfo("Info", "No data available for selected date range")

        ttk.Button(range_window, text="Generate Report", 
                  command=generate_report).pack(pady=10)

    def show_report_window(self, title, data):
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_window.geometry("600x400")

        # Create text widget for report
        report_text = tk.Text(report_window, wrap=tk.WORD, padx=10, pady=10)
        report_text.pack(fill=tk.BOTH, expand=True)

        # Format and display the data
        if isinstance(data, dict):
            report_text.insert(tk.END, f"{title}\n\n")
            for key, value in data.items():
                report_text.insert(tk.END, f"{key}: {value}\n")
        else:
            report_text.insert(tk.END, f"{title}\n\n")
            for entry in data:
                report_text.insert(tk.END, f"Date: {entry['date']}\n")
                report_text.insert(tk.END, f"Mood: {entry['mood_category']}\n")
                report_text.insert(tk.END, f"Sentiment Score: {entry['sentiment_score']}\n")
                report_text.insert(tk.END, "-" * 50 + "\n")

        report_text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
        self.db.close()

if __name__ == "__main__":
    app = MoodAnalyzer()
    app.run()

"""
Program: Genre Statistics Analyzer
This script analySes and visualiSes song genre statistics for a specified 
year from an SQLite database.

Developed by Christian on 15/01/25.

Usage: Ensure the SQLite database is in the same directory. 
Run the script and provide a year between 1998 and 2020 when prompted. 
The program outputs a statistical summary and a pie chart of genre distribution.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

class GenreStatisticsAnalyzer:
    """
    A class to analyse and visualise genre-based song statistics from a SQLite database.

    Attributes:
        db_name (str): Name of the SQLite database file.
        conn (sqlite3.Connection): SQLite database connection object.
        cursor (sqlite3.Cursor): Cursor object for executing SQL queries.

    Methods:
        get_valid_year: Prompts the user to enter a valid year between 1998 and 2020.
        get_songs_for_year: Retrieves songs and their genres for a specific 
        year from the database.
        generate_genre_statistics: Calculates and displays genre-based statistics 
        and visualisations for the specified year.
        close_connection: Closes the connection to the SQLite database.
    """
    def __init__(self, db_name):
        """
        Initializes the GenreStatisticsAnalyzer with the database name 
        and sets up a database connection.

        Parameters:
            db_name (str): Name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_valid_year(self):
        """
        Prompt the user to input a valid year between 1998 and 2020.

        Returns:
            int: A valid year entered by the user.
        """
        while True:
            year = input("Please enter a year between 1998 and 2020: ")
            try:
                year = int(year)
                if 1998 <= year <= 2020:
                    return year
                else:
                    print("Year out of range. Please enter a year between 1998 and 2020.")
            except ValueError:
                print("Invalid input. Please enter a valid year (e.g., 2000).")

    def get_songs_for_year(self, year):
        """
        Retrieve all songs and their genres for a specific year from the database.

        Args:
            year (int): The year for which to retrieve song data.

        Returns:
            list: A list of tuples containing song details (song name, year, danceability, 
            popularity, genre).
        """
        query = """
        SELECT Song.song_name, Song.year, Song.danceability, Song.popularity, Genre.genre_name
        FROM Song
        JOIN SongGenre ON Song.id = SongGenre.song_id
        JOIN Genre ON SongGenre.genre_id = Genre.id
        WHERE Song.year = ?
        """
        self.cursor.execute(query, (year,))
        return self.cursor.fetchall()

    def generate_genre_statistics(self, year):
        """
        Calculate and display statistics for songs in a given year.

        Args:
            year (int): The year for which to generate statistics.

        Displays:
            - A summary table of genre-based statistics (total songs, 
            average danceability, and popularity).
            - A pie chart showing the distribution of songs by genre.
        """
        data = self.get_songs_for_year(year)

        if not data:
            print(f"No data available for the year {year}.")
            return

        # Convert data into a DataFrame
        df = pd.DataFrame(data, columns=["song_name", "year", "danceability", "popularity", "genre"])

        # Calculate key statistics for each genre
        genre_stats = df.groupby("genre").agg(
            total_songs=("song_name", "count"),
            avg_danceability=("danceability", "mean"),
            avg_popularity=("popularity", "mean")
        ).reset_index()

        # Display the tabular summary
        print(f"Statistics for songs in {year}:")
        print(genre_stats)

        # Visualize the data (Pie chart for the total number of songs per genre)
        genre_counts = genre_stats["total_songs"]
        genre_labels = genre_stats["genre"]
        plt.figure(figsize=(8, 6))
        plt.pie(
            genre_counts,
            labels=genre_labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=plt.cm.Paired.colors
        )
        plt.title(f"Distribution of Songs by Genre in {year}")
        plt.axis('equal')
        plt.show()

    def close_connection(self):
        """Close the connection to the SQLite database."""
        self.conn.close()

# Main program execution
if __name__ == "__main__":
    db_name = "CWDatabase.db"
    analyzer = GenreStatisticsAnalyzer(db_name)

    try:
        year = analyzer.get_valid_year()
        analyzer.generate_genre_statistics(year)
    finally:
        analyzer.close_connection()

    print("Program completed successfully!")

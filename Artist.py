"""
Program: Artist Popularity Analyzer
This script analyses and compares an artist's popularity against overall genre 
popularity from the SQLite database.

Developed by Christian on 15/01/25.

Usage: Ensure the SQLite database ('CWDatabase.db' for this case) is in the same directory. 
Run the script and input the artist's name when prompted.
The program will output a table and a bar chart comparing the artist's 
average popularity with overall genre popularity.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

class ArtistPopularityAnalyzer:
    """
    A class to analyze and visualize an artist's popularity compared to 
    overall genre popularity in a database.

    Attributes:
        db_name (str): Name of the SQLite database file.
        conn (sqlite3.Connection): SQLite database connection object.
        cursor (sqlite3.Cursor): Cursor object for executing SQL queries.

    Methods:
        get_artist_id: Retrieves the artist's ID from the database using their name.
        get_artist_popularity_per_genre: Retrieves the artist's average popularity by genre.
        get_overall_genre_popularity: Retrieves the overall average popularity by genre.
        display_artist_vs_genre_popularity: Displays and visualizes a comparison between 
        the artist's and genre's popularity.
        close_connection: Closes the connection to the SQLite database.
    """
    
    def __init__(self, db_name):
        """
        Initializes the ArtistPopularityAnalyzer with the database name and sets up
        a database connection.

        Parameters:
            db_name (str): Name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_artist_id(self, artist_name):
        """
        Retrieve the ID of the specified artist from the database.

        Args:
            artist_name (str): Name of the artist.

        Returns:
            int or None: The artist's ID if found, otherwise None.
        """
        artist_name = artist_name.lower().replace(" ", "_")
        self.cursor.execute("SELECT id FROM Artist WHERE artist_name = ?", (artist_name,))
        artist_id = self.cursor.fetchone()
        if artist_id is None:
            print(f"Artist '{artist_name}' not found in the database.")
            return None
        return artist_id[0]

    def get_artist_popularity_per_genre(self, artist_id):
        """
        Retrieve the average popularity of the artist's songs by genre.

        Args:
            artist_id (int): ID of the artist.

        Returns:
            list: List of tuples containing genre names and the artist's average popularity.
        """
        query = """
        SELECT Genre.genre_name, AVG(Song.popularity) AS avg_artist_popularity
        FROM Song
        JOIN SongGenre ON Song.id = SongGenre.song_id
        JOIN Genre ON SongGenre.genre_id = Genre.id
        WHERE Song.artist_id = ?
        GROUP BY Genre.genre_name
        """
        self.cursor.execute(query, (artist_id,))
        return self.cursor.fetchall()

    def get_overall_genre_popularity(self):
        """
        Retrieve the overall average popularity of each genre.

        Returns:
            list: List of tuples containing genre names and their overall average popularity.
        """
        query = """
        SELECT Genre.genre_name, AVG(Song.popularity) AS avg_genre_popularity
        FROM Song
        JOIN SongGenre ON Song.id = SongGenre.song_id
        JOIN Genre ON SongGenre.genre_id = Genre.id
        GROUP BY Genre.genre_name
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def display_artist_vs_genre_popularity(self, artist_name):
        """
        Display and visualize the artist's popularity compared to overall genre popularity.

        Args:
            artist_name (str): Name of the artist.
        """
        artist_id = self.get_artist_id(artist_name)
        if not artist_id:
            return

        artist_genre_popularity = self.get_artist_popularity_per_genre(artist_id)
        artist_df = pd.DataFrame(artist_genre_popularity, columns=["genre", "avg_artist_popularity"])

        overall_genre_popularity = self.get_overall_genre_popularity()
        overall_df = pd.DataFrame(overall_genre_popularity, columns=["genre", "avg_genre_popularity"])

        comparison_df = pd.merge(artist_df, overall_df, on="genre", how="outer")

        # Highlight rows where artist's popularity exceeds genre's popularity
        def highlight_row(row):
            if row["avg_artist_popularity"] > row["avg_genre_popularity"]:
                return ["background-color: yellow" for _ in row]
            else:
                return ["" for _ in row]
        
        styled_table = comparison_df.style.apply(highlight_row, axis=1)
        print(f"Popularity Comparison for Artist: {artist_name}")
        display(styled_table)  # Display styled DataFrame

        # Plotting a bar chart for the artist's vs genre's popularity
        plt.figure(figsize=(10, 6))
        width = 0.35  # Bar width
        genres = comparison_df["genre"]
        artist_pop = comparison_df["avg_artist_popularity"]
        genre_pop = comparison_df["avg_genre_popularity"]

        x = range(len(genres))
        plt.bar([p - width / 2 for p in x], artist_pop, width, 
                label="Artist's Popularity", color='blue')
        plt.bar([p + width / 2 for p in x], genre_pop, width, 
                label="Overall Genre Popularity", color='orange', alpha=0.7)

        plt.xlabel('Genre')
        plt.ylabel('Average Popularity')
        plt.title(f"Artist vs Overall Genre Popularity for {artist_name}")
        plt.xticks(x, genres, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def close_connection(self):
        """Close the connection to the SQLite database."""
        self.conn.close()

# Main program execution
if __name__ == "__main__":
    db_name = "CWDatabase.db"
    analyzer = ArtistPopularityAnalyzer(db_name)

    try:
        artist_name = input("Please enter the artist's name: ")
        analyzer.display_artist_vs_genre_popularity(artist_name)
    finally:
        analyzer.close_connection()
        
    print("Program completed successfully!")

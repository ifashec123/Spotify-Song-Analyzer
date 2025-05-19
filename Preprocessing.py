"""
Program: This script processes a song dataset from a CSV file and populates an SQLite database 
with normalized tables for songs, artists, genres, and their relationships.

Developed by Christian on 15/01/25.

Usage: Update 'csv_path' with the path to the dataset. Running this script creates a 
database file 'CWDatabase.db' and populates it with preprocessed data.
"""

import pandas as pd
import sqlite3

class SongDatasetProcessor:
    """
    Loads and preprocesses a song dataset to prepare it for database insertion.

    Attributes:
        csv_path (str): Path to the CSV file containing the dataset.
        db_name (str): Name of the SQLite database file.
        df (DataFrame): Processed dataset.

    Methods:
        load_and_preprocess_data: Reads the dataset, applies filtering, and preprocesses columns.
    """
    def __init__(self, csv_path, db_name):
        """
        Initializes the SongDatasetProcessor with the dataset path and database name.

        Parameters:
            csv_path (str): Path to the CSV file.
            db_name (str): Name of the database file.
        """
        self.csv_path = csv_path
        self.db_name = db_name
        self.df = None

    def load_and_preprocess_data(self):
        """
        Reads and preprocesses the dataset:
        - Renames the 'duration_ms' column to 'duration' and converts its units to seconds.
        - Filters rows based on popularity, speechiness, and danceability criteria.
        - Standardizes artist names by converting to lowercase and replacing spaces with underscores.
        """
        self.df = pd.read_csv(self.csv_path)
        self.df.rename(columns={"duration_ms": "duration"}, inplace=True)
        self.df["duration"] = (self.df["duration"] / 1000).round().astype(int)
        self.df = self.df[
            (self.df["popularity"] > 50) &
            (self.df["speechiness"] >= 0.33) &
            (self.df["speechiness"] <= 0.66) &
            (self.df["danceability"] > 0.20)
        ]
        self.df["artist"] = self.df["artist"].str.lower().str.replace(" ", "_")
        self.df.reset_index(drop=True, inplace=True)
        print(f"Filtered dataset contains {len(self.df)} songs.")

class DatabaseManager:
    """
    Manages the creation and population of an SQLite database with song, artist, and genre data.

    Attributes:
        db_name (str): Name of the SQLite database file.
        conn (sqlite3.Connection): SQLite database connection object.
        cursor (sqlite3.Cursor): Cursor object for executing SQL queries.

    Methods:
        create_tables: Creates database tables for storing songs, artists, genres, 
        and their many to many relationships.
        get_or_create_id: Retrieves or inserts a record in the specified table and returns its ID.
        populate_database: Inserts processed dataset rows into the database tables.
        close_connection: Closes the database connection.
    """
    def __init__(self, db_name):
        """
        Initializes the DatabaseManager with the database name and sets up a database connection.

        Parameters:
            db_name (str): Name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """
        Creates normalized tables in the database:
        - Genre: Stores unique genres.
        - Artist: Stores unique artists.
        - Song: Stores song details linked to artists.
        - SongGenre: Stores the many-to-many relationship between songs and genres.
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_name TEXT NOT NULL UNIQUE
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Artist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL UNIQUE
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Song (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            explicit INTEGER NOT NULL,
            year INTEGER NOT NULL,
            popularity INTEGER NOT NULL,
            danceability REAL NOT NULL,
            speechiness REAL NOT NULL,
            artist_id INTEGER NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES Artist(id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS SongGenre (
            song_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (song_id, genre_id),
            FOREIGN KEY (song_id) REFERENCES Song(id),
            FOREIGN KEY (genre_id) REFERENCES Genre(id)
        );
        """)
        self.conn.commit()

    def get_or_create_id(self, table, column, value):
        """
        Retrieves the ID of a record in the specified table by column and value.
        If the record does not exist, inserts it and returns the new ID.

        Parameters:
            table (str): Table name.
            column (str): Column name to search for.
            value (str): Value to search for.

        Returns:
            int: ID of the existing or newly created record.
        """
        self.cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
        row_id = self.cursor.fetchone()
        if row_id is None:
            self.cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
            self.conn.commit()
            return self.cursor.lastrowid
        return row_id[0]

    def populate_database(self, data):
        """
        Populates the database with song data from the processed dataset.

        Parameters:
            data (DataFrame): Processed dataset containing song, artist, and genre details.
        """
        for _, row in data.iterrows():
            artist_id = self.get_or_create_id("Artist", "artist_name", row["artist"])
            self.cursor.execute("""
            INSERT INTO Song (song_name, duration, explicit, year, popularity, danceability, 
            speechiness, artist_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["song"],
                row["duration"],
                int(row["explicit"]),
                row["year"],
                row["popularity"],
                row["danceability"],
                row["speechiness"],
                artist_id
            ))
            song_id = self.cursor.lastrowid

            genres = row["genre"].split(", ")
            for genre in genres:
                genre_id = self.get_or_create_id("Genre", "genre_name", genre)
                self.cursor.execute("""
                INSERT INTO SongGenre (song_id, genre_id)
                VALUES (?, ?)
                """, (song_id, genre_id))
        self.conn.commit()

    def close_connection(self):
        """Closes the SQLite database connection."""
        self.conn.close()

def main():
    csv_path = "songs.csv"  # Update this if the path differs.
    db_name = "CWDatabase.db"
    
    processor = SongDatasetProcessor(csv_path, db_name)
    processor.load_and_preprocess_data()
    
    db_manager = DatabaseManager(db_name)
    db_manager.create_tables()
    db_manager.populate_database(processor.df)
    db_manager.close_connection()

    print("Database and tables populated successfully!")

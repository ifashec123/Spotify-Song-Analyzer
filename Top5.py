import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

"""
Program: Top 5 Artists Ranking Analysis

This program connects to an SQLite database to calculate and display artist rankings 
based on song count and popularity over a specified year range (1998-2020). Results 
are shown in a table and visualised in a line chart.

Written by: F128607
Date: 18/01/25
"""

class ArtistRankingAnalyzer:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_year_range(self):
        """
        Prompt the user to input a year range and validate the input.

        Returns:
            tuple: A tuple containing the start year and end year.
        """
        try:
            start_year = int(input("Enter the start year (1998–2020): "))
            end_year = int(input("Enter the end year (1998–2020): "))
            if start_year < 1998 or end_year > 2020 or start_year > end_year:
                print("Invalid range. Please enter years between 1998 and 2020.")
                return self.get_year_range()
            return start_year, end_year
        except ValueError:
            print("Invalid input. Please enter valid years.")
            return self.get_year_range()

    def fetch_artist_data(self, start_year, end_year):
        """
        Fetch relevant artist data for the given year range from the SQLite database.

        Args:
            start_year (int): Start year of the range.
            end_year (int): End year of the range.

        Returns:
            DataFrame: A pandas DataFrame containing artist data.
        """
        query = f"""
            SELECT 
                Artist.artist_name,
                Song.year,
                COUNT(Song.id) AS total_songs,
                AVG(Song.popularity) AS avg_popularity
            FROM Song
            JOIN Artist ON Song.artist_id = Artist.id
            WHERE Song.year BETWEEN ? AND ?
            GROUP BY Artist.artist_name, Song.year
            ORDER BY Song.year, total_songs DESC;
        """
        data = pd.read_sql_query(query, self.conn, params=(start_year, end_year))
        return data

    def calculate_ranking(self, data, weight_songs=0.6, weight_popularity=0.4):
        """
        Calculate rank values for each artist using a weighted formula.

        Args:
            data (DataFrame): DataFrame containing artist data.
            weight_songs (float): Weight for the total number of songs.
            weight_popularity (float): Weight for the average popularity.

        Returns:
            DataFrame: DataFrame with an additional column for rank values.
        """
        data["rank_value"] = (
            data["total_songs"] * weight_songs + data["avg_popularity"] * weight_popularity
        )
        return data

    def generate_table(self, data, start_year, end_year):
        """
        Create a pivot table for artist rankings over the specified year range.

        Args:
            data (DataFrame): DataFrame containing artist data with rank values.
            start_year (int): Start year of the range.
            end_year (int): End year of the range.

        Returns:
            DataFrame: Pivot table with yearly rankings and average rank values.
        """
        pivot = data.pivot(index="artist_name", columns="year", values="rank_value")
        
        # Ensure all years are included, even if some artists have missing data
        all_years = list(range(start_year, end_year + 1))
        pivot = pivot.reindex(columns=all_years)

        # Calculate the "Average" column after reindexing
        pivot["Average"] = pivot.mean(axis=1, skipna=True)
        pivot = pivot.sort_values(by="Average", ascending=False)
        return pivot

    def display_table(self, table):
        """
        Display the table and highlight the top artist for each year.

        Args:
            table (DataFrame): Pivot table containing rankings.

        Returns:
            Styler: A pandas Styler object for displaying the table.
        """
        def highlight_max(dataframe):
            styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)
            for col in dataframe.columns[:-1]:  # Exclude the 'Average' column
                if dataframe[col].dtype in ["float64", "int64"]:
                    max_value = dataframe[col].max()
                    styles.loc[dataframe[col] == max_value, col] = "background-color: yellow; font-weight: bold;"
            return styles

        styled_table = table.style.apply(highlight_max, axis=None)
        return styled_table

    def plot_ranking(self, data, start_year, end_year):
        """
        Visualise the yearly rank values using a line chart.

        Args:
            data (DataFrame): Pivot table containing rankings.
            start_year (int): Start year of the range.
            end_year (int): End year of the range.
        """
        plt.figure(figsize=(12, 6))

        # Interpolate missing values for each artist
        data_interpolated = data.interpolate(method='linear', axis=1)

        for artist in data.index:
            # Extract actual and interpolated data
            original_yearly_data = data.loc[artist, :].drop("Average", errors="ignore")
            interpolated_yearly_data = data_interpolated.loc[artist, :].drop("Average", errors="ignore")
            
            # Plot the continuous line using interpolated data
            plt.plot(interpolated_yearly_data.index, interpolated_yearly_data.values, label=artist)
            
            # Add points only for years with actual values
            plt.scatter(original_yearly_data.index, original_yearly_data.values, s=30)

        # Plot yearly averages (ensure it covers all years in the range)
        averages = data.drop("Average", axis=1).mean(axis=0)
        averages = averages.reindex(range(start_year, end_year + 1)).interpolate(method='linear')
        plt.plot(averages.index, averages.values, linestyle="--", color="black", label="Yearly Average")

        plt.title(f"Top 5 Artists Ranking ({start_year}–{end_year})")
        plt.xlabel("Year")
        plt.ylabel("Rank Value")
        plt.legend()
        plt.grid()
        plt.show()

    def close_connection(self):
        """Close the connection to the SQLite database."""
        self.conn.close()

    def main(self, start_year=None, end_year=None):
        """
        Main program execution function.
        Args:
            start_year (int): Start year for the analysis. If None, prompt the user.
            end_year (int): End year for the analysis. If None, prompt the user.
        """
        print("Top 5 Artists Ranking Program")

        # Step 1: Get year range if not provided
        if start_year is None or end_year is None:
            start_year, end_year = self.get_year_range()

        # Step 2: Fetch data from the database
        data = self.fetch_artist_data(start_year, end_year)

        if data.empty:
            print("No data available for the specified year range.")
            return

        # Step 3: Calculate rank values
        ranked_data = self.calculate_ranking(data)

        # Step 4: Generate top 5 table
        top_artists = self.generate_table(ranked_data, start_year, end_year).head(5)

        # Step 5: Display and visualize results
        styled_table = self.display_table(top_artists)
        display(styled_table)
        self.plot_ranking(top_artists, start_year, end_year)

# Program execution
if __name__ == "__main__":
    db_name = "CWDatabase.db"
    analyzer = ArtistRankingAnalyzer(db_name)

    try:
        analyzer.main()
    finally:
        analyzer.close_connection()

    print("Program completed successfully!")
# MA31-Project-1-Youtube-Data-Harvesting
         `YouTube Data Harvesting and Warehousing using SQL and Streamlit`

    This application based on Streamlit, fetches, stores, and analyzes YouTube channel and video data with the use of the YouTube Data API and MySQL database.

Features:
    Retrieve channel and video data from YouTube using the YouTube Data API
    Store the retrieved data in a MySQL database
    Execute predefined queries to analyze the stored data

System Requirements:
    Python 3.7+
    MySQL server
    YouTube Data API key

Install the required Python packages: 
           pip install -r requirements.txt

Set up your MySQL database: 
     Create a new database named youtube_data
     Update the MySQL connection details in the create_connection() function if necessary

Set up your YouTube Data API key: 
      Obtain an API key from the Google Developers Console
      Replace the api_key variable in the code with your actual API key

1.	How to Run the Streamlit app: 
              streamlit run app.py
2.	Open your web browser and go to http://localhost:8501
3.	Enter a YouTube Channel ID in the input field and click "Retrieve and Store Channel Data" to fetch and store the data
4.	Use the dropdown menu to select and execute predefined queries on the stored data

Predefined Queries:
  1.	Video names and their channels
  2.	Channels with most videos
  3.	Top 10 most viewed videos
  4.	Comments count for each video
  5.	Videos with highest likes
  6.	Total likes for each video
  7.	Total views for each channel
  8.	Channels with videos published in 2022
  9.	Average video duration for each channel
  10.	Videos with highest comment count

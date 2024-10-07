import streamlit as st
import googleapiclient.discovery
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

# YouTube API details
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyCLs4QUMNYAVSOXVBbE2Qkglsxd95xsaWo" 
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

# MySQL connection established
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect( host="localhost", user="root", password="admin",database="youtube_data",charset='utf8mb4'        )
        print("Successfully connected to MySQL database")
    except Error as e:
        print(f"Error: {e}")
    return connection

# This Function to get channel details
def get_channel_data(channel_id):
    request = youtube.channels().list(part="snippet,statistics,contentDetails", id=channel_id)
    response = request.execute()
    
    if 'items' in response:
        channel_data = response['items'][0]
        return {
            'channel_id': channel_id,
            'channel_name': channel_data['snippet']['title'],
            'subscribers': channel_data['statistics']['subscriberCount'],
            'total_videos': channel_data['statistics']['videoCount'],
            'playlist_id': channel_data['contentDetails']['relatedPlaylists']['uploads']   }
    return None

# This Function to get video details
def get_video_data(video_id):
    request = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id)
    response = request.execute()

    if 'items' in response:
        video_data = response['items'][0]
        published_at = datetime.strptime(video_data['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        return {
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'views': video_data['statistics']['viewCount'],
            'likes': video_data['statistics'].get('likeCount', 0),
            'comments': video_data['statistics'].get('commentCount', 0),
            'duration': video_data['contentDetails']['duration'],
            'published_at': published_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    return None

# To insert data into MySQL
def insert_data_to_mysql(connection, channel_data, videos_data):
    cursor = connection.cursor()
    
    # To Insert channel data
    channel_insert_query = """
    INSERT INTO channels (channel_id, channel_name, subscribers, total_videos, playlist_id)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    channel_name = VALUES(channel_name),
    subscribers = VALUES(subscribers),
    total_videos = VALUES(total_videos),
    playlist_id = VALUES(playlist_id)
    """
    channel_values = (
        channel_data['channel_id'],channel_data['channel_name'],channel_data['subscribers'], channel_data['total_videos'],
        channel_data['playlist_id'] )
    cursor.execute(channel_insert_query, channel_values)
    
    # To Insert video data
    video_insert_query = """
    INSERT INTO videos (video_id, channel_id, title, views, likes, comments, duration, published_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    views = VALUES(views),
    likes = VALUES(likes),
    comments = VALUES(comments),
    duration = VALUES(duration),
    published_at = VALUES(published_at)
    """
    for video in videos_data:
        video_values = (
            video['video_id'],
            channel_data['channel_id'],
            video['title'],
            video['views'],
            video['likes'],
            video['comments'],
            video['duration'],
            video['published_at']
        )
        cursor.execute(video_insert_query, video_values)
    
    connection.commit()
    cursor.close()

def get_predefined_query(query_name):
    queries = {
        "Video names and their channels": """
            SELECT v.title AS video_name, c.channel_name
            FROM videos v
            JOIN channels c ON v.channel_id = c.channel_id
        """,
        "Channels with most videos": """
            SELECT channel_name, total_videos
            FROM channels
            ORDER BY total_videos DESC
            LIMIT 10
        """,
        "Top 10 most viewed videos": """
            SELECT v.title AS video_name, c.channel_name, v.views
            FROM videos v
            JOIN channels c ON v.channel_id = c.channel_id
            ORDER BY v.views DESC
            LIMIT 10
        """,
        "Comments count for each video": """
            SELECT title AS video_name, comments
            FROM videos
            ORDER BY comments DESC
        """,
        "Videos with highest likes": """
            SELECT v.title AS video_name, c.channel_name, v.likes
            FROM videos v
            JOIN channels c ON v.channel_id = c.channel_id
            ORDER BY v.likes DESC
            LIMIT 10
        """,
        "Total likes for each video": """
            SELECT title AS video_name, likes
            FROM videos
            ORDER BY likes DESC
        """,
        "Total views for each channel": """
            SELECT c.channel_name, SUM(v.views) AS total_views
            FROM channels c
            JOIN videos v ON c.channel_id = v.channel_id
            GROUP BY c.channel_id
            ORDER BY total_views DESC
        """,
        "Channels with videos published in 2022": """
            SELECT DISTINCT c.channel_name
            FROM channels c
            JOIN videos v ON c.channel_id = v.channel_id
            WHERE YEAR(v.published_at) = 2022
        """,
        "Average video duration for each channel": """
            SELECT c.channel_name, AVG(TIME_TO_SEC(v.duration)) AS avg_duration_seconds
            FROM channels c
            JOIN videos v ON c.channel_id = v.channel_id
            GROUP BY c.channel_id
            ORDER BY avg_duration_seconds DESC
        """,
        "Videos with highest comment count": """
            SELECT v.title AS video_name, c.channel_name, v.comments
            FROM videos v
            JOIN channels c ON v.channel_id = c.channel_id
            ORDER BY v.comments DESC
            LIMIT 10
        """
    }
    return queries.get(query_name, "SELECT 1") 
# To interact user using Streamlit app
def main():
    st.title("YouTube Data Harvesting and Warehousing")
    
    # to get Input for channel ID from user 
    channel_id = st.text_input("Enter YouTube Channel ID for search")
    if st.button("Retrieve and Store Channel Data"):
        channel_data = get_channel_data(channel_id)
        if channel_data:
            st.write(f"Channel Name: {channel_data['channel_name']}")
            st.write(f"Subscribers: {channel_data['subscribers']}")
            st.write(f"Total Videos: {channel_data['total_videos']}")
          
            # To Get video data 
            playlist_id = channel_data['playlist_id']
            videos_data = []
            next_page_token = None
            
            with st.spinner("Retrieving video data..."):
                while True:
                    request = youtube.playlistItems().list(
                        part="snippet",
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                    response = request.execute()
                    
                    for item in response['items']:
                        video_id = item['snippet']['resourceId']['videoId']
                        video_data = get_video_data(video_id)
                        if video_data:
                            videos_data.append(video_data)
                    
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token or len(videos_data) >= 200:  
                        break
            
            st.write(f"Retrieved data for {len(videos_data)} videos")
            
            # To Store data in MySQL
            connection = create_connection()
            if connection:
                with st.spinner("Storing data in MySQL..."):
                    insert_data_to_mysql(connection, channel_data, videos_data)
                st.success("Data successfully stored in MySQL database")
                connection.close()
        else:
            st.error("Failed to retrieve channel data. Please check the channel ID.")
  
  #to get query from user
    query_options = [
        "Select a query",
        "Video names and their channels",
        "Channels with most videos",
        "Top 10 most viewed videos",
        "Comments count for each video",
        "Videos with highest likes",
        "Total likes for each video",
        "Total views for each channel",
        "Channels with videos published in 2022",
        "Average video duration for each channel",
        "Videos with highest comment count"   ]
    selected_query = st.selectbox("Select any one query to execute:", query_options)

    if selected_query != "Select a query":
        connection = create_connection()
        if connection:
            try:
                query = get_predefined_query(selected_query)
                df = pd.read_sql_query(query, connection)
                st.subheader(selected_query)
                st.dataframe(df)
            except Error as e:
                st.error(f"Error executing query: {e}")
            finally:
                connection.close()
    
if __name__ == "__main__":
    main()

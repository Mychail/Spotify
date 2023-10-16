import requests
import pandas as pd

# Function to get a Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    try:
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        auth_data = auth_response.json()
        return auth_data['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

# Function to search for a track and get its ID
def search_track(track_name, artist_name, token):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    try:
        response = requests.get(url, headers={
            'Authorization': f'Bearer {token}'
        })
        json_data = response.json()
        if 'tracks' in json_data and 'items' in json_data['tracks'] and json_data['tracks']['items']:
            first_result = json_data['tracks']['items'][0]
            track_id = first_result['id']
            return track_id, first_result['name']  # Return both track ID and name
        else:
            print(f"No matching track found for '{track_name}' by '{artist_name}'.")
            return None, None
    except Exception as e:
        print(f"Error searching for track: {e}")
        return None, None

# Function to get track details
def get_track_details(track_id, token):
    # Get the track name from the provided track ID
    _, track_name = search_track("", "", token)
    
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    try:
        response = requests.get(url, headers={
            'Authorization': f'Bearer {token}'
        })
        json_data = response.json()
        if 'album' in json_data and 'images' in json_data['album'] and json_data['album']['images']:
            image_url = json_data['album']['images'][0]['url']
            return image_url, track_name  # Return both image URL and track name
        else:
            print(f"No image URL found for track with ID {track_id}.")
            return None, track_name
    except Exception as e:
        print(f"Error getting track details: {e}")
        return None, track_name

# Your Spotify API Credentials
client_id = 'cce39ae5374b4672b3175ab59d516c4f'
client_secret = '97b857d7d9834890a192e2d8853dcdf2'

# Get Access Token
access_token = get_spotify_token(client_id, client_secret)

if access_token:
    # Read your DataFrame (replace 'your_file.csv' with the path to your CSV file)
    try:
        df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        df_spotify = pd.DataFrame()

    if not df_spotify.empty:
        # Loop through each row to get track details and add to DataFrame
        for i, row in df_spotify.iterrows():
            track_id, track_name = search_track(row['track_name'], row['artist_name'], access_token)
            if track_id:
                image_url, _ = get_track_details(track_id, access_token)  # Use the returned track name
                df_spotify.at[i, 'image_url'] = image_url
                df_spotify.at[i, 'track_name'] = track_name  # Add the track name to the DataFrame

        # Save the updated DataFrame (replace 'updated_file.csv' with your desired output file name)
        try:
            df_spotify.to_csv('updated_spotify.csv', index=False)
            print("Data has been successfully updated and saved.")
        except Exception as e:
            print(f"Error saving the updated DataFrame: {e}")
    else:
        print("The input DataFrame is empty or couldn't be read.")
else:
    print("Access token not obtained. Check your Spotify API credentials.")

# Spotify New Releases Tracker

## Overview

This script tracks new music releases from artists you follow on Spotify and sends you an email with the latest albums and singles. It integrates with Logitech Media Server (LMS) to provide direct play links for your favorite tracks.

## Prerequisites

Before running the script, ensure you have the following:

- Python 3.7 or higher installed
- A Spotify Developer account to create a new application and obtain credentials
- An LMS server setup
- SMTP server details for sending emails

## Configuration

Create a `config.py` file in the same directory as the script with the following content, replacing the placeholders with your actual credentials:

```python
SPOTIPY_CLIENT_ID = 'your_spotify_client_id'
SPOTIPY_CLIENT_SECRET = 'your_spotify_client_secret'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-follow-read user-read-recently-played'
CACHE_PATH = '.spotipyoauthcache'
LMS_SERVER = 'your_lms_server_url'
LMS_PLAYER = 'your_lms_player_mac_address'
SMTP_SERVER = 'your_smtp_server'
SMTP_PORT = 587  # or your SMTP port
SENDER_EMAIL = 'your_email'
SENDER_PASSWORD = 'your_email_password'
RECIPIENT_EMAIL = 'recipient_email'
LAST_CHECK_FILE = 'last_check.txt'
```

## Spotify Developer Account Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in with your Spotify account.

2. Click on "Create an App" and fill in the required information.

3. After creating the app, you will be redirected to the app's dashboard. Note down the **Client ID**, **Client Secret**, and add the above **Redirect URI**.

4. Replace the corresponding placeholders in the `config.py` file with your Spotify app credentials.

## Installation

To install the required Python packages, run the following command in your terminal:

```sh
pip install spotipy
```

## Usage

1.  **Authorize the application**: If this is your first time running the script, you'll need to authorize it to access your Spotify account. Run the script and follow the URL provided to authorize the application. After authorization, the access token will be cached.

2.  **Run the script**:

    ```sh
    python your_script_name.py
    ```

## Functionality

- **get_spotify_client**: Authenticates with Spotify and returns a Spotify client.
- **get_followed_artists**: Retrieves the list of artists you follow on Spotify.
- **get_new_releases**: Checks for new albums and singles from your followed artists since the last check.
- **generate_lms_link**: Generates a link to play the Spotify URI on your LMS.
- **send_email**: Sends an email with the new releases using the provided SMTP server.

## Example Email Content

The email contains the following details for each new release:

- Artist Name
- Album/Song Name
- Release Date
- Links to play on Spotify and LMS

## Set Up a Cron Job

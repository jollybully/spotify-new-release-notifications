import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime
import os
import json
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SCOPE, CACHE_PATH,LMS_SERVER,LMS_PLAYER, SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, LAST_CHECK_FILE)

def generate_lms_link(spotify_uri):
    encoded_uri = urllib.parse.quote(spotify_uri)
    return f"{LMS_SERVER}/status.html?p0=playlist&p1=play&p2={encoded_uri}&player={LMS_PLAYER}"


def get_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH,
        show_dialog=True
    )

    if not os.path.exists(CACHE_PATH):
        # If cache doesn't exist, we need to go through the authorization flow
        print("Please visit this URL to authorize the application: ",
              auth_manager.get_authorize_url())
        auth_code = input("Enter the auth code returned in the url: ")
        auth_manager.get_access_token(auth_code)
        print("Authorization successful. You can now run the script normally.")

    return spotipy.Spotify(auth_manager=auth_manager)


def get_followed_artists(sp):
    artists = []
    results = sp.current_user_followed_artists(limit=50)
    artists.extend(results['artists']['items'])
    while results['artists']['next']:
        results = sp.next(results['artists'])
        artists.extend(results['artists']['items'])
    return artists


def get_new_releases(sp, artists, last_check):
    new_releases = {'albums': [], 'singles': []}
    for artist in artists:
        albums = sp.artist_albums(
            artist['id'], album_type='album,single', limit=50)
        for album in albums['items']:
            release_date = album['release_date']
            release_date_precision = album['release_date_precision']

            if release_date_precision == 'day':
                release_date = datetime.datetime.strptime(
                    release_date, '%Y-%m-%d').date()
            elif release_date_precision == 'month':
                release_date = datetime.datetime.strptime(
                    release_date, '%Y-%m').date().replace(day=1)
            elif release_date_precision == 'year':
                release_date = datetime.datetime.strptime(
                    release_date, '%Y').date().replace(month=1, day=1)
            else:
                print("Unknown release date precision for {}: {}".format(
                    album['name'], release_date_precision))
                continue

            if release_date > last_check.date():
                album_id = album['id']
                spotify_uri = f"spotify:album:{album_id}"
                spotify_deep_link = f"https://open.spotify.com/album/{album_id}"
                lms_link = generate_lms_link(spotify_uri)
                release_info = (
                    release_date, artist['name'], album['name'], spotify_deep_link, lms_link, album['album_type'])
                if album['album_type'] == 'album':
                    new_releases['albums'].append(release_info)
                else:
                    new_releases['singles'].append(release_info)

    # Sort both lists by date, newest first
    new_releases['albums'].sort(reverse=True)
    new_releases['singles'].sort(reverse=True)

    return new_releases


def send_email(new_releases):
    message = MIMEMultipart("alternative")
    text = "New releases since last check:\n\n"
    html = """\
    <html>
      <body>
        <p>New releases since last check:</p>
    """

    if new_releases['albums']:
        text += "New Albums:\n"
        html += "<h2>New Albums:</h2>"
        for release in new_releases['albums']:
            text += f"{release[1]} - {release[2]} (Released on {release[0]})\n"
            text += f"Listen on Spotify: {release[3]}\n"
            text += f"Play on LMS: {release[4]}\n\n"
            html += f"<p><b>{release[1]}</b> - {release[2]} (Released on {release[0]})<br>"
            html += f'<a href="{release[4]}">Play on LMS</a> '
            html += f'<a href="{release[3]}">Listen on Spotify</a></p>'

    if new_releases['singles']:
        text += "New Singles:\n"
        html += "<h2>New Singles:</h2>"
        for release in new_releases['singles']:
            text += f"{release[1]} - {release[2]} (Released on {release[0]})\n"
            text += f"Listen on Spotify: {release[3]}\n"
            text += f"Play on LMS: {release[4]}\n\n"
            html += f"<p><b>{release[1]}</b> - {release[2]} (Released on {release[0]})<br>"
            html += f'<a href="{release[4]}">Play on LMS</a> '
            html += f'<a href="{release[3]}">Listen on Spotify</a></p>'

    html += """\
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    if all([SMTP_SERVER, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        # Email sending code
        message['Subject'] = "Daily New Releases from Your Followed Artists"
        message['From'] = SENDER_EMAIL
        message['To'] = RECIPIENT_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        print("Email sent successfully.")
    else:
        print("Email credentials not set. Logging to console instead.")
        print(message)


def main():
    sp = get_spotify_client()

    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, 'r') as f:
            last_check = datetime.datetime.strptime(
                f.read().strip(), '%Y-%m-%d')
        print(f"Last check date: {last_check}")
    else:
        last_check = datetime.datetime.now() - datetime.timedelta(days=30)
        print(f"No previous check found. Using default date: {last_check}")

    print("Fetching followed artists...")
    artists = get_followed_artists(sp)
    print(f"Found {len(artists)} followed artists.")

    print("Checking for new releases...")
    new_releases = get_new_releases(sp, artists, last_check)

    total_new_releases = len(
        new_releases['albums']) + len(new_releases['singles'])
    if total_new_releases > 0:
        print(f"Found {total_new_releases} new releases.")
        send_email(new_releases)
    else:
        print("No new releases found.")

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(current_date)
    print(f"Updated last check date to {current_date}")


if __name__ == '__main__':
    main()

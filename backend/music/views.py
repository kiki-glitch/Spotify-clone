from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from bs4 import BeautifulSoup as bs
import re


# Create your views here.
def top_artists():

    url = "https://spotify-scraper.p.rapidapi.com/v1/chart/artists/top"

    querystring = {"type":"weekly"}

    headers = {
        "x-rapidapi-key": settings.RAPID_API_KEY,
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    artist_info = []
    seen_ids = set()

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response_data = response.json()

        # Handle error from API
        if not response_data.get('status', True):
            print("API Error:", response_data.get("reason", "Unknown error"))
            return []  # or return a fallback, or raise an exception if critical

        sections = response_data['sections']['items']

        for section in sections:
            items = section.get('contents', {}).get('items', [])

            for track in items:
                for artist in track.get('artists', []):
                    artist_id = artist.get('id', 'No ID')
                    name = artist.get('name', 'No Name')

                    covers = track.get('cover', [])
                    avatar_url = covers[-1]['url'] if covers else ''

                    if artist_id not in seen_ids:
                        artist_info.append((name, avatar_url, artist_id))
                        seen_ids.add(artist_id)

    except requests.exceptions.RequestException as e:
        print("Network error while fetching artists:", e)
    except (KeyError, IndexError, TypeError) as e:
        print("Parsing error while processing API response:", e)

    return artist_info

def top_tracks():
    url = "https://spotify-scraper.p.rapidapi.com/v1/chart/tracks/top"

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    track_details = []

    if 'tracks' in data:
        shortened_data = data['tracks'][:18]

        # id, name, artist, cover url 
        for track in shortened_data:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            cover_url = track['album']['cover'][0]['url'] if track['album']['cover'] else None

            track_details.append({
                'id': track_id,
                'name': track_name,
                'artist': artist_name,
                'cover_url': cover_url
            })

    else:
        print("track not foun in response")

    return track_details

def get_audio_etails(query):
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"

    querystring = {"track": query}

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    audio_details = []

    if response.status_code == 200:
        response_data = response.json()

        if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
            audio_list = response_data['youtubeVideo']['audio']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']

                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
            else:
                print("No audio data availble")
        else:
            print("No 'youtubeVideo' or 'audio' key found")
    else:
        print("Failed to fetch data")

    return audio_details

def get_track_image(track_id, track_name):
    url = 'https://open.spotify.com/track/'+track_id
    r = requests.get(url)
    soup = bs(r.content)
    image_links_html = soup.find('img', {'alt': track_name})
    if image_links_html:
        image_links = image_links_html['srcset']
    else:
        image_links = ''

    match = re.search(r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w', image_links)

    if match:
        url_640w = match.group().rstrip(' 640w')
    else:
        url_640w = ''

    return url_640w

def music(request, pk):
    track_id = pk

    url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"

    querystring = {"trackId": track_id}

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        # extrack track_name, artist_name

        track_name = data.get("name")
        artists_list = data.get("artists", [])
        first_artist_name = artists_list[0].get("name") if artists_list else "No artist found"

        audio_details_query = track_name + first_artist_name
        audio_details = get_audio_etails(audio_details_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]

        track_image = get_track_image(track_id, track_name)

        context = {
            'track_name': track_name,
            'artist_name': first_artist_name,
            'audio_url': audio_url,
            'duration_text': duration_text,
            'track_image': track_image,
        }
    return render(request, 'music.html', context)

def profile(request, pk):
    artist_id = pk

    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"

    querystring = {"artistId": artist_id}

    headers = {
        "X-RapidAPI-Key": "02912db996msh068b089c778126bp13a9d9jsn380afeb7d573",
        "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        name = data["name"]
        monthly_listeners = data["stats"]["monthlyListeners"]
        header_url = data["visuals"]["header"][0]["url"]

        top_tracks = []

        for track in data["discography"]["topTracks"]:
            trackid = str(track["id"])
            trackname = str(track["name"])
            if get_track_image(trackid, trackname):
                trackimage = get_track_image(trackid, trackname)
            else:
                trackimage = "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"

            track_info = {
                "id": track["id"],
                "name": track["name"],
                "durationText": track["durationText"],
                "playCount": track["playCount"],
                "track_image": trackimage
            }

            top_tracks.append(track_info)

        artist_data = {
            "name": name,
            "monthlyListeners": monthly_listeners,
            "headerUrl": header_url,
            "topTracks": top_tracks,
        }
    else:
        artist_data = {}
    return render(request, 'profile.html', artist_data)

def search(request):
    if request.method == 'POST':
        search_query = request.POST['search_query']

        url = "https://spotify-scraper.p.rapidapi.com/v1/search"

        querystring = {"term":search_query,"type":"track"}

        headers = {
            "X-RapidAPI-Key": "02912db996msh068b089c778126bp13a9d9jsn380afeb7d573",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        track_list = []

        if response.status_code == 200:
            data = response.json()

            search_results_count = data["tracks"]["totalCount"]
            tracks = data["tracks"]["items"]

            for track in tracks:
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                duration = track["durationText"]
                trackid = track["id"]

                if get_track_image(trackid, track_name):
                    track_image = get_track_image(trackid, track_name)
                else:
                    track_image = "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"

                track_list.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'duration': duration,
                    'trackid': trackid,
                    'track_image': track_image,
                })
        context = {
            'search_results_count': search_results_count,
            'track_list': track_list,
        }

        return render(request, 'search.html', context)
    else:
        return render(request, 'search.html')


@login_required(login_url = 'login')
def index(request):
    artists_info = top_artists()
    print(artists_info)
    context = {
        'artists_info': artists_info
    }
    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
        
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if not email or not username or not password or not password2:
            messages.info(request, 'All fields are required')
            return redirect('signup') 
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in 
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    return render(request, 'signup.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

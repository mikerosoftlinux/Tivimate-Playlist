import os
import re
import urllib.request

# Define source URLs (BuddyChewChew / i.mjh.nz style lists, excluding Pluto)
SOURCE_URLS = [
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plex_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/roku_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_all.m3u"
]

# Target English regions/languages
ENG_CODES = ['us', 'gb', 'ca', 'au', 'nz', 'en']
# Target Spanish regions/languages
ESP_CODES = ['es', 'mx', 'latam', 'ar', 'cl', 'co', 'es-mx', 'spa']

# Category mapping patterns (English)
ENG_CATEGORIES = {
    "Animation": ["adult animation", "animation", "cartoon", "adult swim", "toons", "animated"],
    "Anime": ["anime", "crunchyroll", "hidive", "japanese animation", "manga", "anime & gaming"],
    "Business & Finance": ["business", "finance", "money", "market", "bloomberg", "stocks", "wealth", "business news"],
    "Crime": ["crime", "law", "investigation", "police", "forensic", "detective", "cops", "crime drama", "true crime", "mystery"],
    "Documentaries": ["documentary", "docu", "nature", "history", "science", "biography", "true crime docs", "documentaries", "educational", "science & nature"],
    "Kids": ["kids", "children", "family", "nickelodeon", "cartoon network", "disney", "babies", "junior", "toons kids", "kids & family", "children music", "card games"],
    "Lifestyle": ["lifestyle", "food", "cooking", "travel", "home", "gardening", "fashion", "craft", "home & food", "food & travel", "good eats", "home improvement", "house & garden", "health"],
    "Movies": ["movie", "film", "cinema", "feature", "hollywood", "action movies", "drama movies", "movie channels", "action & drama", "romance"],
    "News": ["news", "weather", "noticias", "headlines", "global news", "news & opinion", "local news", "national news"],
    "Reality": ["reality", "competition", "game show", "contest", "surviving", "reality tv", "reality competition", "game shows", "games & competition"],
    "Sci-fi and Horror": ["sci-fi", "science fiction", "horror", "thriller", "paranormal", "supernatural", "terror", "sci-fi & horror", "sci-fi & supernatural"],
    "Sports": ["sports", "sport", "football", "baseball", "basketball", "soccer", "racing", "wrestling", "fight", "atletletics", "sports & outdoors", "motor sports", "auto & motorsports", "pro wrestling", "sports on now", "3x3 basketball", "bowling", "gaming & tech"],
    "TV & Entertainment": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "general", "tv series", "tv dramas", "pop culture", "black entertainment", "music", "music & ambiant", "ambiance", "animals", "environment", "shopping", "auction", "faith & family", "other", "nz", "australia", "united kingdom", "canada", "united states"],
    "Western and Classics": ["western", "classic", "vintage", "retro", "old school", "silent", "western & classic tv", "classic tv"]
}

# Category mapping patterns (Spanish counterparts)
ESP_CATEGORIES = {
    "Animación": ["adult animation", "animation", "cartoon", "adult swim", "animacion"],
    "Anime": ["anime", "crunchyroll"],
    "Ciencia Ficción y Terror": ["sci-fi", "science fiction", "horror", "thriller", "paranormal", "supernatural", "terror", "ciencia ficcion"],
    "Clásicos y Western": ["western", "classic", "vintage", "retro", "clasico"],
    "Crimen": ["crime", "law", "investigation", "police", "forensic", "crimen"],
    "Deportes": ["sports", "sport", "football", "baseball", "basketball", "soccer", "racing", "wrestling", "fight", "deporte", "futbol"],
    "Documentales": ["documentary", "docu", "nature", "history", "science", "biography", "documental"],
    "Estilo de Vida": ["lifestyle", "food", "cooking", "travel", "home", "gardening", "fashion", "estilo de vida", "viajes y cocina"],
    "Infantil": ["kids", "children", "family", "junior", "baby", "infant", "nifios", "niños", "infantil"],
    "Negocios y Finanzas": ["business", "finance", "money", "market", "bloomberg", "stocks", "wealth", "finanzas", "negocios"],
    "Noticias": ["news", "weather", "noticias", "headlines", "global news", "noticiero", "actualidad"],
    "Películas": ["movie", "film", "cinema", "feature", "hollywood", "cine", "peliculas"],
    "Reality": ["reality", "competition", "game show", "contest"],
    "TV y Entretenimiento": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "entretimiento", "musica", "telenovela", "spain", "mexico", "latino", "espanol", "español"]
}

# Explicit Alphabetical Ordering Lists (English A-Z, then Spanish A-Z)
ENG_ORDER = [
    "Animation",
    "Anime",
    "Business & Finance",
    "Crime",
    "Documentaries",
    "Kids",
    "Lifestyle",
    "Movies",
    "News",
    "Reality",
    "Sci-fi and Horror",
    "Sports",
    "TV & Entertainment",
    "Western and Classics",
    "Uncategorized"
]

ESP_ORDER = [
    "Animación",
    "Anime",
    "Ciencia Ficción y Terror",
    "Clásicos y Western",
    "Crimen",
    "Deportes",
    "Documentales",
    "Estilo de Vida",
    "Infantil",
    "Negocios y Finanzas",
    "Noticias",
    "Películas",
    "Reality",
    "TV y Entretenimiento",
    "Sin Categoría"
]

def fetch_playlists():
    all_channels = []
    for url in SOURCE_URLS:
        try:
            print(f"Fetching {url}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
                all_channels.extend(parse_m3u_content(content))
                

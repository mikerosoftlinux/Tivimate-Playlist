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
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
                all_channels.extend(parse_m3u_content(content))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return all_channels

def parse_m3u_content(content):
    channels = []
    current_channel = {}
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTM3U'):
            continue
        elif line.startswith('#EXTINF:'):
            current_channel = {'extinf': line}
            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            current_channel['original_group'] = group_match.group(1) if group_match else 'Uncategorized'
            name_match = re.search(r',(.+)$', line)
            current_channel['name'] = name_match.group(1).strip() if name_match else 'Unknown'
            current_channel['raw_meta'] = line.lower()
        elif line and not line.startswith('#'):
            current_channel['url'] = line
            if 'extinf' in current_channel and 'url' in current_channel:
                channels.append(current_channel)
            current_channel = {}
    return channels

def detect_language(channel):
    meta = (channel['name'] + " " + channel['original_group'] + " " + channel['raw_meta']).lower()
    for code in ESP_CODES:
        if f'[{code}]' in meta or f'({code})' in meta or f' {code} ' in meta or meta.endswith(f' {code}'):
            return 'spanish'
        if any(term in meta for term in ['span', 'latino', 'mexico', 'espanol', 'castellano', 'español']):
            return 'spanish'
    for code in ENG_CODES:
        if f'[{code}]' in meta or f'({code})' in meta or f' {code} ' in meta:
            return 'english'
    return 'english'

def categorize_channel(channel, lang):
    orig_grp = channel['original_group'].strip()
    
    # Check explicit mapping dictionary first
    if orig_grp in EXACT_CATEGORY_MAP:
        mapped = EXACT_CATEGORY_MAP[orig_grp]
        # If language is Spanish, translate English mapped category to Spanish equivalent
        if lang == 'spanish':
            trans_map = {
                "Animation": "Animación",
                "Anime": "Anime",
                "Business & Finance": "Negocios y Finanzas",
                "Crime": "Crimen",
                "Documentaries": "Documentales",
                "Kids": "Infantil",
                "Lifestyle": "Estilo de Vida",
                "Movies": "Películas",
                "News": "Noticias",
                "Reality": "Reality",
                "Sci-fi and Horror": "Ciencia Ficción y Terror",
                "Sports": "Deportes",
                "TV & Entertainment": "TV y Entretenimiento",
                "Western and Classics": "Clásicos y Western"
            }
            return trans_map.get(mapped, "TV y Entretenimiento")
        return mapped
        
    # Fallback to Uncategorized if not found
    return "Uncategorized" if lang == 'english' else "Sin Categoría"

def save_m3u(channels, filename, sort_order):
    def sort_key(ch):
        grp = ch['mapped_group']
        try:
            rank = sort_order.index(grp)
        except ValueError:
            rank = 99
        return (rank, ch['name'].lower())
        
    sorted_chs = sorted(channels, key=sort_key)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in sorted_chs:
            updated_extinf = re.sub(r'group-title="[^"]*"', f'group-title="{ch["mapped_group"]}"', ch['extinf'])
            f.write(f"{updated_extinf}\n{ch['url']}\n")

def main():
    raw_channels = fetch_playlists()
    seen_urls = set()
    unique_channels = []
    for ch in raw_channels:
        if ch['url'] not in seen_urls:
            seen_urls.add(ch['url'])
            unique_channels.append(ch)
            
    english_list = []
    spanish_list = []
    
    for ch in unique_channels:
        lang = detect_language(ch)
        if lang == 'english':
            ch['mapped_group'] = categorize_channel(ch, 'english')
            english_list.append(ch)
        else:
            ch['mapped_group'] = categorize_channel(ch, 'spanish')
            spanish_list.append(ch)
            
    save_m3u(english_list, 'english.m3u', ENG_ORDER)
    save_m3u(spanish_list, 'spanish.m3u', ESP_ORDER)
    save_m3u(english_list + spanish_list, 'combined.m3u', ENG_ORDER + ESP_ORDER)

if __name__ == '__main__':
    main()

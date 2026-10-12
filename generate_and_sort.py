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
    "News": ["news", "weather", "noticias", "headlines", "global news", "news & opinion", "local news", "national news"],
    "Business & Finance": ["business", "finance", "money", "market", "bloomberg", "stocks", "wealth", "business news"],
    "Reality": ["reality", "competition", "game show", "contest", "surviving", "reality tv", "reality competition", "game shows", "games & competition"],
    "Documentaries": ["documentary", "docu", "nature", "history", "science", "biography", "true crime docs", "documentaries", "educational", "science & nature"],
    "Lifestyle": ["lifestyle", "food", "cooking", "travel", "home", "gardening", "fashion", "craft", "home & food", "food & travel", "good eats", "home improvement", "house & garden", "health"],
    "Animation": ["adult animation", "animation", "cartoon", "adult swim", "toons", "animated"], # Non-kids animation
    "Anime": ["anime", "crunchyroll", "hidive", "japanese animation", "manga", "anime & gaming"],
    "Sports": ["sports", "sport", "football", "baseball", "basketball", "soccer", "racing", "wrestling", "fight", "atletletics", "sports & outdoors", "motor sports", "auto & motorsports", "pro wrestling", "sports on now", "3x3 basketball", "bowling", "gaming & tech"],
    "Kids": ["kids", "children", "family", "nickelodeon", "cartoon network", "disney", "babies", "junior", "toons kids", "kids & family", "children music", "card games"],
    "Movies": ["movie", "film", "cinema", "feature", "hollywood", "action movies", "drama movies", "movie channels", "action & drama", "romance"],
    "TV & Entertainment": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "general", "tv series", "tv dramas", "pop culture", "black entertainment", "music", "music & ambiant", "ambiance", "animals", "environment", "shopping", "auction", "faith & family", "other", "nz", "australia", "united kingdom", "canada", "united states"],
    "Sci-fi and Horror": ["sci-fi", "science fiction", "horror", "thriller", "paranormal", "supernatural", "terror", "sci-fi & horror", "sci-fi & supernatural"],
    "Crime": ["crime", "law", "investigation", "police", "forensic", "detective", "cops", "crime drama", "true crime", "mystery"],
    "Western and Classics": ["western", "classic", "vintage", "retro", "old school", "silent", "western & classic tv", "classic tv"]
}

# Category mapping patterns (Spanish counterparts)
ESP_CATEGORIES = {
    "Noticias": ["news", "weather", "noticias", "headlines", "global news", "noticiero", "actualidad"],
    "Negocios y Finanzas": ["business", "finance", "money", "market", "bloomberg", "stocks", "wealth", "finanzas", "negocios"],
    "Reality": ["reality", "competition", "game show", "contest"],
    "Documentales": ["documentary", "docu", "nature", "history", "science", "biography", "documental"],
    "Estilo de Vida": ["lifestyle", "food", "cooking", "travel", "home", "gardening", "fashion", "estilo de vida", "viajes y cocina"],
    "Animación": ["adult animation", "animation", "cartoon", "adult swim", "animacion"],
    "Anime": ["anime", "crunchyroll"],
    "Deportes": ["sports", "sport", "football", "baseball", "basketball", "soccer", "racing", "wrestling", "fight", "deporte", "futbol"],
    "Infantil": ["kids", "children", "family", "junior", "baby", "infant", "nifios", "niños", "infantil"],
    "Películas": ["movie", "film", "cinema", "feature", "hollywood", "cine", "peliculas"],
    "TV y Entretenimiento": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "entretimiento", "musica", "telenovela", "spain", "mexico", "latino", "espanol", "español"],
    "Ciencia Ficción y Terror": ["sci-fi", "science fiction", "horror", "thriller", "paranormal", "supernatural", "terror", "ciencia ficcion"],
    "Crimen": ["crime", "law", "investigation", "police", "forensic", "crimen"],
    "Clásicos y Western": ["western", "classic", "vintage", "retro", "clasico"]
}

# Explicit ordering lists
ENG_ORDER = [
    "News", "Business & Finance", "Reality", "Documentaries", 
    "Lifestyle", "Animation", "Anime", "Sports", "Kids", 
    "Movies", "TV & Entertainment", "Sci-fi and Horror", 
    "Crime", "Western and Classics", "Uncategorized"
]

ESP_ORDER = [
    "Noticias", "Negocios y Finanzas", "Reality", "Documentales", 
    "Estilo de Vida", "Animación", "Anime", "Deportes", "Infantil", 
    "Películas", "TV y Entretenimiento", "Ciencia Ficción y Terror", 
    "Crimen", "Clásicos y Western", "Sin Categoría"
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
            
            # Extract group-title
            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            current_channel['group'] = group_match.group(1) if group_match else 'Uncategorized'
            
            # Extract channel name
            name_match = re.search(r',(.+)$', line)
            current_channel['name'] = name_match.group(1).strip() if name_match else 'Unknown'
            
            # Extract tvg-id or language indicators if available
            lang_match = re.search(r'tvg-chno="([^"]*)"|tvg-id="([^"]*)"', line, re.IGNORECASE)
            current_channel['raw_meta'] = line.lower()
        elif line and not line.startswith('#'):
            current_channel['url'] = line
            if 'extinf' in current_channel and 'url' in current_channel:
                channels.append(current_channel)
            current_channel = {}
    return channels

def detect_language(channel):
    meta = (channel['name'] + " " + channel['group'] + " " + channel['raw_meta']).lower()
    
    # Check Spanish identifiers
    for code in ESP_CODES:
        if f'[{code}]' in meta or f'({code})' in meta or f' {code} ' in meta or meta.endswith(f' {code}'):
            return 'spanish'
        if any(term in meta for term in ['span', 'latino', 'mexico', 'espanol', 'castellano', 'español']):
            return 'spanish'
            
    # Check English identifiers or default standard English sources
    for code in ENG_CODES:
        if f'[{code}]' in meta or f'({code})' in meta or f' {code} ' in meta:
            return 'english'
            
    # Default fallback assumption if title is clean standard text without foreign flags
    return 'english'

def categorize_channel(channel, lang):
    text = (channel['name'] + " " + channel['group']).lower()
    mapping = ENG_CATEGORIES if lang == 'english' else ESP_CATEGORIES
    default_cat = "Uncategorized" if lang == 'english' else "Sin Categoría"
    
    for cat, keywords in mapping.items():
        if any(kw in text for kw in keywords):
            # Special rule: Separate Kids from general Animation
            if cat == "Animation" and any(kw in text for kw in ['kids', 'children', 'baby', 'junior', 'family', 'nifios', 'niños']):
                return "Kids" if lang == 'english' else "Infantil"
            return cat
            
    return default_cat

def clean_name(name):
    name = re.sub(r'\b(east|west|central|hd|fhd|sd|720p|1080p|4k)\b', '', name, flags=re.IGNORECASE)
    return re.sub(r'[^a-z0-9]', '', name.lower())

def save_m3u(channels, filename, sort_order):
    # Sort by custom group rank, then alphabetically by channel name
    def sort_key(ch):
        grp = ch['mapped_group']
        try:
            rank = sort_order.index(grp)
        except ValueError:
            rank = 99
        return (rank, grp.lower(), ch['name'].lower())
        
    sorted_chs = sorted(channels, key=sort_key)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in sorted_chs:
            # Clean up group-title in the output string to reflect our clean categories
            updated_extinf = re.sub(r'group-title="[^"]*"', f'group-title="{ch["mapped_group"]}"', ch['extinf'])
            f.write(f"{updated_extinf}\n{ch['url']}\n")
    print(f"Saved {len(sorted_chs)} channels to {filename}")

def main():
    raw_channels = fetch_playlists()
    print(f"Total raw streams fetched: {len(raw_channels)}")
    
    # Layer 1: Deduplicate by stream URL
    seen_urls = set()
    unique_by_url = []
    for ch in raw_channels:
        if ch['url'] not in seen_urls:
            seen_urls.add(ch['url'])
            unique_by_url.append(ch)
            
    # Layer 2: Deduplicate by normalized channel name + language to stop back-to-back spam feeds
    seen_names = set()
    unique_channels = []
    for ch in unique_by_url:
        lang_detect = detect_language(ch)
        name_key = (lang_detect, clean_name(ch['name']))
        
        if clean_name(ch['name']) in ['', 'unknown', 'channel'] or name_key not in seen_names:
            seen_names.add(name_key)
            unique_channels.append(ch)
            
    print(f"Total unique streams after name & URL deduplication: {len(unique_channels)}")
    
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
            
    # Save individual playlists
    save_m3u(english_list, 'english.m3u', ENG_ORDER)
    save_m3u(spanish_list, 'spanish.m3u', ESP_ORDER)
    
    # Combined: English block first, followed by Spanish block sorted identically
    combined_list = english_list + spanish_list
    combined_order = ENG_ORDER + ESP_ORDER
    save_m3u(combined_list, 'combined.m3u', combined_order)

if __name__ == '__main__':
    main()
    

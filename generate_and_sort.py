import os
import re
import urllib.request

SOURCE_URLS = [
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plex_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/roku_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_all.m3u"
]

ENG_CODES = ['us', 'gb', 'ca', 'au', 'nz', 'en']
ESP_CODES = ['es', 'mx', 'latam', 'ar', 'cl', 'co', 'es-mx', 'spa']

# Complete mapping dictionary built directly from your category tiles screenshot
EXACT_CATEGORY_MAP = {
    # --- ENGLISH CATEGORIES ---
    # News
    "News": "News",
    "News & Opinion": "News",
    "Local News": "News",
    "National News": "News",
    "Global News": "News",
    "Weather": "News",
    
    # Business & Finance
    "Business News": "Business & Finance",
    
    # Reality
    "Reality": "Reality",
    "Reality TV": "Reality",
    "Reality Competition": "Reality",
    "Game Show": "Reality",
    "Game Shows": "Reality",
    "Games & Competition": "Reality",
    
    # Documentaries
    "Documentary": "Documentaries",
    "Documentaries": "Documentaries",
    "Nature, History & Sci...": "Documentaries",
    "Nature": "Documentaries",
    "Science & Nature": "Documentaries",
    "Educational": "Documentaries",
    
    # Lifestyle
    "Lifestyle": "Lifestyle",
    "Lifestyle & Pop Cultu...": "Lifestyle",
    "Home & Food": "Lifestyle",
    "Food & Travel": "Lifestyle",
    "Good Eats": "Lifestyle",
    "Cooking": "Lifestyle",
    "Home Improvement": "Lifestyle",
    "House & Garden": "Lifestyle",
    "Health": "Lifestyle",
    
    # Animation (Adult/General)
    "Animated": "Animation",
    "Anime & Gaming": "Animation",
    
    # Anime
    "Anime": "Anime",
    
    # Sports
    "Sports": "Sports",
    "Sport": "Sports",
    "Sports & Outdoors": "Sports",
    "Motor Sports": "Sports",
    "Auto & Motorsports": "Sports",
    "Pro Wrestling": "Sports",
    "Sports On Now": "Sports",
    "3X3 Basketball": "Sports",
    "Bowling": "Sports",
    "Gaming & Tech": "Sports",
    
    # Kids
    "Kids": "Kids",
    "Kids & Family": "Kids",
    "Children Music": "Kids",
    "Card Games": "Kids",
    
    # Movies
    "Movies": "Movies",
    "Movie Channels": "Movies",
    "Action & Drama": "Movies",
    "Romance": "Movies",
    
    # TV & Entertainment
    "TV & Entertainment": "TV & Entertainment",
    "Entertainment": "TV & Entertainment",
    "TV Series": "TV & Entertainment",
    "TV Dramas": "TV & Entertainment",
    "Comedy": "TV & Entertainment",
    "Pop Culture": "TV & Entertainment",
    "Black Entertainment": "TV & Entertainment",
    "Music": "TV & Entertainment",
    "Music & Ambiant": "TV & Entertainment",
    "Ambiance": "TV & Entertainment",
    "Animals": "TV & Entertainment",
    "Environment": "TV & Entertainment",
    "Shopping": "TV & Entertainment",
    "Auction": "TV & Entertainment",
    "Faith & Family": "TV & Entertainment",
    "Other": "TV & Entertainment",
    "NZ": "TV & Entertainment",
    "Australia": "TV & Entertainment",
    "United Kingdom": "TV & Entertainment",
    "Canada": "TV & Entertainment",
    "United States": "TV & Entertainment",

    # Sci-fi and Horror
    "Sci-Fi & Horror": "Sci-fi and Horror",
    "Sci-Fi & Supernatural": "Sci-fi and Horror",
    "Horror": "Sci-fi and Horror",
    "Paranormal": "Sci-fi and Horror",
    
    # Crime
    "Crime": "Crime",
    "Crime Drama": "Crime",
    "True Crime": "Crime",
    "Mystery": "Crime",
    "Law": "Crime",
    
    # Western and Classics
    "Western & Classic TV": "Western and Classics",
    "Classic TV": "Western and Classics",

    # --- SPANISH CATEGORIES ---
    "Noticias": "Noticias",
    "Entretimiento": "TV y Entretenimiento",
    "Crimen": "Crimen",
    "Documentales": "Documentales",
    "Musica & ambiants": "TV y Entretenimiento",
    "Deporte": "Deportes",
    "Telenovela": "TV y Entretenimiento",
    "Spain": "TV y Entretenimiento",
    "Cine": "Películas",
    "Nifios": "Infantil",
    "Series": "TV y Entretenimiento",
    "Comedia": "TV y Entretenimiento",
    "Viajes y Cocina": "Estilo de Vida",
    "Mexico": "TV y Entretenimiento",
    "Latino": "TV y Entretenimiento",
    "Espanol": "TV y Entretenimiento",
    "Español": "TV y Entretenimiento"
}

ENG_ORDER = [
    "Animation", "Anime", "Business & Finance", "Crime", "Documentaries", 
    "Kids", "Lifestyle", "Movies", "News", "Reality", "Sci-fi and Horror", 
    "Sports", "TV & Entertainment", "Western and Classics", "Uncategorized"
]

ESP_ORDER = [
    "Animación", "Anime", "Ciencia Ficción y Terror", "Clásicos y Western", 
    "Crimen", "Deportes", "Documentales", "Estilo de Vida", "Infantil", 
    "Negocios y Finanzas", "Noticias", "Películas", "Reality", 
    "TV y Entretenimiento", "Sin Categoría"
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
    

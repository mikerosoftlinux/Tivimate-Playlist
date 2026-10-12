import os, re, urllib.request

SOURCE_URLS = [
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plex_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/roku_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_all.m3u"
]

ENG_CODES = ['us', 'gb', 'ca', 'au', 'nz', 'en']
ESP_CODES = ['es', 'mx', 'latam', 'ar', 'cl', 'co', 'es-mx', 'spa']

ENG_CATEGORIES = {
    "Animation": ["animation", "cartoon", "adult swim", "toons", "animated"],
    "Anime": ["anime", "crunchyroll", "hidive", "manga"],
    "Business & Finance": ["business", "finance", "money", "market", "bloomberg", "stocks"],
    "Crime": ["crime", "law", "investigation", "police", "forensic", "detective", "mystery"],
    "Documentaries": ["documentary", "docu", "nature", "history", "science", "biography", "educational"],
    "Kids": ["kids", "children", "family", "nickelodeon", "disney", "babies", "junior"],
    "Lifestyle": ["lifestyle", "food", "cooking", "travel", "home", "gardening", "fashion", "health"],
    "Movies": ["movie", "film", "cinema", "feature", "hollywood", "romance"],
    "News": ["news", "weather", "noticias", "headlines", "global news"],
    "Reality": ["reality", "competition", "game show", "contest", "surviving"],
    "Sci-fi and Horror": ["sci-fi", "science fiction", "horror", "thriller", "paranormal", "supernatural", "terror"],
    "Sports": ["sports", "sport", "football", "baseball", "basketball", "soccer", "racing", "wrestling", "fight", "bowling"],
    "TV & Entertainment": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "music", "ambiance", "shopping"],
    "Western and Classics": ["western", "classic", "vintage", "retro", "silent"]
}

ESP_CATEGORIES = {
    "Animación": ["animation", "cartoon", "adult swim", "animacion"],
    "Anime": ["anime", "crunchyroll"],
    "Ciencia Ficción y Terror": ["sci-fi", "horror", "thriller", "paranormal", "terror", "ciencia ficcion"],
    "Clásicos y Western": ["western", "classic", "vintage", "retro", "clasico"],
    "Crimen": ["crime", "law", "police", "crimen"],
    "Deportes": ["sports", "sport", "football", "soccer", "racing", "deporte", "futbol"],
    "Documentales": ["documentary", "docu", "nature", "history", "science", "documental"],
    "Estilo de Vida": ["lifestyle", "food", "cooking", "travel", "home", "estilo de vida", "cocina"],
    "Infantil": ["kids", "children", "family", "junior", "baby", "infantil", "niños"],
    "Negocios y Finanzas": ["business", "finance", "money", "market", "finanzas", "negocios"],
    "Noticias": ["news", "weather", "noticias", "headlines", "noticiero"],
    "Películas": ["movie", "film", "cinema", "feature", "cine", "peliculas"],
    "Reality": ["reality", "competition", "game show"],
    "TV y Entretenimiento": ["entertainment", "series", "drama", "comedy", "sitcom", "show", "tv", "entretimiento", "musica", "telenovela"]
}

ENG_ORDER = list(ENG_CATEGORIES.keys()) + ["Uncategorized"]
ESP_ORDER = list(ESP_CATEGORIES.keys()) + ["Sin Categoría"]

def fetch_playlists():
    all_channels = []
    for url in SOURCE_URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                content = res.read().decode('utf-8', errors='ignore')
                all_channels.extend(parse_m3u(content))
        except Exception as e:
            print(f"Error: {e}")
    return all_channels

def parse_m3u(content):
    channels, curr = [], {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#EXTINF:'):
            curr = {'extinf': line}
            gm = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            curr['group'] = gm.group(1) if gm else 'Uncategorized'
            nm = re.search(r',(.+)$', line)
            curr['name'] = nm.group(1).strip() if nm else 'Unknown'
            curr['raw'] = line.lower()
        elif line and not line.startswith('#') and 'extinf' in curr:
            curr['url'] = line
            channels.append(curr)
            curr = {}
    return channels

def detect_lang(ch):
    meta = f"{ch['name']} {ch['group']} {ch['raw']}".lower()
    if any(c in meta for c in ESP_CODES) or any(t in meta for t in ['span', 'latino', 'mexico', 'espanol', 'español']):
        return 'spanish'
    return 'english'

def categorize(ch, lang):
    text = f"{ch['name']} {ch['group']}".lower()
    mapping = ENG_CATEGORIES if lang == 'english' else ESP_CATEGORIES
    default_cat = "Uncategorized" if lang == 'english' else "Sin Categoría"
    for cat, keywords in mapping.items():
        if any(kw in text for kw in keywords):
            if cat in ["Animation", "Animación"] and any(k in text for kw in ['kids', 'children', 'family', 'junior', 'niños']):
                return "Kids" if lang == 'english' else "Infantil"
            return cat
    return default_cat

def save_m3u(channels, filename, order):
    sorted_chs = sorted(channels, key=lambda c: (order.index(c['mapped']) if c['mapped'] in order else 99, c['mapped'].lower(), c['name'].lower()))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in sorted_chs:
            ext = re.sub(r'group-title="[^"]*"', f'group-title="{ch["mapped"]}"', ch['extinf'])
            f.write(f"{ext}\n{ch['url']}\n")

def main():
    raw = fetch_playlists()
    seen, unique = set(), []
    for ch in raw:
        if ch['url'] not in seen:
            seen.add(ch['url'])
            unique.append(ch)
            
    eng, esp = [], []
    for ch in unique:
        lang = detect_lang(ch)
        if lang == 'english':
            ch['mapped'] = categorize(ch, 'english')
            eng.append(ch)
        else:
            ch['mapped'] = categorize(ch, 'spanish')
            esp.append(ch)
            
    save_m3u(eng, 'english.m3u', ENG_ORDER)
    save_m3u(esp, 'spanish.m3u', ESP_ORDER)
    save_m3u(eng + esp, 'combined.m3u', ENG_ORDER + ESP_ORDER)

if __name__ == '__main__':
    main()
    

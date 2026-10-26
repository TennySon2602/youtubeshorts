import requests

def test_search(query):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6, # File namespace
        "srlimit": 3,
        "format": "json"
    }
    headers = {"User-Agent": "DarkCuriosityBot/1.0"}
    r = requests.get(url, params=params, headers=headers).json()
    files = [item["title"] for item in r.get("query", {}).get("search", [])]
    
    # get image urls
    if not files:
        return []
    
    info_params = {
        "action": "query",
        "titles": "|".join(files),
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    r2 = requests.get(url, params=info_params, headers=headers).json()
    urls = []
    for pid, pdata in r2.get("query", {}).get("pages", {}).items():
        info = pdata.get("imageinfo", [{}])[0]
        if info.get("url"):
            urls.append(info.get("url"))
    return urls

print("Anechoic chamber:", test_search("anechoic chamber"))
print("Brain MRI:", test_search("brain MRI"))
print("Human Heart:", test_search("human heart"))

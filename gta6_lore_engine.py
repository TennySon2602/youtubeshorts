"""
GTA VI Gameplay & Lore Breakdown Engine
Curated deep-dive analysis, mysteries, mechanics, and leaks breakdown for Grand Theft Auto VI.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = BASE_DIR / "assets"
GTAVI_DIR = ASSETS_DIR / "gtavi"
GTAVI_DIR.mkdir(parents=True, exist_ok=True)

GTA6_LORE_TOPICS = [
    {
        "id": "lucia_ankle_monitor",
        "badge": "[ GTA VI SECRET ]",
        "title": "The Dark Secret Behind Lucia's Ankle Monitor... 🤯 #Shorts",
        "hook_header": "LUCIA'S HIDDEN STORYLINE REVEALED",
        "description": "Rockstar hid a dark secret in GTA 6's trailer that reveals the entire storyline! How Lucia's probation ankle monitor traps her in Vice City until Jason helps her break free. Subscribe for daily GTA 6 leaks! #GTA6 #Shorts #GrandTheftAuto6 #RockstarGames #Gaming #ViceCity #GTA6Leaks",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "GTA6Leaks", "RockstarGames", "Gaming", "ViceCity", "Lucia", "Jason", "GTAVI"],
        "scenes": [
            "Rockstar hid a dark storyline detail in GTA 6 that almost everyone completely missed.",
            "In the official trailer, Lucia is seen wearing an active police GPS ankle monitor.",
            "This confirms Lucia starts the story on strict probation, locking her to Vice City until Jason helps her disable it.",
            "Leaked files reveal that cutting this ankle monitor triggers an instant three-star manhunt across Leonida.",
            "This dynamic forces players to plan their crimes carefully, completely redefining open-world freedom.",
            "Which explains the chilling reason why..."
        ],
        "clip_timestamps": [
            (2.0, 7.0),    # Lucia in prison uniform
            (15.0, 20.0),  # Vice City beach aerial
            (63.0, 68.0),  # Police cruiser car chase
            (81.0, 86.0),  # Masked convenience store robbery
            (73.0, 78.0),  # Jason and Lucia driving convertible
            (87.0, 90.0)   # GTA VI logo
        ]
    },
    {
        "id": "leonida_map_scale",
        "badge": "[ MAP SCALE ANALYSIS ]",
        "title": "Why GTA 6's Map Destroys GTA 5 & Red Dead 2... 🗺️ #Shorts",
        "hook_header": "LEONIDA MAP SCALE IS TERRIFYING",
        "description": "Leaked mapping projects prove GTA 6's state of Leonida is 3 times bigger than Los Santos! Full breakdown of Vice City, the Everglades swamps, and islands. Subscribe for more! #GTA6 #Shorts #GrandTheftAuto6 #GTA6Map #Gaming #ViceCity",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "GTA6Map", "RockstarGames", "Gaming", "ViceCity", "Leonida", "RDR2", "GTAVI"],
        "scenes": [
            "Leaked coordinates prove GTA 6's map of Leonida is over three times bigger than Los Santos.",
            "Leonida features three massive metropolitan cities and over a hundred fully enterable tropical islands.",
            "The Florida Everglades swamp region alone is larger than the entire Red Dead Redemption 2 world map.",
            "Rockstar engineered dynamic tropical storm physics that can flood entire highways and neighborhoods in real time.",
            "With over seventy percent of buildings having fully enterable interiors, the exploration scale is terrifying.",
            "And you won't believe the data showing how..."
        ],
        "clip_timestamps": [
            (12.0, 17.0),  # Vice City aerial skyline
            (26.0, 31.0),  # Airboat through Everglades swamp
            (33.0, 38.0),  # Ocean Drive neon nightlife
            (48.0, 53.0),  # Mud club party
            (75.0, 80.0),  # Jason driving into sunset
            (87.0, 90.0)   # GTA VI title card
        ]
    },
    {
        "id": "police_ai_system",
        "badge": "[ 5-STAR WANTED LEAK ]",
        "title": "Rockstar's Frightening New Police AI in GTA 6 🚨 #Shorts",
        "hook_header": "5-STAR WANTED LEVEL WILL BREAK YOU",
        "description": "Getting a 5-star wanted level in GTA 6 won't be like anything you've seen before. Police remember license plates, scan CCTV, and deploy tactical SWAT units. Subscribe for daily GTA 6 leaks! #GTA6 #Shorts #GrandTheftAuto6 #GTA6Police #Gaming #ViceCity",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "GTA6Police", "RockstarGames", "Gaming", "ViceCity", "WantedLevel", "GTAVI"],
        "scenes": [
            "Getting a five-star wanted level in GTA 6 won't be like anything you have ever seen before.",
            "Rockstar completely rebuilt the police artificial intelligence from the ground up.",
            "Cops no longer spawn out of thin air behind you; they dispatch from real police precincts and coordinate tactical roadblocks.",
            "If you escape, police will remember your vehicle's license plate and scan surveillance cameras across Vice City.",
            "K9 tracking units and tactical bodycam SWAT squads will hunt you through dense alleyways and swamplands.",
            "Giving players virtually zero chance of survival, which is why..."
        ],
        "clip_timestamps": [
            (58.0, 63.0),  # Police bodycam footage raid
            (63.0, 68.0),  # Cruisers speeding through intersection
            (43.0, 48.0),  # Security camera livestream
            (27.0, 32.0),  # Swamp alligator & wildlife
            (81.0, 86.0),  # Gas station shootout
            (87.0, 90.0)   # GTA VI logo
        ]
    },
    {
        "id": "social_media_mechanic",
        "badge": "[ VIRAL CRIME FEATURE ]",
        "title": "The GTA 6 Social Media Feature Nobody Is Talking About 📱 #Shorts",
        "hook_header": "IN-GAME TIKTOK CHANGES EVERYTHING",
        "description": "GTA 6's in-game social media isn't just a funny parody; it's a core crime mechanic where NPCs livestream your robberies to millions! Subscribe for more! #GTA6 #Shorts #GrandTheftAuto6 #RockstarGames #Gaming #ViceCity",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "RockstarGames", "Gaming", "ViceCity", "TikTok", "SocialMedia", "GTAVI"],
        "scenes": [
            "GTA 6's in-game TikTok isn't just a parody; it is a game-changing crime mechanic.",
            "In Leonida, every single NPC carries a smartphone with a fully functional in-game social media app.",
            "If you commit a crime in public, bystanders will whip out their phones and livestream you to millions of virtual followers.",
            "Going viral increases your notoriety, causing bounty hunters and rival cartel members to track your exact location.",
            "You can even hijack viral livestreams to scout security guards and plan high-stakes heists.",
            "Completely changing open-world crime forever, and proving that..."
        ],
        "clip_timestamps": [
            (41.0, 45.0),  # Rooftop livestream girl
            (45.0, 49.0),  # Mud club livestream
            (50.0, 54.0),  # Gas station street fight
            (54.0, 58.0),  # Florida Joker news mugshot
            (83.0, 87.0),  # Lucia aiming weapon in store
            (87.0, 90.0)   # GTA VI logo
        ]
    },
    {
        "id": "bonnie_clyde_tragedy",
        "badge": "[ TRAGIC STORY LORE ]",
        "title": "The Tragic Betrayal Ending Leaked for GTA 6... 💔 #Shorts",
        "hook_header": "JASON & LUCIA'S FATAL DESTINY",
        "description": "The tragic Bonnie and Clyde ending hidden in GTA 6's dialogue. Will Jason betray Lucia, or will Lucia leave him behind? Subscribe for daily GTA 6 lore! #GTA6 #Shorts #GrandTheftAuto6 #RockstarGames #Gaming #ViceCity #GTA6Story",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "GTA6Story", "RockstarGames", "Gaming", "ViceCity", "Lucia", "Jason", "GTAVI"],
        "scenes": [
            "The biggest fan theory about Jason and Lucia might actually be a hundred percent true.",
            "Rockstar explicitly confirmed Jason and Lucia are inspired by the legendary outlaws Bonnie and Clyde.",
            "In real history, Bonnie and Clyde met a gruesome end in an ambush, and GTA 6's dialogue drops chilling hints.",
            "Notice how in the trailer, Lucia is the dominant leader while Jason hesitates before answering 'Trust'.",
            "Insiders suggest the final mission will force players to choose between saving their partner or walking away with the loot.",
            "Making everyone terrified that..."
        ],
        "clip_timestamps": [
            (73.0, 77.0),  # Jason and Lucia driving convertible
            (77.0, 81.0),  # Motel bed conversation
            (81.0, 85.0),  # Kicking open store doors
            (85.0, 88.0),  # "Trust? Trust."
            (73.0, 76.0),  # Driving into sunset
            (87.0, 90.0)   # GTA VI logo
        ]
    },
    {
        "id": "physics_and_details",
        "badge": "[ NEXT-GEN PHYSICS ]",
        "title": "Rockstar's Insane Next-Gen Physics in GTA 6... 🤯 #Shorts",
        "hook_header": "GRAPHICS DETAILS THAT WILL BLOW YOUR MIND",
        "description": "The level of detail Rockstar put into GTA 6's physics and graphics is genuinely mind-blowing! Water simulation, car deformation, and NPC emotional AI. Subscribe for more! #GTA6 #Shorts #GrandTheftAuto6 #RockstarGames #Gaming #ViceCity",
        "tags": ["Shorts", "GTA6", "GrandTheftAuto6", "GTA6Physics", "RockstarGames", "Gaming", "ViceCity", "NextGen", "GTAVI"],
        "scenes": [
            "The level of detail Rockstar put into GTA 6's physics is genuinely mind-blowing.",
            "Rockstar spent eight years developing real-time volumetric fluid physics for Leonida's oceans and rivers.",
            "Every single vehicle has individual suspension travel, tire pressure deformation, and modular interior damage.",
            "NPCs have realistic weight distribution, reacting to wind gusts, humidity, and weapon recoil with lifelike emotion.",
            "The dynamic hair and cloth physics alone required custom proprietary rendering patents.",
            "Proving beyond any doubt that..."
        ],
        "clip_timestamps": [
            (15.0, 20.0),  # Speedboats and ocean wake
            (22.0, 26.0),  # Lowrider bouncing car exhaust
            (38.0, 43.0),  # Bikini pool girl hair wind physics
            (33.0, 38.0),  # Ocean Drive neon reflections on car paint
            (48.0, 53.0),  # Mud truck terrain physics
            (87.0, 90.0)   # GTA VI logo
        ]
    }
]

def get_gta6_topic(topic_id: str = None, query: str = None) -> dict:
    """
    Selects a GTA VI lore topic based on topic_id, search query, or rotating day index.
    """
    if topic_id and topic_id.strip().lower() not in ("auto", "none", ""):
        match = next((t for t in GTA6_LORE_TOPICS if t["id"].lower() == topic_id.strip().lower()), None)
        if match:
            return match

    if query:
        q_low = query.lower()
        for t in GTA6_LORE_TOPICS:
            if q_low in t["title"].lower() or q_low in t["description"].lower() or q_low in t["id"]:
                return t

    # Default rotation based on day of month
    import time
    day_idx = int(time.strftime("%d")) % len(GTA6_LORE_TOPICS)
    return GTA6_LORE_TOPICS[day_idx]

if __name__ == "__main__":
    t = get_gta6_topic()
    print("Selected GTA 6 Topic:", t["id"])
    print("Title:", t["title"])
    print("Scenes:", len(t["scenes"]))

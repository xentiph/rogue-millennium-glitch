"""A small procedural model for the whole world's people.
Every NPC is generated — name, appearance, a line to say, and a secret
identity (a "soul"). A soul is a persistent name across runs; when Octavia's
faith is high enough, she begins to REMEMBER the souls who helped her in past
lives. That is how trust is learned.
"""
import random

# name-part banks — combined procedurally, so no two souls are the same
GIVEN = ["Amara", "Elias", "Mara", "Sana", "Tomas", "Hala", "Rami", "Lena",
         "Omar", "Freya", "Idris", "Zoya", "Kofi", "Nadia", "Theo", "Rana",
         "Basir", "Cleo", "Darius", "Ines", "Jovan", "Layla", "Mika",
         "Noor", "Petros", "Safia", "Teoman", "Yara"]
SURNAME = ["al-Khalil", "Okafor", "Mendes", "Bianca", "Petrov", "Al-Hassan",
           "Kowalski", "Duarte", "Teng", "Ivanescu", "Bakr", "Fischer",
           "Novak", "Gonzalez", "Sato", "Yilmaz", "Costa", "Wei", "Diallo",
           "Marques", "Haddad", "Berg", "Toprak", "Ndiaye"]
# where each tongue's people most plausibly come from
TONGUE_HOMES = {
    "ro": ["Bucharest", "Cluj", "Iasi", "Timisoara"],
    "es": ["Madrid", "Mexico City", "Bogota", "Bilbao"],
    "zh": ["Nanjing", "Chengdu", "Qingdao", "Wuhan"],
    "ru": ["Moscow", "Baku", "Tashkent", "Warsaw"],
    "tr": ["Istanbul", "Izmir", "Ankara", "Gaziantep"],
    "ar": ["Cairo", "Rabat", "Dakar", "Tripoli"],
    "fr": ["Paris", "Marseille", "Lyon", "Toulouse"],
}
# fragments to stitch greetings from, per tongue — the small generation model
LINE_CHUNKS = {
    "ro": ["bună, nu te grăbi", "vino mai aproape", "e frig afară",
           "cine te-a trimis", "hăinuțele tale sunt subțiri", "ascultă, nu fugi"],
    "es": ["hola, no tengas miedo", "ven, te estoy esperando",
           "el frio no perdona", "quien te mando aqui", "tienes los ojos tristes",
           "descansa, no sigas todavia"],
    "zh": ["你好，别怕", "来，我等你很久了", "天气太冷", "谁让你来的",
           "你的眼睛很疲惫", "歇一歇，先别走"],
    "ru": ["здравствуй, не бойся", "иди ко мне", "на улице холодно",
           "кто тебя прислал", "у тебя усталые глаза", "отдохни, не уходи ещё"],
    "tr": ["merhaba, korkma", "gel, seni bekliyordum", "soğuk acıtmaz",
           "seni kim gönderdi", "gözlerin yorgun", "dinlen, henüz gitme"],
    "ar": ["أهلاً، لا تخافي", "تعالي، أنا بانتظارك", "البرد لا يرحم",
           "من أرسلكِ", "عيناكِ متعبتان", "استريحي، لا تمشي بعد"],
    "fr": ["bonjour, n'aie pas peur", "viens, je t'attendais",
           "le froid ne pardonne pas", "qui t'a envoyée", "tu as les yeux fatigués",
           "repose-toi, ne pars pas encore"],
}
# a soul that "helped her in a past life" — for the memory system
HELPED_VERBS = ["carried your blanket", "fed you when you were too weak",
                "held the door when the night came", "spoke for you at a border",
                "gave you water from their own bottle",
                "pointed east when you had lost the way"]
MEMORY_FLASH = "A face from a life you half-forget surfaces: {soul}, who {helped}. You remember. Trust, it seems, is carried across the dark too."


def make_soul(rng):
    """Generate a persistent soul: the hidden identity under any NPC."""
    given = rng.choice(GIVEN)
    sur = rng.choice(SURNAME)
    helped = rng.choice(HELPED_VERBS)
    return {"name": f"{given} {sur}", "helped": helped}


def make_npc(rng, tongue):
    """Generate an NPC who speaks a given tongue, procedurally.
    Returns (soul, glyph, color, name, line). The name shown is a present-life
    alias; the soul is the deeper, cross-life truth."""
    soul = make_soul(rng)
    home = rng.choice(TONGUE_HOMES[tongue])
    alias = f"the {home} {rng.choice(['busker', 'cook', 'grocer', 'nurse', 'dockworker', 'porter'])}"
    # stitch 2-3 chunks into one line of greeting
    n_chunks = rng.randint(2, 3)
    line = ", ".join(rng.sample(LINE_CHUNKS[tongue], n_chunks)) + "."
    return soul, alias, line


def make_teacher(npc_index, rng):
    """Full teacher generation for a fixed tongue slot (index 0..6)."""
    tongues = ["ro", "es", "zh", "ru", "tr", "ar", "fr"]
    tongue = tongues[npc_index]
    glyph = "mM WrR AF"[npc_index] if npc_index < 7 else "?"
    colors = ["magenta", "yellow", "cyan", "red", "green", "blue", "white"]
    soul, alias, line = make_npc(rng, tongue)
    return {
        "tongue": tongue, "glyph": glyph, "color": colors[npc_index],
        "alias": alias, "line": line, "soul": soul,
    }

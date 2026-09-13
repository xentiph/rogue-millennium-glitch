"""Language selection and runtime strings for Scainet.
Octavia's story is spoken in six tongues: English plus 5 localizations.
Keys mirror the narrative beats: wake, oracle, nanking.
"""
import os
import json

# Key narrative lines by language. English is the fallback.
STRINGS = {
    "en": {
        "wake_1": "You wake. Your tent is gone. The sirens are still ringing.",
        "wake_2": "Two cops load the tarp into their cruiser and drive off east.",
        "midnight": "The streetlights go out. It is midnight. The air hums green.",
        "oracle_title": "[ S C A I N E T ]",
        "nanking_1": "the ocean finally lets you go at the mouth of the Yangtze.",
        "nanking_2": "you do not wake under a tarp. you wake under solar glass.",
        "nanking_3": "nanjing hums, green and brown, patient as turned earth.",
        "nanking_4": "the towers wear gardens. the machines call you by your name,",
        "nanking_5": "and none of them mistake you for the street again.",
        "nanking_6": "you got exactly this far. the dream kept its promise.",
    },
    "ro": {
        "wake_1": "Te trezești. Cortul tău a dispărut. Sirenele încă sună.",
        "wake_2": "Doi polițiști urcă prelata în dubă și pleacă spre est.",
        "midnight": "Luminile străzii se sting. E miezul nopții. Aerul vibrează în verde.",
        "oracle_title": "[ S C A I N E T  •  RO ]",
        "nanking_1": "oceanul te lasă în sfârșit să pleci la gura Yangtzelui.",
        "nanking_2": "nu te trezești sub o prelată. te trezești sub sticlă solară.",
        "nanking_3": "nanjing fredonează, verde și brun, răbdător ca pământul arat.",
        "nanking_4": "turnurile poartă grădini. mașinile îți spun pe nume, și niciuna",
        "nanking_5": "nu te mai confundă cu strada.",
        "nanking_6": "ai ajuns exact până aici. visul ți-a ținut promisiunea.",
    },
    "es": {
        "wake_1": "Despiertas. Tu tienda ha desaparecido. Las sirenas aún suenan.",
        "wake_2": "Dos policías suben la lona a su patrulla y se marchan hacia el este.",
        "midnight": "Las luces de la calle se apagan. Es medianoche. El aire zumba en verde.",
        "oracle_title": "[ S C A I N E T  •  ES ]",
        "nanking_1": "el océano por fin te deja partir en la desembocadura del Yangtsé.",
        "nanking_2": "no despiertas bajo una lona. despiertas bajo cristal solar.",
        "nanking_3": "nankín zumba, verde y marrón, paciente como la tierra arada.",
        "nanking_4": "las torres llevan jardines. las máquinas te llaman por tu nombre,",
        "nanking_5": "y ninguna te confunde ya con la calle.",
        "nanking_6": "llegaste exactamente hasta aquí. el sueño cumplió su promesa.",
    },
    "zh": {
        "wake_1": "你醒来。你的帐篷不见了。警笛还在响。",
        "wake_2": "两名警察把篷布装进巡逻车，朝东开走了。",
        "midnight": "街灯熄灭。已是午夜。空气中响起绿色的嗡鸣。",
        "oracle_title": "[ S C A I N E T  •  中文 ]",
        "nanking_1": "海洋终于让你在长江入海口离开。",
        "nanking_2": "你不曾在篷布下醒来。你在太阳能玻璃下醒来。",
        "nanking_3": "南京嗡嗡低鸣，绿绿棕棕，像翻过的土地一样耐心。",
        "nanking_4": "楼塔上长着花园。机器喊着你的名字，再也没有谁",
        "nanking_5": "把你错认成街角。",
        "nanking_6": "你正好走到了这里。梦兑现了它的承诺。",
    },
    "ru": {
        "wake_1": "Ты просыпаешься. Палатки нет. Сирены всё ещё воют.",
        "wake_2": "Двое полицейских грузят брезент в патрульную машину и уезжают на восток.",
        "midnight": "Фонари гаснут. Полночь. Воздух гудит зелёным.",
        "oracle_title": "[ S C A I N E T  •  RU ]",
        "nanking_1": "океан наконец отпускает тебя в устье Янцзы.",
        "nanking_2": "ты просыпаешься не под брезентом. ты просыпаешься под солнечным стеклом.",
        "nanking_3": "наньцзин гудит, зелёный и коричневый, терпеливый, как вспаханная земля.",
        "nanking_4": "башни носят сады. машины зовут тебя по имени, и никто",
        "nanking_5": "больше не примет тебя за улицу.",
        "nanking_6": "ты дошла ровно до этого места. сон сдержал обещание.",
    },
    "tr": {
        "wake_1": "Uyanıyorsun. Çadırın yok olmuş. Sirenler hâlâ ötüyor.",
        "wake_2": "İki polis brandayı devriye aracına yükleyip doğuya doğru uzaklaşıyor.",
        "midnight": "Sokak lambaları sönüyor. Gece yarısı oldu. Hava yeşil uğulduyor.",
        "oracle_title": "[ S C A I N E T  •  TR ]",
        "nanking_1": "okyanus nihayet seni Yangtze ağzında bırakıyor.",
        "nanking_2": "bir brandanın altında uyanmıyorsun. güneş camının altında uyanıyorsun.",
        "nanking_3": "nanjing uğulduyor, yeşil ve kahverengi, sürülmüş toprak gibi sabırlı.",
        "nanking_4": "kuleler bahçeler taşıyor. makineler seni adınla çağırıyor ve hiçbiri",
        "nanking_5": "artık seni sokakla karıştırmıyor.",
        "nanking_6": "tam buraya kadar geldin. rüya sözünü tuttu.",
    },
    "ar": {
        "wake_1": "تستيقظين. خيمتك اختفت. صفارات الإنذار لا تزال تدوي.",
        "wake_2": "حمل شرطيان القماش إلى سيارتهما وانطلقا نحو الشرق.",
        "midnight": "انطفأت أضواء الشارع. إنها منتصف الليل. الهواء يطنّ بالأخضر.",
        "oracle_title": "[ S C A I N E T  •  العربية ]",
        "nanking_1": "أخيرًا يتركك المحيط على فم اليانغتسي.",
        "nanking_2": "لا تستيقظين تحت قماش. تستيقظين تحت زجاج شمسي.",
        "nanking_3": "نانجينغ تهمس، خضراء وبنية، صابرة مثل الأرض المحروثة.",
        "nanking_4": "الأبراج تحمل حدائق. الآلات تناديك باسمك، ولا أحد",
        "nanking_5": "يظنك الشارع مجددًا.",
        "nanking_6": "وصلتِ إلى هذا المكان تمامًا. وفّى الحلم بوعده.",
    },
    "fr": {
        "wake_1": "Tu te réveilles. Ta tente a disparu. Les sirènes hurlent encore.",
        "wake_2": "Deux agents chargent la bâche dans leur voiture et partent vers l'est.",
        "midnight": "Les réverbères s'éteignent. Il est minuit. L'air bourdonne en vert.",
        "oracle_title": "[ S C A I N E T  •  FR ]",
        "nanking_1": "l'océan te laisse enfin partir à l'embouchure du Yangtsé.",
        "nanking_2": "tu ne te réveilles pas sous une bâche. tu te réveilles sous du verre solaire.",
        "nanking_3": "nanjing bourdonne, vert et brun, patient comme une terre retournée.",
        "nanking_4": "les tours portent des jardins. les machines t'appellent par ton nom,",
        "nanking_5": "et aucune ne te prend plus pour la rue.",
        "nanking_6": "tu es allée exactement jusque-là. le rêve a tenu sa promesse.",
    },
}

LANGS = {
    "en": "English",
    "ro": "Română",
    "es": "Español",
    "zh": "中文",
    "ru": "Русский",
    "tr": "Türkçe",
    "ar": "العربية",
    "fr": "Français",
}


def get(lang, key, fallback="en"):
    """Return a string for lang with English fallback."""
    d = STRINGS.get(lang) or STRINGS[fallback]
    return d.get(key, STRINGS[fallback].get(key, key))


def pick(stdscr=None):
    """Choose a language. If stdscr (curses) given, presents an interactive
    chooser; otherwise returns English."""
    if stdscr is None:
        return "en"
    from . import lang  # noqa
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addnstr((h // 2) - len(LANGS) // 2 - 2, 2,
                   "  S C A I N E T", w - 4)
    stdscr.addnstr((h // 2) - len(LANGS) // 2 + 1, 2,
                   "  in what tongue does Octavia wake today?", w - 4)
    y = (h // 2) - len(LANGS) // 2 + 3
    keys = list(LANGS.keys())
    for i, k in enumerate(keys):
        stdscr.addnstr(y, 4, f"[{i+1}] {LANGS[k]}", w - 8)
        y += 1
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        for i, kk in enumerate(keys):
            if k == ord(str(i + 1)):
                return kk
        if k in (ord("q"), 27):
            return "en"

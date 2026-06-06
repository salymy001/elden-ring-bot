# main.py - Elden Ring Text RPG Bot (Enhanced UI Version)
import os, json, random
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set!")
    exit()

# ==================== GAME DATA ====================
C = {
    "vagabond":{"n":"ولگرد","d":"شوالیه تبعیدی با زره سنگین","s":{"STR":12,"DEX":10,"INT":5,"VIT":15,"PER":8,"LCK":5,"CHR":6,"END":14,"AGI":7,"WIS":4},"sk":["ضربه طوفان","گام خونین","چنگال شیر"]},
    "samurai":{"n":"سامورایی","d":"جنگجوی چابک با کاتانا","s":{"STR":8,"DEX":15,"INT":4,"VIT":10,"PER":12,"LCK":8,"CHR":5,"END":10,"AGI":12,"WIS":6},"sk":["برش ماه گذرا","رقص تیغ","هجوم باد"]},
    "astrologer":{"n":"اخترشناس","d":"جادوگر گلینت‌استون","s":{"STR":4,"DEX":6,"INT":18,"VIT":6,"PER":10,"LCK":4,"CHR":7,"END":6,"AGI":5,"WIS":14},"sk":["تیر گلینت","سنگ‌انداز","ستاره آبی"]},
    "prophet":{"n":"پیامبر","d":"واعظ معجزات اردتری","s":{"STR":7,"DEX":5,"INT":8,"VIT":12,"PER":6,"LCK":7,"CHR":12,"END":8,"AGI":6,"WIS":16},"sk":["نیزه برق","شعله جنون","شفای اردتری"]},
    "bandit":{"n":"راهزن","d":"دزد چابک سایه‌ها","s":{"STR":5,"DEX":14,"INT":4,"VIT":8,"PER":10,"LCK":14,"CHR":8,"END":7,"AGI":14,"WIS":3},"sk":["گام شکارچی","پرتاب خنجر","سم مار"]},
    "hero":{"n":"قهرمان","d":"جنگجوی قدرتمند شمال","s":{"STR":16,"DEX":8,"INT":3,"VIT":14,"PER":5,"LCK":6,"CHR":4,"END":12,"AGI":4,"WIS":3},"sk":["لگد طوفان","ضربه زمین","چرخش تبر"]},
    "wretch":{"n":"بی‌چاره","d":"شروع از صفر مطلق","s":{"STR":10,"DEX":10,"INT":10,"VIT":10,"PER":10,"LCK":10,"CHR":10,"END":10,"AGI":10,"WIS":10},"sk":[]},
}

E = {
    "wandering_noble":{"n":"اشراف‌زاده سرگردان","t":"easy","te":"🟢","hp":80,"mp":0,"d":8,"df":3,"lv":3,"sk":["خنجر زهرآگین"],"sd":[12],"se":["☠️سم"],"rn":50,"xp":30,"dr":["سنگ آهنگری"],"dc":[0.6]},
    "godrick_soldier":{"n":"سرباز گادریک","t":"easy","te":"🟢","hp":120,"mp":0,"d":12,"df":8,"lv":5,"sk":["ضربه نیزه"],"sd":[15],"se":[None],"rn":80,"xp":50,"dr":["شمشیر سرباز"],"dc":[0.4]},
    "grafted_scion":{"n":"پیوندخورده نجیب","t":"medium","te":"🟡","hp":250,"mp":30,"d":22,"df":15,"lv":12,"sk":["رقص شمشیرها","پیوند خشمگین"],"sd":[35,40],"se":[None,"🩸خونریزی"],"rn":500,"xp":200,"dr":["شمشیر طلایی"],"dc":[0.2]},
    "giant_crab":{"n":"خرچنگ غول‌پیکر","t":"medium","te":"🟡","hp":300,"mp":0,"d":18,"df":25,"lv":10,"sk":["چنگال خردکننده"],"sd":[25],"se":[None],"rn":350,"xp":150,"dr":["گوشت خرچنگ"],"dc":[0.8]},
    "crucible_knight":{"n":"شوالیه کوره مقدس","t":"hard","te":"🔴","hp":600,"mp":80,"d":35,"df":40,"lv":20,"sk":["بال فرشته","نفس آتشین","نیزه مقدس"],"sd":[60,45,55],"se":["stun","🔥آتش",None],"rn":1500,"xp":600,"dr":["زره کوره","شمشیر تقدیس"],"dc":[0.1,0.08]},
    "black_knife":{"n":"آدمکش خنجر سیاه","t":"hard","te":"🔴","hp":400,"mp":50,"d":40,"df":20,"lv":22,"sk":["گام سایه","خنجر مرگبار"],"sd":[30,55],"se":["dodge","🩸خونریزی"],"rn":2000,"xp":800,"dr":["خنجر سیاه"],"dc":[0.05]},
    "tree_sentinel":{"n":"نگهبان درخت اردتری","t":"elite","te":"⚫","hp":1200,"mp":100,"d":45,"df":50,"lv":30,"sk":["ضربه هَلبرد","تازش اسب","خشم اردتری"],"sd":[80,70,100],"se":[None,"stun","🔥آتش"],"rn":5000,"xp":2000,"dr":["هلبرد طلایی","زره نگهبان"],"dc":[0.15,0.08],"boss":True},
    "stormhawk":{"n":"باز طوفان","t":"medium","te":"🟡","hp":200,"mp":40,"d":20,"df":12,"lv":15,"sk":["پنجه آذرخش"],"sd":[30],"se":[None],"rn":400,"xp":180,"dr":["پر طوفان"],"dc":[0.5]},
    "glintstone_sorc":{"n":"جادوگر گلینت","t":"medium","te":"🟡","hp":180,"mp":150,"d":25,"df":10,"lv":18,"sk":["پیکان گلینت","سنگ آسمانی"],"sd":[35,45],"se":[None,None],"rn":450,"xp":200,"dr":["عصای گلینت"],"dc":[0.2]},
}

N = {
    "merchant_kale":{"n":"کیل تاجر","loc":"کلیسای الی","area":"limgrave","shop":True,"items":{"مشعل":100,"تلسکوپ":300,"زره زنجیری":1000,"تیر ×10":150},
        "d":{"place":["این کلیسای الی... آخرین پناهگاه امن قبل از استورویل. گادریک اینجا رو هنوز نسوزونده.","تارنیش‌ها اینجا جمع می‌شن. بعضی‌هاشون دیوونه شدن.","اگه می‌خوای به استورویل بری، از دروازه اصلی نرو. گاستوک رو پیدا کن..."],
              "enemies":["اون سربازای گادریک رو می‌بینی؟ قبلاً آدم بودن. حالا فقط پوسته‌ان.","یه چیزی تو تپه‌های طوفان هست... یه سوارکار طلایی. نگهبان درخت. نزدیکش نشو."],
              "greet":"تارنیش... هه. دیگری آمده که به دنبال اردتری بگردد. من اینجام تا کمک کنم... البته با قیمت مناسب."}},
    "varre":{"n":"وار صورت‌سفید","loc":"قدم اول","area":"limgrave","shop":False,
        "d":{"place":["این لیمگریو، محل شروع تارنیش‌های بی‌عرضه. می‌دونی چند نفر قبل از تو پریدن پایین؟","استورویل رو می‌بینی؟ گادریک منتظره تا اعضای بدنت رو پیوند بزنه."],
              "enemies":["سربازای گادریک؟ تفاله‌ان. اگه از پسشون برنیای، برگرد خونه.","نگهبان درخت رو دیدی؟ اون فقط یه طعم‌ست."],
              "greet":"آه، تارنیش تازه‌ای. چه تازه و بی‌تجربه... شاید باید کشته شوی؟ نه، بذار ببینیم چقدر دوام میاری."}},
    "roderika":{"n":"رودریکا","loc":"کلبه تپه طوفان","area":"limgrave","shop":False,
        "d":{"place":["همه‌جا جرقه‌های روح می‌بینم... می‌درخشند و می‌میرند.","این کلبه... آخرین جاییه که احساس امنیت می‌کنم."],
              "enemies":["گادریک... اون هیولا. آدم‌ها رو تکه‌تکه می‌کنه.","روح‌ها می‌گن یه شوالیه طلایی تو تپه‌ها هست."],
              "greet":"تو هم تارنیشی... مثل بقیه. من می‌تونم کمک کنم، با روح‌ها حرف می‌زنم."}},
    "boc":{"n":"باک درزگر","loc":"غار ساحلی","area":"limgrave","shop":True,"items":{"تعمیر لباس":50,"تغییر لباس":200},
        "d":{"place":["من تو این غار گیر افتاده‌م... آدم‌بزرگ‌ها منو کتک زدن. کمکم کن!","مادر من یه درزگر عالی بود. به من یاد داد چطور لباس‌ها رو زیبا کنم."],
              "enemies":["اون آدم‌بزرگ‌های بد تو غار هستن! با چماق‌های بزرگ.","تو ساحل خرچنگ‌های غول‌پیکر هستن. خیلی خطرناکن."],
              "greet":"آه! یه تارنیش! خواهش می‌کنم، منو نزن! من فقط یه درزگرم..."}},
    "d_hunter":{"n":"دی، شکارچی مردگان","loc":"دهکده سامورایی‌وَر","area":"limgrave","shop":False,
        "d":{"place":["این دهکده... بوی مرگ می‌ده. ریشه مرگ اینجا قوی‌تر از هر جای دیگه‌ست.","اگه استخوان‌های راه‌رونده رو دیدی، نابودشون کن."],
              "enemies":["اونایی که در مرگ زندگی می‌کنن... خطرناک‌ترین دشمنان هستن.","موجودات ریشه مرگ رو می‌شناسی؟ استخوان‌های زنده، روح‌های سرگردان."],
              "greet":"تارنیش. من دی هستم، شکارچی کسانی که در مرگ زندگی می‌کنند."}},
    "gostoc":{"n":"دربان گاستوک","loc":"دروازه اصلی استورویل","area":"stormveil","shop":False,
        "d":{"place":["خوش آمدی به استورویل، قصر لرد گادریک. می‌خوای از دروازه اصلی بری؟ *زمزمه* یا راه مخفی رو ترجیح می‌دی؟","این قلعه پر از تله‌ست. خیلی‌ها اومدن و... دیگه نرفتن."],
              "enemies":["سربازای گادریک همه‌جا هستن. ولی اگه از راه مخفی بری... شاید کمتر ببینیشون.","پرنده‌های طوفانی رو می‌بینی؟ اون بالا لونه دارن."],
              "greet":"سلام، دوست من. من گاستوکم، دربان این قلعه. می‌تونم کمکت کنم..."}},
    "nepheli":{"n":"نفلی لوکس","loc":"حیاط پادگان","area":"stormveil","shop":False,
        "d":{"place":["من اومدم گادریک رو سرنگون کنم. ظلمش به مردم لیمگریو خیلی طول کشیده.","این قلعه بوی خون می‌ده."],
              "enemies":["سربازای گادریک قوی‌ان، ولی من قوی‌ترم. من جنگجوی هوارا لوکس هستم.","گادریک خودش ضعیفه، ولی اعضایی که پیوند زده خیلی خطرناکن."],
              "greet":"تارنیش! من نفلی لوکس هستم. اومدم این هیولا رو نابود کنم. به کمک نیاز داری؟"}},
    "renna":{"n":"جادوگر رنا","loc":"کلیسای عهد","area":"liurnia","shop":False,
        "d":{"place":["این کلیسا... روزگاری محل عهد و پیمان بود. حالا فقط سایه‌ای از گذشته‌ست.","لیورنیا پر از جادوئه. آکادمی رایا لوکاریا، دریاچه مه‌آلود..."],
              "enemies":["جادوگرای آکادمی خطرناکن. ذهنشون در بلورهای گلینت غرق شده.","خرچنگ‌های غول‌پیکر تو دریاچه هستن."],
              "greet":"تارنیش... من رنا هستم، جادوگر این سرزمین‌ها. این زنگ رو بگیر. با روح‌ها حرف بزن."}},
    "thops":{"n":"جادوگر تاپس","loc":"شهر دروازه آکادمی","area":"liurnia","shop":True,"items":{"سنگریزه گلینت":500,"سپر محقق":800,"کلید آکادمی":5000},
        "d":{"place":["من محقق آکادمی بودم... تا کلیدم رو گم کردم. نمی‌تونم برگردم.","آکادمی پر از قدرته. جادوهایی که تصورش رو هم نمی‌کنی."],
              "enemies":["جادوگرای آکادمی قبلاً همکارام بودن. حالا دشمن.","اژدهای گلینت‌استون رو شنیدی؟ تو دریاچه زندگی می‌کنه."],
              "greet":"سلام، تارنیش. من تاپس هستم. می‌تونی کمکم کنی کلید رو پیدا کنم؟"}},
}

L = {
    "limgrave":{"n":"لیمگریو","start":"first_step",
        "sub":{
            "first_step":{"n":"قدم اول","co":"(3,1)","npcs":["varre"],"cn":{"north":"elleh_church","west":"coastal_cave"}},
            "elleh_church":{"n":"کلیسای الی","co":"(4,2)","npcs":["merchant_kale"],"cn":{"south":"first_step","east":"samurai_village","west":"gatefront"}},
            "gatefront":{"n":"دروازه‌گاه طوفان","co":"(3,2)","npcs":[],"cn":{"north":"stormhill","east":"elleh_church"}},
            "samurai_village":{"n":"دهکده سامورایی‌وَر","co":"(5,2)","npcs":["d_hunter"],"cn":{"west":"elleh_church"}},
            "stormhill":{"n":"تپه‌های طوفان","co":"(4,3)","npcs":["roderika"],"cn":{"south":"gatefront","north":"stormveil_entrance"}},
            "coastal_cave":{"n":"غار ساحلی","co":"(1,1)","npcs":["boc"],"cn":{"east":"first_step"}}}},
    "stormveil":{"n":"استورویل","start":"stormveil_entrance",
        "sub":{
            "stormveil_entrance":{"n":"دروازه اصلی","co":"(4,4)","npcs":["gostoc"],"cn":{"south":"stormhill","north":"courtyard"}},
            "courtyard":{"n":"حیاط پادگان","co":"(4,5)","npcs":["nepheli"],"cn":{"south":"stormveil_entrance","north":"bell_tower"}},
            "bell_tower":{"n":"برج ناقوس","co":"(5,5)","npcs":[],"cn":{"south":"courtyard"}}}},
    "liurnia":{"n":"لیورنیا","start":"liurnia_lake",
        "sub":{
            "liurnia_lake":{"n":"دریاچه اصلی","co":"(6,3)","npcs":[],"cn":{"east":"academy_gate","west":"vows_church"}},
            "academy_gate":{"n":"شهر دروازه آکادمی","co":"(7,3)","npcs":["thops"],"cn":{"west":"liurnia_lake"}},
            "vows_church":{"n":"کلیسای عهد","co":"(5,3)","npcs":["renna"],"cn":{"east":"liurnia_lake"}}}},
}

LE = {"limgrave":["wandering_noble","godrick_soldier","grafted_scion","giant_crab","crucible_knight","black_knife","tree_sentinel"],
      "stormveil":["godrick_soldier","stormhawk","grafted_scion","crucible_knight"],
      "liurnia":["glintstone_sorc","giant_crab","black_knife"]}

# ==================== HELPERS ====================
def bar(v,mx,ln=10):
    f=int((v/mx)*ln) if mx>0 else 0
    return "▰"*f+"▱"*(ln-f)

def sp(p):
    os.makedirs("players",exist_ok=True)
    with open(f"players/{p['id']}.json","w",encoding="utf-8") as f:
        json.dump(p,f,ensure_ascii=False)

def lp(uid):
    try:
        with open(f"players/{uid}.json","r",encoding="utf-8") as f:
            return json.load(f)
    except: return None

def pe(uid): return os.path.exists(f"players/{uid}.json")

def np(uid,un,cn,cc):
    cd=C[cc]; s=cd["s"].copy()
    return {"id":uid,"username":un,"name":cn,"class":cc,"cn":cd["n"],"lv":1,"xp":0,"xpn":100,
            "rn":100,"dm":0,"kills":0,"karma":0,"st":s,"sp":0,
            "hp":100+s["VIT"]*10,"mhp":100+s["VIT"]*10,
            "mp":50+s["INT"]*5,"mmp":50+s["INT"]*5,
            "en":100,"men":100+s["END"]*2,
            "eq":{"right_hand":None,"left_hand":None,"chest":None,"head":None,"hands":None,"legs":None,"talisman":None},
            "inv":[],"imx":30+s["END"],"sk":cd.get("sk",[]),"sl":{sk:1 for sk in cd.get("sk",[])},
            "area":"limgrave","loc":"first_step","vis":["first_step"],
            "def_bosses":[],"quests":[],"daily":None,"combat":False,"cs":None}

def md(p):
    a=L.get(p["area"],{}); l=a.get("sub",{}).get(p["loc"],{})
    return f"""⚜️ سرزمین‌های خاکستر
━━━━━━━━━━━━━━━━━
📍 {l.get('n','?')} | 🗺️ {a.get('n','?')}
👑 ماری: {p['name']} | ⚡ Lv.{p['lv']}
━━━━━━━━━━━━━━━━━
❤️ HP: {bar(p['hp'],p['mhp'])} {p['hp']}/{p['mhp']}
💧 MP: {bar(p['mp'],p['mmp'])} {p['mp']}/{p['mmp']}
⚡ EN: {bar(p['en'],p['men'])} {int(p['en']/p['men']*100) if p['men']>0 else 0}%
📊 XP: {bar(p['xp'],p['xpn'])} {p['xp']}/{p['xpn']}
━━━━━━━━━━━━━━━━━
💰 سکه: {p['rn']:,} | 💎 الماس: {p['dm']}
🎒 کوله: {len(p['inv'])}/{p['imx']} | ⚔️ کشتار: {p['kills']}
🧠 امتیاز مهارت: {p['sp']}"""

def cd_disp(p):
    s=p["st"]
    return f"""👤 مشخصات {p['name']}
━━━━━━━━━━━━━━━━━
🎭 کلاس: {p['cn']} | ⚡ Lv.{p['lv']}
⚖️ کارما: {p['karma']}
━━━━━━━━━━━━━━━━━
❤️ HP: {bar(p['hp'],p['mhp'])} {p['hp']}/{p['mhp']}
💧 MP: {bar(p['mp'],p['mmp'])} {p['mp']}/{p['mmp']}
⚡ EN: {int(p['en']/p['men']*100) if p['men']>0 else 0}%

📊 ویژگی‌های پایه:
▪ قدرت (STR): {s['STR']}     ▪ چابکی (DEX): {s['DEX']}
▪ هوش (INT): {s['INT']}      ▪ استقامت (VIT): {s['VIT']}
▪ ادراک (PER): {s['PER']}     ▪ شانس (LCK): {s['LCK']}
▪ جذبه (CHR): {s['CHR']}     ▪ پایداری (END): {s['END']}
▪ سرعت (AGI): {s['AGI']}     ▪ فرزانگی (WIS): {s['WIS']}
━━━━━━━━━━━━━━━━━
💰 سکه: {p['rn']:,} | 💎 الماس: {p['dm']}
🧠 امتیاز مهارت: {p['sp']}"""

def wd_disp(p):
    a=L.get(p["area"],{}); l=a.get("sub",{}).get(p["loc"],{})
    npcs="".join([f"\n  • {N[n]['n']}" for n in l.get("npcs",[]) if n in N])
    return f"""🗺️ جهان الدن رینگ
━━━━━━━━━━━━━━━━━
📍 {l.get('n','?')}
🗺️ منطقه: {a.get('n','?')}
🧭 مختصات: {l.get('co','?')}
━━━━━━━━━━━━━━━━━
🔊 ساکنین:{npcs if npcs else ' (کسی اینجا نیست)'}
━━━━━━━━━━━━━━━━━
⬆️⬇️⬅️➡️ برای حرکت"""

def sp_enemy(area,tier=None):
    if area not in LE: return None
    ae=LE[area]
    if tier:
        ae=[e for e in ae if E[e]["t"]==tier]
        if not ae: return None
    eid=random.choice(ae)
    ed=E[eid].copy()
    ed["id"]=eid; ed["chp"]=ed["hp"]; ed["cmp"]=ed["mp"]; ed["status"]=[]
    return ed

def cs_create(p,en):
    return {"pid":p["id"],"en":en,"turn":"player","tn":1,"log":[],
            "php":p["hp"],"pmp":p["mp"],"pen":p["en"],
            "pdf":p["st"]["VIT"],"patk":5,
            "weather":random.choice(["☀️","🌧️","⛈️"]),"boss":en.get("boss",False)}

def cs_disp(cs,p):
    en=cs["en"]
    return f"""⚔️ نبرد حماسی
━━━━━━━━━━━━━━━━━
🛡️ {p['name']} (Lv.{p['lv']})
❤️ {bar(cs['php'],p['mhp'])} {cs['php']}/{p['mhp']}
💧 MP: {cs['pmp']}/{p['mmp']} | ⚡ EN: {cs['pen']}

😈 {en['te']} {en['n']} (Lv.{en['lv']})
❤️ {bar(en['chp'],en['hp'])} {en['chp']}/{en['hp']}
💧 MP: {en['cmp']}/{en['mp']}
━━━━━━━━━━━━━━━━━
📜 وقایع نبرد:
{chr(10).join(['» '+l for l in cs['log'][-5:]]) if cs['log'] else '» نبرد آغاز می‌شود...'}
━━━━━━━━━━━━━━━━━
⏳ نوبت: {'🟢 شما' if cs['turn']=='player' else f'🔴 {en["n"]}'}
💎 اقدام خود را انتخاب کن:"""

def patk(cs,heavy=False):
    en=cs["en"]
    en_cost=15 if heavy else 8
    if cs["pen"]<en_cost: return "⚡ انرژی کافی نیست!"
    cs["pen"]-=en_cost
    dmg=max(1,cs["patk"]+random.randint(5,15)-en["df"])
    if heavy: dmg=int(dmg*1.8)
    crit=random.random()<0.1
    if crit: dmg*=2
    en["chp"]=max(0,en["chp"]-dmg)
    atype="🗡️ سنگین" if heavy else "⚔️ سبک"
    msg=f"⚡ ضربه کاری! {dmg} آسیب!" if crit else f"{atype}: {dmg} آسیب به {en['n']}!"
    cs["log"].append(msg); return msg

def defend(cs):
    cs["pdf"]=int(cs["pdf"]*1.5)
    cs["pen"]=min(cs["pen"]+10,p["men"])
    msg="🛡️ حالت دفاعی! آسیب کمتر، انرژی بیشتر!"
    cs["log"].append(msg); return msg

def psk(cs,sk):
    en=cs["en"]
    if cs["pmp"]<15: return "💧 MP کافی نیست!"
    cs["pmp"]-=15; dmg=max(1,random.randint(15,40)-en["df"]//2)
    en["chp"]=max(0,en["chp"]-dmg)
    msg=f"🧠 «{sk}»! {dmg} آسیب جادویی!"
    cs["log"].append(msg); return msg

def eatk(cs):
    en=cs["en"]
    if en.get("sk") and en.get("cmp",0)>=10 and random.random()<0.6:
        i=random.randint(0,len(en["sk"])-1); dmg=max(1,en["sd"][i]-cs["pdf"]//2)
        cs["php"]=max(0,cs["php"]-dmg); en["cmp"]=max(0,en["cmp"]-10)
        msg=f"😈 {en['n']} 《{en['sk'][i]}》! {dmg} آسیب!"
    else:
        dmg=max(1,en["d"]-cs["pdf"]); cs["php"]=max(0,cs["php"]-dmg)
        msg=f"😈 {en['n']} حمله کرد! {dmg} آسیب!"
    cs["log"].append(msg); cs["pdf"]=p["st"]["VIT"]; return msg

def chk_end(cs):
    if cs["en"]["chp"]<=0: return "win"
    if cs["php"]<=0: return "lose"
    return None

def victory(cs,p):
    en=cs["en"]; xp,rn=en["xp"],en["rn"]
    drops=[d for d,c in zip(en.get("dr",[]),en.get("dc",[])) if random.random()<c]
    for d in drops:
        if len(p["inv"])<p["imx"]: p["inv"].append(d)
    p["xp"]+=xp; p["rn"]+=rn; p["kills"]+=1
    while p["xp"]>=p["xpn"]:
        p["lv"]+=1; p["xp"]-=p["xpn"]; p["xpn"]=int(p["xpn"]*1.5); p["sp"]+=3
        p["mhp"]+=10; p["hp"]=p["mhp"]; p["mmp"]+=5; p["mp"]=p["mmp"]
    p["combat"]=False; p["cs"]=None; p["en"]=p["men"]
    return f"✨🎊 پیروزی شکوهمند!\n⭐ {en['n']} را شکست دادی!\n🎁 +{xp} XP | +{rn} سکه"+(f"\n📦 غنائم: {', '.join(drops)}" if drops else "")

def defeat(p):
    p["rn"]=int(p["rn"]*0.9); p["combat"]=False; p["cs"]=None; p["hp"]=p["mhp"]; p["en"]=p["men"]
    return "💀 شکست خوردی...\n📉 ۱۰٪ سکه‌ها از دست رفت.\n🔥 برخیز و دوباره تلاش کن!"

# ==================== KEYBOARDS (ENHANCED) ====================
def kmain(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("⚔️ ماجراجویی (نبرد)",callback_data="adv")],
    [InlineKeyboardButton("🗺️ جهان (ناوبری)",callback_data="wrld"),InlineKeyboardButton("👤 شخصیت (آمار)",callback_data="char")],
    [InlineKeyboardButton("🎒 کوله‌پشتی (آیتم‌ها)",callback_data="eq"),InlineKeyboardButton("🏛️ تعامل با مکان",callback_data="intr")],
    [InlineKeyboardButton("⚙️ سیستم (تنظیمات)",callback_data="sys"),InlineKeyboardButton("🏕️ استراحت",callback_data="rest")]])

def kchar(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 آمار کامل",callback_data="stats"),InlineKeyboardButton("⚡ مهارت‌ها",callback_data="skm")],
    [InlineKeyboardButton("🎒 کوله‌پشتی",callback_data="eq"),InlineKeyboardButton("🔄 توزیع مجدد",callback_data="respec")],
    [InlineKeyboardButton("🔙 بازگشت به منوی اصلی",callback_data="back")]])

def ktier(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("🟢 آسان - دشمنان ضعیف",callback_data="t_easy")],
    [InlineKeyboardButton("🟡 متوسط - پاداش خوب",callback_data="t_medium")],
    [InlineKeyboardButton("🔴 سخت - غنائم باارزش",callback_data="t_hard")],
    [InlineKeyboardButton("⚫ نخبه - باس‌فایت",callback_data="t_elite")],
    [InlineKeyboardButton("🎲 تصادفی",callback_data="t_random")],
    [InlineKeyboardButton("🔙 بازگشت",callback_data="back")]])

def kcombat(p): return InlineKeyboardMarkup([
    [InlineKeyboardButton("⚔️ حمله سبک (EN:8)",callback_data="c_atk"),InlineKeyboardButton("🗡️ حمله سنگین (EN:15)",callback_data="c_hatk")],
    [InlineKeyboardButton("🛡️ دفاع (+EN, کم‌آسیب)",callback_data="c_def"),InlineKeyboardButton("🧠 مهارت‌ها (MP:15)",callback_data="c_sk")],
    [InlineKeyboardButton("🧪 استفاده از آیتم",callback_data="c_item"),InlineKeyboardButton("🏃 فرار (AGI)",callback_data="c_flee")]])

def ksys(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("🎁 جایزه روزانه",callback_data="daily"),InlineKeyboardButton("📊 پاداش‌های لول",callback_data="lvlrwd")],
    [InlineKeyboardButton("💡 راهنمای بازی",callback_data="guide"),InlineKeyboardButton("⚙️ تنظیمات",callback_data="settings")],
    [InlineKeyboardButton("🔙 بازگشت",callback_data="back")]])

def kworld(p):
    a=L.get(p["area"],{}); l=a.get("sub",{}).get(p["loc"],{}); cn=l.get("cn",{})
    btns=[]; nr=[]
    for d,k in [("north","⬆️ شمال"),("south","⬇️ جنوب"),("east","➡️ شرق"),("west","⬅️ غرب")]:
        if d in cn: nr.append(InlineKeyboardButton(k,callback_data=f"mv_{cn[d]}"))
    if nr: btns.append(nr)
    btns.append([InlineKeyboardButton("🖐️ تعامل با این مکان",callback_data=f"int_{p['loc']}")])
    btns.append([InlineKeyboardButton("⚔️ ماجراجویی در اینجا",callback_data="adv_here"),InlineKeyboardButton("🏕️ استراحت",callback_data="rest")])
    btns.append([InlineKeyboardButton("🔥 آتش‌گاه (سفر سریع)",callback_data="fast_travel"),InlineKeyboardButton("🗺️ نقشه منطقه",callback_data="area_map")])
    btns.append([InlineKeyboardButton("👤 شخصیت",callback_data="char"),InlineKeyboardButton("🔙 منوی اصلی",callback_data="back")])
    return InlineKeyboardMarkup(btns)

def knpc(nid):
    npc=N[nid]; btns=[
        [InlineKeyboardButton("📖 درباره این مکان",callback_data=f"np_{nid}")],
        [InlineKeyboardButton("⚔️ درباره دشمنان",callback_data=f"ne_{nid}")]]
    if npc.get("shop"): btns.append([InlineKeyboardButton("🛒 خرید و فروش",callback_data=f"nsh_{nid}")])
    btns.append([InlineKeyboardButton("🎁 درخواست کمک",callback_data=f"nhelp_{nid}"),InlineKeyboardButton("📜 شروع کوئست",callback_data=f"nquest_{nid}")])
    btns.append([InlineKeyboardButton("👋 خداحافظی",callback_data="bkw")])
    return InlineKeyboardMarkup(btns)

# ==================== HANDLERS ====================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; un=update.effective_user.username or update.effective_user.first_name
    if pe(uid):
        p=lp(uid); p["combat"]=False; p["cs"]=None; sp(p)
        await update.message.reply_text(f"🌟 خوش برگشتی {p['name']}!\n\n{md(p)}",reply_markup=kmain())
    else:
        k=[[InlineKeyboardButton(f"{cd['n']} - {cd['d'][:35]}",callback_data=f"sc_{cid}")] for cid,cd in C.items()]
        await update.message.reply_text("🌟 به سرزمین‌های خاکستر خوش آمدی تارنیش!\n\n🎭 کلاس خود را با دقت انتخاب کن:",reply_markup=InlineKeyboardMarkup(k))

async def btn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=update.effective_user.id
    p=lp(uid)
    if not p: await q.edit_message_text("❌ لطفاً /start را بزن"); return
    d=q.data

    if d.startswith("sc_"):
        cc=d[3:]; ctx.user_data["cc"]=cc
        await q.edit_message_text(f"🗡️ کلاس {C[cc]['n']} انتخاب شد.\n\n📝 نام شخصیت خود را وارد کن:")
    elif d=="adv":
        await q.edit_message_text("⚔️ ماجراجویی\n\nسطح دشواری نبرد را انتخاب کن:",reply_markup=ktier())
    elif d.startswith("t_"):
        tier=d[2:] if d!="t_random" else None
        en=sp_enemy(p["area"],tier)
        if not en: await q.edit_message_text("❌ دشمنی در این منطقه پیدا نشد!",reply_markup=kmain()); return
        cs=cs_create(p,en); p["combat"]=True; p["cs"]=cs; ctx.user_data["cs"]=cs; sp(p)
        await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="adv_here":
        await q.edit_message_text("⚔️ سطح دشواری:",reply_markup=ktier())
    elif d=="wrld":
        await q.edit_message_text(wd_disp(p),reply_markup=kworld(p))
    elif d.startswith("mv_"):
        nl=d[3:]; p["loc"]=nl
        if nl not in p.get("vis",[]): p.setdefault("vis",[]).append(nl)
        sp(p); await q.edit_message_text(wd_disp(p),reply_markup=kworld(p))
    elif d=="char":
        await q.edit_message_text(cd_disp(p),reply_markup=kchar())
    elif d=="stats":
        await q.edit_message_text(cd_disp(p),reply_markup=kchar())
    elif d=="eq":
        inv=p["inv"]
        txt="🎒 کوله‌پشتی\n━━━━━━━━━━━━━━━━━\n"
        if not inv: txt+="(خالی)"
        else:
            for i,it in enumerate(inv[:10],1):
                eqd=" ⚡تجهیز شده" if it in p["eq"].values() else ""
                txt+=f"{i}. {it}{eqd}\n"
        txt+=f"\n━━━━━━━━━━━━━━━━━\n📦 {len(inv)}/{p['imx']} آیتم"
        btns=[]
        for i,it in enumerate(inv[:5]):
            btns.append([InlineKeyboardButton(f"{'⚡' if it in p['eq'].values() else '•'} {it[:30]}",callback_data=f"use_{it}")])
        btns.append([InlineKeyboardButton("🔙 بازگشت",callback_data="char")])
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(btns))
    elif d.startswith("use_"):
        it=d[4:]
        if it in p["inv"]:
            if it in p["eq"].values():
                for s,eid in p["eq"].items():
                    if eid==it: p["eq"][s]=None; break
                await q.edit_message_text(f"🔓 {it} از تجهیز خارج شد.",reply_markup=kchar())
            else:
                p["eq"]["right_hand"]=it
                await q.edit_message_text(f"⚡ {it} تجهیز شد!",reply_markup=kchar())
            sp(p)
    elif d=="skm":
        txt="🧠 مهارت‌های تو\n━━━━━━━━━━━━━━━━━\n"
        for sk in p.get("sk",[]): txt+=f"🔹 {sk} (Lv.{p['sl'].get(sk,1)})\n"
        txt+=f"\n🧠 امتیاز مهارت: {p['sp']}"
        btns=[]
        if p['sp']>0:
            for sk in p.get("sk",[]): btns.append([InlineKeyboardButton(f"⬆️ ارتقاء {sk} (-1)",callback_data=f"usk_{sk}")])
        btns.append([InlineKeyboardButton("🔙 بازگشت",callback_data="char")])
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(btns))
    elif d.startswith("usk_"):
        sk=d[4:]
        if p['sp']>0: p['sp']-=1; p['sl'][sk]=p['sl'].get(sk,1)+1; sp(p)
        await q.edit_message_text(f"⬆️ {sk} ارتقاء یافت!\nسطح جدید: {p['sl'][sk]}",reply_markup=kchar())
    elif d=="sys":
        await q.edit_message_text("⚙️ سیستم\n\nیک گزینه انتخاب کن:",reply_markup=ksys())
    elif d=="daily":
        tdy=str(date.today())
        if p.get("daily")==tdy: await q.edit_message_text("🎁 جایزه امروز رو گرفتی!\n⏰ فردا دوباره بیا.",reply_markup=ksys()); return
        p["daily"]=tdy; p["rn"]+=500; p["dm"]+=2; sp(p)
        await q.edit_message_text("🎁 جایزه روزانه\n\n💰 +۵۰۰ سکه\n💎 +۲ الماس\n\nفردا هم یادت نره!",reply_markup=ksys())
    elif d=="lvlrwd":
        txt="📊 پاداش‌های لول آپ\n━━━━━━━━━━━━━━━━━\n\n"
        for lv,rwd in {1:"🎁 معجون سلامت ×5",5:"💰 ۱,۰۰۰ سکه",10:"💎 ۵ الماس",15:"🎁 معجون ×10",20:"🔧 کیت تعمیر",25:"💎 ۱۵ الماس",30:"⚗️ معجون بزرگ",50:"💎 ۵۰ الماس",100:"🎁 اشک لارو"}.items():
            txt+=f"{'✅' if lv<=p['lv'] else '🔒'} Lv.{lv}: {rwd}\n"
        await q.edit_message_text(txt,reply_markup=ksys())
    elif d=="rest":
        if p["en"]==p["men"] and p["hp"]==p["mhp"]:
            await q.edit_message_text("😴 نیازی به استراحت نداری!",reply_markup=kmain())
        else:
            p["hp"]=p["mhp"]; p["mp"]=p["mmp"]; p["en"]=p["men"]; sp(p)
            await q.edit_message_text("🏕️ استراحت کردی...\n❤️💧⚡ کاملاً بازیابی شد!\n\nاحساس بهتری داری.",reply_markup=kmain())
    elif d=="intr":
        a=L[p["area"]]; l=a["sub"].get(p["loc"],{})
        btns=[]
        for nid in l.get("npcs",[]):
            if nid in N: btns.append([InlineKeyboardButton(f"💬 گفتگو با {N[nid]['n']}",callback_data=f"tk_{nid}")])
        btns.append([InlineKeyboardButton("⛏️ کاوش منابع",callback_data="gath")])
        btns.append([InlineKeyboardButton("🔍 جستجوی تجهیزات",callback_data="srch")])
        btns.append([InlineKeyboardButton("🤫 دزدی در سایه",callback_data="steal")])
        btns.append([InlineKeyboardButton("🔙 بازگشت",callback_data="bkw")])
        await q.edit_message_text(f"🏛️ {l['n']}\n\nانتخاب کن:",reply_markup=InlineKeyboardMarkup(btns))
    elif d.startswith("tk_"):
        nid=d[3:]; npc=N.get(nid)
        if not npc: await q.edit_message_text("❌",reply_markup=kmain()); return
        await q.edit_message_text(f"💬 {npc['n']}\n━━━━━━━━━━━━━━━━━\n*«{npc['d']['greet']}»*\n━━━━━━━━━━━━━━━━━\nچه می‌پرسی؟",reply_markup=knpc(nid),parse_mode="Markdown")
    elif d.startswith("np_"):
        nid=d[3:]; npc=N[nid]
        await q.edit_message_text(f"📖 {npc['n']}:\n\n_{random.choice(npc['d']['place'])}_",reply_markup=knpc(nid),parse_mode="Markdown")
    elif d.startswith("ne_"):
        nid=d[3:]; npc=N[nid]
        await q.edit_message_text(f"⚔️ {npc['n']}:\n\n_{random.choice(npc['d']['enemies'])}_",reply_markup=knpc(nid),parse_mode="Markdown")
    elif d.startswith("nsh_"):
        nid=d[4:]; npc=N[nid]
        if not npc.get("shop"): await q.edit_message_text("❌",reply_markup=kmain()); return
        txt=f"🛒 {npc['n']}\n━━━━━━━━━━━━━━━━━\n\n"
        for item,price in npc.get("items",{}).items(): txt+=f"• {item}: {price:,} سکه\n"
        txt+=f"\n💰 موجودی تو: {p['rn']:,} سکه"
        await q.edit_message_text(txt,reply_markup=knpc(nid))
    elif d.startswith("nhelp_"):
        nid=d[6:]; npc=N[nid]
        await q.edit_message_text(f"🎁 {npc['n']}:\n\n_کمکی برای تو ندارم تارنیش... شاید بعداً._",reply_markup=knpc(nid),parse_mode="Markdown")
    elif d.startswith("nquest_"):
        nid=d[7:]; npc=N[nid]
        await q.edit_message_text(f"📜 {npc['n']}:\n\n_کوئستی برای تو ندارم... هنوز._",reply_markup=knpc(nid),parse_mode="Markdown")
    elif d=="gath":
        if p["en"]<20: await q.edit_message_text("⚡ انرژی کافی نداری! استراحت کن.",reply_markup=kmain()); return
        p["en"]-=20
        if random.random()<0.5+min(p["st"]["LCK"]*0.02,0.3):
            rid=random.choice(["سنگ آهنگری [1]","گیاه دارویی","تکه رون","کریستال اشک"])
            if len(p["inv"])<p["imx"]: p["inv"].append(rid)
            sp(p); await q.edit_message_text(f"⛏️ {rid} پیدا کردی!",reply_markup=kmain())
        else: sp(p); await q.edit_message_text("⛏️ چیزی پیدا نکردی...\n⚡ انرژی باقی‌مانده: "+str(p["en"]),reply_markup=kmain())
    elif d=="srch":
        if p["en"]<30: await q.edit_message_text("⚡ انرژی کافی نداری!",reply_markup=kmain()); return
        p["en"]-=30
        if random.random()<0.3+min(p["st"]["LCK"]*0.02,0.2):
            rid=random.choice(["شمشیر سرباز","زره چرمی","طلسم کوچک","حلقه طلایی"])
            if len(p["inv"])<p["imx"]: p["inv"].append(rid)
            sp(p); await q.edit_message_text(f"🔍 {rid} پیدا کردی!",reply_markup=kmain())
        else: sp(p); await q.edit_message_text("🔍 چیزی پیدا نکردی...",reply_markup=kmain())
    elif d=="steal":
        if p["en"]<25: await q.edit_message_text("⚡ انرژی کم!",reply_markup=kmain()); return
        p["en"]-=25
        if random.random()<0.2+min(p["st"]["AGI"]*0.02,0.3):
            rid=random.choice(["سکه دزدیده شده","جواهر مخفی","نقشه قدیمی"])
            if len(p["inv"])<p["imx"]: p["inv"].append(rid); p["karma"]-=1
            sp(p); await q.edit_message_text(f"🤫 {rid} دزدیدی!\n⚖️ کارما: {p['karma']}",reply_markup=kmain())
        else: sp(p); await q.edit_message_text("🤫 گیر افتادی! فرار کن!",reply_markup=kmain())
    elif d=="c_atk":
        cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        patk(cs,False); res=chk_end(cs)
        if res=="win": msg=victory(cs,p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        elif res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        eatk(cs); res=chk_end(cs)
        if res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        ctx.user_data["cs"]=cs; p["cs"]=cs; sp(p)
        await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="c_hatk":
        cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        patk(cs,True); res=chk_end(cs)
        if res=="win": msg=victory(cs,p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        elif res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        eatk(cs); res=chk_end(cs)
        if res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        ctx.user_data["cs"]=cs; p["cs"]=cs; sp(p)
        await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="c_def":
        cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        defend(cs); eatk(cs); res=chk_end(cs)
        if res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        ctx.user_data["cs"]=cs; p["cs"]=cs; sp(p)
        await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="c_sk":
        cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        btns=[[InlineKeyboardButton(f"🧠 {sk} (MP:15)",callback_data=f"cusk_{sk}")] for sk in p.get("sk",[])]
        btns.append([InlineKeyboardButton("🔙 بازگشت به نبرد",callback_data="c_back")])
        await q.edit_message_text("🧠 مهارت خود را انتخاب کن:",reply_markup=InlineKeyboardMarkup(btns))
    elif d.startswith("cusk_"):
        sk=d[5:]; cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        psk(cs,sk); res=chk_end(cs)
        if res=="win": msg=victory(cs,p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        elif res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        eatk(cs); res=chk_end(cs)
        if res=="lose": msg=defeat(p); sp(p); await q.edit_message_text(msg,reply_markup=kmain()); return
        ctx.user_data["cs"]=cs; p["cs"]=cs; sp(p)
        await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="c_back":
        cs=ctx.user_data.get("cs")
        if cs: await q.edit_message_text(cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="c_flee":
        cs=ctx.user_data.get("cs")
        if not cs: await q.edit_message_text("❌",reply_markup=kmain()); return
        if random.random()<0.3+min(p["st"]["AGI"]*0.02,0.3):
            p["combat"]=False; p["cs"]=None; sp(p)
            await q.edit_message_text("🏃 با موفقیت فرار کردی!",reply_markup=kmain())
        else:
            eatk(cs); ctx.user_data["cs"]=cs; p["cs"]=cs; sp(p)
            await q.edit_message_text("❌ فرار ناموفق!\n\n"+cs_disp(cs,p),reply_markup=kcombat(p))
    elif d=="back":
        await q.edit_message_text(md(p),reply_markup=kmain())
    elif d=="bkw":
        await q.edit_message_text(wd_disp(p),reply_markup=kworld(p))
    else:
        await q.edit_message_text(md(p),reply_markup=kmain())

async def name_inp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; un=update.effective_user.username or update.effective_user.first_name
    cc=ctx.user_data.get("cc","vagabond"); cn=update.message.text
    p=np(uid,un,cn,cc); sp(p)
    await update.message.reply_text(f"✨ شخصیت {cn} ساخته شد!\n🎭 کلاس: {p['cn']}\n\n{md(p)}",reply_markup=kmain())

async def stuck_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    if pe(uid): p=lp(uid); p["combat"]=False; p["cs"]=None; sp(p); await update.message.reply_text("✅ بازیابی موفق!\n\n"+md(p),reply_markup=kmain())

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("stuck",stuck_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,name_inp))
    print("🌟 Elden Ring RPG Bot (Enhanced) running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
    main()

import telebot
import random
from datetime import datetime

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

bekleyenler = []
aktif_sohbetler = {}
profil_notlari = {}
itiraflar = []

def gece_mi():
    now = datetime.now().hour
    return 0 <= now <= 5

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "🌘 Gece Uykusuzlar Botuna hoş geldin!\n"
                                      "00:00 - 05:00 arasında biriyle rastgele sohbet edebilirsin.\n"
                                      "Başlamak için /gecesohbet yaz.")

@bot.message_handler(commands=['gecesohbet'])
def gecesohbet(message):
    user_id = message.chat.id

    if not gece_mi():
        bot.send_message(user_id, "⏰ Bu özellik sadece gece 00:00 - 05:00 arası aktiftir.")
        return

    if user_id in aktif_sohbetler:
        bot.send_message(user_id, "🔄 Zaten bir sohbettesin. Bitirmek için /bitir yaz.")
        return

    if bekleyenler:
        partner_id = bekleyenler.pop(0)
        aktif_sohbetler[user_id] = partner_id
        aktif_sohbetler[partner_id] = user_id

        profil1 = profil_notlari.get(user_id, "🌙 Profil notu yok.")
        profil2 = profil_notlari.get(partner_id, "🌙 Profil notu yok.")

        bot.send_message(user_id, f"🎉 Bir uykusuzla eşleştin!\n👤 Kişi hakkında: {profil2}")
        bot.send_message(partner_id, f"🎉 Bir uykusuzla eşleştin!\n👤 Kişi hakkında: {profil1}")
    else:
        bekleyenler.append(user_id)
        bot.send_message(user_id, "⌛ Bekleyen kimse yok. Bir uykusuz daha gelene kadar bekliyorsun...")

@bot.message_handler(commands=['bitir'])
def bitir(message):
    user_id = message.chat.id
    partner_id = aktif_sohbetler.pop(user_id, None)

    if partner_id:
        aktif_sohbetler.pop(partner_id, None)
        bot.send_message(user_id, "👋 Sohbet sonlandırıldı.")
        bot.send_message(partner_id, "👋 Karşı taraf sohbeti bitirdi.")
    else:
        if user_id in bekleyenler:
            bekleyenler.remove(user_id)
        bot.send_message(user_id, "❌ Şu anda aktif bir sohbetin yok.")

@bot.message_handler(func=lambda m: m.chat.id in aktif_sohbetler)
def sohbet_aktar(message):
    partner_id = aktif_sohbetler.get(message.chat.id)
    if partner_id:
        bot.send_message(partner_id, message.text)

@bot.message_handler(commands=['profilnotu'])
def not_al(message):
    bot.send_message(message.chat.id, "🎭 Gece uykusuz profil notunu yaz (bir cümle):")
    bot.register_next_step_handler(message, notu_kaydet)

def notu_kaydet(message):
    user_id = message.from_user.id
    profil_notlari[user_id] = message.text
    bot.send_message(message.chat.id, "✅ Notun kaydedildi! Yeni eşleşmelerde görünecek.")

gece_muzikleri = [
    {"ad": "Joji - Glimpse of Us", "link": "https://www.youtube.com/watch?v=k4xFqf2qPHE"},
    {"ad": "Billie Eilish - lovely", "link": "https://www.youtube.com/watch?v=V1Pl8CzNzCw"},
    {"ad": "lofi hip hop radio - beats to relax/study to", "link": "https://www.youtube.com/watch?v=jfKfPfyJRdk"},
    {"ad": "Kurtuluş Kuş - Geceler", "link": "https://www.youtube.com/watch?v=_6XThQH5dQE"},
    {"ad": "Jazz for Sleep", "link": "https://www.youtube.com/watch?v=-5KAN9_CzSA"}
]

@bot.message_handler(commands=['müzik'])
def muzik_oner(message):
    secim = random.choice(gece_muzikleri)
    bot.send_message(
        message.chat.id,
        f"🎧 Bugünün gece modu müziği:\n*{secim['ad']}*\n{secim['link']}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['itiraf'])
def itiraf_al(message):
    bot.send_message(message.chat.id, "🙊 Geceye bir itiraf bırak! (Anonim gönderilecek)")
    bot.register_next_step_handler(message, itiraf_kaydet)

def itiraf_kaydet(message):
    itiraflar.append(message.text)
    bot.send_message(message.chat.id, "🌌 İtirafın geceye karıştı... Belki bir başkası okur.")

@bot.message_handler(commands=['itirafoku'])
def itiraf_oku(message):
    if not itiraflar:
        bot.send_message(message.chat.id, "😶 Henüz kimse itiraf etmedi.")
    else:
        secim = random.choice(itiraflar)
        bot.send_message(message.chat.id, f"🕯 Gece İtirafı:\n\n_{secim}_", parse_mode='Markdown')

bot.polling()

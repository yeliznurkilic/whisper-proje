import random
import csv

random.seed(42)

TOPICS = {
    "teknik": [
        "sistem performansı arttırıldı",
        "teknik bir sorun çözüldü",
        "altyapı çalışmaları devam ediyor",
        "donanım kontrolü yapıldı",
        "ağ bağlantı problemleri giderildi",
        "sistem hatası analiz edildi",
        "teknik testler tamamlandı"
    ],
    "egitim": [
        "ders çalışıyorum",
        "sınava hazırlanıyorum",
        "konu tekrarları yaptım",
        "ödevlerimi tamamladım",
        "online eğitim izledim",
        "yeni bir konu öğrendim",
        "eğitim videosu izledim",
        "notlarımı gözden geçirdim",
        "öğretmenimiz konuyu anlattı",
        "kurs programı başladı"
    ],
    "gunluk": [
        "markete gittim",
        "arkadaşlarımla buluştum",
        "bugün çok yoruldum",
        "ev işleri yaptım",
        "yürüyüşe çıktım",
        "film izledim",
        "kahve içmeye gittik",
        "akşam yemeği yedim",
        "güzel bir gündü",
        "evde dinlendim"
    ],
    "hukuk": [
        "mahkeme kararı açıklandı",
        "dava süreci devam ediyor",
        "sözleşme maddeleri incelendi",
        "hukuki danışmanlık alındı",
        "kanun değişikliği yapıldı",
        "avukat ile görüşme yapıldı",
        "yasal süreç başlatıldı",
        "resmi belgeler imzalandı",
        "hukuki haklar konuşuldu",
        "dosya incelemesi yapıldı"
    ],
    "finans": [
        "bütçe planlaması yapıldı",
        "yatırım kararı alındı",
        "borsa bugün yükseldi",
        "döviz kurları değişti",
        "finansal rapor hazırlandı",
        "gelir gider hesaplandı",
        "ekonomik veriler açıklandı",
        "faiz oranları güncellendi",
        "hisse senedi alımı yapıldı",
        "piyasa dalgalıydı"
    ],
    "yazilim": [
        "log kayıtları incelendi",
        "veritabanı sorguları optimize edildi",
        "sunucu ayarları yapılandırıldı",
        "python ile kod yazdım",
        "api geliştirdim",
        "yazılım hatası çözdüm",
        "backend servisi yazıyorum",
        "fastapi projesi oluşturdum",
        "frontend tasarımı yaptım",
        "kod refactoring yaptım",
        "versiyon kontrol sistemi kullandım",
        "test kodları yazıldı"
    ],
    "saglik": [
        "doktor kontrolüne gittim",
        "sağlık raporu alındı",
        "tedavi süreci başladı",
        "ilaç kullanmam gerekiyor",
        "hastanede muayene oldum",
        "kan tahlili yapıldı",
        "sağlık durumu iyi",
        "diyet programına başladım",
        "fizik tedavi önerildi",
        "check up yaptırdım"
    ]
}

PREFIXES = [
    "bugün",
    "dün",
    "bu hafta",
    "son zamanlarda",
    "genelde",
    "çoğunlukla",
    ""
]

SUFFIXES = [
    "",
    "ve oldukça faydalıydı",
    "üzerinde çalışıyorum",
    "ile ilgiliydi",
    "beni epey meşgul etti",
    "hakkında bilgi aldım"
]

def generate_sentence(base):
    return f"{random.choice(PREFIXES)} {base} {random.choice(SUFFIXES)}".strip()

def generate_dataset(samples_per_topic=300, output_file="topic_data.csv"):
    rows = []

    for topic, sentences in TOPICS.items():
        for _ in range(samples_per_topic):
            base = random.choice(sentences)
            text = generate_sentence(base)
            rows.append([text, topic])

    random.shuffle(rows)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)

    print(f"✅ Veri seti olusturuldu: {output_file}")
    print(f"Toplam ornek sayisi: {len(rows)}")
    print("Konu dagilimi:")
    for k in TOPICS:
        print(f"- {k}: {samples_per_topic}")

if __name__ == "__main__":
    generate_dataset(samples_per_topic=300)

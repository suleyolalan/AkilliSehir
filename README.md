# Akıllı Şehir: İstanbul Airbnb Fiyat Tahmini ve Analizi

Bu proje, veri madenciliği yaşam döngüsünü kullanarak İstanbul'daki Airbnb ilanlarının fiyatlarını etkileyen unsurları analiz etmeyi ve tahminlemeyi amaçlar. Projede emeği geçenler:
* Fatma Zehra Ateş 230229082
* Münevver Şule Yolalan 210229014

## Proje Amacı
* Veri toplama ve ön işleme süreçlerini deneyimlemek.
* İstanbul özelinde semt bazlı fiyat analizi ve görselleştirme yapmak.
* Makine öğrenmesi modelleri ile fiyat tahmini gerçekleştirmek.

## Veri Seti
Veri Seti Notu: Projede kullanılan veri setleri (listings, calendar, reviews) dosya boyutları GitHub sınırlarını (100MB+) aştığı için depoya dahil edilmemiştir. Verilere Inside Airbnb üzerinden İstanbul şehri seçilerek ulaşılabilir.
Veriler [Inside Airbnb](http://insideairbnb.com/get-the-data/) üzerinden temin edilmiştir.
* -listings https://data.insideairbnb.com/turkey/marmara/istanbul/2025-09-29/data/listings.csv.gz
* -reviews https://data.insideairbnb.com/turkey/marmara/istanbul/2025-09-29/data/reviews.csv.gz
* -calendar https://data.insideairbnb.com/turkey/marmara/istanbul/2025-09-29/data/calendar.csv.gz

# Proje Gelişim Süreci

## 1. Veri Anlama ve Keşifsel Analiz (EDA)
Veri setinin genel yapısını anlamak ve model performansını etkileyebilecek gürültüleri saptamak amacıyla kapsamlı bir EDA süreci yürütülmüştür:

* Özellik Seçimi: Tahminleme başarısı için kritik olan 11 temel öznitelik (fiyat, konum, oda sayısı, puan vb.) filtrelenmiştir.  

* Aykırı Değer Analizi: İstatistiksel özetler sonucunda 4,4 milyon TL gibi hatalı uç değerler saptanmış ve verinin dağılımı görselleştirilmiştir.  

## 2. Veri Ön İşleme (Preprocessing)
Ham veriyi makine öğrenmesi modelleri için "altın standartta" bir veri setine dönüştürmek amacıyla şu adımlar uygulanmıştır:
* Temizlik: Fiyatı olmayan gözlemler silinmiş; modelin genelleme yeteneğini korumak adına finansal dalgalanmaları dengelemek için fiyatlar Dolar (USD) bazına çevrilmiş ve IQR yöntemiyle aykırı değerlerden arındırılmıştır.
* Eksik Veri Tamamlama: Eksik yatak, oda ve banyo bilgileri istatistiksel sapmayı önlemek amacıyla genel bir ortalama yerine, ilanların kendi konaklama kapasitesi gruplarının medyan değerlerine göre doldurulmuştur.
* Veri Dönüştürme: Metin tabanlı banyo bilgileri sayısal verilere (float) çevrilmiştir. Operasyonel kaldıraçlar olan anında rezervasyon ve süper ev sahibi alanlarındaki eksiklikler pazar gerçeklerine uygun olarak tamamlanmıştır.  

## 3. Özellik Mühendisliği ve Kodlama (Feature Engineering & Encoding)
Veri madenciliği derinliği kazandırmak amacıyla yeni değişkenler üretilmiştir:
* Coğrafi Analiz (Haversine): Her ilanın koordinat verileri kullanılarak İstanbul'un 3 ana merkez noktasına (Sultanahmet, Taksim, Levent) olan mesafesi kilometre bazında hesaplanmış ve öznitelik olarak eklenmiştir.

* Olanak Kodlama (Amenities): Metin bloklarından taranarak fiyata etki eden lüks ve konfor öznitelikleri (klima, havuz, otopark vb.) ikili (binary) değişkenlere dönüştürülmüştür.

* Mikro Konfor Oranları ve Kalite Skorları: Ev içi alan dağılımını ölçmek adına banyo/oda dengesi gibi oranlar önceden hesaplanmıştır. Ayrıca sektörel ağırlıklar dikkate alınarak (Banyo: 2.0, Yatak Odası: 1.5, Yatak: 0.5) evin toplam fiziksel donanım gücünü temsil eden "Sezgisel Oda Kalite Skoru" (room_quality_score) ve kişi başına düşen yatak oranı (beds_per_person) modele eklenmiştir.

* Kategorik Veri Kodlama: Çok fazla alt kategori barındıran semt sütunu, matris seyrekliğine ve overfitting'e yol açmaması için 5-Katlı Çapraz Çapraz Eşleştirme (5-Fold K-Fold Target Encoding) tekniği kullanılarak sızıntısız bir "Semt Fiyat Endeksi" yapısına dönüştürülmüştür. Kalan oda tipi ve operasyonel sütunlar için One-Hot Encoding uygulanarak 65 sütunluk modelleme matrisi elde edilmiştir.

## Zaman Serisi Entegrasyonu ve Hibrit Modelleme
* Hibrit Veri Hattı: Sadece fiziksel özelliklere odaklanan baz modellerin zamansal ve sezonsal dalgalanmaları ıskalamasını önlemek amacıyla projeye calendar.csv verileri entegre edilmiştir. Her bir ilanın geçmiş takvim verilerinden fiyat oynaklığı standart sapması (calendar_price_std) ve pazar talep yoğunluğu (occupancy_rate) hesaplanarak ana matrisle evlendirilmiştir.

* Model Yarışı (Benchmark): Veri seti %80 Eğitim ve %20 Test olarak bölünmüş, logaritmik dönüşüm uygulanarak CatBoost ve XGBoost algoritmaları yarıştırılmıştır. Yarış sonucunda XGBoost Hibrit Modeli %61.87 R² doğruluk skoru ve 16.13 USD Ortalama Mutlak Hata (MAE) ile şampiyon seçilmiştir.

# Arayüz Entegrasyonu

* Model ve Artıkların Kaydedilmesi: Şampiyon XGBoost modeli, canlı arayüzde semt isimlerini endekse çevirecek olan JSON sözlüğü ve matris sırasını koruyan sütun şablonu joblib ile diske kalıcı olarak kaydedilmiştir.

* Kullanıcı Arayüzü (Streamlit): Python tabanlı reaktif web mimarisi olan Streamlit kullanılarak app.py üzerinden interaktif bir yapay zeka fiyat danışmanı arayüzü kodlanmıştır.

* Piyasa Esneklik Payı Analizi: Canlı sistem, nokta tahmininin yanı sıra modelin test setinden elde edilen MAE hata payını (16.13 USD) esneklik payı olarak kullanır. Kullanıcıya pazar koşullarına göre güvenli bir alt ve üst fiyat sınırı hesaplar ve tüm çıktıları anlık döviz kuru üzerinden dinamik olarak TL karşılıklarına çevirir.

# Son Durum
Yönergedeki tüm çalışma takvimi, veri ön işleme, özellik mühendisliği, hibrit modelleme, algoritma yarışı ve canlı Streamlit web uygulaması entegrasyonu aşamaları başarıyla, uçtan uca tamamlanmıştır. Proje üretime ve canlı sunuma hazır durumdadır.

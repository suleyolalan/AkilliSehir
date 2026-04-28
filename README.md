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
* Ham veriyi makine öğrenmesi modelleri için "altın standartta" bir veri setine dönüştürmek amacıyla şu adımlar uygulanmıştır:
* Temizlik: Fiyatı olmayan gözlemler silinmiş; modelin genelleme yeteneğini korumak adına 15.000 TL üzerindeki aykırı değerler veri setinden arındırılmıştır.  
* Eksik Veri Tamamlama: Eksik yatak, oda ve banyo bilgileri istatistiksel sapmayı önlemek amacıyla medyan değerlerle doldurulmuştur.  
* Veri Dönüştürme: Metin tabanlı banyo bilgileri sayısal verilere (float) çevrilmiştir.  
* Sonuç: Modellemeye hazır 24.661 adet temizlenmiş ilan elde edilmiştir.  

## 3. Özellik Mühendisliği ve Kodlama (Feature Engineering & Encoding)
Veri madenciliği derinliği kazandırmak amacıyla yeni değişkenler üretilmiştir:
* Merkeze Uzaklık (Haversine): Her ilanın koordinat verileri kullanılarak İstanbul'un merkezi noktasına (Sultanahmet) olan mesafesi kilometre bazında hesaplanmış ve modele yeni bir öznitelik olarak eklenmiştir.  
* Kategorik Veri Kodlama: Semt ve Oda Tipi gibi metin verileri, One-Hot Encoding yöntemiyle (drop_first=True) sayısal matrislere dönüştürülmüştür.  

## Mevcut Durum
Yönergedeki çalışma takvimine göre Hafta Veri Ön İşleme ve Özellik Mühendisliği aşaması başarıyla tamamlanmıştır. Bir sonraki aşama olarak Modelleme ve Performans Analizi süreçlerine odaklanılacaktır.

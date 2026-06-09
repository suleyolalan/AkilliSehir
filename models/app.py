import streamlit as st
import joblib
import json
import numpy as np
import pandas as pd

# Web Sayfası Tasarım Ayarları
st.set_page_config(page_title="İstanbul Airbnb Fiyat Tahmin Sistemi", layout="centered")

# Başlık
st.markdown(
    """
    <h1 style='text-align: center; color: #1E3A8A; margin-bottom: 10px;'>
        🏙️ İstanbul Airbnb Yapay Zeka Fiyat Danışmanı
    </h1>
    """, 
    unsafe_allow_html=True
)
st.write("Evinizin fiziksel ve operasyonel özelliklerini girerek pazar analizi temelli fiyat tahminini anında alın.")
st.markdown("---")

# ==========================================
# 1. ARTIKLARIN (ARTIFACTS) HAFIZAYA YÜKLENMESİ
# ==========================================
@st.cache_resource # Sayfa her yenilendiğinde dosyaları tekrar yükleyip sistemi yavaşlatmasın diye kilitliyoruz
def load_assets():
    model = joblib.load('../models/champion_xgb_model.joblib')
    
    with open('../models/neighborhood_price_index.json', 'r', encoding='utf-8') as f:
        neighborhood_mapping = json.load(f)
        
    with open('../models/model_columns.json', 'r', encoding='utf-8') as f:
        model_columns = json.load(f)
        
    return model, neighborhood_mapping, model_columns

try:
    model, neighborhood_mapping, model_columns = load_assets()
    st.success("XGBoost Hibrit Yapay Zeka Modeli Başarıyla Yüklendi!")
except Exception as e:
    st.error(f"Model dosyaları yüklenemedi. Lütfen '../models/' klasörünü kontrol edin. Hata: {e}")
    st.stop()

# ==========================================
# 2. KULLANICI ARAYÜZÜ - VERİ GİRİŞ FORMU
# ==========================================
st.subheader("Evinizin Özellikleri")

col1, col2 = st.columns(2)

with col1:
    # Semt Seçimi (JSON sözlüğümüzdeki anahtarları doğrudan çekiyoruz)
    selected_neighborhood = st.selectbox("Evin Bulunduğu Semt:", sorted(list(neighborhood_mapping.keys())))
    room_type = st.selectbox("Oda Tipi:", ["Entire home/apt", "Private room", "Shared room", "Hotel room"])
    accommodates = st.number_input("Maksimum Konaklayacak Kişi Sayısı:", min_value=1, max_value=16, value=2)
    bedrooms = st.number_input("Yatak Odası Sayısı:", min_value=0, max_value=10, value=1)

with col2:
    bathrooms = st.number_input("Banyo Sayısı:", min_value=0.0, max_value=10.0, value=1.0, step=0.5)
    beds = st.number_input("Yatak Sayısı:", min_value=1, max_value=20, value=1)
    minimum_nights = st.number_input("Minimum Konaklama Gecesi:", min_value=1, max_value=365, value=1)

st.subheader(" Operasyonel ve Lüks Donanım Seçenekleri")
col3, col4 = st.columns(2)

with col3:
    host_is_superhost = st.checkbox("Süper Ev Sahibi (Superhost) Misiniz?")
    instant_bookable = st.checkbox("Anında Rezervasyon (Instant Bookable) Açık Mı?")
    has_air_con = st.checkbox("Klima Var Mı?")

with col4:
    has_pool = st.checkbox("Yüzme Havuzu Var Mı?")
    has_luxury = st.checkbox("Lüks Donanım (Jakuzi, Sauna, Hot Tub) Var Mı?")
    has_parking = st.checkbox("Otopark Alanı Var Mı?")

# Coğrafi Mesafeler İçin Simüle Edilmiş Sabitler (Canlıda haritadan veya API'den alınabilir, şimdilik ortalama veriyoruz)
# Modelin hata almaması için bu 3 GIS özelliğini de şablon gereği beslemeliyiz
dist_sultanahmet = 5.0
dist_taksim = 4.5
dist_levent = 6.0

# ==========================================
# 3. ÖZNİTELİK MÜHENDİSLİĞİ (YENİ SÜTUNLARIN CANLI HESAPLANMASI)
# ==========================================
if st.button("Gecelik Fiyatı Tahmin Et", use_container_width=True):
    
    # Aşama 4'teki mikro oranların canlı simülasyonu
    bathrooms_per_bedroom = bathrooms / (bedrooms + 1)
    accommodates_per_room = accommodates / (bedrooms + 1)
    beds_per_bedroom = beds / (bedrooms + 1)
    
    # Aşama 4.5'teki kalite skorlarının canlı simülasyonu
    beds_per_person = beds / (accommodates + 1)
    room_quality_score = (bedrooms * 1.5) + (bathrooms * 2.0) + (beds * 0.5)
    
    # Kullanıcının seçtiği semtin JSON'dan sayısal endeks karşılığını buluyoruz
    neighbourhood_price_index = neighborhood_mapping[selected_neighborhood]
    
    # Aşama 6'daki zaman serisi (Calendar) medyan dinamik değerleri
    # Yeni bir ev ilanının başlangıçtaki pazar tahmini için pazar genel ortalamalarını bağlıyoruz
    calendar_price_std = 12.5  
    occupancy_rate = 0.65     

    # Boş bir veri satırı oluşturup eğitime giren tüm 65 sütunu sıfırla ayağa kaldırıyoruz
    input_data = pd.DataFrame(0, index=[0], columns=model_columns)
    
    # Sürekli (sayısal) sütunları doğrudan yerleştiriyoruz
    input_data['accommodates'] = float(accommodates)
    input_data['bedrooms'] = float(bedrooms)
    input_data['beds'] = float(beds)
    input_data['minimum_nights'] = float(minimum_nights)
    input_data['bathrooms'] = float(bathrooms)
    input_data['dist_sultanahmet'] = float(dist_sultanahmet)
    input_data['dist_taksim'] = float(dist_taksim)
    input_data['dist_levent'] = float(dist_levent)
    input_data['has_air_con'] = int(has_air_con)
    input_data['has_pool'] = int(has_pool)
    input_data['has_luxury'] = int(has_luxury)
    input_data['has_parking'] = int(has_parking)
    input_data['bathrooms_per_bedroom'] = float(bathrooms_per_bedroom)
    input_data['accommodates_per_room'] = float(accommodates_per_room)
    input_data['beds_per_bedroom'] = float(beds_per_bedroom)
    input_data['neighbourhood_price_index'] = float(neighbourhood_price_index)
    input_data['beds_per_person'] = float(beds_per_person)
    input_data['room_quality_score'] = float(room_quality_score)
    input_data['calendar_price_std'] = float(calendar_price_std)
    input_data['occupancy_rate'] = float(occupancy_rate)

    # One-Hot Encoded (Kategorik) sütunların aktif edilmesi
    # Seçilen semt dummie başlığını tetikliyoruz
    neighborhood_col = f"neighbourhood_cleansed_{selected_neighborhood}"
    if neighborhood_col in input_data.columns:
        input_data[neighborhood_col] = 1
        
    # Seçilen oda tipi dummie başlığını tetikliyoruz
    room_col = f"room_type_{room_type}"
    if room_col in input_data.columns:
        input_data[room_col] = 1
        
    # Operasyonel dummielerin tetiklenmesi ('t' durumu aktifse dummie 1 olur)
    if instant_bookable:
        if "instant_bookable_t" in input_data.columns: input_data["instant_bookable_t"] = 1
    if host_is_superhost:
        if "host_is_superhost_t" in input_data.columns: input_data["host_is_superhost_t"] = 1

    # ==========================================
    # 4. TAHMİN VE ESNEKLİK PAYININ (MAE) HESAPLANMASI
    # ==========================================
    # Model log dünyasında eğitildiği için tahmini alıp expm1 ile dolara çeviriyoruz
    prediction_log = model.predict(input_data)[0]
    predicted_price_usd = np.expm1(prediction_log)
    
    # Aşama 6'da elde ettiğimiz gerçek test seti hata payımız (MAE)
    mae_usd = 16.13 
    
    # Esneklik sınırlarının hesaplanması (Taban fiyatın sıfırın altına düşmesini engelliyoruz)
    lower_bound_usd = max(5.0, predicted_price_usd - mae_usd)
    upper_bound_usd = predicted_price_usd + mae_usd
    
    # Güncel döviz kuru üzerinden TL karşılıklarının hesaplanması
    exchange_rate = 45.42
    predicted_price_tl = predicted_price_usd * exchange_rate
    lower_bound_tl = lower_bound_usd * exchange_rate
    upper_bound_tl = upper_bound_usd * exchange_rate

    # ==========================================
    # 5. SONUÇLARIN EKRANA BASILMASI
    # ==========================================
    st.markdown("---")
    st.subheader("Yapay Zeka Fiyat Analiz Raporu")
    
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric(label="Önerilen Optimal Fiyat (Gecelik)", value=f"{predicted_price_tl:,.2f} TL", delta=f"{predicted_price_usd:.2f} USD")
    with metric_col2:
        st.metric(label="Model Güvenilirliği (R² Skoru)", value="%61.87", delta="Yüksek Hassasiyet", delta_color="normal")
        
    st.warning(
        f"**Piyasa Esneklik Payı Analizi:** İstanbul Airbnb pazarındaki anlık talep, sezon dalgalanmaları ve "
        f"gerçek test seti hata payı (`MAE = 16.13 USD`) göz önüne alındığında; bu mülk için belirlenebilecek "
        f"**güvenli fiyat aralığı {lower_bound_tl:,.2f} TL ile {upper_bound_tl:,.2f} TL ({lower_bound_usd:.2f} USD - {upper_bound_usd:.2f} USD)** arasındadır. "
        f"Yoğun sezonlarda üst sınıra, düşük talep dönemlerinde ise alt sınıra yaklaşmanız önerilir."
    )
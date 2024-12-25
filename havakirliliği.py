import requests
import sqlite3

# OpenWeatherMap API anahtarınızı buraya yapıştırın
api_key = "7a89ed2ef4f92ba417c9" # Kendi kullandığınız API anahtarınızı yapıştırın

# İstediğiniz şehri buraya girin (örneğin Ankara)
city_name = "Ankara"

# Hava durumu verileri için API URL'si
weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"

# Hava durumu verilerini alma
response = requests.get(weather_url)
weather_data = response.json()

# API yanıtını kontrol et
if weather_data.get("cod") != 200:
    print(f"Hata: {weather_data.get('message', 'Bilinmeyen bir hata oluştu')}")
else:
    main_data = weather_data["main"]
    weather_desc = weather_data["weather"][0]["description"]
    temperature = main_data["temp"]
    humidity = main_data["humidity"]
    pressure = main_data["pressure"]

    print(f"Şehir: {city_name}")
    print(f"Sıcaklık: {temperature}°C")
    print(f"Nem: {humidity}%")
    print(f"Basınç: {pressure} hPa")
    print(f"Hava Durumu: {weather_desc}")

    # Hava kirliliği verileri için koordinatları al
    lat = weather_data['coord']['lat']
    lon = weather_data['coord']['lon']

    # Hava kirliliği verileri için API URL'si
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    # Hava kirliliği verilerini alma
    response_pollution = requests.get(pollution_url)
    pollution_data = response_pollution.json()

    if "list" in pollution_data and len(pollution_data["list"]) > 0:
        air_quality_index = pollution_data['list'][0]['main']['aqi']
        print(f"Hava Kalitesi İndeksi (AQI): {air_quality_index}")

        # AQI'ye göre uyarı mesajı
        if air_quality_index <= 50:
            alert_message = "Hava kalitesi iyi. Uyarı gerekmez."
        elif 51 <= air_quality_index <= 100:
            alert_message = "Dikkat: Hava kalitesi orta seviyede. Hassas gruplar için uyarı yapılmalıdır."
        elif 101 <= air_quality_index <= 150:
            alert_message = "Uyarı: Hava kalitesi sağlıksız. Hassas gruplar için dikkatli olunmalı."
        elif 151 <= air_quality_index <= 200:
            alert_message = "Uyarı: Hava kalitesi sağlıksız. Genel halk için de uyarı yapılmalıdır."
        elif 201 <= air_quality_index <= 300:
            alert_message = "Dikkat: Hava kalitesi çok sağlıksız. Tüm halk için uyarı yapılmalı."
        else:
            alert_message = "Acil durum: Hava kalitesi tehlikeli. Açık hava faaliyetlerinden kaçınılmalıdır."

        print(alert_message)

        # Veritabanı bağlantısı
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()

        # Tablo oluşturma (eğer tablo yoksa)
        cursor.execute('''CREATE TABLE IF NOT EXISTS Weather (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          city TEXT,
                          temperature REAL,
                          humidity REAL,
                          pressure REAL,
                          description TEXT,
                          air_quality_index INTEGER)''')

        # Verileri tabloya ekleme
        cursor.execute('''INSERT INTO Weather (city, temperature, humidity, pressure, description, air_quality_index)
                          VALUES (?, ?, ?, ?, ?, ?)''', (city_name, temperature, humidity, pressure, weather_desc, air_quality_index))

        # Değişiklikleri kaydet ve bağlantıyı kapat
        conn.commit()
        conn.close()

        # Veritabanını kontrol etme ve kaydedilen verileri gösterme
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Weather')
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        conn.close()
    else:
        print("Hata: Hava kirliliği verileri alınamadı.")

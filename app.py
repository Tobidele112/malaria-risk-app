import streamlit as st
import requests
import pandas as pd
import numpy as np
import os

# 🔑 Secure API key
API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="Malaria Risk AI System", page_icon="🦟", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.big-title {font-size:40px; font-weight:bold; color:#1f77b4;}
.high {color:red; font-size:22px;}
.medium {color:orange; font-size:22px;}
.low {color:green; font-size:22px;}
.card {
    padding:15px;
    border-radius:10px;
    background-color:#f5f5f5;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🦟 Malaria Risk AI System (Nigeria)</div>", unsafe_allow_html=True)

# ---------------- CITIES ----------------
cities_data = {
    "Ibadan": [7.3775, 3.9470],
    "Lagos": [6.5244, 3.3792],
    "Abuja": [9.0765, 7.3986],
    "Kano": [12.0022, 8.5919],
    "Port Harcourt": [4.8156, 7.0498],
    "Enugu": [6.5244, 7.5086],
    "Kaduna": [10.5105, 7.4165]
}

# ---------------- WEATHER ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},NG&appid={API_KEY}&units=metric"
    r = requests.get(url)

    if r.status_code == 200:
        d = r.json()
        temp = d["main"]["temp"]
        humidity = d["main"]["humidity"]
        rain = d.get("rain", {}).get("1h", 0)
        return temp, humidity, rain
    else:
        return None, None, None

# ---------------- AI PREDICTION ----------------
def ai_predict(temp, humidity, rain):
    score = (temp * 0.3) + (humidity * 0.4) + (rain * 5)

    if score > 60:
        return "High", 3
    elif score > 40:
        return "Medium", 2
    else:
        return "Low", 1

# ---------------- HEALTH ADVICE ----------------
def advice(level):
    if level == "High":
        return [
            "Use mosquito net",
            "Apply insect repellent",
            "Avoid stagnant water",
            "Seek medical test if fever occurs"
        ]
    elif level == "Medium":
        return [
            "Sleep under mosquito net",
            "Keep environment clean",
            "Watch for malaria symptoms"
        ]
    else:
        return [
            "Maintain good hygiene",
            "Stay informed",
            "Low risk but stay cautious"
        ]

# ---------------- USER INPUT ----------------
st.subheader("📍 Check Your City Risk")

city = st.selectbox("Select City", list(cities_data.keys()))

if st.button("Check Risk"):
    temp, humidity, rain = get_weather(city)

    if temp is not None:
        level, val = ai_predict(temp, humidity, rain)

        st.markdown(f"<div class='card'>🌡 Temp: {temp} °C<br>💧 Humidity: {humidity}%<br>🌧 Rain: {rain} mm</div>", unsafe_allow_html=True)

        if level == "High":
            st.markdown("<div class='high'>🔴 HIGH RISK</div>", unsafe_allow_html=True)
        elif level == "Medium":
            st.markdown("<div class='medium'>🟡 MEDIUM RISK</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='low'>🟢 LOW RISK</div>", unsafe_allow_html=True)

        st.subheader("💡 Health Advice")
        for tip in advice(level):
            st.write("✔️", tip)
    else:
        st.error("Could not fetch weather data")

# ---------------- MAP ----------------
st.subheader("🗺️ Nigeria Malaria Risk Map")

data = []

for city, coord in cities_data.items():
    temp, humidity, rain = get_weather(city)

    if temp is not None:
        level, val = ai_predict(temp, humidity, rain)

        data.append({
            "city": city,
            "lat": coord[0],
            "lon": coord[1],
            "risk": level
        })

df = pd.DataFrame(data)

if not df.empty:
    st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}))
else:
    st.warning("No data available")

# ---------------- LIVE LOCATION ----------------
st.subheader("🌍 Check Your Current Location")

user_city = st.text_input("Enter your city (e.g., Abuja)")

if st.button("Check My Location Risk"):
    temp, humidity, rain = get_weather(user_city)

    if temp is not None:
        level, _ = ai_predict(temp, humidity, rain)
        st.success(f"{user_city} Risk Level: {level}")
    else:
        st.error("City not found")

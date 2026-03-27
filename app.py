import streamlit as st
import requests
import pandas as pd
import numpy as np

# 🔑 API KEY
import os
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
        return d["main"]["temp"], d["main"]["humidity"], d.get("rain", {}).get("1h", 0)
    return None, None, None

# ---------------- AI MODEL (simple) ----------------
def ai_predict(temp, humidity, rain):
    # Simple weighted prediction
    score = (temp * 0.3) + (humidity * 0.4) + (rain * 5)

    if score > 60:
        return "High", 3
    elif score > 40:
        return "Medium", 2
    else:
        return "Low", 1

# ---------------- ADVICE ----------------
def advice(level):
    if level == "High":
        return ["Use mosquito net", "Apply repellent", "Avoid stagnant water", "Seek test if fever"]
    elif level == "Medium":
        return ["Sleep under net", "Keep environment clean", "Monitor symptoms"]
    else:
        return ["Maintain hygiene", "Stay cautious"]

# ---------------- USER SECTION ----------------
st.subheader("📍 Check Your Location Risk")

city = st.selectbox("Select City", list(cities_data.keys()))

if st.button("Check My Risk"):
    temp, humidity, rain = get_weather(city)

    if temp:
        level, val = ai_predict(temp, humidity, rain)

        st.markdown(f"<div class='card'>🌡 Temp: {temp} °C<br>💧 Humidity: {humidity}%<br>🌧 Rain: {rain} mm</div>", unsafe_allow_html=True)

        if level == "High":
            st.markdown(f"<div class='high'>🔴 HIGH RISK</div>", unsafe_allow_html=True)
        elif level == "Medium":
            st.markdown(f"<div class='medium'>🟡 MEDIUM RISK</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='low'>🟢 LOW RISK</div>", unsafe_allow_html=True)

        st.subheader("💡 Health Advice")
        for tip in advice(level):
            st.write("✔️", tip)

# ---------------- MAP DATA ----------------
data = []

for city, coord in cities_data.items():
    temp, humidity, rain = get_weather(city)
    if temp:
        level, val = ai_predict(temp, humidity, rain)

        color = "green"
        if level == "High":
            color = "red"
        elif level == "Medium":
            color = "orange"

        data.append({
            "city": city,
            "lat": coord[0],
            "lon": coord[1],
            "risk": level,
            "color": color,
            "size": val * 50
        })

df = pd.DataFrame(data)

# ---------------- MAP ----------------
st.subheader("🗺️ Nigeria Malaria Risk Map")

if not df.empty:
    st.map(df.rename(columns={"lat":"latitude","lon":"longitude"}))
else:
    st.error("No data available")

# ---------------- LIVE LOCATION ----------------
st.subheader("🌍 Use Your Current Location")

st.info("Copy your city name from Google Maps and paste below")

user_city = st.text_input("Enter your current city manually")

if st.button("Check Live Location Risk"):
    temp, humidity, rain = get_weather(user_city)

    if temp:
        level, _ = ai_predict(temp, humidity, rain)
        st.success(f"{user_city} Risk Level: {level}")
    else:
        st.error("Could not detect location")

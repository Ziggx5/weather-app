import requests
import json
from customtkinter import *
from PIL import *
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import sys

# --- path finding ---
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

favourites_path = os.path.join(base_path, "favourites.json")

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

# --- load every picture and json file ---
if not os.path.exists(favourites_path):
    with open (favourites_path, "w") as f:
        json.dump([], f)

star_path = os.path.join(base_path, "images", "star.png")
star2_path = os.path.join(base_path, "images", "star2.png")
app_icon_path = os.path.join(base_path, "images", "weather_icon.ico")
search_image_path = os.path.join(base_path, "images", "search_icon.png")
sunrise_image_path = os.path.join(base_path, "images", "sunrise.png")
sunset_image_path = os.path.join(base_path, "images", "sunset.png")

# --- App config ---
app = CTk()
app.geometry("800x700")
app.title("Weather")
app.iconphoto(True, ImageTk.PhotoImage(file = app_icon_path))
app.configure(fg_color = "#242424")
app.resizable(False, False)

# --- Frame for favourite places ---
favourite_frame = CTkFrame(app, fg_color = "transparent", width = 225, height = 650, border_color = "#333333", border_width = 1)
favourite_frame.grid_propagate(False)
favourite_frame.place(x = 0, y = 70, relheight = 1, relwidth = 0.28)

# --- Frame for search bar and search button ---
search_frame = CTkFrame(app, fg_color = "transparent")
search_frame.place(x = 10, y = 10)

def load_favourites():
    try:
        with open (favourites_path, "r") as f:
            return json.load(f)
    except:
        return []

favourites = load_favourites()

def save_favourites(favourites):
    with open (favourites_path, "w") as f:
        json.dump(favourites, f, indent = 4)

def toggle_favourite(place):
    if not place:
        status_label.configure(text = "No place selected yet.")
        return
    if place in favourites:
        favourites.remove(place)
        save_favourites(favourites)
        star_image = Image.open(star_path)
        favourite_button.configure(image = CTkImage(light_image = star_image, dark_image = star_image))
        status_label.configure(text = "")

    else:
        favourites.append(place)
        save_favourites(favourites)
        star2_image = Image.open(star2_path)
        favourite_button.configure(image = CTkImage(light_image = star2_image, dark_image = star2_image))
        status_label.configure(text = "")
    update_favourite_list()

def update_favourite_list():
    for widget in favourite_frame.winfo_children():
        widget.destroy()
    
    for place in favourites:
        try:
            cords_url = f"http://api.openweathermap.org/geo/1.0/direct?q={place}&limit=1&appid={api_key}"
            response1 = requests.get(cords_url)
            data1 = response1.json()
            if not data1:
                temp_text = "N/A"
            else:
                lat = data1[0]["lat"]
                lon = data1[0]["lon"]
                weather_data_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
                response2 = requests.get(weather_data_url)
                if response2.status_code == 200:
                    data2 = response2.json()
                    temperature = int(data2["main"]["temp"])
                    temp_text = f"{temperature} °C"
                else:
                    temp_text = "N/A"
        except:
            temp_text = "N/A"

        btn = CTkButton(favourite_frame, text = f"{place} | {temp_text}", fg_color = "#2f2f2f", border_width= 2, corner_radius = 5, height = 40, font = ("Segoe UI", 20), border_color= "#333333", command = lambda p = place: search_by_name(p))
        btn.pack(pady = 5, padx = 5, fill = "x")

update_favourite_list()

def search_by_name(place_name):
    search_bar.delete(0, "end")
    search_bar.insert(0, place_name)
    search_handler()

def search_handler():
    search_bar_entry = search_bar.get().strip()
    if search_bar_entry == "":
        status_label.configure(text = "Empty input")
        return

    cords_url = f"http://api.openweathermap.org/geo/1.0/direct?q={search_bar_entry}&limit=1&appid={api_key}"
    response1 = requests.get(cords_url)

    # --- get coordinates ---
    if response1.status_code == 200:
        data1 = response1.json()
        if data1:
            status_label.configure(text = "")
            lat = data1[0]["lat"]
            lon = data1[0]["lon"]
            
            # --- Get weather and forecast info ---
            weather_data_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
            response2 = requests.get(weather_data_url)
            if response2.status_code == 200:
                status_label.configure(text = "")
                data2 = response2.json()
                temperature = int(data2["main"]["temp"])
                feels_like = int(data2["main"]["feels_like"])
                description = data2["weather"][0]["description"]
                humidity = data2["main"]["humidity"]
                sunrise_unix_timestamp = data2["sys"]["sunrise"]
                sunset_unix_timestamp = data2["sys"]["sunset"]
                timezone_offset = data2["timezone"]

                sunrise = (datetime.fromtimestamp(sunrise_unix_timestamp, tz = timezone.utc) + timedelta(seconds = timezone_offset))
                sunrise = sunrise.strftime("%H:%M")
                sunset = (datetime.fromtimestamp(sunset_unix_timestamp, tz = timezone.utc) + timedelta(seconds = timezone_offset))
                sunset = sunset.strftime("%H:%M")

                # --- looking for rain ---
                if "rain" in data2:
                    precipitation = data2["rain"]["1h"]
                else:
                    precipitation = 0

                # --- Looking for english name ---
                if "local_names" in data1[0]:
                    if "en" in data1[0]["local_names"]:
                        place_name = data1[0]["local_names"]["en"]
                    else:
                        place_name = data1[0]["name"]
                else:
                    place_name = data1[0]["name"]
                
                # --- Temperature color ---
                if temperature <= -10:
                    temp_color = "#2196F3"
                elif -10 < temperature <= 0:
                    temp_color = "#4FC3F7"
                elif 0 < temperature <= 10:
                    temp_color = "#81D4FA"
                elif 10 < temperature <= 20:
                    temp_color = "#FFF176"
                elif 20 < temperature <= 30:
                    temp_color = "#FFB74D"
                else:
                    temp_color = "#FF7043"
                
                if place_name in favourites:
                    star2_image = Image.open(star2_path)
                    favourite_button.configure(image = CTkImage(light_image = star2_image, dark_image = star2_image))
                else:
                    star_image = Image.open(star_path)
                    favourite_button.configure(image = CTkImage(light_image = star_image, dark_image = star_image))

                place_name_label.configure(text = place_name)
                temperature_label.configure(text = str(temperature) + "°", text_color = temp_color)
                description_label.configure(text = description+ " | Feels like: " + str(feels_like) + "°")
                humidity_percentage.configure(text = str(humidity) + " %")
                precipitation_measure.configure(text = str(precipitation) + " mm")
                sunrise_time.configure(text = str(sunrise))
                sunset_time.configure(text = str(sunset))

            else:
                print("Error getting weather info", response2.status_code, response2.text)
                status_label.configure(text = "Error getting weather info" + response2.status_code + response2.text)
        else:
            status_label.configure(text = "Place not found.")
    else:
        status_label.configure(text = "Error:" + response1.status_code + response1.text)
    search_bar.delete(0, "end")

# --- favourite button ---
star_image = Image.open(star_path)
favourite_button = CTkButton(app, text = "", image = CTkImage(light_image = star_image, dark_image = star_image), width = 30, height = 30, fg_color = "white", command = lambda: toggle_favourite(place_name_label.cget("text")))
favourite_button.place(x = 727.5, y = 40)

# --- Search button ---
search_image = Image.open(search_image_path)
search_button = CTkButton(search_frame, image = CTkImage(dark_image = search_image, light_image = search_image), text = "", width = 30, height = 30, fg_color = "white", corner_radius = 20, border_width = 0, command = search_handler)
search_button.pack(side = "right")

# --- Search bar ---
search_bar = CTkEntry(search_frame, placeholder_text = "Search", width = 150, height = 30, corner_radius = 20, border_width = 0)
search_bar.pack(side = "left", padx = (0, 10))
search_bar.bind("<Return>", lambda event: search_handler())

# --- status placeholder ---
status_label = CTkLabel(app, text = "", font = ("Segoe UI", 15), text_color = "#f71616")
status_label.place(x = 10, y = 40)

# --- Place name placeholder ---
place_name_label = CTkLabel(app, text = "", font = ("Segoe UI", 40))
place_name_label.place(x = 512.5, y = 100, anchor = "center")

# --- Temperature placeholder ---
temperature_label = CTkLabel(app, text = "", font = ("Segoe UI", 60))
temperature_label.place(x = 512.5, y = 170, anchor = "center")

# --- Description placeholder ---
description_label = CTkLabel(app, text = "", font = ("Segoe UI", 20))
description_label.place(x = 512.5, y = 230, anchor = "center")

# --- Humidity ---
humidity_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
humidity_frame.place(x = 267.5, y = 270)
humidity_frame.grid_propagate(False)
humidity_frame.grid_columnconfigure(0, weight = 1)
humidity_frame.grid_rowconfigure((0, 1, 2), weight = 1)

humidity_label = CTkLabel(humidity_frame, text = "Humidity", font = ("Segoe UI", 23))
humidity_label.grid(row = 0, column = 0)
humidity_percentage = CTkLabel(humidity_frame, text = "%", font = ("Segoe UI", 26))
humidity_percentage.grid(row = 1, column = 0)

# --- precipitation ---
precipitation_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
precipitation_frame.place(x = 437.5, y = 270)
precipitation_frame.grid_propagate(False)
precipitation_frame.grid_columnconfigure(0, weight = 1)
precipitation_frame.grid_rowconfigure((0, 1, 2), weight = 1)

precipitation_label = CTkLabel(precipitation_frame, text = "Precipitation", font = ("Segoe UI", 23))
precipitation_label.grid(row = 0, column = 0)

precipitation_measure = CTkLabel(precipitation_frame, text = "mm", font = ("Segoe UI", 26))
precipitation_measure.grid(row = 1, column = 0)

# --- Sunrise and sunset ---
sunrise_image = Image.open(sunrise_image_path)
sunset_image = Image.open(sunset_image_path)

sunrise_sunset_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
sunrise_sunset_frame.place(x = 607.5, y = 270)
sunrise_sunset_frame.grid_propagate(False)
sunrise_sunset_frame.grid_columnconfigure(0, weight = 1)
sunrise_sunset_frame.grid_rowconfigure((0, 1, 2, 3), weight = 1)

sunrise_label = CTkLabel(sunrise_sunset_frame, image = CTkImage(light_image = sunrise_image, dark_image = sunrise_image, size = (30, 30)), text = "")
sunrise_label.grid(row = 0, column = 0)
sunrise_time = CTkLabel(sunrise_sunset_frame, text = "Sunrise time", font = ("Segoe UI", 20))
sunrise_time.grid(row = 1, column = 0)

sunset_label = CTkLabel(sunrise_sunset_frame, image = CTkImage(light_image = sunset_image, dark_image = sunset_image, size = (30, 30)), text = "")
sunset_label.grid(row = 2, column = 0)
sunset_time = CTkLabel(sunrise_sunset_frame, text = "Sunset time", font = ("Segoe UI", 20))
sunset_time.grid(row = 3, column = 0)

app.mainloop()

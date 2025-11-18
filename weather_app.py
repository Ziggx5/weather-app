#Copyright © 2025 Maj Sedonja
#Licensed under the MIT License. See LICENSE file for details.
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
app_icon_path = os.path.join(base_path, "images", "weather_icon.ico")
arrow_image_path = os.path.join(base_path, "images", "arrow.png")
load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

# --- json file ---
if not os.path.exists(favourites_path):
    with open (favourites_path, "w") as f:
        json.dump([], f)

images_path = os.path.join(base_path, "images")
images = {}
for file_name in os.listdir(images_path):
    filepath = os.path.join(images_path, file_name)
    open_image = Image.open(filepath)
    if "search_icon.png" in file_name or "star.png" in file_name or "star2.png" in file_name or "refresh.png" in file_name:
        images[file_name] = CTkImage(light_image = open_image, dark_image = open_image, size = (20, 20))
    elif "precipitation.png" in file_name:
        images[file_name] = CTkImage(light_image = open_image, dark_image = open_image, size = (60, 60))
    else:
        images[file_name] = CTkImage(light_image = open_image, dark_image = open_image, size = (40, 40))

# --- App config ---
app = CTk()
app.geometry("800x700")
app.title("Weather")
app.iconphoto(True, ImageTk.PhotoImage(file = app_icon_path))
app.configure(fg_color = "#242424")
app.resizable(False, False)

# --- Frame for favourite places ---
favourite_frame = CTkFrame(app, fg_color = "transparent", border_color = "#3a3a3a", border_width = 2)
favourite_frame.grid_propagate(False)
favourite_frame.place(x = 0, y = 70, relheight = 0.75, relwidth = 0.28)

# --- Frame for search bar and search button ---
search_frame = CTkFrame(app, fg_color = "transparent")
search_frame.place(x = 10, y = 10)

# --- status placeholder ---
status_label = CTkLabel(app, text = "", font = ("Segoe UI", 15), text_color = "#f71616")
status_label.place(x = 10, y = 40)

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
        favourite_button.configure(image = images["star.png"])
        status_label.configure(text = "")

    else:
        favourites.append(place)
        save_favourites(favourites)
        favourite_button.configure(image = images["star2.png"])
        status_label.configure(text = "")
    update_favourite_list()

def update_favourite_list():
    for widget in favourite_frame.winfo_children():
        widget.destroy()
    
    for place in favourites:
        if len(place) > 10:
            place_text = place[:10] + "..."
        else:
            place_text = place

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
                    if units_switch.get() == 1:
                        temp_text = f"{temperature}°"
                    else:
                        temperature_fahrenheit = (temperature * 1.8) + 32
                        temp_text = f"{temperature_fahrenheit}°F"
                else:
                    temp_text = "N/A"
        except Exception as e:
            status_label.configure(text = f"Favourite list update error: {e}")
            temp_text = "N/A"

        favourite_buttons = CTkButton(favourite_frame, text = f"{place_text} | {temp_text}", fg_color = "#2f2f2f", border_width= 2, corner_radius = 5, height = 40, font = ("Segoe UI", 20), border_color= "#333333", hover_color = "gray", command = lambda p = place: search_by_name(p))
        favourite_buttons.pack(pady = 5, padx = 5, fill = "x")

def refresh():
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
                if units_switch.get() == 1:
                    
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

                    temperature_label.configure(text = str(temperature) + "°", text_color = temp_color)
                    description_label.configure(text = description + " | Feels like: " + str(feels_like) + "°")
                else:
                    temperature_fahrenheit = (temperature * 1.8) + 32
                    feels_like_fahrenheit = (feels_like * 1.8) + 32
                    if temperature_fahrenheit <= 14:
                        temp_color = "#2196F3"
                    elif 14 < temperature_fahrenheit <= 32:
                        temp_color = "#4FC3F7"
                    elif 32 < temperature_fahrenheit <= 50:
                        temp_color = "#81D4FA"
                    elif 50 < temperature_fahrenheit <= 68:
                        temp_color = "#FFF176"
                    elif 68 < temperature_fahrenheit <= 86:
                        temp_color = "#FFB74D"
                    else:
                        temp_color = "#FF7043"

                    temperature_label.configure(text = str(temperature_fahrenheit) + "°F", text_color = temp_color)
                    description_label.configure(text = description + " | Feels like: " + str(feels_like_fahrenheit) + "°F")

                humidity = data2["main"]["humidity"]
                sunrise_unix_timestamp = data2["sys"]["sunrise"]
                sunset_unix_timestamp = data2["sys"]["sunset"]
                timezone_offset = data2["timezone"]
                wind_speed = data2["wind"]["speed"]
                wind_degrees = data2["wind"]["deg"]
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
                
                if place_name in favourites:
                    favourite_button.configure(image = images["star2.png"])
                else:
                    favourite_button.configure(image = images["star.png"])

                place_name_label.configure(text = place_name)
                humidity_percentage.configure(text = str(humidity) + "%")
                precipitation_measure.configure(text = str(precipitation) + "mm")
                sunrise_time.configure(text = str(sunrise))
                sunset_time.configure(text = str(sunset))
                wind_speed_label.configure(text = str(wind_speed) + "km/h")
                wind_degrees_label.configure(text = str(wind_degrees) + "°")
                rotate_arrow = arrow_image.rotate(-wind_degrees + 180)
                rotated_arrow = CTkImage(light_image = rotate_arrow, dark_image = rotate_arrow, size = (80, 80))
                wind_arrow.configure(image = rotated_arrow)
                
            else:
                print("Error getting weather info", response2.status_code, response2.text)
                status_label.configure(text = "Error getting weather info" + response2.status_code + response2.text)
        else:
            status_label.configure(text = "Place not found.")
    else:
        status_label.configure(text = "Error:" + response1.status_code + response1.text)

# --- favourite button ---
favourite_button = CTkButton(app, text = "", image = images["star.png"], width = 30, height = 30, fg_color = "white", command = lambda: toggle_favourite(place_name_label.cget("text")), hover_color = "gray")
favourite_button.place(x = 727.5, y = 40)

# --- Search button ---
search_button = CTkButton(search_frame, image = images["search_icon.png"], text = "", width = 30, height = 30, fg_color = "white", corner_radius = 20, border_width = 0, command = search_handler, hover_color = "gray")
search_button.pack(side = "right")

# --- Search bar ---
search_bar = CTkEntry(search_frame, placeholder_text = "Search", width = 150, height = 30, corner_radius = 20, border_width = 0)
search_bar.pack(side = "left", padx = (0, 10))
search_bar.bind("<Return>", lambda event: search_handler())

# --- Refresh button ---
refresh_button = CTkButton(app, image = images["refresh.png"], text = "", width = 30, height = 30, fg_color = "white", hover_color = "gray",command = lambda: refresh())
refresh_button.place(x = 230, y = 71)

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

humidity_label = CTkLabel(humidity_frame, image = images["humidity.png"], text = "")
humidity_label.grid(row = 0, column = 0)
humidity_percentage = CTkLabel(humidity_frame, text = "%", font = ("Segoe UI", 30))
humidity_percentage.grid(row = 1, column = 0, pady = (0, 30))

# --- precipitation ---
precipitation_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
precipitation_frame.place(x = 437.5, y = 270)
precipitation_frame.grid_propagate(False)
precipitation_frame.grid_columnconfigure(0, weight = 1)
precipitation_frame.grid_rowconfigure((0, 1, 2), weight = 1)

precipitation_label = CTkLabel(precipitation_frame, image = images["precipitation.png"], text = "", font = ("Segoe UI", 23))
precipitation_label.grid(row = 0, column = 0)

precipitation_measure = CTkLabel(precipitation_frame, text = "mm", font = ("Segoe UI", 30))
precipitation_measure.grid(row = 1, column = 0, pady = (0, 40))

# --- Sunrise and sunset ---
sunrise_sunset_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
sunrise_sunset_frame.place(x = 607.5, y = 270)
sunrise_sunset_frame.grid_propagate(False)
sunrise_sunset_frame.grid_columnconfigure(0, weight = 1)
sunrise_sunset_frame.grid_rowconfigure((0, 1, 2, 3), weight = 1)

sunrise_image_placeholder = CTkLabel(sunrise_sunset_frame, image = images["sunrise.png"], text = "")
sunrise_image_placeholder.grid(row = 0, column = 0, pady = (5, 0))
sunrise_time = CTkLabel(sunrise_sunset_frame, text = "Sunrise time", font = ("Segoe UI", 20))
sunrise_time.grid(row = 1, column = 0)

sunset_label = CTkLabel(sunrise_sunset_frame, image = images["sunset.png"], text = "")
sunset_label.grid(row = 2, column = 0)
sunset_time = CTkLabel(sunrise_sunset_frame, text = "Sunset time", font = ("Segoe UI", 20))
sunset_time.grid(row = 3, column = 0)

# --- wind speed / degrees ---
wind_speed_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
wind_speed_frame.place(x = 267.5, y = 440)
wind_speed_frame.grid_propagate(False)
wind_speed_frame.columnconfigure(0, weight = 1)
wind_speed_frame.rowconfigure((0, 1, 2), weight = 1)

wind_image_placeholder = CTkLabel(wind_speed_frame, text = "", image = images["wind.png"])
wind_image_placeholder.grid(row = 0, column = 0)
wind_speed_label = CTkLabel(wind_speed_frame, text = "km/h", font = ("Segoe UI", 25))
wind_speed_label.grid(row = 1, column = 0, pady = (0, 40))

# --- Wind degrees ---
arrow_image = Image.open(arrow_image_path)

wind_degrees_frame = CTkFrame(app, fg_color = "#2b2b2b", width = 150, height = 150, border_color = "#3a3a3a", border_width = 2, corner_radius = 20)
wind_degrees_frame.place(x = 437.5, y = 440)
wind_degrees_frame.grid_propagate(False)
wind_degrees_frame.columnconfigure(0, weight = 1)
wind_degrees_frame.rowconfigure((0, 1, 2), weight = 1)

init_arrow_image = CTkImage(light_image = arrow_image, dark_image = arrow_image, size = (80, 80))
wind_arrow = CTkLabel(wind_degrees_frame, text = "", image = init_arrow_image)
wind_arrow.grid(row = 0, column = 0)
wind_degrees_label = CTkLabel(wind_degrees_frame, text = "°", font = ("Segoe UI", 25))
wind_degrees_label.grid(row = 1, column = 0)

# --- Units switch ---
units_switch = CTkSwitch(app, text = "metric", command = lambda: search_handler())
units_switch.place(x = 10, y = 670)

search_bar.insert(0, "New York")
search_handler()

update_favourite_list()

app.mainloop()

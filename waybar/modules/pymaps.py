#!/usr/bin/env python
import requests
import json
import datetime
import math

# --- Configuration ---
# Your Mapbox Public Access Token (redacted in repo — use your own)
API_KEY = "YOUR_MAPBOX_PUBLIC_TOKEN_HERE"

# Coordinates [Longitude, Latitude]
ORIGIN_LON_LAT = "80.25353490016428,13.009258764678766"
DESTINATION_LON_LAT = "80.18072297522023,13.032271540399002"
PROFILE = "driving-traffic"

# Mapbox Directions API endpoint structure
URL = f"https://api.mapbox.com/directions/v5/mapbox/{PROFILE}/{ORIGIN_LON_LAT};{DESTINATION_LON_LAT}?access_token={API_KEY}"

try:
    # 1. Capture the time of execution
    current_time = datetime.datetime.now().strftime("%I:%M %p")  # e.g., 11:45 AM

    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    if data["routes"]:
        duration_sec = data["routes"][0]["duration"]
        minutes = math.ceil(duration_sec / 60)

        # Calculate ETA based on the current time and duration
        eta_seconds = datetime.datetime.now().timestamp() + duration_sec
        eta = datetime.datetime.fromtimestamp(eta_seconds).strftime("%I:%M %p")

        # Determine CSS class for styling
        if minutes > 45:
            traffic_class = "high-traffic"
        elif minutes > 30:
            traffic_class = "medium-traffic"
        else:
            traffic_class = "low-traffic"

        # --- Waybar Output (i3blocks style: 3 lines) ---
        # Line 1 (text): ETA and Last Checked Time
        print(f"📦 {minutes}m (ETA {eta}) - {current_time}")

        # Line 2 (tooltip): Detailed information
        print(f"Route checked at {current_time}")

        # Line 3 (class): For CSS styling
        print(traffic_class)

    else:
        # Fallback output if route is not found
        print(f"Route Error - {current_time}")
        print("Could not get route data.")
        print("error")

except requests.exceptions.RequestException as e:
    # Fallback output if API connection fails
    error_time = datetime.datetime.now().strftime("%I:%M %p")
    print(f"API Failed - {error_time}")
    print(f"Failed to fetch traffic: {e}")
    print("error")
except Exception as e:
    error_time = datetime.datetime.now().strftime("%I:%M %p")
    print(f"Script Error - {error_time}")
    print(f"An unexpected error occurred: {e}")
    print("error")

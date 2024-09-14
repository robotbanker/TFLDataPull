import network
import urequests
import ujson
import time
from machine import ADC
from secrets import ssid,password,api_id,api_key

# WiFi setup
host = "api.tfl.gov.uk"

# Potentiometer setup
potentiometer = ADC(26)

# Define station and line pairs
station_line_pairs = [
    {"station_id": "490012105HA", "line_id": "26"},
    {"station_id": "490012105HA", "line_id": "15"},
    {"station_id": "490012105HA", "line_id": "76"}
]
num_pairs = len(station_line_pairs)

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
            print(".", end="")
    print("\nWiFi connected! IP:", wlan.ifconfig()[0])

# Get arrivals from API
def get_arrivals(station_id, line_id):
    try:
        url = "https://{}/StopPoint/{}/Arrivals?lineName={}&app_id={}&app_key={}".format(
            host, station_id, line_id, api_id, api_key)
        response = urequests.get(url)
        arrivals = ujson.loads(response.text)
        response.close()
        return arrivals
    except Exception as e:
        print("Failed to retrieve data:", e)
        return []

# Display arrivals in the console, filtered by line_id and sorted by timeToStation
def display_arrivals(arrivals, line_id):
    if len(arrivals) == 0:
        print("No data available")
        return

    # Filter arrivals by line_id
    filtered_arrivals = [arrival for arrival in arrivals if arrival["lineName"] == line_id]

    if len(filtered_arrivals) == 0:
        print(f"No arrivals found for line {line_id}")
        return

    # Sort arrivals by timeToStation
    sorted_arrivals = sorted(filtered_arrivals, key=lambda x: x["timeToStation"])

    for i in range(min(2, len(sorted_arrivals))):  # Show the first two arrivals
        station_name = sorted_arrivals[i]["stationName"]
        destination_name = sorted_arrivals[i]["destinationName"]
        time_to_station = sorted_arrivals[i]["timeToStation"] // 60  # Convert seconds to minutes
        print(f"Station: {station_name}, Destination: {destination_name}, Time: {time_to_station} min")

# Main loop
def main():
    connect_wifi()

    while True:
        # Read the potentiometer value
        pot_value = potentiometer.read_u16()  # Read value in the range 0-65535
        current_pair_index = pot_value * num_pairs // 65536

        # Get selected station and line IDs
        selected_pair = station_line_pairs[current_pair_index]
        station_id = selected_pair["station_id"]
        line_id = selected_pair["line_id"]

        print("Selected Station:", station_id, "Line:", line_id)

        # Get and display arrivals, filtered by line_id and sorted by timeToStation
        arrivals = get_arrivals(station_id, line_id)
        display_arrivals(arrivals, line_id)

        time.sleep(10)  # Delay between requests

# Start the main loop
main()

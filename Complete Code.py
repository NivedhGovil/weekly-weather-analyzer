import requests  # Enables Python to access data from the internet.

# 1. Ask the user which city they want
city = input("Enter a city name: ")

# 2. Turn that city name into latitude/longitude using Open-Meteo's geocoding API
geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
geo_response = requests.get(geo_url).json()  # saves the data obtained from geo_url


if "results" not in geo_response:  # Is the label "results" missing in the geo_response box?
    print(f"Couldn't find a city called '{city}'. Try a different spelling.")
else:
    place = geo_response["results"][0]     # Open the box "Results" and grab the first item.
    latitude = place["latitude"]           # Pull out latitude from place
    longitude = place["longitude"]
    found_name = place["name"]
    country = place["country"]

    print(f" Found: {found_name}, {country} ({latitude}, {longitude})")  # Prints the values obtained above.

    # 3. Now fetch the weather using the coordinates we just found
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m&past_days=7&timezone=auto"
    )
    response = requests.get(weather_url).json()  # Fetches the weather data as JSON.

    # Grab the list of hours and the list of temperatures
    hours = response['hourly']['time']  # Open response, then hourly, then time -> store as hours.
    temps = response['hourly']['temperature_2m']  # Same, but for temperature at 2 metres above ground.

    # Open (or create) Temperature.csv and write the data into it
    with open('Temperature.csv', 'w') as file:
        file.write("Time,Temperature\n")  # Write the column headers at the top.

        for i in range(168):  # i goes 0, 1, 2 ... all the way to 167 (24 hours x 7 days)
            file.write(f"{hours[i]},{temps[i]}\n")  # Writes one row per hour.

    print("Saved 7 days of live weather data into Temperature.csv!")

    # 4. Now analyse and chart the CSV we just saved
    import pandas as pd
    import matplotlib.pyplot as plt

    data = pd.read_csv("Temperature.csv")  # Reads the file and loads it into a table shaped box
    data["Date"] = pd.to_datetime(data["Time"]).dt.strftime("%d-%b-%Y")  # New column: nicely formatted date

    daily = data.groupby("Date", sort=False)["Temperature"].agg(["min", "mean", "median", "max"]) # Take all the rows that share the same value in the Date column, and join them into one pile.
    # sort = False says don't reorder anything. Perform calcs on the values in the temperature column.

    daily["mean"] = daily["mean"].round(2)      # rounds the mean to 2dp
    daily["median"] = daily["median"].round(2)  # rounds the median to 2dp
    daily.insert(0, "City", found_name) # Inserts a column at place 0, labels it City and the values is the city.

    print(daily)  # Prints the table

    daily.to_csv("Daily_Summary.csv")  # save the summary table.

    daily.plot(marker="o", figsize=(10, 5), title=f"Daily Temperature Summary of {city}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()  # Labels don't get cut out by graph borders.
    plt.savefig("weekly_temperature.png")  # Saves the chart as a png
    plt.show()

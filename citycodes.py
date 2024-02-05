import requests
import json

# Define the URL and headers for the GraphQL API
URL = 'https://ra.co/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}

def get_area_code(city_name):
    # Define the GraphQL query and variables
    query = """
    query GetAreaCode($city: String!) {
        areas(searchTerm: $city) {
            id
        }
    }
    """
    variables = {"city": city_name}

    # Send the request to the GraphQL API
    response = requests.post(URL, headers=HEADERS, json={"query": query, "variables": variables})

    # Check the response status code and return the area code if successful
    if response.status_code == 200:
        data = response.json()
        if data["data"]["areas"]:  # Check if the 'areas' list is not empty
            return data["data"]["areas"][0]["id"]
        else:
            print(f"No area found for city: {city_name}")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# Load the city names from a text file
with open("cities.txt", "r") as file:
    cities = [line.strip() for line in file]

# Get the area code for each city and store them in a dictionary
area_codes = {city: get_area_code(city) for city in cities}


# Assuming 'area_codes' is your dictionary mapping city names to area codes
with open("cities.txt", "r") as file:
    lines = [line.strip() for line in file]

with open("cities.txt", "w") as file:
    for line in lines:
        # If the line is a city name and it has an area code, append the area code
        if line in area_codes:
            file.write(f"{line} - {area_codes[line]}\n")
        else:
            file.write(line + "\n")

# Print the area codes
print(area_codes)

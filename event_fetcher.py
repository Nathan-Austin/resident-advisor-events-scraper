import requests
import json
import time
import csv
import sys
import argparse
from datetime import datetime, timedelta
from utils import commit_to_dataBase, name_cleaner
from psycopg2 import sql

URL = 'https://ra.co/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Referer': 'https://ra.co/events/de/berlin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
}
QUERY_TEMPLATE_PATH = "graphql_query_template.json"
DELAY = 1  # Adjust this value as needed


class EventFetcher:
    """
    A class to fetch and print event details from RA.co
    """

    def __init__(self, areas, listing_date_gte, listing_date_lte):
        self.payload = self.generate_payload(areas, listing_date_gte, listing_date_lte)

    @staticmethod
    def generate_payload(areas, listing_date_gte, listing_date_lte):
        """
        Generate the payload for the GraphQL request.

        :param areas: The area code to filter events.
        :param listing_date_gte: The start date for event listings (inclusive).
        :param listing_date_lte: The end date for event listings (inclusive).
        :return: The generated payload.
        """
        with open(QUERY_TEMPLATE_PATH, "r") as file:
            payload = json.load(file)

        payload["variables"]["filters"]["areas"]["eq"] = areas
        payload["variables"]["filters"]["listingDate"]["gte"] = listing_date_gte
        payload["variables"]["filters"]["listingDate"]["lte"] = listing_date_lte

        return payload

    def get_events(self, page_number):
        """
        Fetch events for the given page number.

        :param page_number: The page number for event listings.
        :return: A list of events.
        """
        self.payload["variables"]["page"] = page_number
        response = requests.post(URL, headers=HEADERS, json=self.payload)

        try:
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError):
            print(f"Error: {response.status_code}")
            return []

        #print("GraphQL Response:", data)

        # Save response data to a JSON file
        #with open(f"response_page_{page_number}.json", "w", encoding="utf-8") as file:
            #json.dump(data, file, ensure_ascii=False, indent=2)

        if 'data' not in data:
            print(f"Error: {data}")
            return []

        return data["data"]["eventListings"]["data"]

    @staticmethod
    def print_event_details(events):
        """
        Print the details of the events.

        :param events: A list of events.
        """
        for event_listing in events:
            event = event_listing.get("event", {})
            if not event:
                continue

            print("Full event:", event)
        
        for event in events:
            print("Full event:", event)
            event_data = event["event"]
            print("Full event data:", event_data)
            print(f"Event ID: {event_data['id']}")
            print(f"Event name: {event_data['title']}")
            print(f"Date: {event_data['date']}")
            print(f"Start Time: {event_data['startTime']}")
            print(f"End Time: {event_data['endTime']}")
            print(f"Venue: {event_data['venue']['name']}")
            print(f"Artists: {event_data['artists']}")
            print(f"Genre Info: {event_data['genres']}")
            print(f"Event URL: {event_data.get('contentUrl', '')}")
            print(f"Number of guests attending: {event_data.get('attending', '')}")
            print("-" * 80)
            for artist_info in event_data.get('artists', []):
                print(f"  - Name: {artist_info.get('name', '')}")
                print(f"    ID: {artist_info.get('id', '')}")
                print(f"    Country ID: {artist_info.get('countryId', '')}")
                print(f"    Facebook: {artist_info.get('facebook', '')}")
                print(f"    Instagram: {artist_info.get('instagram', '')}")
                print(f"    Twitter: {artist_info.get('twitter', '')}")
                print(f"    Soundcloud: {artist_info.get('soundcloud', '')}")
                print(f"    Discogs: {artist_info.get('discogs', '')}")
                print(f"    Bandcamp: {artist_info.get('bandcamp', '')}")
                print(f"    Website: {artist_info.get('website', '')}")
                print("-" * 40)
            


    def fetch_and_print_all_events(self):
        """
        Fetch and print all events.
        """
        print("Fetching and printing all events...")
        page_number = 1

        while True:
            events = self.get_events(page_number)

            if not events:
                break

            self.print_event_details(events)
            page_number += 1
            time.sleep(DELAY)

    def fetch_all_events(self):
        """
        Fetch all events and return them as a list.

        :return: A list of all events.
        """
        all_events = []
        page_number = 1

        while True:
            events = self.get_events(page_number)

            if not events:
                break

            all_events.extend(events)
            page_number += 1
            time.sleep(DELAY)

        return all_events

    def save_events_to_csv(self, events, output_file="events.csv"):
        """
        Save events to a CSV file.

        :param events: A list of events.
        :param output_file: The output file path. (default: "events.csv")
        """
        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Event id", "Event name", "Date", "Start Time", "End Time",
                "Artists", "Genres",
                "Venue", "Event URL", "Number of guests attending",
                "Artist ID", "Artist Country ID", "Artist Name",
                "Artist First Name", "Artist Last Name", "Artist Facebook",
                "Artist Instagram", "Artist Twitter", "Artist Soundcloud",
                "Artist Discogs", "Artist Bandcamp", "Artist Website",  # Add new fields here
            ])

            for event in events:
                event_data = event.get("event", {})
                artists_info = event_data.get("artists", [])
                genres_info = event_data.get("genres", [])
                genres = [genre.get('name', '') for genre in genres_info]

                if not genres:
                    genres = ['N/A']

    
                for artist in artists_info:
                    writer.writerow([
                        event_data.get('id', ''),
                        event_data.get('title', ''),
                        event_data.get('date', ''),
                        event_data.get('startTime', ''),
                        event_data.get('endTime', ''),
                        ', '.join([artist_info.get('name', '') for artist_info in artists_info]),
                        ', '.join(genres),
                        event_data.get('venue', {}).get('name', ''),
                        event_data.get('contentUrl', ''),
                        event_data.get('attending', ''),
                        artist.get('id', ''),
                        artist.get('countryId', ''),
                        artist.get('name', ''),
                        artist.get('firstName', ''),
                        artist.get('lastName', ''),
                        artist.get('facebook', ''),
                        artist.get('instagram', ''),
                        artist.get('twitter', ''),
                        artist.get('soundcloud', ''),
                        artist.get('discogs', ''),
                        artist.get('bandcamp', ''),
                        artist.get('website', ''),
                        # Add new fields here
                    ])



    def save_events_to_postgres(self, events):
        """
        Export event data to postgres

        :param events: A list of events.
        
        """
        """     "Event id", "Event name", "Date", "Start Time", "End Time",
                "Artists", "Genres", "Venue", "Event URL", "Number of guests attending",
        """
        unique_event_names = set()  # Keep track of unique event names

        for event in events:
            event_data = event.get("event", {})
            artists_info = event_data.get("artists", [])
            genres_info = event_data.get("genres", [])
            genres = [genre.get('name', '') for genre in genres_info]

            eventName = event_data.get('title', '')
                    # Check if the event name is already in the set, if so, skip this event
            if eventName in unique_event_names:
                continue

            unique_event_names.add(eventName)  # Add event name to the set

                
            #event_data.get('id', ''),
            eventName = event_data.get('title', ''),
            eventDate = str(event_data.get('date', '')),
            startTime = event_data.get('startTime', ''),
            endTime   = event_data.get('endTime', ''),
            artists   = ', '.join([artist_info.get('name', '') for artist_info in artists_info]),
            genres_str    = ', '.join(genres),
            clubName  = event_data.get('venue', {}).get('name', ''),
            popularity= event_data.get('attending', ''),
            clubAddress = event_data.get('venue', {}).get('address', ''),
            price     = event_data.get('cost', '')          
            eventDate = event_data.get('date', '').split('T')[0]
            startTime = event_data.get('startTime', '').split('T')[1].split('.')[0]
            endTime = event_data.get('endTime', '').split('T')[1].split('.')[0]
            query = sql.SQL("""INSERT INTO event_data (
                                event_name, club_name, club_address,
                                event_date, start_time, end_time, artists, popularity, price, event_genres
                            ) VALUES (
                                {eventName}, {clubName}, {clubAddress}, {eventDate}, {startTime},
                                {endTime}, {artists}, {popularity}, {price}, {genres}
                            )ON CONFLICT (event_name) DO NOTHING;""").format(
                    eventName=sql.Literal(eventName),
                    clubName=sql.Literal(clubName),
                    clubAddress=sql.Literal(clubAddress),
                    eventDate=sql.Literal(eventDate),
                    startTime=sql.Literal(startTime),
                    endTime=sql.Literal(endTime),
                    artists=sql.SQL("ARRAY[{}]::TEXT[]").format(sql.Literal(artists)),
                    popularity=sql.Literal(popularity),
                    price=sql.Literal(price),
                    genres=sql.SQL("ARRAY[{}]::TEXT[]").format(sql.Literal(genres_str))
                    )
            
                    #print(query)
            commit_to_dataBase(query)
    
    def save_artists_to_postgres(self, events):   
        """
        Export event data to postgres

        :param events: A list of events.
        
        """
        """       
            "Artist ID", "Artist Country ID", "Artist Name",
            "Artist First Name", "Artist Last Name", "Artist Facebook",
            "Artist Instagram", "Artist Twitter", "Artist Soundcloud",
            "Artist Discogs", "Artist Bandcamp", "Artist Website", 
        """                           
        for event in events:
            event_data = event.get("event", {})
            artists_info = event_data.get("artists", [])
            genres_info = event_data.get("genres", [])
            genres = [genre.get('name', '') for genre in genres_info]

            for artist in artists_info:
                artistName = name_cleaner(artist.get('name', ''))
                facebook = artist.get('facebook', '')
                instagram = artist.get('instagram', '')
                soundcloud = artist.get('soundcloud', '')
                discogs = artist.get('discogs', '')
                bandcamp = artist.get('bandcamp', '')
                website = artist.get('website', '')

                query2 = sql.SQL("""INSERT INTO artists (
                                    artist_name, facebook_link, instagram_link, genres, soundcloud_link, bandcamp_link, website, other_link
                                ) VALUES (
                                    {artistName}, {facebook}, {instagram}, ARRAY[{genres}], {soundcloud}, {bandcamp}, {website}, {discogs}
                                )ON CONFLICT (artist_name) DO NOTHING;""").format(
                    artistName=sql.Literal(artistName[0] if artistName else ''),
                    facebook=sql.Literal(facebook),
                    instagram=sql.Literal(instagram),
                    genres=sql.SQL("ARRAY[{}]::TEXT[]").format(sql.Literal(genres)),
                    soundcloud=sql.Literal(soundcloud),
                    bandcamp=sql.Literal(bandcamp),
                    website=sql.Literal(website),
                    discogs=sql.Literal(discogs)
                )
                            #print(query2)
                commit_to_dataBase(query2)
                     

   
   
    def save_events_to_json(self, events, output_file="events.json"):
        """
        Save events to a JSON file.

        :param events: A list of events.
        :param output_file: The output file path. (default: "events.json")
        """
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(events, file, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Fetch events from ra.co and save them to a CSV file.")
    parser.add_argument("areas", type=int, help="The area code to filter events.")
    parser.add_argument("start_date", type=str, help="The start date for event listings (inclusive, format: YYYY-MM-DD).")
    parser.add_argument("end_date", type=str, help="The end date for event listings (inclusive, format: YYYY-MM-DD).")
    #parser.add_argument("-o", "--output", type=str, default="events.csv", help="The output file path (default: events.csv).")
    args = parser.parse_args()

    listing_date_gte = f"{args.start_date}T00:00:00.000Z"
    listing_date_lte = f"{args.end_date}T23:59:59.999Z"

    event_fetcher = EventFetcher(args.areas, listing_date_gte, listing_date_lte)
    

    #event_fetcher.fetch_and_print_all_events()

    all_events = []
    current_start_date = datetime.strptime(args.start_date, "%Y-%m-%d")

    while current_start_date <= datetime.strptime(args.end_date, "%Y-%m-%d"):
        listing_date_gte = current_start_date.strftime("%Y-%m-%dT00:00:00.000Z")
        event_fetcher.payload = event_fetcher.generate_payload(args.areas, listing_date_gte, listing_date_lte)
        events = event_fetcher.fetch_all_events()
        all_events.extend(events)
        current_start_date += timedelta(days=len(events))

    #event_fetcher.save_events_to_csv(all_events, args.output)
    #event_fetcher.save_events_to_json(all_events, "events.json")
    event_fetcher.save_events_to_postgres(all_events)
    event_fetcher.save_artists_to_postgres(all_events)

if __name__ == "__main__":
    main()

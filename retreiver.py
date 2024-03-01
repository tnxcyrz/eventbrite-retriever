import json
import os
from time import sleep
from random import uniform as random_uniform
import random
import requests

def get_organization_id(organization_page_url):
  # Extract the organization id from the its page url.
  return organization_page_url.split("-")[-1]

def process_event_data(event_data):
  # Process the event data. Return a dictionary with the desired key-value pairs.

  # The keys and subkeys to track in the event data. These keys and subkeys can be easily extracted
  # from event_data using dictionary comprehensions.
  keys_to_track = ["id", "url", "is_free", "online_event"]
  subkeys_to_track = {
    "organizer": ["id", "name", "url", "website"],
    "start": ["utc", "timezone"],
    "end": ["utc", "timezone"],
  }

  result = {key: event_data[key] for key in keys_to_track}
  for key in subkeys_to_track:
    result[key] = {subkey: event_data[key][subkey] for subkey in subkeys_to_track[key]}

  # Add venue data to the result.
  venue_address_subkeys_to_track = ["address_1", "address_2", "city", "region", "country",
                                    "postal_code", "latitude", "longitude"]

  result["venue"] = {"name": event_data["venue"]["name"]}
  for subkey in venue_address_subkeys_to_track:
    result["venue"][subkey] = event_data["venue"]["address"][subkey]  

  # Add event date to the result.
  result["name"] = event_data["name"]["text"]

  return result

def process_response_data(data):
  # Process the response data. Return a list of processed events and a boolean indicating whether
  # there are more pages of events to retrieve.
  evnts = [process_event_data(evnt) for evnt in data["events"]]

  return evnts, data["has_next_page"]

def random_sleep(min_seconds, max_seconds):
  # Sleep for a random number of seconds between min_seconds and max_seconds.
  sleep(random_uniform(min_seconds, max_seconds))

def get_all_upcoming_events(organization_id):
  # Retreive all upcoming events for the organization with the given id.

  has_next_page = True # Indicates whether there are more pages of events to retrieve.
  page_number = 1 # The page number to retrieve.
  events_per_page = 12 # The number of events to retrieve per page. The default page size is 12.

  evnts = [] # A list to store all the upcoming events.

  try:
    while has_next_page:
      page_url = f"https://www.eventbrite.com/org/{organization_id}/showmore/?\
                    page_size={events_per_page}&type=future&page={page_number}"
      
      response = requests.get(page_url)
      response.raise_for_status() # Raise an exception if the request was unsuccessful.

      response_json = response.json()

      if not response_json["success"]:
        break

      page_evnts, has_next_page = process_response_data(response_json["data"])
      evnts.extend(page_evnts)

      page_number += 1 # The next page will be loaded in the next iteration.
      random_sleep(3.8, 6.3) # Sleep for a random number of seconds between 3.8 and 6.3. This is
                             # done to avoid loading the pages too quickly.

      if not has_next_page:
        break

  except requests.exceptions.RequestException as e:
    print("Error occurred:", e)

  return evnts

if __name__ == "__main__":
  organzation_page_url = "https://www.eventbrite.com/o/leaderboard-games-32824819501"
  organization_id = get_organization_id(organzation_page_url)

  evnts = get_all_upcoming_events(organization_id)
  print(f"Retrieved {len(evnts)} upcoming events.")

  # Check if "output" directory exists. If not, create it.
  if not os.path.isdir("output"):
    os.mkdir("output")

  # Write the data of all the upcoming events to a json file.
  with open("output/upcoming_events.json", "w") as file:
    json.dump(evnts, file, indent=2)
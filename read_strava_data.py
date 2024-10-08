import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

import requests
import webbrowser

load_dotenv()

# Replace with your Strava app details
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost/exchange_token'  # Can be any valid redirect URI
ACCESS_TOKEN_URL = 'https://www.strava.com/oauth/token'
AUTHORIZE_URL = 'https://www.strava.com/oauth/authorize'
ACTIVITIES_URL = 'https://www.strava.com/api/v3/athlete/activities'
GEAR_URL = 'https://www.strava.com/api/v3/gear'


def read_json_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Step 1: Get Authorization Code by redirecting user to Strava OAuth URL
def get_authorization_code():
    auth_url = (f"{AUTHORIZE_URL}"
                f"?client_id={CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={REDIRECT_URI}"
                f"&approval_prompt=force"
                f"&scope=activity:read")

    print("Opening browser for OAuth authentication...")
    webbrowser.open(auth_url)

    # Once user logs in, they will be redirected to your redirect URI with a code.
    # Capture the authorization code manually for now.
    print(f"Please visit the following URL and complete the authentication: {auth_url}")
    auth_code = input("Enter the authorization code from the redirect URL: ")
    return auth_code


# Step 2: Exchange Authorization Code for Access Token
def exchange_code_for_token(auth_code):
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(ACCESS_TOKEN_URL, data=payload)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print(f"Failed to get access token: {response.status_code}")
        print(response.text)
        return None


# Step 3: Fetch Recent Activities from Strava API
def fetch_activities(access_token, from_date, to_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    activities = []
    page = 1
    while True:
        print(f"Fetching page {page}...")
        params = {
            'after': int(time.mktime(from_date.timetuple())),
            'before': int(time.mktime(to_date.timetuple())),
            'page': page
        }
        response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
        if response.status_code == 200:
            activities_page = response.json()
            if len(activities_page) == 0:
                break
            page += 1
            activities.extend(activities_page)

    # dump to a JSON file
    write_json_file('data/strava_activities.json', activities)

    return activities


def fetch_gear(access_token, gear_ids: set[str]):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    gear = []
    for gear_id in gear_ids:
        print(f"Fetching gear {gear_id}...")
        response = requests.get(f"{GEAR_URL}/{gear_id}", headers=headers)
        if response.status_code == 200:
            gear_response = response.json()
            gear.append(gear_response)

    # dump to a JSON file
    write_json_file('data/strava_gear.json', gear)
    return gear


def extract_gear_from_activities(activities):
    gear_ids = set()
    for activity in activities:
        if 'gear_id' in activity:
            gear = activity['gear_id']
            if gear:
                gear_ids.add(gear)
    return gear_ids


def extract_activity_stats(activity):
    # get start_date_loca, distance, sport_type from activity and return dict
    start_date_local = activity.get('start_date_local')
    distance = activity.get('distance')
    sport_type = activity.get('type')
    return {
        'start_date_local': start_date_local,
        'distance': distance,
        'sport_type': sport_type
    }


def get_group_activities_by_gear(gear, activities):
    gear_map = {g['id']: g for g in gear}
    grouped = {}
    for activity in activities:
        gear_id = activity.get('gear_id')
        activity_stats = extract_activity_stats(activity)
        if gear_id:
            gear = gear_map.get(gear_id)
            if gear:
                gear_name = gear.get('name')
                if gear_name not in grouped:
                    grouped[gear_name] = []
                grouped[gear_name].append(activity_stats)
    write_json_file('data/strava_activities_by_gear.json', grouped)
    return grouped


# Main script flow
def main():
    # Step 1: Get authorization code
    auth_code = get_authorization_code()

    # Step 2: Exchange authorization code for access token
    access_token = exchange_code_for_token(auth_code)

    if access_token:
        # Step 3: Fetch recent activities
        from_date = datetime(2024, 7, 1)
        to_date = datetime(2024, 10, 27)
        activities = fetch_activities(access_token, from_date, to_date)
        gear_ids = extract_gear_from_activities(activities)
        gear = fetch_gear(access_token, gear_ids)
        activities_by_gear = get_group_activities_by_gear(gear, activities)


if __name__ == '__main__':
    main()

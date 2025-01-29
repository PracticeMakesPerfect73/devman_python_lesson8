import json
import requests
from geopy import distance
from pprint import pprint
import os
from dotenv import load_dotenv
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = (
        response.json()['response']['GeoObjectCollection']['featureMember']
    )

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coffeeshop_distance(coffeeshop):
    return coffeeshop['distance']


if __name__ == '__main__':
    load_dotenv()
    apikey = os.getenv("APIKEY")

    user_location = input('Где вы находитесь? ')
    user_coords = fetch_coordinates(apikey, user_location)
    print('Ваши координаты', user_coords)

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_content_json = my_file.read()

    coffeeshops = json.loads(file_content_json)

    coffeeshop_list = []

    for coffeeshop in coffeeshops:
        coffeeshop_coords = coffeeshop['geoData']['coordinates']
        coffeeshop_info = dict()
        coffeeshop_info['title'] = coffeeshop['Name']
        coffeeshop_info['distance'] = distance.distance(coffeeshop_coords,
                                                        user_coords).km
        coffeeshop_info['latitude'] = coffeeshop_coords[1]
        coffeeshop_info['longitude'] = coffeeshop_coords[0]
        coffeeshop_list.append(coffeeshop_info)

    wished_coffeeshop = sorted(coffeeshop_list,
                               key=get_coffeeshop_distance)[:5]
    pprint(wished_coffeeshop, sort_dicts=False)

    m = folium.Map(location=(user_coords[1], user_coords[0]), zoom_start=12)

    for coffeeshop in wished_coffeeshop:
        folium.Marker(
            location=[coffeeshop['latitude'], coffeeshop['longitude']],
            tooltip="Click me!",
            popup=coffeeshop['title'],
            icon=folium.Icon(icon="cloud"),
        ).add_to(m)
    m.save('index.html')

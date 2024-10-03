import os
import random
import json
from flask import request


file_path = os.path.join('app', 'webspider', 'estate_data.json')
blog_path = os.path.join('app', 'webspider', 'blog_data.json')

def load_estate_data():
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def load_blog_data():
    with open(blog_path, 'r') as file:
        data = json.load(file)
    return data


def featuring_data(*args: list) -> list:
    '''Randomly select data from given arguments'''
    selected_data = []
    for arg in args:
        if  len(arg) > 0:
            num_items_from_each = random.randint(1, min(5, len(arg)))
            selected_data.extend(random.sample(arg, num_items_from_each))
    return selected_data




data_set = load_estate_data()['featured_data'] + load_estate_data()['lefke_data'] + load_estate_data()['guzelyurt_data'] + load_estate_data()[
    'rent_data'] + load_estate_data()['iskele_data'] + load_estate_data()['cyprus_data'] + load_estate_data()['magusa_data'] + load_estate_data()['konut_data'] + load_estate_data()['sale_data_1'] + load_estate_data()['sale_data_2'] + load_estate_data()['sale_data_3'] + load_estate_data()['sale_data_4']

def get_form_data():
    city = request.form.get('city')
    status = request.form.get('status')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    property_type = request.form.get('property_type')

    return city, status, min_price, max_price, property_type


def perform_filtering(json_data, city, status, min_price, max_price, property_type):
    filtered_data = []

    for item in json_data:
        price_string = item.get('Price', '0').replace(
            '£', '').replace(',', '').split('\n')[0].strip()

        try:
            price = float(price_string)
        except ValueError:
            continue

        if (
            (not city or city in item.get('Location')) and
            (not status or status in item.get('Status')) and
            (not min_price or price >= float(min_price)) and
            (not max_price or price <= float(max_price)) and
            (not property_type or property_type in item.get('Property Type'))
        ):
            filtered_data.append(item)

    return filtered_data

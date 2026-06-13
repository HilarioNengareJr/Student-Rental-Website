import os
import re
import random
import json
from flask import request, url_for


file_path = os.path.join('app', 'webspider', 'estate_data.json')
blog_path = os.path.join('app', 'webspider', 'blog_data.json')

# All region-keyed arrays in estate_data.json, in display order.
REGION_KEYS = ['featured_data', 'lefke_data', 'guzelyurt_data', 'rent_data',
               'cyprus_data', 'iskele_data', 'magusa_data', 'konut_data',
               'sale_data_1', 'sale_data_2', 'sale_data_3', 'sale_data_4']


def load_estate_data():
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def load_blog_data():
    with open(blog_path, 'r') as file:
        data = json.load(file)
    return data


def normalize_listing(item: dict) -> dict:
    '''Return a copy of a listing with the keys the card templates index into
    guaranteed present and well-formed, so rendering never raises on a short
    or missing field (e.g. a scraped item whose "Room Details" has < 2 entries).'''
    item = dict(item)
    images = item.get('Images')
    if not isinstance(images, list) or not images:
        item['Images'] = ['']
    room_details = item.get('Room Details')
    room_details = list(room_details) if isinstance(room_details, list) else []
    while len(room_details) < 3:
        room_details.append('-')   # non-empty so [0] (first-char access) is safe
    item['Room Details'] = room_details
    if not item.get('Usable Internal Area'):
        item['Usable Internal Area'] = '-'
    return item


def merge_estate_listings(estate_data: dict = None) -> list:
    '''Concatenate every region array in estate_data into one normalized list.
    Loads the JSON once when no data is passed (replaces the old pattern of
    reading the file a dozen times per request).'''
    if estate_data is None:
        estate_data = load_estate_data()
    listings = []
    for key in REGION_KEYS:
        listings.extend(estate_data.get(key, []))
    return [normalize_listing(item) for item in listings]


def post_to_listing(post) -> dict:
    '''Convert a user-submitted Post row into the same dict shape the scraped
    listings use, so user posts render through the existing card templates.'''
    images = json.loads(post.file_path) if post.file_path else []
    outside = [{'Feature': post.outside_features}] if post.outside_features else []
    return normalize_listing({
        'Listing Number': f'user-{post.id}',
        'Images': images,
        'Status': post.status,
        'Location': post.location,
        'Last Updated': post.timestamp,
        'Price': post.rent,
        'Property Type': post.title,
        'Description': post.description,
        'Room Details': [f'{post.bedrooms} Bedroom', f'{post.bathrooms} Bathroom', f'{post.area} m²'],
        'Usable Internal Area': post.area,
        'Agent Image': url_for('static', filename='profile_pics/' + post.author.profile_image),
        'Agent Name': post.author.username,
        'Furnishing Type': post.furnishes,
        'Outside Features': outside,
        'PhoneNumber': post.phone,
    })


def featuring_data(*args: list) -> list:
    '''Randomly select data from given arguments'''
    selected_data = []
    for arg in args:
        if  len(arg) > 0:
            num_items_from_each = random.randint(1, min(5, len(arg)))
            selected_data.extend(random.sample(arg, num_items_from_each))
    return selected_data


def get_form_data():
    city = request.form.get('city')
    status = request.form.get('status')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    property_type = request.form.get('property_type')

    return city, status, min_price, max_price, property_type


def parse_price(item: dict):
    '''Pull the first numeric value out of a Price string like "£4,500 / month".
    Returns a float, or None when there is no parseable number.'''
    match = re.search(r'[\d,]+', str(item.get('Price', '')))
    return float(match.group().replace(',', '')) if match else None


def perform_filtering(json_data, city=None, status=None, min_price=None,
                      max_price=None, property_type=None):
    '''Filter listings by the search criteria. A criterion is only applied when
    provided; price parsing only excludes items when a price bound is set (so a
    text/city/status search never silently drops items with non-numeric prices).'''
    filtered_data = []
    for item in json_data:
        if city and city.casefold() not in str(item.get('Location', '')).casefold():
            continue
        if status and status.casefold() not in str(item.get('Status', '')).casefold():
            continue
        if property_type and property_type.casefold() not in str(item.get('Property Type', '')).casefold():
            continue
        if min_price or max_price:
            price = parse_price(item)
            if price is None:
                continue
            if min_price and price < float(min_price):
                continue
            if max_price and price > float(max_price):
                continue
        filtered_data.append(item)
    return filtered_data


def all_listings():
    '''Every listing the site knows about: scraped + user-submitted, normalized.'''
    from app.models import Post
    return merge_estate_listings() + [post_to_listing(post) for post in Post.query.all()]


def _es_search(query, city, status, min_price, max_price, property_type):
    '''Query Elasticsearch. Raises if the client is absent or unreachable so the
    caller can fall back to in-memory filtering.'''
    from app import es, ELASTICSEARCH_INDEX
    if es is None:
        raise RuntimeError('Elasticsearch not configured')

    must = []
    if query:
        must.append({'multi_match': {
            'query': query,
            'fields': ['Location', 'Price', 'Property Type', 'Description'],
        }})
    filt = []
    if city:
        filt.append({'match': {'Location': city}})
    if status:
        filt.append({'term': {'Status.keyword': status}})
    if property_type:
        filt.append({'match': {'Property Type': property_type}})
    price_range = {}
    if min_price:
        price_range['gte'] = float(min_price)
    if max_price:
        price_range['lte'] = float(max_price)
    if price_range:
        filt.append({'range': {'PriceValue': price_range}})

    body = {'query': {'bool': {'must': must or [{'match_all': {}}], 'filter': filt}}, 'size': 200}
    response = es.search(index=ELASTICSEARCH_INDEX, body=body)
    return [hit['_source'] for hit in response['hits']['hits']]


def search_listings(query='', city=None, status=None, min_price=None,
                    max_price=None, property_type=None):
    '''Search via Elasticsearch when available, otherwise in-memory filtering.
    The two paths return the same listing-dict shape.'''
    try:
        return _es_search(query, city, status, min_price, max_price, property_type)
    except Exception:
        # Elasticsearch unconfigured or unreachable — fall back to in-memory.
        results = all_listings()
        if query:
            q = query.casefold()
            results = [x for x in results
                       if q in str(x.get('Location', '')).casefold()
                       or q in str(x.get('Price', '')).casefold()]
        return perform_filtering(results, city, status, min_price, max_price, property_type)


def reindex_listings():
    '''(Re)build the Elasticsearch index from all current listings. No-op when ES
    is not configured. Safe to call on demand; failures are surfaced to caller.'''
    from app import es, ELASTICSEARCH_INDEX
    if es is None:
        return False
    if es.indices.exists(index=ELASTICSEARCH_INDEX):
        es.indices.delete(index=ELASTICSEARCH_INDEX)
    es.indices.create(index=ELASTICSEARCH_INDEX)
    for i, listing in enumerate(all_listings()):
        doc = dict(listing)
        doc['PriceValue'] = parse_price(listing)
        es.index(index=ELASTICSEARCH_INDEX, id=str(listing.get('Listing Number', i)), document=doc)
    es.indices.refresh(index=ELASTICSEARCH_INDEX)
    return True


def index_listing(listing: dict):
    '''Best-effort index of a single listing (e.g. a freshly created user post).'''
    from app import es, ELASTICSEARCH_INDEX
    if es is None:
        return
    doc = dict(listing)
    doc['PriceValue'] = parse_price(listing)
    es.index(index=ELASTICSEARCH_INDEX, id=str(listing.get('Listing Number', '')), document=doc)

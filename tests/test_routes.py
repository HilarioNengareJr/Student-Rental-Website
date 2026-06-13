import io

import pytest

from app import db
from app.models import Post, User


@pytest.mark.parametrize('path', [
    '/', '/properties', '/to-rent', '/to-buy', '/about',
    '/register', '/login', '/reset_password', '/search',
    '/feature/swimming-pool', '/feature/with-garden',
])
def test_public_routes_ok(client, path):
    assert client.get(path).status_code == 200


def test_search_post_fallback(client):
    assert client.post('/search', data={'query': 'iskele'}).status_code == 200
    assert client.post('/search', data={'query': '', 'status': 'To Rent'}).status_code == 200


def test_register_then_login(client):
    r = client.post('/register', data={'username': 'newuser', 'email': 'new@example.com',
                                       'password': 'secret123'}, follow_redirects=True)
    assert r.status_code == 200
    assert User.query.filter_by(username='newuser').first() is not None
    r = client.post('/login', data={'email': 'new@example.com', 'password': 'secret123'},
                    follow_redirects=True)
    assert r.status_code == 200


def test_register_rejects_bad_email(client):
    client.post('/register', data={'username': 'baduser', 'email': 'not-an-email',
                                   'password': 'secret123'}, follow_redirects=True)
    assert User.query.filter_by(username='baduser').first() is None


def test_register_rejects_duplicate_username(client, make_user):
    make_user(username='dup', email='dup@example.com')
    client.post('/register', data={'username': 'dup', 'email': 'other@example.com',
                                   'password': 'secret123'}, follow_redirects=True)
    assert User.query.filter_by(email='other@example.com').first() is None


def _listing_form(**overrides):
    data = {'status': 'To Rent', 'title': 'Test Listing', 'rent': '£500 / month',
            'location': '1 Test St, North Cyprus', 'phone': '0533111222',
            'whatsapp': '0533111222', 'description': 'desc', 'bedrooms': '2',
            'bathrooms': '1', 'area': '650', 'furnishes': 'Furnished',
            'outside_features': 'Otopark'}
    data.update(overrides)
    return data


def test_add_listing_requires_login(client):
    r = client.get('/add-listing', follow_redirects=False)
    assert r.status_code == 302 and '/login' in r.headers['Location']


def test_add_listing_creates_post(auth_client):
    data = _listing_form()
    data['file'] = (io.BytesIO(b'fake'), 'photo.png')
    r = auth_client.post('/add-listing', data=data, content_type='multipart/form-data',
                         follow_redirects=True)
    assert r.status_code == 200
    post = Post.query.filter_by(title='Test Listing').first()
    assert post is not None
    assert post.status == 'To Rent' and post.bedrooms == '2'


def test_user_listing_appears_in_properties_and_rent(auth_client):
    data = _listing_form()
    data['file'] = (io.BytesIO(b'fake'), 'photo.png')
    auth_client.post('/add-listing', data=data, content_type='multipart/form-data',
                     follow_redirects=True)
    assert b'Test Listing' in auth_client.get('/properties').data
    assert b'Test Listing' in auth_client.get('/to-rent').data


def test_ownership_enforced_on_edit_and_delete(client, make_user):
    owner = make_user(username='owner', email='owner@example.com')
    post = Post(status='To Rent', title='Owned', rent='£1', location='x', phone='0533111222',
                whatsapp='0533111222', description='d', file_path='[]', bedrooms='1',
                bathrooms='1', area='1', furnishes='Furnished', author=owner)
    db.session.add(post)
    db.session.commit()
    post_id = post.id

    make_user(username='intruder', email='intruder@example.com')
    client.post('/login', data={'email': 'intruder@example.com', 'password': 'secret123'},
                follow_redirects=True)
    assert client.get(f'/listing/{post_id}/edit').status_code == 403
    assert client.post(f'/listing/{post_id}/delete').status_code == 403
    assert db.session.get(Post, post_id) is not None


def test_owner_can_edit_and_delete(client, make_user):
    owner = make_user(username='owner2', email='owner2@example.com')
    post = Post(status='To Rent', title='My First Flat', rent='£1', location='x',
                phone='0533111222', whatsapp='0533111222', description='d', file_path='[]',
                bedrooms='1', bathrooms='1', area='1', furnishes='Furnished', author=owner)
    db.session.add(post)
    db.session.commit()
    post_id = post.id
    client.post('/login', data={'email': 'owner2@example.com', 'password': 'secret123'},
                follow_redirects=True)

    edit = _listing_form(title='My Updated Flat', rent='£99000', status='For Sale', bedrooms='3')
    client.post(f'/listing/{post_id}/edit', data=edit, follow_redirects=True)
    assert db.session.get(Post, post_id).status == 'For Sale'

    client.post(f'/listing/{post_id}/delete', follow_redirects=True)
    assert db.session.get(Post, post_id) is None


def test_password_reset_token_roundtrip(app, make_user):
    user = make_user(username='resetme', email='resetme@example.com')
    token = user.get_reset_token()
    assert User.verify_reset_token(token).id == user.id
    assert User.verify_reset_token('garbage') is None

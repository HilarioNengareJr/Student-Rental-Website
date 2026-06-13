import os
import tempfile

import pytest

# Point the app at a throwaway SQLite file BEFORE importing it, so tests never
# touch the real instance/site.db.
_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + _db_path

from app import app as flask_app, db, bcrypt  # noqa: E402
from app.models import User  # noqa: E402
import app.routes.routes as routes_module  # noqa: E402


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, MAIL_SUPPRESS_SEND=True)
    routes_module.mail.send = lambda msg: None  # never hit SMTP in tests
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    def _make(username='tester', email='tester@example.com', password='secret123'):
        user = User(username=username, email=email,
                    password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        return user
    return _make


@pytest.fixture
def auth_client(client, make_user):
    make_user()
    client.post('/login', data={'email': 'tester@example.com', 'password': 'secret123'},
                follow_redirects=True)
    return client


def pytest_unconfigure(config):
    os.close(_db_fd)
    os.unlink(_db_path)

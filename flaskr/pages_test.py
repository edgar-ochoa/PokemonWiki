from flaskr import create_app
from flask import render_template, json
from unittest.mock import MagicMock
import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
class mock_backend():
    def __init__(self):
        self.backend = MagicMock()
        #self.backend.get_all_page_names.return_value(["pages/abra","pages/mudkip","pages/bob"])
    #backend.get_all_page_names.return_value(["pages/abra","pages/mudkip","pages/bob"])
    def get_all_page_names(self):
        return ["pages/abra","pages/mudkip","pages/bob"]
    
    def get(self,x):
        if x == "/pages":
            return self.backend.get_all_page_names()
        elif x == "pages/test":
            return '{"name":"abra","hit_points":"999","image":"NONE","attack":"999","defense":"999","speed":"999","special_attack":"999","special_defense":"999","type":"999"}'

    """
       @app.route("/pages")
        def pages(pages=None):
        backend = Backend()
        pages = backend.get_all_page_names()
        return render_template('pages.html', pages=pages)
    """
    
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mockend():
    return mock_backend()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Pokemon Wiki" in response.data
    assert b"Browse, upload, have fun." in response.data

# Tests about page, should return author's names
def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"Edgar Ochoa Sotelo" in resp.data
    assert b"Mark Toro" in resp.data
    assert b"Javier Garcia" in resp.data

# should return list of pages
def test_pages(client):
    response = client.get("/pages")
    assert response.status_code == 200
    assert b"User Generated Pages" in response.data

# should return page for abra
def test_get_wiki_page(client):
    response = client.get("/pages/abra")
    assert response.status_code == 200
    assert b"abra" in response.data

# should return back to upload page
def test_upload_get(client):
    response = client.get("/upload")
    assert response.status_code == 302
    assert "upload" in response.location


def test_upload_post(client):
    form_dict = '{"name":"abra","hit_points":"999","image":"NONE","attack":"999","defense":"999","speed":"999","special_attack":"999","special_defense":"999","type":"999"}'
    form = json.dumps(form_dict)
    response = client.post("/upload", data=form, headers={'Content-Type':'application/json'})
    assert response.status_code == 400
  




def test_sign_up(client):
    data={'username': 'username', 'password': 'password'}
    resp = client.post('/signup', data=data)
    assert resp.status_code == 200
    assert b'username' in resp.data
    assert b'Sign Up' in resp.data

def test_sign_in(client):
    data={'username': 'marktoro', 'password': 'mypassword'}
    resp = client.post('login', data=data)
    assert resp.status_code == 200
    assert b'marktoro' in resp.data
    assert b'Log In' in resp.data

def test_logout(client):
    resp = client.post('/logout')
    assert resp.status_code == 302 # Redirection found
    assert 'login' in resp.location
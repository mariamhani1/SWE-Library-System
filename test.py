import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_books(client):
    response = client.get('/get-books')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_add_book(client):
    book = {
        "title": "Test Book",
        "author": "Test Author",
        "published_year": "2023",
        "ISBN": "1234567890",
        "genre": "Test Genre"
    }
    response = client.post('/add-book', json=book)
    assert response.status_code == 201
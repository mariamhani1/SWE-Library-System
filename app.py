"""
Library Management System API
Provides endpoints for managing books in a library system including
CRUD operations and search functionality.
"""
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/api-docs'
API_URL = '/static/swagger.json'
swagger = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Library Backend API '
    }
)
app.register_blueprint(swagger, url_prefix=SWAGGER_URL)

books = []

def validate_book(book):
    """
    Validates book data against required parameters and data types.
    
    Args:
        book (dict): Book data to validate
    
    Returns:
        tuple: (bool, list) Validation result and list of missing/invalid fields
    """
    parameters = ['title', 'author', 'published_year', 'ISBN', 'genre']
    missing_fields = []
    
    for param in parameters:
        if param not in book:
            missing_fields.append(param)
    
    if 'published_year' in book:
        try:
            int(book['published_year'])
        except (ValueError, TypeError):
            missing_fields.append('published_year must be a number')
    
    return len(missing_fields) == 0, missing_fields

@app.route('/get-books', methods=['GET'])
def get_books():
    """Retrieve all books from the library system."""
    return jsonify(books), 200

@app.route('/search-books', methods=['GET'])
def search_books():
    """Search books using query parameters for author, year, and genre."""
    search_params = request.args
    filtered_books = []
    for book in books:
        if search_params.get('author') and book not in filtered_books:
            if book['author'].lower() == search_params.get('author').lower():
                filtered_books.append(book)
        if search_params.get('publish_year') and book not in filtered_books:
            if book['publish_year'] == search_params.get('publish_year'):
                filtered_books.append(book)
        if search_params.get('genre') and book not in filtered_books:
            if book['genre'].lower() == search_params.get('genre').lower():
                filtered_books.append(book)
    return jsonify(filtered_books), 200

@app.route('/add-book', methods=['POST'])
def add_book():
    """Add a new book to the library system with validation."""
    book_data = request.json
    is_valid, missing_fields = validate_book(book_data)
    
    if not is_valid:
        return jsonify({
            'error': 'validation failed',
            'missing': missing_fields
        }), 400

    try:
        book = {
            'title': book_data['title'],
            'ISBN': book_data['ISBN'],
            'author': book_data['author'],
            'published_year': int(book_data['published_year']),
            'genre': book_data['genre']
        }
        books.append(book)
        return jsonify(book), 201
    except ValueError as err:
        return jsonify({'error': str(err)}), 500

@app.route('/update-book/<isbn>', methods=['PUT'])
def update_book(isbn):
    """
    Update an existing book's information.
    
    Args:
        isbn (str): ISBN of the book to update
    """
    book_data = request.json
    for book in books:
        if book['ISBN'] == isbn:
            book.update({
                'title': book_data.get('title', book['title']),
                'author': book_data.get('author', book['author']),
                'published_year': book_data.get('published_year', book['published_year']),
                'genre': book_data.get('genre', book['genre'])
            })
            return jsonify(book), 201
    return jsonify({'error': 'Book not found'}), 404

@app.route('/delete-book/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    """
    Delete a book from the library system.
    
    Args:
        isbn (str): ISBN of the book to delete
    """
    for i, book in enumerate(books):
        if book['ISBN'] == isbn:
            del books[i]
            return make_response('', 204)
    return jsonify({'error': 'Book not found'}), 404

if __name__ == '__main__':
    app.run(port=4000)


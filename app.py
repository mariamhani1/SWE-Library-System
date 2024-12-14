from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)

swagger_url = '/api-docs'
api = '/static/swagger.json'
swagger = get_swaggerui_blueprint(
    swagger_url,
    api,
    config={
        'app_name': 'Library Backend API '
    }
)
app.register_blueprint(swagger, url_prefix=swagger_url)

books = []

def validate_book(book):
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
    return jsonify(books), 200

@app.route('/search-books', methods=['GET'])
def search_books():
    filter = request.args
    filtered_books = []
    for b in books:
        if filter.get('author') and b not in filtered_books:
            if b['author'].lower() == filter.get('author').lower():
                filtered_books.append(b)
        if filter.get('publish_year') and b not in filtered_books:
            if b['publish_year'] == filter.get('publish_year'):
                filtered_books.append(b)
        if filter.get('genre') and b not in filtered_books:
            if b['genre'].lower() == filter.get('genre').lower():
                filtered_books.append(b)
    return jsonify(filtered_books), 200

@app.route('/add-book', methods=['POST'])
def add_book():
    book_data = request.json
    is_valid, missing_fields = validate_book(book_data)
    
    if not is_valid:
        return jsonify({
            'error': 'validation failed',
            'missing': missing_fields
        }), 400

    try:
        b = {
            'title': book_data['title'],
            'ISBN': book_data['ISBN'],
            'author': book_data['author'],
            'published_year': int(book_data['published_year']),
            'genre': book_data['genre']
        }
        books.append(b)
        return jsonify(b), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-book/<ISBN>', methods = ['PUT'])
def update_book(ISBN):
    book_data = request.json
    for b in books:
        if b['ISBN'] == ISBN:
            b.update({
                'title': book_data.get('title', b['title']),
                'author': book_data.get('author', b['author']),
                'published_year': book_data.get('published_year', b['published_year']),
                'genre': book_data.get('genre', b['genre'])
            })
            return jsonify(b),201
    return jsonify({'error': 'Book not found'}),404

@app.route('/delete-book/<ISBN>', methods = ['DELETE'])
def delete_book(ISBN):
    for i, b in enumerate(books):
        if b['ISBN'] == ISBN:
            del books[i]
            return make_response('', 204)
    return jsonify({'error': 'Book not found'}),404

if __name__ == '__main__':
    app.run(port=4000)


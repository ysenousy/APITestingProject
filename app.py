from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, isbn TEXT NOT NULL)')
    conn.commit()
    conn.close()

@app.route('/books', methods=['POST'])
def add_book():
    book_details = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                   (book_details['title'], book_details['author'], book_details['isbn']))
    book_id = cursor.lastrowid  # Get the ID of the last inserted row
    conn.commit()
    conn.close()
    
    book_details['id'] = book_id  # Add the ID to the response data
    return jsonify(book_details), 201

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    # Simulated authorization check
    auth_token = request.headers.get('Authorization')
    if not auth_token or auth_token != "ValidToken":
        return {"error": "Unauthorized"}, 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = cursor.fetchone()
    conn.close()

    if book is None:
        return {"error": "Book not found"}, 404

    return jsonify(dict(book)), 200

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book_details = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the book exists
    cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = cursor.fetchone()
    if book is None:
        return {"error": "Book not found"}, 404

    # Update the book if it exists
    cursor.execute('UPDATE books SET title = ?, author = ?, isbn = ? WHERE id = ?',
                   (book_details['title'], book_details['author'], book_details['isbn'], id))
    conn.commit()
    conn.close()

    # Return the updated book details
    book_details['id'] = id
    return jsonify(book_details), 200

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the book exists
    cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return {"error": "Book not found"}, 404

    # If the book exists, proceed with deletion
    cursor.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    initialize_db()  # Ensure the database and table are created
    app.run(debug=True)
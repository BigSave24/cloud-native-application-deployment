from logging import handlers
import multiprocessing
import sqlite3
import logging
from distutils.log import debug
from urllib import response
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Database connection counter
db_connection_count = 0

# Function to get a database connection
# This function connects to database with the name `datbase.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Function to get application health status
@app.route('/healthz')
def get_health_status():
    response = app.response_class(
        response=json.dumps({
            "result": "OK - Healthy"
            }),
            status=200
    )
    return response

# Function to get application metrics
@app.route('/metrics')
def get_metrics():
    connection = get_db_connection()
    total_posts = connection.execute(
        'Select * FROM posts'
    ).fetchall()
    response = app.response_class(
        status = 200,
        response = json.dumps({
            "db_connection_count": db_connection_count,
            "post_count": len(total_posts)
        }))
    connection.close()
    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      # Log Line Message
      logging.error('404 Error: Article #%s not found.' %(post_id))
      return render_template('404.html'), 404
    else:
      # Log Line Message
      logging.info('Article "%s" successfully retrieved.' %(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # Log Line Message
    logging.info('About Us page request successful.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content,))
            connection.commit()
            connection.close()
            # Log Line Message
            logging.info('Article "%s" created successfully.' %(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111info
if __name__ == "__main__":
   # Stream application logs
   logging.basicConfig(
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ], 
    level=logging.DEBUG, 
    format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
    datefmt='%m/%d/%Y, %I:%M:%S %p'
    )
   app.run(debug=True, host='0.0.0.0', port='3111')

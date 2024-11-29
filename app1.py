from flask import Flask, send_from_directory, render_template_string, url_for, redirect, request
import subprocess
import openai
import random
import re

app = Flask(__name__)

# Configure OpenAI API
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "dummy_key"  # Prevent API key error

# Game configurations, including AI reviewer
items = [
    {"script": "1Colorful Python.py", "title": "Colorful Python", "image": "game1.jpg"},
    {"script": "2Guess Who I Am.py", "title": "Guess Who I Am", "image": "game2.jpg"},
    {"script": "3Rainfall.py", "title": "Rainfall", "image": "game3.jpg"},
    {"script": "Let's Draw Together.py", "title": "Let's Draw Together", "image": "game4.jpg"},
    {"script": "effect5.py", "title": "Magic Bubble", "image": "game6.jpg"}, 
    {"script": "Deal with it.py", "title": "Deal With It", "image": "game5.jpg"},
    {"script": "bury me with money.py", "title": "Bury Me with Money", "image": "game7.jpg"}, 
    {"script": "effect6.py", "title": "Make a Cloth Tiger", "image": "game9.jpg"}, 
    {"script": "11Russian Roulette.py", "title": "Russian Roulette", "image": "game11.png"},
    {"script": None, "title": "AI Media Reviewer", "image": "game8.png", "url": "/reviewer"}, 
    {"script": None, "title": "Praise and Roast AI", "image": "game10.png", "url": "http://localhost:8501"},
]

# Function to generate a review
def generate_review(name, category):
    prompt = f"""
    You are a professional reviewer. Provide a review and rating for the following:
    - Name: {name}
    - Category: {category}.
    Include a rating out of 10 and a professional review.
    """
    try:
        response = openai.ChatCompletion.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "You are a professional reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating review: {e}"

# Fallback review function
def fallback_review(name, category):
    ratings = [f"{round(random.uniform(7.0, 10.0), 1)}/10" for _ in range(3)]
    reviews = [
        "A spectacular achievement.",
        "Critics acclaim its groundbreaking appeal.",
        "A mixed reception but with standout moments."
    ]
    return f"Rating: {ratings[0]}, Review: {random.choice(reviews)}"

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Hub</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Open+Sans:wght@400&display=swap');
        body {
            font-family: 'Open Sans', sans-serif;
            background: linear-gradient(135deg, #ffecd2, #fcb69f);
            background-image: url('https://example.com/james-jean-inspired-bg.jpg'); /* Replace with an actual URL */
            background-size: cover;
            background-attachment: fixed;
            color: #2c2c2c;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        h1 {
            font-family: 'Playfair Display', serif;
            margin: 20px 0;
            font-size: 3rem;
            color: #3a3a3a;
            text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 30px;
            width: 90%;
            max-width: 1200px;
        }
        .item {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            overflow: hidden;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .item:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
        }
        .item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-bottom: 5px solid rgba(0, 0, 0, 0.1);
        }
        .item p {
            font-size: 1.5rem;
            margin: 15px 0;
            font-weight: 600;
            color: #4a4a4a;
        }
        footer {
            margin-top: 40px;
            font-size: 1rem;
            color: rgba(50, 50, 50, 0.8);
        }
        button {
            padding: 10px 20px;
            font-size: 1rem;
            font-family: 'Open Sans', sans-serif;
            background-color: #ff9472;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        button:hover {
            background-color: #f857a6;
        }
    </style>
</head>
<body>
    <h1>Welcome to the Interactive Hub</h1>
    <div class="gallery">
        {% for item in items %}
        <div class="item">
            {% if item.script %}
            <a href="{{ url_for('launch_game', script=item.script) }}">
                <img src="{{ url_for('serve_image', filename=item.image) }}" alt="{{ item.title }}">
            </a>
            {% else %}
            <a href="{{ item.url }}">
                <img src="{{ url_for('serve_image', filename=item.image) }}" alt="{{ item.title }}">
            </a>
            {% endif %}
            <p>{{ item.title }}</p>
        </div>
        {% endfor %}
    </div>
    <footer>
        Made with ❤️ by Flask | © 2024
    </footer>
</body>
</html>
    ''', items=items)

@app.route('/reviewer', methods=['GET', 'POST'])
def reviewer():
    if request.method == 'POST':
        media_name = request.form.get('media_name')
        category = request.form.get('category')
        if not media_name or not category:
            return render_template_string('''
                <!DOCTYPE html>
                <html lang="en">
                <head><title>Error</title></head>
                <body>
                    <h1>Error</h1>
                    <p>Please provide both media name and category.</p>
                    <a href="{{ url_for('reviewer') }}">Go Back</a>
                </body>
                </html>
            ''')
        try:
            review = generate_review(media_name, category)
        except Exception:
            review = fallback_review(media_name, category)
        
        # Extract the rating and review text
        rating_match = re.search(r'Rating\s*[:\-]?\s*([\d\.]+\/10)', review, re.IGNORECASE)
        if rating_match:
            rating = rating_match.group(1)
            # Remove the rating part from the review text
            review_text = review.replace(rating_match.group(0), '').strip()
            # Remove leading 'Review:' if present
            review_text = re.sub(r'^Review\s*[:\-]?\s*', '', review_text, flags=re.IGNORECASE)
        else:
            rating = 'N/A'
            review_text = review  # Use the whole text if rating is not found

        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Review Generated</title>
                <style>
                    body {
                        font-family: 'Poppins', sans-serif;
                        background: url('{{ url_for('serve_image', filename="game8.png") }}') no-repeat center center fixed;
                        background-size: cover;
                        color: white;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black overlay */
                        background-blend-mode: overlay;
                        text-align: center;
                    }
                    h1 {
                        font-size: 2.5rem;
                        margin-bottom: 20px;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
                    }
                    .rating {
                        font-size: 4rem;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }
                    .review-text {
                        font-size: 1.5rem;
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    .back-link {
                        margin-top: 20px;
                        padding: 10px 20px;
                        font-size: 1.1rem;
                        text-decoration: none;
                        background-color: #4caf50;
                        color: white;
                        border-radius: 5px;
                        transition: background 0.3s ease;
                    }
                    .back-link:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <h1>Review for "{{ media_name }}"</h1>
                <div class="rating">{{ rating }}</div>
                <div class="review-text">{{ review_text }}</div>
                <a href="{{ url_for('reviewer') }}" class="back-link">Go Back</a>
            </body>
            </html>
        ''', media_name=media_name, rating=rating, review_text=review_text)
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Media Reviewer</title>
            <style>
                body {
                    font-family: 'Poppins', sans-serif;
                    background: url('{{ url_for('serve_image', filename="game8.png") }}') no-repeat center center fixed;
                    background-size: cover;
                    color: white;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black overlay */
                    background-blend-mode: overlay;
                }
                h1 {
                    font-size: 2.5rem;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
                }
                form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 15px;
                }
                label {
                    font-size: 1.2rem;
                }
                input, select {
                    padding: 10px;
                    font-size: 1rem;
                    border: none;
                    border-radius: 5px;
                    width: 300px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 1.1rem;
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>AI Media Reviewer</h1>
            <form method="POST">
                <label for="media_name">Enter Name:</label>
                <input type="text" id="media_name" name="media_name" placeholder="Media Name" required>
                <label for="category">Select Category:</label>
                <select id="category" name="category">
                    <option value="Singer">Singer</option>
                    <option value="Album">Album</option>
                    <option value="Single Song">Single Song</option>
                    <option value="EP">EP</option>
                    <option value="Movie">Movie</option>
                    <option value="TV Series">TV Series</option>
                    <option value="Game">Game</option>
                </select>
                <button type="submit">Generate Review</button>
            </form>
        </body>
        </html>
    ''')


@app.route('/launch/<script>')
def launch_game(script):
    try:
        subprocess.Popen(["python", script])  # Launch the selected Pygame script
        return '', 204  # No intermediate response for Pygame
    except Exception as e:
        return f"Error launching {script}: {str(e)}", 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('.', filename)  # Serve images from the current directory

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os
import pprint
import logging
#import json

import tvdb_v4_official
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from tmdbv3api import TMDb, Movie
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed


#Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.debug('Debug message')

#Loads dotEnv for testing
load_dotenv()

#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condensrr.db'
db = SQLAlchemy()
tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))
tmdb = TMDb()
tmdb.api_key = os.getenv('TMDB_API_KEY')
movie = Movie()




class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    tmdb_id = db.Column(db.String(100))
    tvdb_id = db.Column(db.String(100))
    img_url = db.Column(db.String(100))

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    series_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    series = db.relationship(
        'Item',
        backref=db.backref('episodes', lazy=True)
    )
    tvdb_id = db.Column(db.String(100))
    tmdb_id = db.Column(db.String(100))
    imdb_id = db.Column(db.String(100))
    img_url = db.Column(db.String(100))
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condensrr.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app

app = create_app()

def clear_data():
    db.session.query(Item).delete()
    db.session.query(Episode).delete()
    db.session.commit()

def send_webhook():
    webhook = DiscordWebhook(url=os.getenv('WEBHOOK_URL'))
    embed = DiscordEmbed(title='New Media Added!', description="New media has been added to the server! Check it out below to see what's new! Enjoy!")
    webhook.add_embed(embed)
    for item in Item.query.all():
        embed = DiscordEmbed(title = item.name, description = item.description)
        embed.set_thumbnail(item.img_url)
        if item.type == 'Series':
            all_episodes = {}
            for episode in Episode.query.filter_by(series_id=item.id).order_by(Episode.season.asc(), Episode.episode.asc()).all():
                if episode.season not in all_episodes:
                    all_episodes[episode.season] = []
                all_episodes[episode.season].append(episode.episode)
            for season in all_episodes:
                episode_list = ', '.join(map(str, all_episodes[season]))
                embed.add_embed_field(name=f"Season {season}", value=episode_list)
        webhook.add_embed(embed)
    webhook.execute()

@app.route('/condenserr', methods=['POST'])
def webook_receive():
    # JSON to Python Dictionary WEBHOOK
    #new_content = json.loads(request.get_data())
    new_content = request.get_json()
    try:
        if new_content['Item']['Type'] == 'Movie':
            movie_lookup = movie.details(int(new_content['Item']['ProviderIds']['Tmdb']))
            new_item = Item(
                name=new_content['Item']['Name'],
                type=new_content['Item']['Type'],
                tmdb_id=new_content['Item']['ProviderIds']['Tmdb'],
                img_url="https://image.tmdb.org/t/p/original" + movie_lookup['poster_path'],
                description=movie_lookup['overview']
            )
            db.session.add(new_item)
            db.session.commit()
            example = Item.query.filter_by(tmdb_id=new_content['Item']['ProviderIds']['Tmdb']).first()
            pprint.pprint(example.img_url)
            return 'success', 200

        elif new_content['Item']['Type'] == 'Episode':
            episode_lookup = tvdb.get_episode(new_content['Item']['ProviderIds']['Tvdb'])
            if Item.query.filter_by(tvdb_id=episode_lookup['seriesId']).first() is None:
                series_lookup = tvdb.get_series(int(episode_lookup['seriesId']))
                new_item = Item(
                    name=series_lookup['name'],
                    type='Series',
                    tvdb_id=episode_lookup['seriesId'],
                    img_url=series_lookup['image'],
                    description=series_lookup['overview']
                )
                db.session.add(new_item)
                db.session.commit()
            new_item = Episode(
                name=new_content['Item']['Name'],
                tvdb_id=new_content['Item']['ProviderIds']['Tvdb'],
                img_url=episode_lookup['image'],
                season=int(new_content['Item']['ParentIndexNumber']),
                episode=int(new_content['Item']['IndexNumber']),
                series_id=Item.query.filter_by(tvdb_id=episode_lookup['seriesId']).first().id
            )
            db.session.add(new_item)
            db.session.commit()
            return 'success', 200
    except:
        return 'error', 400

@app.route('/', methods=['GET'])
def home():
    return 'success', 200

@app.route('/clear', methods=['GET'])
def clear():
    clear_data()
    return 'success', 200

@app.route('/send', methods=['GET'])
def send():
    send_webhook()
    return 'success', 200

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    items = Item.query.all()
    episodes = Episode.query.all()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Clear':
            clear_data()
            return render_template('manage.html', items=items, episodes=episodes)
        elif request.form['submit_button'] == 'Send':
            send_webhook()
            return render_template('manage.html', items=items, episodes=episodes)
    elif request.method == 'GET':
        return render_template('manage.html', items=items, episodes=episodes)

@app.route("/clearlog")
def clearlog():
    with open('app.log', 'w'):
        pass
    return 'Debug Log Cleared', 200
#if __name__ == '__main__':
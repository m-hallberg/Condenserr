import os
import pprint

import tvdb_v4_official
from flask import request, Blueprint, render_template, redirect, url_for
from tmdbv3api import TMDb, Movie
from .models import Item, Episode, Test
from . import db
from .discord import send_webhook

tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))
tmdb = TMDb()
tmdb.api_key = os.getenv('TMDB_API_KEY')
movie = Movie()

backend = Blueprint('backend', __name__)

def clear_data():
    db.session.query(Item).delete()
    db.session.query(Episode).delete()
    db.session.commit()

@backend.route('/condenserr', methods=['POST'])
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
                description=movie_lookup['overview'],
                local_url = "https://watch.mjstcmedia.me/web/index.html#!/item?id=" + new_content['Item']['Id'] + "&serverId=8276dc4e24854e8582535f961b85e2e7"
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
                    description=series_lookup['overview'],
                    local_url = "https://watch.mjstcmedia.me/web/index.html#!/item?id="
                                + new_content['Item']['Id']
                                + "&serverId=8276dc4e24854e8582535f961b85e2e7"
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

@backend.route('/clear', methods=['GET'])
def clear():
    clear_data()
    return 'success', 200

@backend.route('/manage', methods=['GET', 'POST'])
def manage():
    items = Item.query.all()
    episodes = Episode.query.all()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Clear':
            clear_data()
            return redirect(url_for('backend.manage'))
        elif request.form['submit_button'] == 'Send':
            send_webhook()
            return redirect(url_for('backend.manage'))
    elif request.method == 'GET':
        return render_template('management.html', items=items, episodes=episodes)
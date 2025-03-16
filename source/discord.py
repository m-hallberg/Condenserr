import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from flask import Blueprint
from .models import Item, Episode

discord = Blueprint('discord', __name__)

def send_webhook():
    webhook = DiscordWebhook(url=os.getenv('WEBHOOK_URL'))
    embed = DiscordEmbed(title='New Media Added!', description="New media has been added to the server! Check it out below to see what's new! Enjoy!")
    webhook.add_embed(embed)
    for item in Item.query.all():
        embed = DiscordEmbed(title = item.name, description = item.description, url = item.local_url)
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

@discord.route('/send', methods=['GET'])
def send():
    send_webhook()
    return 'success', 200
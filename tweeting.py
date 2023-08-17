import json
from copy import deepcopy
from datetime import datetime
from functools import wraps, partial
from pathlib import Path
from urllib.parse import urlencode
import asyncio
import hashlib
import logging
from login import login
from uploading import upload_media

# Constants for the tweet API
TWEET_API_URL = "https://mobile.twitter.com/i/api/graphql/x5_f-4gzOst6Yke9bUdBdw/CreateTweet"
TWEET_API_AUTH = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
TWEET_API_QUERY_ID = "x5_f-4gzOst6Yke9bUdBdw"
TWEET_API_FEATURES = {
    "tweetypie_unmention_optimization_enabled": True,
    "vibe_api_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "interactive_text_enabled": True,
    "responsive_web_text_conversations_enabled": False,
    "longform_notetweets_richtext_consumption_enabled": False,
    "blue_business_profile_image_shape_enabled": False,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": False,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "responsive_web_enhance_cards_enabled": False
}

def create_headers(session):
    """Create headers for the tweet API request."""
    return {
        'authorization': TWEET_API_AUTH,
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '; '.join(f'{k}={v}' for k, v in session.cookies.items()),
        'referer': 'https://twitter.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'x-csrf-token': session.cookies.get('ct0'),
    }

def build_data(text: str, media: list, session: object) -> dict:
    """Build data for the tweet API request."""
    data = {
        "variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {
                "media_entities": [],
                "possibly_sensitive": False
            },
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "semantic_annotation_ids": []
        },
        "features": TWEET_API_FEATURES,
        "queryId": TWEET_API_QUERY_ID
    }
    for m in media:
        media_id = upload_media(m, session=session)
        data["variables"]["media"]["media_entities"].append({"media_id": media_id, "tagged_users": []})
    
    return data

def tweet(text: str, media: list = [], session: object = None) -> dict:
    """Send a tweet with text and optional media using the tweet API."""
    headers = create_headers(session)
    data = build_data(text, media, session)
    response = session.post(TWEET_API_URL, headers=headers, json=data)
    
    if response.ok:
        logging.info(f"Tweeted successfully: {text}")
        return response.json()
    else:
        logging.error(f"Tweet failed: {response.status_code}, {response.text}")
        response.raise_for_status()
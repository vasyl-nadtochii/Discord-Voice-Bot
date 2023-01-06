import re
import requests
import urllib
import json

from lxml import etree

def youtube_url_validation(url) -> bool:
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match

def check_video_availability(video_url) -> bool:
    checker_url = "https://www.youtube.com/oembed?url="
    video_url = checker_url + video_url

    request = requests.get(video_url)

    return request.status_code == 200

def get_video_name(video_url) -> str:
    checker_url = "https://www.youtube.com/oembed?url="
    video_url = checker_url + video_url

    request = requests.get(video_url)
    response_data_json_str = request.text
    
    response_data_dict = json.loads(response_data_json_str)
    return response_data_dict["title"]
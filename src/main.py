#!/usr/bin/env python3
import requests
import browser_cookie3
import re
import progressbar
from bs4 import BeautifulSoup


def main():
    own = input(f"Your bsaber.com username: ")
    friend = input(f"your friends username: ")

    print("getting your songs ...")
    own_songs = get_bookmarks(own)
    print(f"You have {len(own_songs)} songs in your bookmarks.")

    print("Getting your friends bookmarks...")
    friend_songs = get_bookmarks(friend)
    print(f"Your friend {friend} has {len(friend_songs)} songs in there bookmarks")

    my_diffs = get_diffs(own_songs, friend_songs)

    if len(my_diffs) > 0:
        print(f"There are {len(my_diffs)} songs missing in your bookmarks")
        song_ids = get_post_id(my_diffs)

        cj = get_browser_cookies()

        print("Adding missing songs to your bookmarks")
        add_to_bookmark(cj, song_ids)

        print("Adding done, be sure to resync in the BMBF app.")
    else:
        print("You dont have any missing songs.")


def get_bookmarks(username: str, page=1):
    url = f"https://bsaber.com/wp-json/bsaber-api/songs/?bookmarked_by={username}&page={page}&count=200"

    with requests.get(url) as response:
        songs = response.json()['songs']

        if len(songs) == 200:
            songs.extend(get_bookmarks(username, page + 1))

    return songs


def get_diffs(own: list, friend: list):
    notinlist = []
    for song in friend:
        if song['song_key'] != str() and song not in own:
            notinlist.append(song)

    print(f"Found {len(notinlist)} differences.")
    return notinlist


def get_post_id(diffs: list):
    print(f"Getting {len(diffs)} song Id's")
    song_ids = []
    url = 'https://bsaber.com/songs/{}'
    for song in progressbar.progressbar(diffs):
        song_url = url.format(song['song_key'])
        soup = BeautifulSoup(requests.get(song_url).content, 'html.parser')
        for data_id in soup.findAll("a", attrs={"data-id": re.compile(r"\d+")}):
            song_ids.append(data_id.attrs.get("data-id", None))
    return song_ids


def get_browser_cookies():
    return browser_cookie3.load(domain_name='bsaber.com')


def add_to_bookmark(cj: any, song_ids: list):
    print(f"adding {len(song_ids)} to your bookmarks.")
    for song in progressbar.progressbar(song_ids):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://bsaber.com',
            'Connection': 'keep-alive',
            'Referer': 'https://bsaber.com/songs/' + song,
        }
        data = {
            'action': 'bsaber_bookmark_post',
            'type': 'add_bookmark',
            'post_id': song
        }
        response = requests.post('https://bsaber.com/wp-admin/admin-ajax.php', headers=headers, cookies=cj, data=data)
        if response.status_code != 200:
            print(f'error adding song with id {song}')


if __name__ == '__main__':
    main()

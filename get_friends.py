#!env python
import requests
import shelve
from collections import deque

GIT_FOLLOWER_URL = 'https://api.github.com/users/{login}/followers'
GIT_FOLLOWING_URL = 'https://api.github.com/users/{login}/following'


def get_template(login_name, page_size, auth, URL_TEMPLATE):
    """Common function for get_follow and get_following"""
    return_list = []
    url = URL_TEMPLATE.format(login=login_name)
    params = {'per_page': page_size}
    r = requests.get(url, params=params, auth=auth)
    while True:
        results = r.json()
        return_list.extend(result['login'] for result in results)

        # handle pagination
        if 'next' not in r.links: break
        r = requests.get(r.links['next']['url'])
    return return_list


def get_followers(login_name, page_size, auth):
    """Return list of followers of `login_name`"""
    return get_template(login_name, page_size, auth, GIT_FOLLOWER_URL)


def get_followings(login_name, page_size, auth):
    """Return list of followers of `login_name`"""
    return get_template(login_name, page_size, auth, GIT_FOLLOWING_URL)


def get_friends(login_name, page_size, auth):
    """If the two follow each other, they are friends"""
    followers = get_followers(login_name, page_size, auth)
    followings = get_followings(login_name, page_size, auth)
    return list(set(followers) & set(followings))


def breath_first_search(login_name, page_size, auth, stop_count,
                        shelve_file):
    """Use breath first search to construct the friendship of github and pickle
    it into `shelve_file`
    The shelve_file has a queue object to store the search state, and a 
    currenct_count to count the users already retreived. Therefore, you can call
    this function any times you want.
    *NOTE*: github has a invokation limit policy: 5000 times per hour.
    """
    friends_shelve = shelve.open('git_friends', writeback=True)
    friends_shelve.setdefault('queue', deque())
    friends_shelve.setdefault('current_count',0)
    friends_shelve.setdefault('data', {})
    queue = friends_shelve['queue']
    data = friends_shelve['data']
    if friends_shelve['current_count'] == 0:        # Initialization
        queue.append(login_name)
        friends_shelve['current_count'] += 1
    while True:
        if friends_shelve['current_count'] > stop_count:
            break
        user_name = queue.popleft()
        if user_name in data:                       # Visited before
            continue
        print 'No.', friends_shelve['current_count'], '\t',
        print 'USER:', user_name
        friends = get_friends(user_name, page_size, auth)
        data[user_name] = friends
        queue.extend(friend for friend in friends if friend not in data)
        friends_shelve['current_count'] += 1
    friends_shelve.close()


if __name__ == '__main__':
    page_size = 100
    # auth = ('your login name', 'your password')
    auth = ''
    login_name = 'Sean-Lan'
    stop_count = 15
    shelve_file = 'git_friends'
    breath_first_search(login_name, page_size, auth, stop_count, shelve_file)

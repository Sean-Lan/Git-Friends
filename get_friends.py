#!env python
import requests
import shelve
import time
from collections import deque
try:
    import cPickle as pickle
except:
    import pickle

GIT_FOLLOWER_URL = 'https://api.github.com/users/{login}/followers'
GIT_FOLLOWING_URL = 'https://api.github.com/users/{login}/following'


def get_template(login_name, page_size, auth, URL_TEMPLATE, sleep_time=0.5):
    """Common function for get_follow and get_following"""
    return_list = []
    url = URL_TEMPLATE.format(login=login_name)
    params = {'per_page': page_size}
    r = requests.get(url, params=params, auth=auth)
    while True:
        results = r.json()
        print '\t', '-' * 40
        print '\t', 'X-RateLimit-Limit:', r.headers['X-RateLimit-Limit']
        print '\t', 'X-RateLimit-Remaining:', r.headers['X-RateLimit-Remaining']
        return_list.extend(result['login'] for result in results)
        time.sleep(sleep_time)

        # handle pagination
        if 'next' not in r.links: break
        r = requests.get(r.links['next']['url'], auth=auth)
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
    friends_shelve = shelve.open(shelve_file, writeback=True)
    friends_shelve.setdefault('queue', deque())
    friends_shelve.setdefault('current_count',0)
    friends_shelve.setdefault('data', {})
    queue = friends_shelve['queue']
    data = friends_shelve['data']
    if friends_shelve['current_count'] == 0:        # Initialization
        queue.append(login_name)
        friends_shelve['current_count'] += 1
    while True:
        if friends_shelve['current_count'] > stop_count or len(queue) == 0:
            break
        user_name = queue.popleft()
        if user_name in data:                       # Visited before
            continue
        queue.appendleft(user_name)                 # In case failed
        print 'No.', friends_shelve['current_count'], '\t',
        print 'USER:', user_name
        try:
            friends = get_friends(user_name, page_size, auth)
            data[user_name] = friends
            queue.extend(friend for friend in friends if friend not in data)
            friends_shelve['current_count'] += 1
        except TypeError:                           # Dirty data or request failed
            print 'No.', friends_shelve['current_count'], '\t',
            print 'USER:', user_name, '\t', 'Failed.'
            pass
        finally:
            queue.popleft()                         # Sure success
    friends_shelve.close()


def data_cleaning(adjacent_table):
    """Remove all the node not in the existing node list."""
    cleaned_table = {}
    for node in adjacent_table:
        node_neighbours = []
        for neighbour in adjacent_table[node]:
            if neighbour in adjacent_table:
                node_neighbours.append(neighbour)
        cleaned_table[node] = node_neighbours
    return cleaned_table


if __name__ == '__main__':
    page_size = 100
    # auth = ('your user name', 'your password')
    auth = ''
    login_name = 'Sean-Lan'
    stop_count = 2000
    shelve_file = 'git_friends'
    breath_first_search(login_name, page_size, auth, stop_count, shelve_file)

    # use pickle instead of shelve due to the
    # portability issue.
    friends_shelve = shelve.open(shelve_file)
    cleaned_friends = data_cleaning(friends_shelve['data'])
    pickle.dump(cleaned_friends, open('cleaned_data', 'w'))

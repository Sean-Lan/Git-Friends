#!env python
import requests

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


if __name__ == '__main__':
    page_size = 5
    # auth = ('your login name', 'your password')
    auth =''
    login_name = 'Sean-Lan'
    followers = get_followers('Sean-Lan', page_size, auth)
    print 'followers:', followers

    followings = get_followings(login_name, page_size, auth)
    print 'followings:', followings

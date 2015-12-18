try:
    import cPickle as pickle
except:
    import pickle
import csv

pickle_file = open('cleaned_data')
cleaned_friends = pickle.load(pickle_file)

with open('friends.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow( ('Source', 'Target') )

    # add an edge for each friend relationship
    for username, friends in cleaned_friends.items():
        for friend in friends:
            writer.writerow( (username, friend) )

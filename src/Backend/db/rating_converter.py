import random
from os.path import abspath, dirname

TARGET_DIR = dirname(dirname(dirname(dirname(abspath(__file__)))))
RATINGS_FILE_NAME = TARGET_DIR + '/ratingresults/ratings.csv'
CONVERTED_RATINGS_FILE_NAME = TARGET_DIR + '/ratingresults/convertedratings.csv'


def convert_exported_ratings():
    rating_dict = {}
    with open(RATINGS_FILE_NAME, 'r') as source_file:
        for line in source_file:
            aspect, rating_str, pair_str = line.split(';', 2)
            pair = pair_str.replace(';', '///')
            pair = pair.replace('\n', '')
            rating = int(rating_str)
            if pair not in rating_dict.keys():
                rating_dict[pair] = {}
            if aspect not in rating_dict[pair].keys():
                rating_dict[pair][aspect] = []
            rating_dict[pair][aspect].append(rating)

    with open(CONVERTED_RATINGS_FILE_NAME, 'w') as target_file:
        target_file.write(
            'OBJECT A;OBJECT B;ASPECT;MOST FREQUENT RATING;CONFIDENCE;AMOUNT OF GOOD RATINGS;AMOUNT OF BAD RATINGS\n')

        for pair in rating_dict.keys():
            object_a, object_b = pair.split('///', 1)

            for aspect in rating_dict[pair].keys():
                target_file.write(
                    object_a + ';' + object_b + ';' + aspect + ';')

                good_ratings = rating_dict[pair][aspect].count(1)
                bad_ratings = rating_dict[pair][aspect].count(0)

                if good_ratings > bad_ratings:
                    most_frequent_rating = 'GOOD'
                    confidence = good_ratings / \
                        float(good_ratings + bad_ratings)
                elif bad_ratings > good_ratings:
                    most_frequent_rating = 'BAD'
                    confidence = bad_ratings / \
                        float(good_ratings + bad_ratings)
                else:
                    most_frequent_rating = 'NONE'
                    confidence = good_ratings / \
                        float(good_ratings + bad_ratings)

                target_file.write(most_frequent_rating + ';' + str(confidence) +
                                  ';' + str(good_ratings) + ';' + str(bad_ratings) + '\n')

from constants import OPPOSITE_MARKERS, POSITIVE_MARKERS, NEGATIVE_MARKERS, NEGATIONS
from aspect_searcher import find_aspects
from marker_searcher import get_marker_count, get_marker_pos
from link_extracter import extract_main_links
from regex_service import find_pos_in_sentence


def find_winner(sentences, obj_a, obj_b, aspects):
    '''
    Finds the winner of two objects for given sentences and aspects. Returns a dictionary
    containing all the information of the comparison (winner, sentences for each object, score for
    each object and more).

    sentences:  Dictionary
                dictionary containing sentences

    obj_a:      Argument
                the first competing object

    obj_b:      Argument
                the second competing object

    aspects:    List
                list of Aspects
    '''
    if sentences.values():
        max_sentscore = max(sentences.values())
    for s in sentences:
        comp_result = what_is_better(s, obj_a, obj_b)
        if comp_result['winner'] == obj_a:  # objectA won the sentence
            add_points(find_aspects(s, aspects), obj_a,
                       sentences[s], s, max_sentscore, comp_result['marker_cnt'])
        else:  # objectB won the sentence
            add_points(find_aspects(s, aspects), obj_b,
                       sentences[s], s, max_sentscore, comp_result['marker_cnt'])

    return build_final_dict(obj_a, obj_b)


def add_points(contained_aspects, winner, score, sentence, max_score, marker_count):
    '''
    Adds the points of the won sentence to the points of the winner.

    contained_aspects:  List
                        The aspects the user entered that are 
                        contained in the sentence

    winner:             Argument
                        The winner of the given sentence

    score:              Integer
                        The score of the given sentence

    sentence:           String
                        The given sentence to add

    max_score:          Integer
                        Max score over all sentences

    marker_count:       Integer
                        How many markers are countained in the 
                        Sentence
    '''
    if contained_aspects:
        if len(contained_aspects) == 1:
            winner.add_points(
                contained_aspects[0].name, (score / max_score) * (contained_aspects[0].weight + marker_count))
            winner.add_sentence(contained_aspects[0].name, sentence)
        else:
            for aspect in contained_aspects:
                winner.add_points('multiple', (score / max_score)
                                  * (aspect.weight + marker_count))
            winner.add_sentence('multiple', sentence)
    else:
        # multiple markers, multiple points
        winner.add_points('none', (score / max_score) * marker_count)
        winner.add_sentence('none', sentence)


def build_final_dict(obj_a, obj_b):
    '''
    Builds the final dictionary containing all necessary information regarding the comparison to 
    be returned to the frontend.

    obj_a:  Argument
            the first object of the comparison

    obj_b:  Argument
            the second object of the comparison
    '''
    final_dict = {}  # the dictionary to be returned

    sentences_obja = []
    for value in obj_a.sentences.values():
        sentences_obja = sentences_obja + value

    sentences_objb = []
    for value in obj_b.sentences.values():
        sentences_objb = sentences_objb + value

    if obj_a.totalPoints > obj_b.totalPoints:
        final_dict['winner'] = obj_a.name
    elif obj_b.totalPoints > obj_a.totalPoints:
        final_dict['winner'] = obj_b.name
    else:
        final_dict['winner'] = 'No winner found'
    linked_words = extract_main_links(
        sentences_obja, sentences_objb, obj_a, obj_b)
    final_dict['object1'] = obj_a.name
    final_dict['object2'] = obj_b.name
    final_dict['totalScoreObject1'] = obj_a.totalPoints
    final_dict['totalScoreObject2'] = obj_b.totalPoints
    final_dict['scoreObject1'] = obj_a.points
    final_dict['scoreObject2'] = obj_b.points
    final_dict['extractedAspectsObject1'] = linked_words['A']
    final_dict['extractedAspectsObject2'] = linked_words['B']
    final_dict['sentencesObject1'] = obj_a.sentences
    final_dict['sentencesObject2'] = obj_b.sentences

    return final_dict


def what_is_better(sentence, obj_a, obj_b):
    '''
    Analyzes a sentence that contains two given objects. Returns object containing winner
    and a boolean marking multiple markers.
    Currently only sentences are supported that are built in the form of
        ... object ... marker ... object ...

    sentence:   String
                the sentence to analyze. Has to contain obj_a and obj_b.
    obj_a:      Argument
                the first object to be compared to the second.
    obj_b:      Argument
                the second object to be compared to the first.
    '''
    sentence = sentence.lower()
    result = {}

    a_pos = find_pos_in_sentence(obj_a.name, sentence)
    b_pos = find_pos_in_sentence(obj_b.name, sentence)

    first_pos = min(a_pos, b_pos)
    second_pos = max(a_pos, b_pos)
    opp_pos = get_marker_pos(sentence, first_pos, second_pos, OPPOSITE_MARKERS)
    neg_pos = get_marker_pos(sentence, first_pos, second_pos, NEGATIONS)
    positive_pos = get_marker_pos(
        sentence, first_pos, second_pos, POSITIVE_MARKERS)
    if positive_pos != -1:  # there's a positive marker, check if a won
        result['marker_cnt'] = get_marker_count(
            sentence, first_pos, second_pos, POSITIVE_MARKERS)
        result['winner'] = obj_a if obj_a_wins_sentence(
            first_pos, a_pos, opp_pos, neg_pos, positive_pos) else obj_b
        return result
        # we can return because there's never both markers in a sentence
    negative_pos = get_marker_pos(
        sentence, first_pos, second_pos, NEGATIVE_MARKERS)
    result['marker_cnt'] = get_marker_count(
        sentence, first_pos, second_pos, NEGATIVE_MARKERS)
    # we're only here if there's no positive marker, so there must be negative one
    result['winner'] = obj_b if obj_a_wins_sentence(
        first_pos, a_pos, opp_pos, neg_pos, negative_pos) else obj_a
    return result


def obj_a_wins_sentence(first_pos, a_pos, opp_pos, neg_pos, marker_pos):
    '''
    Returns whether obj_a wins the sentence or not.

    first_pos:  number
                the first position of one of the objects within the sentence

    a_pos:      number
                the position of obj_a within the sentence

    opp_pos:    number
                the position of an opposite marker within the sentence

    neg_pos:    number
                the position of a negation within the sentence

    marker_pos: number
                the position of a marker within the sentence
    '''
    if opp_pos != -1 and first_pos < opp_pos < marker_pos:
        return first_pos != a_pos  # example: a is not better than b
    elif neg_pos != -1 and first_pos < neg_pos < marker_pos:
        return first_pos != a_pos  # example: a couldn't be better than b
    else:
        return first_pos == a_pos  # example: a is better than b

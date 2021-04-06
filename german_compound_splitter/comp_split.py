#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
# Copyright 2020 by repodiac (see https://github.com/repodiac, also for information how to provide attribution to this work)
#

import ahocorasick

# selection of common prefixes
MERGE_LEFT = ['ab', 'an', 'auf', 'aus', 'außer', 'be', 'bei', 'binnen', 'dar', 'dran', 'durch', 'ein', 'ent', 'er',
              'fehl', 'fort', 'frei', 'ge', 'her', 'hin', 'hinter', 'hoch', 'miss', 'mit', 'nach', 'ober',
              'tief', 'über', 'um', 'un', 'unter', 'ur', 'ver', 'voll', 'vor', 'weg', 'zer', 'zu', 'zur']

# selection of common suffixes
MERGE_RIGHT = ['ff', 'au', 'ei', 'ung', 'ion', 'um',
               'er', 'el', 'or', 'eur', 'ent', 'ant', 'ist', 'oge',
               'us', 'e', 't', 'heit', 'keit', 'schaft', 'tion', 'ur',
               'ar', 'ät', 'a', 'ie', 'ine', 'euse',  # 'in'
               'chen', 'lein', 'nis', 'ium', 'mus']

PLURAL_SUFFIX = ['en', 'er', 'e', 'n', 's']

PLURAL_TRANSITION_VOWEL = {'ä': 'a',
                           'ü': 'u',
                           'ö': 'o'}


def read_dictionary_from_file(input_file):
    """
    Load dictionary from file into efficient data structures for efficient search and retrieval

    :param input_file: a text file dictonary holding one item per line
    :return: ahocorasick.Automaton, data structure for efficient search and retrieval
    """
    # initialize the efficient data structures
    A = ahocorasick.Automaton()

    print('Loading data file -', input_file)
    with open(input_file, 'r', encoding='utf8') as f:
        input_list = f.read().splitlines()

    # load one item per line
    for w in input_list:
        # omit empty lines
        if not w:
            continue
        # add key as lower-case in order to be able to compare it with any substring in a compound word
        # use the item (i.e. word) and if it's upper case as sort of flag (item can be regarded as noun then)
        A.add_word(w.lower(), (w[0].isupper(), w))

    # generate with data
    A.make_automaton()

    return A


def _is_abbreviation(tuple):
    """
    Checks if value can be interpreted as an abbreviation (thus, not a compound word)

    :param tuple: the value as tuple, (is_upper_case_flag, value)
    :return: boolean True or False, if value was determined as abbreviation or not
    """

    # example tuple[1].isupper(): ARD
    # example (tuple[1][0].islower() and tuple[1][-1].isupper()): mA
    # example (len(tuple[1])==2 and tuple[1][0].isupper() and tuple[1][1].islower()): Mi, St
    return tuple[1].isupper() \
           or (tuple[1][0].islower() and tuple[1][-1].isupper()) \
           or (len(tuple[1]) == 2 and tuple[1][0].isupper() and tuple[1][1].islower())


def _check_if_suffix(item):
    """
    Checks if item starts with a suffix from the list of common suffixes

    :param item: the item (snippet) to be checked upon
    :return: the suffix, if item was found in list of suffixes, None otherwise
    """

    for suf in PLURAL_SUFFIX:
        if item.startswith(suf):
            return suf

    return None


def merge_fractions(dissection: list):
    """
    Simple method to merge fractions or artifacts as post-processing step after splitting up a compound word
    Merges are carried out, if pre- or suffix are found in the list of common pre-/suffixes; in particular this may be
    useful, when "only_nouns=False" is used as parameter with the dissect(..) method.

    :param dissection: list of split words
    :return: new list with merged split words, in case
    """

    cleaned = []
    ignore_next = False
    for i in range(len(dissection) - 1):
        # compares left and right word of the current word in the split word list
        # if there is a suitable match for merging both
        if not ignore_next and dissection[i + 1].lower() in MERGE_RIGHT:
            cleaned.append(dissection[i] + dissection[i + 1])
            ignore_next = True
        elif not ignore_next and dissection[i].lower() in MERGE_LEFT:
            cleaned.append(dissection[i] + dissection[i + 1])
            ignore_next = True
        else:
            if not ignore_next:
                cleaned.append(dissection[i])
            ignore_next = False

    if not ignore_next:
        cleaned.append(dissection[-1])

    return cleaned


def compute_singular(item, ahocs):
    """
    Computes a singular form of the given item, uses two methods: a) looks up singular form in dictionary
    b) checks for "umlauts" and replaces them by their base vowel

    :param item: a word to be transformed to its singular form
    :param ahocs: the data structure holding an efficient representation of the dictionary
    :return: transformed singular form of item
    """
    for suf in sorted(PLURAL_SUFFIX, reverse=True):
        # check for matching suffix
        if item.endswith(suf):
            item_singular = item[:len(item) - len(suf)]
            if item_singular.lower() in ahocs and ahocs.get(item_singular.lower())[0]:
                return item_singular
            # alternatively check for "umlauts" and convey to base vowels, in case
            else:
                for umlaut, vowel in PLURAL_TRANSITION_VOWEL.items():
                    if umlaut in item_singular:
                        uml_repl_item = item_singular.replace(umlaut, vowel)
                        if uml_repl_item.lower() in ahocs:
                            return uml_repl_item

    return item


def dissect(compound, ahocs, only_nouns=True, make_singular=False, mask_unknown=False):
    """
    Dissects any compound word if splits are to be found in loaded dictionary

    :param compound: the compound to be split up
    :param ahocs: the data structure holding an efficient representation of the dictionary
    :param only_nouns: if True (default), return only recognized nouns, no pre- or suffixes and no verbs or adjectives
    :param make_singular: if True, compute simple approach to extract singular form for each split word, default is False
    :param mask_unknown: if True, mask each part which is unknown from the dictionary, if False (default) the method tries to insert it anyway as lower-case; often this is still valid, but can come with artifacts sometimes
    :return: list of strings, holding all the split words from the compound
    """

    print('Dissect compound: ', compound)

    # dict of candidate words for splitting up the compound word
    # for each *end index* with substrings, the list of substrings is stored, i.e. all strings which end there
    matches = {}

    # iterates over all found substrings in compound word, provides end index and substring itself
    for end, val in ahocs.iter(compound.lower()):
        # skip if abbreviation or if not a noun in case only_nouns is set (val[0] is False if first letter is lowercase)
        if _is_abbreviation(val) or (only_nouns and not val[0]):
            continue

        # store each substring having the same end index in the same list but with its own start index attached
        start = end + 1 - len(val[1])
        if end not in matches:
            matches[end] = []
        matches[end].append((start, val))

    # make sure the list per end index is reversely sorted by *start index*, such as the *shortest* substring per list
    # comes first
    for k in matches.keys():
        matches[k] = sorted(matches[k], key=lambda s: s[0], reverse=True)

    results = []
    # if no substrings were found, return compound word
    if not matches:
        results = [compound]
        return results

    # start from the end, use last index available
    max_end_pos = max(matches.keys())
    current_end_pos = max_end_pos

    # end position for unknown parts of the compound which cannot be found in or via the dictionary
    lost_end_pos = -1
    # make sure you cover the full tail of the compound, in case the last part is unknown
    if (max_end_pos+1) < len(compound):
        lost_end_pos = len(compound)

    # loop over the compound from the end to the start (reverse order)
    while current_end_pos > 0:
        end_next = -1

        if current_end_pos in matches:
            # attach unknown middle part, in case
            if lost_end_pos > -1 and results:
                if mask_unknown:
                    results.insert(0, '__unknown__')
                else:
                    results.insert(0, compound[current_end_pos + 1:lost_end_pos])
                lost_end_pos = -1

            # if current_end_pos is a valid end index, loop over the list of substrings ending there and
            # try to find the next split position
            for select_compound in matches[current_end_pos]:
                start_compound = select_compound[0]
                # valid split found, but may contain case "s"
                if (start_compound - 1) in matches:
                    end_next = start_compound - 1
                # valid split found, but may have plural form of split word
                elif (start_compound - 2) in matches and _check_if_suffix(compound[start_compound - 1:]):
                    end_next = start_compound - 2
                # invariant: end of string (reached start of compound, pos=0)
                elif start_compound == 0:
                    end_next = 0

                # add valid split word to result list
                if end_next > -1:
                    results.insert(0, select_compound[1][1])
                    current_end_pos = end_next
                    lost_end_pos = -1
                    break

        # no split found in current list of substrings (with the same end index),
        # thus continue with one end index to the left and see if there are valid splits (in the next iteration)
        if end_next == -1:
            if lost_end_pos == -1:
                lost_end_pos = current_end_pos + 1
            current_end_pos -= 1

    # attach unknown remainder in the front, in case
    if lost_end_pos > -1 and results:
        results.insert(0, compound[current_end_pos:lost_end_pos])

    # post-corrections, e.g. merge invalid splits if split and succeeding split word merged
    # is a valid entry in the dictionary
    if only_nouns:
        # workaround to prevent unwanted behaviour (only nouns are eligible)
        results[0] = results[0][0].upper() + results[0][1:]
        for ri in range(len(results) - 1):
            if results[ri].islower():
                merged = results[ri] + results[ri + 1].lower()
                if ahocs.exists(merged):
                    part1 = results[ri]
                    part2 = results[ri + 1]
                    results.insert(ri, merged[0].upper() + merged[1:])
                    results.remove(part1)
                    results.remove(part2)
                else:
                    # workaround for single letters (most likely artifacts)
                    if len(results[ri]) == 1:
                        aritfact_single_letter = results[ri]
                        results[ri-1] += aritfact_single_letter
                        results.remove(aritfact_single_letter)

    # if set, compute singular version of each split word
    if make_singular:
        for ri in range(len(results)):
            results[ri] = compute_singular(results[ri], ahocs)

    return results

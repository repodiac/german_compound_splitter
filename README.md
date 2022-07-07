# german_compound_splitter

**german_compound_splitter** is a Python module to split up German compound words (for instance the famous *Donaudampfschifffahrtskapitänsmützenabzeichen*), based on a given external German dictionary and a highly-efficient implementation of the [Aho–Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm), [pyahocorasick](https://pypi.org/project/pyahocorasick/), for multi-pattern string search and retrieval.

This method works really well compared to the available other alternatives I know of for German compound splitting. Depending on your use case you may want normalized forms of the resulting components (split words), most likely the singular form. You can try `make_singular=True`, it works for me in most cases.

Sometimes the result has artifacts -- it may be that the dictionary lacks certain entries at this point or this is a bug :-)
Nonetheless, you can play around with the parameter `only_nouns=False` which allows for any type of word (verb, adjective, prefix, suffix) in the dictionary to be used for splitting. Sometimes the results are
good or better than if limiting to nouns only.

Also depending on the use case is the option to mark everything which is not found in the dictionary to be masked as "__unknown__" split word in the results. Otherwise and per default, the compound splitter tries to workaround these issues or simply copies the unknown part directly to the results. You can see that if you use with `only_nouns=True` and a split word is lower-case though. This is most likely an unknown part not found in the dictionary or interfering with other words from the dictionary.

This is also true for words where you wonder why they haven't been split up appropriately (even for "simple" words this may occur). At the time of writing this README, some very basic words like "Zeit" or "Fahrt" are not in the dictionary (either by mistake of the author or for other reasons).

## License and Attribution

This work is licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

To provide **attribution or cite this work** please use the following text snippet:
```
german_compound_splitter, Copyright 2020 by repodiac, see https://github.com/repodiac for updates and further information
```

## Version History

* `release 0.1.1` - fixed issue #1 (thank you for pointing out, @sebag90) and added some improvements for handling plural
* `release 0.1` - initial release of the software, please let me know about bugs or issues

# Installation/Setup

Installation is easy using `pip` and built-in `git` package installation based on `setup.py`:

* `pip install git+https://github.com/repodiac/german_compound_splitter`

Setup:

- It should install and behave (`import german_compound_splitter`) to your current Python environment as any other `pip` package (in case, create a virtual environment with `virtualenv` or `conda` before).

## Some Notes on an External Dictionary

Due to unclear license and depending on the kind of use (private, research, commercial, ...) I cannot include a dictionary here in this setting. I strongly recommend the [Free German Dictionary](https://sourceforge.net/projects/germandict/files/latest/download) by [Jan Schreiber](https://github.com/janschreiber), though. It is constantly or often updated and includes currently more than 2.1 million entries! But apart from this, you can use any dictionary containing one item per line.

**Note:**
* The *Free German Dictionary* needs to be saved as UTF8 and with Unix/Linux line breaks before it can be used with Python, otherwise loading gives byte errors (at least on my machine)

* A useful tool available on "linux-ish" operating systems proved to be very useful here:
`iconv -f ISO_8859-15 german.dic > german_utf8_linux.dic` saves the dictionary to a version (`german_utf8_linux.dic`) readable py Python

# Documentation

## Example Usage

In Python code or as library:

```
from german_compound_splitter import comp_split

compound = 'Donaudampfschifffahrtskapitänsmützenabzeichen'
# please load an appropriate (external) dictionary, see the notes in section Installation/Setup on the dictionary
input_file = 'german.dic'
ahocs = comp_split.read_dictionary_from_file(input_file)

dissection = comp_split.dissect(compound, ahocs, make_singular=True)
print('SPLIT WORDS (plain):', dissection)
print('SPLIT WORDS (post-merge):', comp_split.merge_fractions(dissection))
```

## Input Parameters

The main method to be used is `dissect('Kompositumszerlegungsmaschinerie', ahocs)`

It has the following input parameters:

* `only_nouns` - if `True` (default), return only recognized nouns, no pre- or suffixes and no verbs or adjectives
* `make_singular` - if `True`, compute simple approach to extract singular form for each split word, default is `False`
* `mask_unknown` - if `True`, mask each part which is unknown from the dictionary, if `False (default) the method tries to insert it anyway as lower-case; often this is still valid, but can come with artifacts sometimes

## Performance

If you have multiple splittings (or multiple compound words) to process, it is advisable to load the dictionary only **once** and reuse the `ahocorasick` automaton every other time -- loading the dictionary can take a few seconds depending on your machine. However, the actual split up work is blazing fast, thanks to `pyahocorasick`'s implementation and you can easily process a lot of compound words in very little time.

# Issues and Comments

Please open issues on github for bugs or feature requests. You can also reach out to me via email.

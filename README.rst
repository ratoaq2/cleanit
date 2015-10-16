CleanIt
==========
Subtitles extremely clean.

.. image:: https://img.shields.io/pypi/v/cleanit.svg
    :target: https://pypi.python.org/pypi/cleanit
    :alt: Latest Version

.. image:: https://travis-ci.org/ratoaq2/cleanit.svg?branch=master
   :target: https://travis-ci.org/ratoaq2/cleanit
   :alt: Travis CI build status

.. image:: https://img.shields.io/github/license/ratoaq2/cleanit.svg
   :target: https://github.com/ratoaq2/cleanit/blob/master/LICENSE
   :alt: License

:Project page: https://github.com/ratoaq2/cleanit

**CleanIt** is a command line tool (written in python) that helps you to keep your subtitles clean. You can specify rules to detect subtitle entries to be removed or patterns to be replaced. Simple text matching or complex regex can be used.

Usage
-----
CLI
^^^
Clean subtitles::

    $ cleanit --config my-config.yml my-subtitle.srt
    Collected 1 subtitles
    Saving <Subtitle [my-subtitle.srt]>
    Saved <Subtitle [my-subtitle.srt]>

Library
^^^^^^^
How to clean subtitles in a specific path using a specific configuration:

.. code:: python

    from cleanit.api import clean_subtitle, save_subtitle
    from cleanit.config import Config
    from cleanit.subtitle import Subtitle

    subtitle = Subtitle('/subtitle/path')
    config = Config.from_file('/config/path')
    if clean_subtitle(subtitle, config.rules):
        save_subtitle(subtitle)

YAML Configuration file
^^^^^^^^^^^^^^^^^^^^^^^
The yaml configuration file has 2 main sections: *templates* and *groups*.

- **Templates** can help you to define common configuration snippets to be used in several groups.
- **Groups**: where you can define your rules.

.. code:: yaml

 # Reference:
 #   type: [text*, regex]
 #   match: [contains*, exact, startswith, endswith]
 #   flags: [ignorecase, dotall, multiline, locale, unicode, verbose]
 #   whitelist: no* 
 #   rules:
 #   - sometext
 #   - (\b)(\d{1,2})x(\d{1,2})(\b): {replacement: \1S\2E\3\4, type: regex, match: contains, flags: [unicode], whitelist: no}
 
 
 templates:
   common:
     type: text
     match: contains
 
 groups:
   # Groups can have any name, in this case 'blacklist' we have all the rules to remove subtitle  entries
   blacklist:
     template: common
     rules:
       # Removes any subtitle entry that contains the word FooBar
       - FooBar
 
       # Removes any subtitle entry that contains the pattern S00E00
       # Example:
       #   My Series S01E02
       - \bs\d{2}\s?e\d{2}\b: {type: regex, flags: ignorecase}
 
       # Removes any subtitle entry that is exactly the word: 'Ah' or 'Oh' (with 1 or more h)
       # Example:
       #   Ohhh!
       - ((Ah+)|(Oh+))\W?: {match: exact}
 
   # The group 'tidy' has all rules to replace certain patterns in your subtitles.
   tidy:
     template: common
     type: regex
     rules:
       # Description: Replace extra spaces to a single space
       # Example:
       #   Foo     bar.
       # to
       #   Foo bar.
       - \s{2,}: ' '
 
       # Description: Add space when starting phrase with '-'. It ignores tags, such as <i>, <b>
       # Example:
       #   <i>-Francine, what has happened?
       #   -What has happened? You tell me!</i>
       # to
       #   <i>- Francine, what has happened?
       #   - What has happened? You tell me!</i>
       - '(?:^(|(?:\<\w\>)))-([''"]?\w+)': { replacement: '\1- \2', flags: [multiline, unicode] }

\* The default value if none is defined



CleanIt will try to load configuration file from ~/.config/cleanit/config.yml if no configuration file is defined.
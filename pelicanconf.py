#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Blaze Developers'
SITENAME = u'The Blaze Ecosystem'
SITEURL = 'https://blaze.github.io/'
TITLE = 'The Blaze Ecosystem'
SUBTITLE = 'Connecting people to data'

PATH = 'content'

THEME = 'theme/'
TIMEZONE = 'UTC'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_RSS = 'feeds/all.rss.xml'

DEFAULT_PAGINATION = 10

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["page_hierarchy", "ipynb"]

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/{slug}.html'
SLUGIFY_SOURCE = 'basename'

STATIC_PATHS = ['images', 'CNAME']
# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# ipynb plugin
MARKUP = ('md', 'ipynb')

ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

DISQUS_SITENAME = 'blaze-ecosystem'

GOOGLE_ANALYTICS_CODE = 'UA-67320551-1'

SUMMARY_MAX_LENGTH = 10

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WordpressItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
	plugin_name = scrapy.Field()
	author = scrapy.Field()
	screenshot_1 = scrapy.Field()
	screenshot_2 = scrapy.Field()
	screenshot_3 = scrapy.Field()
	tags = scrapy.Field()
	version = scrapy.Field()
	last_updated = scrapy.Field()
	tested_up_to = scrapy.Field()
	wordpress_url = scrapy.Field()
	download_url = scrapy.Field()
	description = scrapy.Field()
	installation = scrapy.Field()
	plugin_img_url = scrapy.Field()



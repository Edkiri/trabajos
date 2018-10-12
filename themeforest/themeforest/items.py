import scrapy


class ThemeforestItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	
	full_name = scrapy.Field()

	first_name = scrapy.Field()

	last_name = scrapy.Field()

	theme_url = scrapy.Field()

	last_update = scrapy.Field()

	created = scrapy.Field()

	compatible_browsers = scrapy.Field()

	compatible_with = scrapy.Field()

	files_included = scrapy.Field()

	software_version = scrapy.Field()

	tags = scrapy.Field()

	price = scrapy.Field()

	img_url = scrapy.Field()

	author = scrapy.Field()

	last_version = scrapy.Field()

	description = scrapy.Field()

	category = scrapy.Field()

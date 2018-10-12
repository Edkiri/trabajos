from scrapy.exceptions import DropItem


class ThemeforestPipeline(object):
	def process_item(self, item, spider):
		
		if item["compatible_browsers"]:
			return item
		else:
			raise DropItem()

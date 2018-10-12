import scrapy
import random
import re
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from wordpress.items import WordpressItem

class PluginSpider(scrapy.Spider):

	name = "plugins"

	start_urls = ["https://wordpress.org/plugins/browse/popular/"]

	items_count = 0

	download_delay = 4


	def parse(self, response):
		

		for url in response.xpath("//h2[@class='entry-title']").css("a::attr(href)").extract():
			url = response.urljoin(url)
			yield scrapy.Request(url=url, callback=self.parse_items)


		next_pagination = response.xpath("//div/a[@class='next page-numbers']/@href").extract_first()
		if next_pagination:
			next_pagination = response.urljoin(next_pagination)
			yield scrapy.Request(url=next_pagination, callback=self.parse)


	# def parse_installation(self, response):
	# 	item = response.meta['item']
	# 	# item['installation'] = response.xpath("//*[@id='main']/div[2]/div[1]/ul/li[2]/a/text()").extract()
	# 	item['installation'] = response.xpath("//div[@class='plugin-installation section']/ol[1]/li/text()").extract()
	# 	self.logger.info("Visited %s", response.url)
		 
	# 	yield item
			

	def parse_items(self, response):

		# item count
		self.items_count += 1
		if self.items_count == 2000:
			raise CloseSpider()


		# Get name
		plugin_name = response.xpath("//h1[@class='plugin-title']/text()").extract_first()
		author = response.xpath("//span[@class='author vcard']/a/text()").extract_first()

		""" Looking for Screenhost """
		screenshot_1 = ""
		screenshot_2 = ""
		screenshot_3 = ""
		screenshots = response.xpath("//div[@class='plugin-screenshots section']/ul//li/figure/a/img/@src").extract()
		if screenshots:
			if len(screenshots) >= 3:
				screenshot_1 = screenshots[0]
				screenshot_2 = screenshots[1]
				screenshot_3 = screenshots[2]
			elif len(screenshots) == 2:
				screenshot_1 = screenshots[0]
				screenshot_2 = screenshots[1]
			elif len(screenshots) == 1:
				screenshot_1 = screenshots[0]

		# Version 
		version = response.xpath("normalize-space(//div[@class='entry-meta']/div[@class='widget plugin-meta']/ul/li/strong/text())").extract_first()
		last_updated = response.xpath("normalize-space(//div[@class='entry-meta']/div[@class='widget plugin-meta']/ul/li/strong/span/text())").extract_first()

		""" Loking for Tested_up_to"""
		tested = ""
		for li in response.xpath("//div[@class='widget plugin-meta']/ul/li"):
			if "Tested" in li.xpath("text()").extract_first():
				tested = response.xpath("//div[@class='widget plugin-meta']/ul/li/strong/text()").extract_first()



		# Description
		description = []
		for p in response.xpath("//div[@class='plugin-description section']/p/text()").extract():
			if len(p) > 120:
				if len(p.split(".")) > 1:
					description.append(p.split(".")[0]+"."+p.split(".")[1]+".")
					break
				elif len(p.split(".")) == 1:
					description.append(p)

		if len(description) > 1:
			if description[0][0] == ' ' or description[0][0] == ",":
				description = description[0].lstrip(",").lstrip(" ")
				description = description[0][0].upper() + description[1:]
		elif len(description) == 1:
			if description[0][0] == ' ' or description[0][0] == ",":
				description = description[0].lstrip(",").lstrip(" ")
				description = description[0][0].upper() + description[1:]

		# Setting img
		tag_img = response.xpath("//header/div[@class='entry-thumbnail']/style/text()").extract_first()
		reg = re.compile("\(\'?http.*?rev\=\d+\)*?")
		img_cleanig = reg.findall(tag_img)
		img_url = img_cleanig[0].lstrip("('").rstrip("';)")


		# setting installation
		installation = response.xpath("//div[@class='plugin-installation section']/*").extract()
		cleaned_installation = "".join(installation)


		""" Making description """
		lista1 = [
			"Now you can",
			"It's the time!",
			"It's the time! You can",
			"How to",
			"Let's",
			"Today you can"]

		lista2 = [
			"for free.",
			"free.",
			"free and safe."]	

		lista3 = [
			"wp plugin",
			"plugin",
			"website plugin"]

		lista4 = [
			"install",
			"use"]	

		lista5 = [
			"project.",
			"personal or business site.",
			"own project.",
			"client."]

		lista6 = [
			"WP Plugin",
			"Plugin",
			"wordpress plugin",
			"themeforest plugin"]	

		lista7 = [
			"maybe",
			"perhaps",
			"possibly",
			"conceivably",
			"it is possible"]

		lista8 = [
			"What could you do with this awesome wp-plugin?",
			"What can you do with this wp plugin?",
			"What could you do with this great plugin?",
			"What could you do with this template?",
			"Check out what everyone is talking about this wpplugin.",
			"Why you should buy this plugin?",
			"Why you should buy this wordpress plugin?"]

		lista9 = [
			"Are you thinking of installing {name} plugin?".format(name=plugin_name),
			"Are you thinking of installing this wordpress plugin?",
			"Are you thinking of installing this wp-plugin?",
			"Do you want to install {name}?".format(name=plugin_name),
			"Do you want to test {name}?".format(name=plugin_name)]

		p1 = "<span class='dfirst'>{lista1} <strong>Download {name} {lista3} {lista2}. <strong>Get {name} {version}</strong> (or higher version) {lista3} created by {author} and {lista4} it for your {lista5}. This {lista6} {version} version was updated on {updated} but {lista7} there is a newer version available.</span>".\
				format(
					lista1=lista1[random.randint(0,5)], lista2=lista1[random.randint(0,2)],
					lista3=lista3[random.randint(0,2)], lista4=lista4[random.randint(0,1)],
					lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)],
					lista7=lista7[random.randint(0,4)], name=plugin_name, author=author,
					version=version, updated=last_updated)
		p2 = ""
		if description:
			p2 = "<span class='dsecond'>{lista8}</span> <span class='desctheme'>{description}</span> <span class='dthird'>{lista9} Let's check out:</span>".\
				format(
					lista8=lista8[random.randint(0,6)], lista9=lista9[random.randint(0,4)],
					description=description)


		p3 = ""
		if installation:
			p3 = "<span class='dthird'><h2>How to Install {name} WordPress Plugin?</h2></span> <span class='descplugin'>{installation}</span>".\
				format(name=plugin_name, installation=cleaned_installation)



		# Return items
		item = WordpressItem()
	
		item['plugin_name'] = plugin_name
		item['author'] = author
		item['plugin_img_url'] = img_url

		item['last_updated'] = last_updated

		item['screenshot_1'] = screenshot_1
		item['screenshot_2'] = screenshot_2
		item['screenshot_3'] = screenshot_3
		
		item['tags'] = response.xpath("//div[@class='tags']/a/text()").extract()
		item['version'] = version
		item['tested_up_to'] = tested
		item['wordpress_url'] = response.url
		item['download_url'] = response.xpath("//a[@class='plugin-download button download-button button-large']/@href").extract_first()
		item['description'] = p1 + p2 + p3
		item['installation'] = installation

		return item

		# request = scrapy.Request(url="https://wordpress.org/support/plugin/updraftplus", callback=self.parse_installation)
		# url = response.xpath("//ul[@class='tabs clear']/li/a/@href").extract_first()
		# request = scrapy.Request(url=url, callback=self.parse_installation)
		# request.meta['item'] = item
		# return request

		# todo = l.load_item()


		# yield {
		# 	"plugin_name": response.xpath("//h1[@class='plugin-title']/text()").extract_first(),
		# 	"author": response.xpath("//span[@class='author vcard']/a/text()").extract_first(),
		# 	"screenshot_1": screenshot_1,
		# 	"screenshot_2": screenshot_2,
		# 	"screenshot_3": screenshot_3,
		# 	"tags": response.xpath("//div[@class='tags']/a/text()").extract(),
		# 	"version": version,
		# 	"tested_up_to": tested,
		# 	"wordpress_url": response.url,
		# 	"download_url": response.xpath("//a[@class='plugin-download button download-button button-large']/@href").extract_first(),
		# 	"description": description,
		# 	# "img_url": "",
		# 	# "installaion": get_installation(response)

		# }

"""plugin name, 
author, 
screenshot img1,screenshot img2,screenshot img3
tags, version, last updated, tested up to, wordpress url, 
download url, description details,

 description installation, ,

img, 
img es la principal

"""


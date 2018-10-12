import json
import random
import scrapy
from scrapy.exceptions import CloseSpider

class WordpressSpider(scrapy.Spider):
	name = 'wordpress'

	the_url = "https://api.wordpress.org/themes/info/1.1/?callback=jQuery112406090698302568378_1539087885022&action=query_themes&request%5Bper_page%5D=24&request%5Blocale%5D=en_US&request%5Bfields%5D%5Bdescription%5D=true&request%5Bfields%5D%5Bsections%5D=false&request%5Bfields%5D%5Btested%5D=true&request%5Bfields%5D%5Brequires%5D=true&request%5Bfields%5D%5Bdownloaded%5D=false&request%5Bfields%5D%5Bdownloadlink%5D=true&request%5Bfields%5D%5Blast_updated%5D=true&request%5Bfields%5D%5Bhomepage%5D=true&request%5Bfields%5D%5Btheme_url%5D=true&request%5Bfields%5D%5Bparent%5D=true&request%5Bfields%5D%5Btags%5D=true&request%5Bfields%5D%5Brating%5D=true&request%5Bfields%5D%5Bratings%5D=true&request%5Bfields%5D%5Bnum_ratings%5D=true&request%5Bfields%5D%5Bextended_author%5D=true&request%5Bfields%5D%5Bphoton_screenshots%5D=true&request%5Bfields%5D%5Bactive_installs%5D=true&request%5Bbrowse%5D=popular&request%5Bpage%5D={}&_=153908788502{}"

	pag_1 = 1
	pag_2 = 2

	item_count = 0

	download_delay = 5

	start_urls = [the_url.format(pag_1, pag_2)]


	def parse(self, response):

		response_cleaned = response.text.lstrip("jQuery112406090698302568378_1539087885022(").rstrip(");")

		data = json.loads(response_cleaned)

		while data['info']['page'] < 151:
			yield scrapy.Request(url=self.the_url.format(self.pag_1, self.pag_2), callback=self.parse_themes)


	def parse_themes(self, response):
		self.pag_1 += 1
		self.pag_2 += 1

		response_cleaned = response.text.lstrip("jQuery112406090698302568378_1539087885022(").rstrip(");")
		data = json.loads(response_cleaned)

		for theme in data['themes']:
			""" Extract theme's data """
			self.item_count += 1
			if self.item_count == 2100:
				raise CloseSpider()



			""" Cleaning description """
			if len(theme['sections']['description'].split(".")) > 1:
				description = theme['sections']['description'].split(".")[0] +"."+ theme['sections']['description'].split(".")[1]+"."
			elif len(theme['sections']['description'].split(".")) == 1:
				description = theme['sections']['description'].split(".")[0]

			# Spining description
			lista1 = [
				"Now you can",
				"It's the time!",
				"It's the time! You can",
				"How to",
				"Let's",
				"Today you can",]

			lista2 = [
				"wordpress theme",
				"wp theme"]

			lista3 = [
				"for free",
				"free",
				"free and safe"]

			lista4 = [
				"website template",
				"template",
				"wp theme"]

			lista5 = [
				"install",
				"use"]

			lista6 = [
				"project",
				"personal or business site",
				"own project",
				"client"]

			lista7 = [
				"WP Theme",
				"theme",
				"wordpress theme",
				"free wordpress.org theme"]

			lista8 = [
				"maybe",
				"perhaps",
				"possibly",
				"conceivably",
				"it is possible"]

			lista9 = [
				"What could you do with this awesome wp-theme?",
				"What can you do with this wp theme?",
				"What could you do with this great theme?",
				"What could you do with this template?",
				"Check out what everyone is talking about this wptheme.",
				"Why you should get this theme?",
				"Why you should use this wordpress theme?"]

			lista10 = [
				"Are you thinking of installing {} theme?".format(theme['name']),
				"Are you thinking of installing this wordpress theme?",
				"Are you thinking of installing this wp-theme",
				"Do you want to install {}?".format(theme['name']),
				"Do you want to test {}?".format(theme['name'])]

			p1 = "<span class='dfirst'>{lista1} <strong>Download {theme_name} {lista2} {lista3}. <strong>Get {theme_name} {version}</strong> (or higher version) {lista4} and {lista5} it for your {lista6}. This {lista7} {version} version was updated on {updated} but {lista8} there is a newer version available.</span>"\
							.format(
								lista1=lista1[random.randint(0,5)], lista2=lista2[random.randint(0,1)],
								lista3=lista3[random.randint(0,2)], lista4=lista4[random.randint(0,2)],
								lista5=lista5[random.randint(0,1)], lista6=lista6[random.randint(0,3)],
								lista7=lista7[random.randint(0,3)], lista8=lista8[random.randint(0,4)],
								theme_name=theme['name'], version=theme['version'],
								updated=theme['last_updated'])

			p2 = "<span class='dsecond'>{lista9}</span> <span class='desctheme'>{description}</span> <span class='dthird'>{lista10} Let's check out:</span>".\
					format(
						lista9=lista9[random.randint(0,6)], lista10=lista10[random.randint(0,4)],
						description=description)



			""" Cleaning tags """
			tags_cleaned = []
			for tag in theme['tags'].values():
				tags_cleaned.append(tag)



			""" Return items """
			yield {	
				'theme_name': theme['name'],
				'author': theme['author']['display_name'],
				'img_url': theme['screenshot_url'],
				'version': theme['version'],
				'last_update': theme['last_updated'],
				'tags': tags_cleaned,
				'preview_url': theme['preview_url'],
				'download_url': theme['download_link'],
				'wordpress_url': theme['homepage'],
				'description': p1 + p2
			}


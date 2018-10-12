import scrapy
import re
import random

from scrapy.exceptions import CloseSpider
from scrapy.exceptions import IgnoreRequest
from scrapy.loader import ItemLoader
from themeforest.items import ThemeforestItem



class ThemeForestSpider(scrapy.Spider):

	name = "themeforest"

	start_urls = ["https://codecanyon.net/category/wordpress?sort=saless"]

	item_count = 0
	download_delay = 1

	def parse(self, response):


		"""Looking for items"""
		for url in response.xpath("//article[@class='_3eK24']/section/div/h3").css("a::attr(href)").extract():
			url = response.urljoin(url)
			yield scrapy.Request(url=url, callback=self.parse_items)

		"""Next pagination"""
		next_page = response.css("a.riG7A::attr(href)").extract_first()
		if next_page:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(url=next_page, callback=self.parse)

	def parse_items(self, response):
		
		"""		# Return items    """

		# Items count
		self.item_count += 1
		if self.item_count == 2000:
			raise CloseSpider("Tamos listos por aquí")



		# Set names
		full_name = response.xpath("normalize-space(//div[@class='item-header__title']/h1/text())").extract_first()
		first_name = ""
		last_name = ""
		if " - " in full_name:
			first_name = full_name.split(" - ")[0]
			last_name = full_name.split(" - ")[1]
			last_name = " ".join(last_name.split())
		if " -" in full_name:
			first_name = full_name.split(" -")[0]
			last_name = full_name.split(" -")[1]
			last_name = " ".join(last_name.split())
		if " | " in full_name:
			first_name = full_name.split(" | ")[0]
			last_name = full_name.split(" | ")[1]
			last_name = " ".join(last_name.split())
		if " – " in full_name:
			first_name = full_name.split(" – ")[0]
			last_name = full_name.split(" – ")[1]
			last_name = " ".join(last_name.split())
		if first_name == "":
			first_name = full_name


		""" Times """
		
		# updated
		updated = response.xpath("normalize-space(//time[@class='updated']/text())").extract_first()
		# created
		created = response.xpath("normalize-space(//div[@class='meta-attributes']" + \
									"/table/tbody/tr[2]/td[2]/span/text())").extract_first()


		 # """ seting tags """

		browsers = []
		for i in range(1,5):
			if "Compatible Browsers" in response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(i)).extract_first():
				browsers = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/a/text()".format(i)).extract()

		compatibles = []
		for i in range(2,6):
			if "Compatible With" in response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(i)).extract():
				compatibles = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/a/text()".format(i)).extract()

		# cleaning compatibles
		s = " "
		p = re.compile(r'[a-zA-Z][a-zA-Z]+')
		todo = p.findall(s.join(compatibles))

		cleaned_compatible = []

		for match in todo:
			if match not in cleaned_compatible:
				cleaned_compatible.append(match)

		cleaned_compatible = ", ".join(cleaned_compatible)

		# continue extracting tags
		files_included = []
		for i in range(3,7):
			if "Files Included" in response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(i)).extract_first():
				files_included = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/a/text()".format(i)).extract()

		software_version = [] 
		for i in range(3,8):
			if "Software Version" in response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(i)).extract():
				software_version = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/a/text()".format(i)).extract()
			
		tags = []
		for i in range(3,10):
			a = i
			if "Tags" in response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(a)).extract():
				tags = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/span/a/text()".format(a)).extract()


		""" Easys """
		price = response.xpath("//span[@class='js-purchase-price']/text()").extract_first()
		img_url = response.xpath("//div[@class='item-preview -preview-live']/a").css("img::attr(src)").extract_first()
		author = response.xpath("//div[@class='media']/div/h2/a/text()").extract_first()


			# Category 
		cleaned_category = []
		category = response.xpath("//div[@class='context-header ']/div/nav/a/text()").extract()
		if not category: 
			category = response.xpath("//div[@class='context-header']/div/nav/a/text()").extract()
		for item in category:
			if item != "Home" and item != "Files":
				cleaned_category.append(item)

		# cleaning last version
		ahora_si = ""

		v = response.xpath("normalize-space(//pre/text())").extract_first()
		reg = re.compile("\d\.\d\.?\d?\.?\d?")
		todito = reg.findall(v)
		if len(todito) > 0:
			ahora_si = "v."+todito[0]

		""" Description """

		description = []
		text = response.xpath("//div[@class='user-html']/p/text()").extract()
		for p in text:
			if len(p) > 110:
				exp = re.compile("\n")
				description = exp.sub("", p)
				break

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
			"we plugin",
			"plugin"]

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
			"What could you do with this awesome wp-plugin?",
			"What can you do with this wp plugin?",
			"What could you do with this great plugin?",
			"What could you do with this template?",
			"Check out what everyone is talking about this wpplugin.",
			"Why you should buy this plugin?",
			"Why you should buy this wordpress plugin?"]

		lista8 = [
			"Are you thinking of buying {first} plugin?".format(first=first_name),
			"Are you thinking of buying this wordpress plugin?",
			"Are you thinking of installing this wp-plugin?",
			"Do you want to buy {name}?".format(name=full_name),
			"Do you want to buy {first}?".format(first=first_name)
		]

		p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name}</strong> {lista2}. <strong>Buy {first_name}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, created=created, updated=updated,)	

		if last_name != "" and ahora_si != "":
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_version} {last_name}</strong> {lista2}. <strong>Buy {first_name} {last_version}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_version=ahora_si, last_name=last_name,
						created=created, updated=updated,)		

		if last_name != "":
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_name}</strong> {lista2}. <strong>Buy {first_name}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_name=last_name,
						created=created, updated=updated,)	

		if ahora_si != "" and cleaned_compatible != []:
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_version}</strong> {lista2}. <strong>Buy {first_name} {last_version}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {compatible}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_version=ahora_si,
						created=created, updated=updated,)		

		if ahora_si != "" and cleaned_compatible != []:
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_version}</strong> {lista2}. <strong>Buy {first_name} {last_version}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {compatible}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_version=ahora_si,
						created=created, updated=updated,)		

		if cleaned_compatible != [] and last_name != "":
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_name}</strong> {lista2}. <strong>Buy {first_name}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {compatible}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_name=last_name,
						created=created, updated=updated, compatible=cleaned_compatible)
		
		if cleaned_compatible != [] and last_name != "" and ahora_si != "":
			p1 = "<span class='dfirst'>{lista1}<strong>Download {first_name} {last_version} {last_name}</strong> {lista2}. <strong>Buy {first_name} {last_version}</strong> {lista3} and {lista4} it for your {lista5}. This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {compatible}.</span>".format( \
						lista1=lista1[random.randint(0, 5)], lista2=lista2[random.randint(0, 2)],
						lista3=lista3[random.randint(0, 1)], lista4=lista4[random.randint(0, 1)],
						lista5=lista5[random.randint(0, 3)], lista6=lista6[random.randint(0, 3)],
						first_name=first_name, last_version=ahora_si, last_name=last_name,
						created=created, updated=updated, compatible=cleaned_compatible)		

		p2 = ""
		if description != []:
			p2 = "<span class='dsecond'>{lista7}</span> <span class='desctheme'>{description}</span> <span class='dthird'>{lista8} Let's check out:</span>".format( \
						lista7=lista7[random.randint(0, 6)], lista8=lista8[random.randint(0, 4)],
						description=description)
		else:
			p2 = "<span class='dsecond'>{lista7}</span> <span class='dthird'>{lista8} Let's check out:</span>".format( \
						lista7=lista7[random.randint(0, 6)], lista8=lista8[random.randint(0, 4)],)




		""" Yield item.load_item() """

		l = ItemLoader(item=ThemeforestItem(), response=response)

		# names
		l.add_value('full_name', full_name)
		l.add_value('first_name', first_name)
		l.add_value('last_name', last_name)
		l.add_value('theme_url', response.url)

		# times
		l.add_value('last_update', updated)
		l.add_value('created', created)

		# tr/td barra de la derecha
		l.add_value('compatible_browsers', browsers)
		l.add_value('compatible_with', compatibles)
		l.add_value('files_included', files_included)
		l.add_value('software_version', software_version)
		l.add_value('tags', tags)

		# easys
		l.add_value('price', price)
		l.add_value('img_url', img_url)
		l.add_value('author', author)
		l.add_value('category', cleaned_category)

		# hardest
		l.add_value('last_version', ahora_si)
		l.add_value('description', p1 + p2)

		yield l.load_item()


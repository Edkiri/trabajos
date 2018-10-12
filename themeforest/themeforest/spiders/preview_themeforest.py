import scrapy
import re
import random
from scrapy.exceptions import CloseSpider
from scrapy.exceptions import IgnoreRequest
from scrapy.loader import ItemLoader
from themeforest.items import ThemeforestItem



class ThemeForestSpider(scrapy.Spider):

	name = "themeforest-best"

	start_urls = ["https://themeforest.net/category/wordpress?sort=sales"]

	item_count = 0
	download_delay = 1

	def parse(self, response):


		"""Looking for items"""

		# url IS NOT FROM HERE
		for url in response.xpath("//article[@class='_3eK24']/section/div/h3").css("a::attr(href)").extract():
			url = response.urljoin(url)
			yield scrapy.Request(url=url, callback=self.parse_items)

		"""Next pagination"""
		next_page = response.css("a.riG7A::attr(href)").extract_first()
		if next_page:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(url=next_page, callback=self.parse)

	def parse_items(self, response):
		
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

		#created
		created = response.xpath("normalize-space(//tr/td/span)").extract_first()
		updated = response.xpath("normalize-space(//time[@class='updated'])").extract_first()

		# seting Tags
		browsers = []
		index = 0
		for i in range(1, 10):
			navigators = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[5]/td[2]/a/text()".format(i)).extract()
			if "Chrome" in navigators:
				browsers = navigators
				index = i

		cleaned_navigators = ", ".join(browsers) 

		compatibles = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[6]/td[2]/a/text()".format(index)).extract()

		framework = ""
		for i in range(3, 8):
			if "Framework" == response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[1]/text()".format(i)).extract_first():
				framework = response.xpath("//table[@class='meta-attributes__table']/tbody/tr[{}]/td[2]/a/text()".format(i)).extract_first()


		files_included = ""
		for i in range(4, 10):
			prueba = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[1]/text()".format(index, i)).extract_first()
			if prueba == "ThemeForest Files Included":
				files_included = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[2]/a/text()".format(index, i)).extract()
		
		columns = ""
		for i in range(6, 12):
			prueba = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[1]/text()".format(index, i)).extract_first()
			if prueba == "Columns":
				columns = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[2]/a/text()".format(index, i)).extract_first()
		if columns != "":
			if "+" in columns:
				regx = re.compile("\+")
				columns = "more than " + regx.sub("", columns)

		software_version = ""
		for i in range(6, 12):
			prueba = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[1]/text()".format(index, i)).extract_first()
			if prueba == "Software Version":
				software_version = response.xpath("//*[@id='content']/div/div[2]/div[{}]/div/table/tbody/tr[{}]/td[2]/a/text()".format(index, i)).extract()




		#getting img_url
		a = response.xpath("//div[@class='box--no-padding']/div/a")
		img_url = a.css("img::attr(src)").extract_first()




		# cleaning compatible info 
		s = " "
		p = re.compile(r'[a-zA-Z][a-zA-Z]+')
		todo = p.findall(s.join(compatibles))

		cleaned_data = []

		for match in todo:
			if match not in cleaned_data:
				cleaned_data.append(match)

		cleaned_compatible = ", ".join(cleaned_data)



		# cleaning last version
		ahora_si = ""

		v = response.xpath("normalize-space(//pre/text())").extract_first()
		reg = re.compile("\*")
		cleaned_version = reg.sub("", v)
		reg2 = re.compile("\s\d\.\d\.?\d?")
		todito = reg2.findall(cleaned_version)
		reg3 = re.compile("\s")

		if len(todito) > 0:
			ahora_si = "v."+reg3.sub("", todito[0])


		# Descrption *****
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
			"website template",
			"template"]

		lista4 = [
			"install",
			"use"]	

		lista5 = [
			"project.",
			"personal or business site.",
			"own project.",
			"client."]

		lista6 = [
			"WP Theme",
			"theme",
			"wordpress theme",
			"themeforest theme"]	

		lista7 = [
			"What could you do with this awesome wp-theme?",
			"What can you do with this wp theme?",
			"What could you do with this great theme?",
			"What could you do with this template?",
			"Check out what everyone is talking about this wptheme.",
			"Why you should buy this theme?",
			"Why you should buy this wordpress theme?"]

		lista8 = [
			"Are you thinking of buying {first} theme?".format(first=first_name),
			"Are you thinking of buying this wordpress theme?",
			"Are you thinking of installing this wp-theme?",
			"Do you want to buy {name}?".format(name=full_name),
			"Do you want to buy {first}?".format(first=first_name)
		]


		# p1
		p1 = "<span class='dfirst'>{lista1} <strong>Download {name}</strong> {lista2}. <strong>Buy {first}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns. <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)],first=first_name, last= last_name, lista2=lista2[random.randint(0,2)], lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], created=created, updated=updated, browsers=cleaned_navigators, columns=columns, name=full_name, compatible=cleaned_compatible)
		if len(todito) > 0 and framework != "" and last_name != "":
			p1 = "<span class='dfirst'>{lista1} <strong>Download {first} {version} {last}</strong> {lista2}. <strong>Buy {first} {version}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns and use the {framework} framework. <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)], \
																first=first_name, version=ahora_si, \
																last= last_name, lista2=lista2[random.randint(0,2)], \
																lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], \
																lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], \
																created=created, updated=updated, browsers=cleaned_navigators, \
																columns=columns, framework=framework, name=full_name, \
																compatible=cleaned_compatible)

		if len(todito) > 0 and framework != "":
			p1 = "<span class='dfirst'>{lista1} <strong>Download {first} {version}</strong> {lista2}. <strong>Buy {first} {version}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns and use the {framework} framework. <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)], \
																first=first_name, version=ahora_si, \
																last= last_name, lista2=lista2[random.randint(0,2)], \
																lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], \
																lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], \
																created=created, updated=updated, browsers=cleaned_navigators, \
																columns=columns, framework=framework, name=full_name, \
																compatible=cleaned_compatible)
		elif len(todito) > 0 and last_name != "":
			p1 = "<span class='dfirst'>{lista1} <strong>Download {first} {version} {last}</strong> {lista2}. <strong>Buy {first} {version}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)], \
																first=first_name, version=ahora_si, \
																last= last_name, lista2=lista2[random.randint(0,2)], \
																lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], \
																lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], \
																created=created, updated=updated, browsers=cleaned_navigators, \
																columns=columns, name=full_name, \
																compatible=cleaned_compatible)
		elif len(todito) > 0:
			p1 = "<span class='dfirst'>{lista1} <strong>Download {first} {version}</strong> {lista2}. <strong>Buy {first} {version}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)], \
																first=first_name, version=ahora_si, \
																lista2=lista2[random.randint(0,2)], \
																lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], \
																lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], \
																created=created, updated=updated, browsers=cleaned_navigators, \
																columns=columns, name=full_name, \
																compatible=cleaned_compatible)
		elif framework != "":
			p1 = "<span class='dfirst'>{lista1} <strong>Download {name}</strong> {lista2}. <strong>Buy {first}</strong> {lista3} and {lista4} it for your {lista5} This {lista6} was released on {created} and updated on {updated}. Also it is compatible with {browsers}, has {columns} columns and use the {framework} framework. <strong>{name}</strong> is compatible with {compatible}.".format(lista1=lista1[random.randint(0,5)], \
																first=first_name, \
																last= last_name, lista2=lista2[random.randint(0,2)], \
																lista3=lista3[random.randint(0,1)], lista4=lista4[random.randint(0,1)], \
																lista5=lista5[random.randint(0,3)], lista6=lista6[random.randint(0,3)], \
																created=created, updated=updated, browsers=cleaned_navigators, \
																columns=columns, framework=framework, name=full_name, \
																compatible=cleaned_compatible)
		

		# p2
		p2 = "</span><span class='dsecond'>{lista7}</span><span class='dthird'>{lista8} Let's check out:</span>".format(lista7=lista7[random.randint(0,6)], lista8=lista8[random.randint(0,4)])


		# cleaned category
		cleaned_category = []
		category = response.xpath("//div[@class='context-header ']/div/nav/a/text()").extract()
		if not category: 
			category = response.xpath("//div[@class='context-header']/div/nav/a/text()").extract()
		for item in category:
			if item != "Home" and item != "Files":
				cleaned_category.append(item)




		# Return items
		l = ItemLoader(item=ThemeforestItem(), response=response)
		l.add_value('full_name', full_name)
		l.add_value('first_name', first_name)
		l.add_value('last_name', last_name)
		l.add_value('theme_url', response.url)
		l.add_value('last_update', updated)
		l.add_value('created', created)
		l.add_value('compatible_browsers', browsers)
		l.add_value('compatible_with', cleaned_compatible)
		l.add_value('framework', framework)
		l.add_value('files_included', files_included)
		l.add_value('columns', columns)
		l.add_value('software_version', software_version)
		l.add_value('tags', response.xpath("//tr/td/span[@class='meta-attributes__attr-tags']/a/text()").extract())
		l.add_value('price', response.xpath("//b/span[@class='js-purchase-price']/text()").extract_first())
		l.add_value('img_url', img_url)
		l.add_value('author', response.xpath("//div[@class='media']/div/h2/a/text()").extract_first())
		l.add_value('last_version', ahora_si)
		l.add_value('description', p1 + p2)
		l.add_value('category', cleaned_category)

		yield l.load_item()

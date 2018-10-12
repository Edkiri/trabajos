import scrapy
import random

class BirthdaysSpider(scrapy.Spider):
	name = 'onthisday'

	start_urls = ["https://www.onthisday.com/birthdays-calendar.php"]

	def parse(self, response):

		for url in response.css("section.calendar-month ul a::attr(href)").extract():
			url = response.urljoin(url)
			yield scrapy.Request(url=url, callback=self.looking_for_interest)


	def looking_for_interest(self, response):
		"""Buscando personas destacadas"""
		for url in response.css("div.section--person-of-interest a.section__link::attr(href)").extract():
			url = response.urljoin(url)
			yield scrapy.Request(url=url, callback=self.parse_details)
			
		"""Página siguiente"""
		next_page = response.css("ul.pag li > a::attr(href)").extract_first()
		if next_page:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(url=next_page, callback=self.looking_for_interest)


	def parse_details(self, response):
		"""Extrayendo información"""

		#set description
		year_born = response.xpath("//span[@property='birthDate']/a/text()").extract()[1]
		month_born = response.xpath("//span[@property='birthDate']/a/text()").extract()[0].split(" ")[0]
		day_born = response.xpath("//span[@property='birthDate']/a/text()").extract()[0].split(" ")[1]
		name = response.xpath("//span[@property='name']/text()").extract_first()
		birthdate = month_born + ", " + day_born
		birthplace = response.xpath("//span[@property='birthPlace']/text()").extract_first()
		try:
			died = response.xpath("//span[@property='deathDate']/a/text()").extract()[0] + ", " + response.xpath("//span[@property='deathDate']/a/text()").extract()[1]
		except:
			died = ""

		def rd_int(min, max):
			return random.randint(min, max)

		sentences = [
			"Are you searching for",
			"Are you looking for",
			"Do you know",
			"Do you want to know",
			"Do you need to know",
			"Are you interested in knowing",
			"Would do you like to know", 
		]

		died_social_sentences = [
			"Twitter, Facebook, Youtube fan pages?",
			"related twitter accounts, facebook pages or youtube channels?",
			"youtube channels, twitter accounts, facebook pages or interesting websites?",
			"facebook pages, youtube channels or twitter accounts?"
		]
		social_sentences = [
			"Instagram profile, Facebook page, Youtube channel or Twitter account?",
			"Facebook page, Instagram profile, Youtube channel or Twitter account?",
			"Twitter account, Instagram profile, Youtube channel or Facebook page?"
		]

		# descraption
		pattern = "<p class='celeb'>{} <strong>{}'s Age and Birthday date</strong>? <strong>{}</strong> was born on {} in {}.</p><p> How old is this celebrity? And what are his/her social media accounts? {} {}'s {} Let's check out:</p>".format(sentences[rd_int(0,6)], name, name, birthdate, birthplace, sentences[rd_int(0,6)], name, social_sentences[rd_int(0,2)])
		if int(response.xpath("//span[@property='birthDate']/a/text()").extract()[1]) < 1915:
			pattern = "<p class='celeb'>{} {}'s Age and Birthday date? {} was born on {} in {}. <strong>{}</strong> died on {}.</p><p> {} any {}'s {} Let's check out:</p>".format(sentences[rd_int(0,6)], name, name, birthdate, birthplace, name, died, sentences[rd_int(0,6)], name, died_social_sentences[rd_int(0,3)])
		


		description = response.xpath("//span[@property='description']/text()").extract_first()
		description = pattern  + "<p>{}</p>".format(description)

		yield {
			'name': name,
			'born': response.xpath("//span[@property='birthDate']/a/text()").extract()[0]+ ", " + response.xpath("//span[@property='birthDate']/a/text()").extract()[1],
			'birthplace': birthplace,
			'birthsign': response.xpath("//p/b/a/text()").extract_first(),
			'died': died,
			'profession': response.xpath("//span[@property='jobTitle']/a/text()").extract_first(),
			'image_url': "https://www.onthisday.com" + response.css("p.no-margin-bottom > img::attr(src)").extract_first(),
			'month_born': month_born,
			'year_born': year_born,
			'day_born': day_born,
			'nation': response.css("figure > a > img::attr(alt)").extract_first(),
			'description': description,
		}
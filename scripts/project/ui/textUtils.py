import math
import re

class GibberishDetector(object):
	"""Will evaluate the string to determine if it was just random characters pressed on the keyboard..
	
	Source: https://www.codeproject.com/articles/894766/gibberish-classification-algorithm-and-implementat#:~:text=An%20algorithm%20to%20classify%20whether%20text%20is%20gibberish,text%2C%20and%20a%20high%20one%20means%20gibberish%20text.
	
	Args:
		text (str): The string to evaluate.
	
	Example:
			
		txt1 = 'asdfghkl;' #'12345'
		txt2 = 'Hello, this is a lot of text.  Do you think it is jibberish? If you do, then sorry. It took me a long time to formulate these thoughts.'
		detector1 = project.ui.textUtils.GibberishDetector(txt1)
		detector2 = project.ui.textUtils.GibberishDetector(txt2)
		
		print '==============================================='
		print 'This example should FAIL.'
		print 'Detecting gibberish: %s' % (txt1)
		if detector1.isGibberish():
			print "Result: C'mon, did you just smash keys on the keyboard!?!"
		else:
			print "Result: Thanks for the effort!"
			
		print system.util.jsonEncode( detector1.getResults(), 4 )
		
		
		print '==============================================='
		print 'This example should PASS.'
		print 'Detecting gibberish: %s' % (txt2)
		if detector2.isGibberish():
			print "Result: C'mon, did you just smash keys on the keyboard!?!"
		else:
			print "Result: Thanks for the effort!"
			
		print system.util.jsonEncode( detector2.getResults(), 4 )
	"""
	def __init__(self, text, minLength=10, minWords=2):
		self.__text = text
		self.__minLength = minLength
		self.__minWords = minWords
		self.__isEmptyString = False
		self.__isGibberish = True
		
		self.__chunk_size = 35
		self.__chunks =  []
		
		self__classification = 100.0
		self.__ucpcp = 0.0
		self.__vp = 0.0
		self.__wtcr = 0.0
		self.__ucpcp_dev = 0.0
		self.__vp_dev = 0.0
		self.__wtcr_dev = 0.0
		
		self.__classify()

	
	def isEmptyString(self):
		return self.__isEmptyString


	def isGibberish(self):
		return self.__isGibberish

	
	def getConfidence(self):
		if self.__isEmptyString:
			return 0.0
		
		return 100.0 - self.__classification


	def getResults(self):
		return {
			'percents': {
				'unique_chars_per_chunk_percentage': self.__ucpcp, 'vowels_percentage': self.__vp, 'word_to_char_ratio': self.__wtcr
			},
			'deviations': {
				'unique_chars_per_chunk_percentage': self.__ucpcp_dev, 'vowels_percentage': self.__vp_dev, 'word_to_char_ratio': self.__wtcr_dev
			},
			'chunk_size': self.__chunk_size,
			'classification': self.__classification,
			'isEmptyString': self.__isEmptyString,
			'isGibberish': self.__isGibberish,
			'text': self.__text
		}


	def getText(self):
		return self.__text
	
	
	def __split_in_chunks(self, chunk_size):
		chunks = []
		for i in range(0, len(self.__text), chunk_size):
			chunks.append(self.__text[i:i+chunk_size])
		if len(chunks) > 1 and len(chunks[-1]) < 10:
			chunks[-2] += chunks[-1]
			chunks.pop(-1)
		
		return chunks
	
	
	def __unique_chars_per_chunk_percentage(self, chunk_size):
		self.__chunks = self.__split_in_chunks(chunk_size)
						
		unique_chars_percentages = []
		for chunk in self.__chunks:
			total = float(len(chunk))
			unique = float(len(set(chunk)))
			unique_chars_percentages.append(unique / total)
		
		return (sum(unique_chars_percentages) / len(unique_chars_percentages)) * 100.0
	
	
	def __vowels_percentage(self):
		vowels = 0.0
		total = 0.0
		for c in self.__text:
			if not c.isalpha():
				continue
			total += 1.0
			if c in "aeiouAEIOU":
				vowels += 1.0
		
		if total != 0.0:
			return (vowels / total) * 100
		else:
			return 0.0
	
	
	def __word_to_char_ratio(self):
		chars = float(len(self.__text))
		words = float(len([x for x in re.split(r"[\W_]", self.__text) if x.strip() != ""]))
		return (words / chars) * 100
	
	
	def __deviation_score(self, percentage, lower_bound, upper_bound):
		if percentage < lower_bound:
			return math.log(lower_bound - percentage, lower_bound) * 100
		elif percentage > upper_bound:
			return math.log(percentage - upper_bound, 100 - upper_bound) * 100
		else:
			return 0.0
	
	
	def __classify(self):
		if self.__text is None or len(self.__text) == 0:
			self.__isEmptyString = True
			self.__classification = 0.0
		else:
			self.__isEmptyString = False
			
			if len(self.__text) <= self.__minLength or len(self.__text.split(' ')) < self.__minWords:
				self.__classification = 100.0
			else:
				if len(self.__text) < 35:
					self.__chunk_size = len(self.__text) / 1
					
				self.__ucpcp = self.__unique_chars_per_chunk_percentage(self.__chunk_size)
				self.__vp = self.__vowels_percentage()
				self.__wtcr = self.__word_to_char_ratio()
	
				ucpcp_min = 45
				ucpcp_max = 55
				
				vp_min = 35
				vp_max = 45
				
				wtcr_min = 15
				wtcr_max = 20
				if len(self.__text) < 35:
					ucpcp_min = 25
					ucpcp_max = 85
					
					vp_min = 25
					vp_max = 55
					
					wtcr_min = 10
					wtcr_max = 45
					
				self.__ucpcp_dev = max(self.__deviation_score(self.__ucpcp, ucpcp_min, ucpcp_max), 1.0)
				self.__vp_dev = max(self.__deviation_score(self.__vp, vp_min, vp_max), 1.0)
				self.__wtcr_dev = max(self.__deviation_score(self.__wtcr, wtcr_min, wtcr_max), 1.0)
	
				self.__classification = max((math.log10(self.__ucpcp_dev) + math.log10(self.__vp_dev) + math.log10(self.__wtcr_dev)) / 6 * 100, 1.0)
				
				self.__isGibberish = self.__classification >= 50.0
		
	
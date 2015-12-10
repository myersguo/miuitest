# coding=utf-8

'''
@author myersguo

0. 基本思路来源于selenium ide,链接http://www.seleniumhq.org/docs/02_selenium_ide.jsp
1. 定义一个json的数组的testcase
2. 读取该testcase,对每一条记录执行
eg:
	testcases = []
	testcase = ('url','https://buy.mi.com/in/book','')
	testcases.append(testcase)
	testcase = ('text','#enter_user input.first-enter-item','267255090')
	testcases.append(testcase)
	testcase = ('text','#miniLogin_pwd','gg111111')
	testcases.append(testcase)
	testcase = ('click','message_LOGIN_IMMEDIATELY','')
	testcases.append(testcase)
3. 
'''

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class UITestDriver():
	
	@property
	def driverhost(self):
		return self._driverhost
	@property
	def driverurl(self):
		return 'http://'+self.driverhost+':4444/wd/hub'
	
	@property
	def driver(self):
		return self._driver
			
	def __init__(self, host='127.0.0.1'):
		self._driverhost = host
		self._driverurl = 'http://'+self.driverhost+':4444/wd/hub'
		self._driver = webdriver.Remote(
	   		command_executor=self.driverurl,
	   		desired_capabilities=DesiredCapabilities.CHROME)
		self.driver.implicitly_wait(20) # seconds
		
	def createbrowser(self, host, browsertype):
		self.driverhost = host
		self.driverurl = 'http://'+self.driverhost+':4444/wd/hub'
		self.driver = webdriver.Remote(
	   		command_executor=self.driverurl,
	   		desired_capabilities=DesiredCapabilities.CHROME)
		self.driver.implicitly_wait(10) # seconds
		
	def __del__(self):
		if self.driver.session_id is not None:
			self.driver.quit()
			self.driver.session_id = None
			
	def find_element(self, location):
		tmp = location.split(':')
		method = tmp[0]
		if len(tmp) == 1:
			method = 'css'
			target = tmp[0]
		else:
			target = tmp[1]
		
		if method == 'css':
			elem = self.driver.find_element_by_css_selector(target)
		elif method == 'xpath':
			elem = self.driver.find_element_by_xpath_selector(target)
		elif method == 'id':
			elem = self.driver.find_element_by_id(target)
		elif method == 'name':
			elem = self.driver.find_element_by_name(target)
		elif method == 'tag':
			elem = self.driver.find_element_by_tag_name(target)
		
		return elem
	
	def openurl(self, *args, **kwds):
		target = args[1]
		self.driver.get(target)
	
	def text(self, *args, **kwds):
		target = args[1]
		value = args[2]
		elem = self.find_element(target)
		elem.send_keys(value)
	
	def click(self, *args, **kwds):
		target = args[1]
		elem = self.find_element(target)
		elem.click()
		
	
	def assertText(self, *args, **kwds):
		target = args[1]
		expected = args[2]
		elem = self.find_element(target)
		actual = elem.text
		
		pattern = re.compile(expected)
		
		matched = pattern.match(actual)
		msg = '预期: ' + expected + '实际: ' + actual
		if matched :
			return True, msg
		else:
			return False, msg
	
		
	def quit(self, *args, **kwds):
		self.driver.quit()
		self.driver.session_id = None	
	
	
	def process(self, testcase):
		if self.driver.session_id is None:
			self.createbrowser(self.driverhost, 'CHROME')

		if len(testcase) == 2:
			value = ''
			print 'testcase length is two'
		if len(testcase) == 1:
			target = ''
			value = ''
			print 'testcase length is one'
		action = testcase[0]
		target = testcase[1]
		value = testcase[2]
		functions = {'url': self.openurl,
		'text':self.text,
		'click':self.click,
		'assertText':self.assertText,
		'quit': self.quit}
		
		func = functions[action]
		print action
		func(action,target,value)

	


if __name__ == "__main__":

	#python uitest.py > a 2>&1
	#init testcases
	testcases = []
	driver = UITestDriver()
	files = ['testcases/book.py']
	for file in files:
		try:
			with open(file) as f:
				for test in f:
					testcases.append(eval(test))
		except:
			print 'read test case file:error'
		finally:
			pass
			
		for testcase in testcases:
			driver.process(testcase)
		
	
	
	
	
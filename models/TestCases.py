# coding=utf-8

from os import listdir, getcwd, sep
from os.path import isfile, join


basedir = getcwd() + sep + "testcases"


class TestCases():
	def __init__(self):
		self.TestCases = []
		self.gen_TestCases()
		
	def gen_TestCases(self, curdir=basedir):
		for f in listdir(curdir):
			filename = join(curdir,f)
			if not isfile(filename):
				self.gen_TestCases(filename)
			else:
				self.TestCases.append(filename)
				
	def get_testcase(file):
		with open(file) as f:
			return f.read()

# -*- coding: utf-8 -*-

'''
@author:myersguo
@date:2015.
'''

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (WebDriverException, TimeoutException, StaleElementReferenceException)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from appium import webdriver as android_driver

try:
    from collections import OrderedDict
except Exception,e:
    from .ordereddict import OrderedDict

from textwrap import dedent

import re
import sys
import time
from datetime import datetime
from os import getcwd,sep,path
reload(sys)
sys.setdefaultencoding('utf8')

global_cur_section = 'default'
screen_folder = getcwd() + sep + "public" + sep + "screen" + sep
ALWAYS_SAVE_FOLDER = True
MAIL_OPEN = False

PATH = lambda p: path.abspath(
    path.join(path.dirname(__file__), p)
)



class MyException(Exception):
    pass


class UITestDriver():

    @property
    def driverhost(self):
        return self._driverhost
    @property
    def driverurl(self):
        return 'http://'+self.driverhost+':4444/wd/hub'
    @property
    def global_variable(self):
        return self.global_variable

    @property
    def driver(self):
        return self._driver
    @property
    def timeout(self):
        return self._TIMEOUT

    @property
    def result(self):
        return self._result

    @staticmethod
    def instance():
        if not hasattr(UITestDriver, '_instance'):
            if self.isapp == False:
                UITestDriver._instance = UITestDriver()
            else:
                UITestDriver._instance = UITestDriver(isapp=True,appname = self.testapp)
        return UITestDriver._instance

    def __init__(self, host='127.0.0.1',isapp=False,appname=''):
        self._driver = None
        self._driverhost = host
        self._driverurl = 'http://'+self.driverhost+':4444/wd/hub'
        #http://docs.seleniumhq.org/docs/04_webdriver_advanced.jsp#using-a-proxy
        self.USER_AGENT_STRING='Mozilla/5.0 (Linux; Android 4.4.2; GT-I9505 Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Version/1.5 Chrome/28.0.1500.94 Mobile Safari/537.36'

        self.CHROME = {
            "browserName": "chrome",
            "version": "",
            "platform": "ANY",
            "javascriptEnabled": True,
            "chrome.prefs": {"profile.managed_default_content_settings.images": 2},
            "proxy": {"httpProxy":None,"ftpProxy":None,"sslProxy":None,"noProxy":None,"proxyType":"DIRECT","class":"org.openqa.selenium.Proxy","autodetect":False},
            "chrome.switches": ["window-size=1003,719",
            "allow-running-insecure-content",
            "disable-web-security",
            "disk-cache-dir=selenium-chrome-cache",
            "--user-agent="+self.USER_AGENT_STRING,
            "no-referrers"],
        }

        self.isapp = isapp
        self.testapp = ''
        if self.isapp == True:
            if path.isfile(PATH('../app/' + appname)) == True:
                self.testapp = PATH('../app/' + appname)
            else:
                self.isapp = False#app not exits

        self.ANDROID  = {
            'platformName': 'Android',
            'platformVersion': '4.4',
            'deviceName': 'Android MI3WC',
            'app': self.testapp,
            "chrome.prefs": {"profile.managed_default_content_settings.images": 2},
            "javascriptEnabled": True,
            "locationContextEnable":True,
            "takesScreenshot":True,
            'newCommandTimeout': 240
        }

        self._result = {}
        self.step = 0
        self.cur_testcase = ''
        self.native_context = None
        self.webview_context = None
        self.SCREEN_ID = 1

        if self.isapp == True:
            #webdriver = __import__('appium.webdriver.*')
            self._driver = android_driver.Remote(
                command_executor='http://'+self.driverhost+':4723/wd/hub',
                desired_capabilities=self.ANDROID
            )
            time.sleep(5)#等待打开应用
            #前提条件是，必须在前两个，
            #TODO，后续用更好的方式解决
            self.all_contexts = self._driver.contexts[0:2]
            for i in range(0,2):
                print self.all_contexts[i]
                if self.all_contexts[i].startswith('NATIVE_'):
                    self.native_context = self.all_contexts[i]
                elif self.all_contexts[i].startswith('WEBVIEW_'):
                    self.webview_context = self.all_contexts[i]

        else:
            self._driver = webdriver.Remote(
                command_executor=self.driverurl,
                desired_capabilities=self.CHROME)

        self._TIMEOUT = 20 #50s
        self._driver.implicitly_wait(self.timeout) # Sets a sticky timeout to implicitly wait for an element to be found,
        if self.isapp == False:
            self._driver.set_script_timeout(self.timeout)#Set the amount of time that the script should wait during an
            self._driver.set_page_load_timeout(self.timeout)#Set the amount of time to wait for a page load to complete
        #define global variable to save values
        self.global_variable = {}
        self.baseurl = None#default no base url
        #max window
        #self.driver.maximize_window()
        if self._driver is None:
            print 'Cannot start driver'
            raise MyException('Driver starts failed')
        else:
            print 'Driver is good'


    def createbrowser(self, host, browsertype):
        self.driverhost = host
        self.driverurl = 'http://'+self.driverhost+':4444/wd/hub'
        self.driver = webdriver.Remote(
            command_executor=self.driverurl,
            desired_capabilities=self.CHROME)
        self.driver.implicitly_wait(self.timeout) # Sets a sticky timeout to implicitly wait for an element to be found,
        self.driver.set_script_timeout(self.timeout)#Set the amount of time that the script should wait during an
        self.driver.set_page_load_timeout(self.timeout)#Set the amount of time to wait for a page load to complete


    def __del__(self):
        try:
            if self.driver is not None and self.driver.session_id is not None:
                self.driver.quit()
                self.driver.session_id = None
        except:
            pass

    #全局self,exec,
    def save_to_global(fn):
        def __check(*args, **kwds):
            if not args:
                result = fn()
            else:
                #default save the third args
                result = fn(*args ,**kwds)
                if args[3] is None and args[2] is None:
                    pass
                else:
                    if args[3] is None or len(args[3])==0:
                        args[0].global_variable[args[2]] = result
                    else:
                        args[0].global_variable[args[3]] = result

        return __check
    #保存最有一个参数到全局里面
    def save_to_global_ex(fn):
        def __check(*args, **kwds):
            if not args:
                result = fn()
            else:
                result = fn(*args ,**kwds)
                i = len(args)
                args[0].global_variable[args[i-1]] = result
        return __check

    def quit_onFalse(fn):
        def __check(*args, **kwds):
            if not args:
                result = fn()
            else:
                result = fn(*args ,**kwds)
            if result != True:
                try:
                    args[0].quit()
                except:
                    pass
                finally:
                    raise MyException('quit on check false')

        return __check
    #Re-find the element again. (Because the element has been refresh.)
    def try_again_when_exception(fn):
        def __check(*args, **kwds):
            if not args:
                try:
                    fn()
                except StaleElementReferenceException:
                    fn()
            else:
                try:
                    fn(*args ,**kwds)
                except StaleElementReferenceException:
                    fn(*args ,**kwds)
        return __check

    #目前，只有本地可用
    def screen_when_error(fn):
        def __check(*args, **kwds):
            if not args:
                result = fn()
            else:
                result = fn(*args ,**kwds)
                try:
                    if  result == False or (type(result) is tuple and result[0] == False):
                        global screen_folder
                        filename = screen_folder + str(time.time()) +'.png'
                        #filename = sep + str(time.time()) +'.png'
                        hrefname = 'screen\\'+ str(time.time()) +'.png'
                        args[0].driver.get_screenshot_as_file(filename)
                        href = '<a href='+hrefname+' target=_blank>'+hrefname+'</a>'
                        args[0].result[args[0].step] = args[0].result[args[0].step] + (href,)
                except Exception,e:
                    print e
                    pass
        return __check

    def try_again(fn):
        def __check(*args, **kwds):
            for i in(0,4):
                if not args:
                    result = fn()
                else:
                    result = fn(*args ,**kwds)
                if result == True:
                    break
        return __check


    def find_elements(self, location, index):
        tmp = location.split('::')
        method = tmp[0]
        if len(tmp) == 1:
            if self.isapp == True:
                if 'WEBVIEW' not in self.driver.current_context:
                    method = 'id'
                else:
                    method = 'css'
            else:
                method = 'css'
            target = tmp[0]
        else:
            target = tmp[1]
        elem = None
        if self.isapp == False:
            self.wait_for_pageload()
        try:
            if method == 'css':
                elem = self.driver.find_elements_by_css_selector(target)
            elif method == 'xpath':
                elem = self.driver.find_elements_by_xpath_selector(target)
            elif method == 'id':
                elem = self.driver.find_elements_by_id(target)
            elif method == 'name':
                if self.isapp == True:
                    uiautomator_text = 'new UiSelector().text("' + target + '")'
                    elem = self.driver.find_elements_by_android_uiautomator(uiautomator_text)
                else:
                    elem = self.driver.find_elements_by_name(target)
            elif method == 'tag':
                elem = self.driver.find_elements_by_tag_name(target)
            if elem is not None and len(elem)>0:
                return elem[index]
            else:
                return None
        except Exception,e:
            print 'find element error'
            print e
            raise


    def find_element(self, location):
        elem = self.find_elements(location, 0)
        if elem is not None and elem.is_displayed():
            return elem
        else:
            return None

    @save_to_global
    def check_exists(self, *args, **kwds):
        try:
            target = args[1]
            elem = self.find_element(target)
            if elem is None:
                return False
            else:
                return True
        except Exception,e:
            print e
            return False
        return True

    @try_again
    def openurl(self, *args, **kwds):
        target = args[1]
        if target.startswith('http')  == False and target.startswith('https') == False:
            if  self.baseurl is None:
                raise MyException('url is invalid')
            else:
                if target.startswith('/') == False:
                    target = self.baseurl + '/' + target
                else:
                    target = self.baseurl + target
        else:
            pass


        try:
            self.driver.get(target)
        except:
            return False
        if self.driver.current_url == target:
            return True
        else:
            return False
        ''' 不对url进行检查
        self.check_url(*args, **kwds)
        if self.driver.current_url == target:
            return True
        else:
            return False
        '''
    @try_again_when_exception
    def text(self, *args, **kwds):
        target = args[1]
        #value = unicode(args[2],'utf-8')
        value = args[2]
        elem = self.find_element(target)
        self.scroll_element_into_view(elem)
        elem.clear()
        elem.send_keys(value)

    @save_to_global_ex
    def getattr_fn(self, attr, target, value):
        elem = self.find_element(target)
        return elem.get_attribute(attr)

    @save_to_global
    def gettext(self, *args, **kwds):
        target = args[1]
        elem = self.find_element(target)
        text = elem.text.strip()
        return text

    @save_to_global
    def gettext_withoutchild(self, *args, **kwds):
        target = args[1]
        elem = self.find_element(target)
        script = """
            var parent = arguments[0];
            var child = parent.firstChild;
            var ret = "";
            while(child) {
                if (child.nodeType === Node.TEXT_NODE)
                    ret += child.textContent;
                child = child.nextSibling;
            }
            return ret;
        """
        text = self.driver.execute_script(script, elem)
        text = text.strip()
        return text

    #https://code.google.com/p/selenium/issues/detail?id=2766#c27
    def scroll_element_into_view(self, element):
        if self.isapp == True or element is None:
            return True
        y = element.location['y']
        self.driver.execute_script('window.scrollTo(0, {0})'.format(y))


    #@try_again_when_exception
    def click(self, *args, **kwds):
        target = args[1]
        elem = self.find_element(target)
        if elem is not None:
            try:
                if self.isapp == False:
                    self.scroll_element_into_view(elem)
                elem.click()
            except:
                self.driver.execute_script("arguments[0].click();", elem)
                #
            #try:
            #   WebDriverWait(self.driver, 10).until(elem.is_enabled())
            #finally:
            #   elem.click()
        else:
            pass
    def back(self, *args, **kwds):
        self.driver.back()
    def forward(self, *args, **kwds):
        self.driver.forward()

    def mouseover(self, *args, **kwds):
        target = args[1]
        elem = self.find_element(target)
        ActionChains(self.driver).move_to_element(elem).perform()

    def clickyes(self, *args, **kwds):
        alert = self.driver.switch_to.alert
        alert.accept()

    def clickno(self, *args, **kwds):
        alert = self.driver.switch_to.alert
        alert.dismiss()

    def wait_for_pageload(self):
        javascript = """
            var callback = arguments[arguments.length - 1];
            var id = setInterval(function() {
              if(window.document.readyState  == 'complete') {
                clearInterval(id);
                callback(true);
              }
            }, 2000);
        """

        for _ in range(10):
            try:
                result = self.driver.execute_async_script(dedent(javascript))
                if result == True:
                    break
            except WebDriverException as r:
                if "document unloaded while waiting for result" in r.msg:
                    self.driver.wait(1)
                    continue
                else:
                    raise

        return result

    @save_to_global
    def save_js_variable(self, *args, **kwds):
        script = args[1]
        if "return" not in args[1]:
            script = " return " + args[1]
        return self.driver.execute_script(script)

    def get_js_variable(self, *args, **kwds):
        try:
            self.save_js_variable(*args, **kwds)
            return self.global_variable[args[2]]
        except Exception,e:
            print 'save js error' + e
            pass


    def exec_script(self, *args, **kwds):
        script = args[1]
        #self.wait_for_pageload()
        return self.driver.execute_script(script)

    #异步执行js
    def asyncexec_script(self, *args, **kwds):
        script = args[1]
        #self.wait_for_pageload()
        return self.driver.execute_async_script(script)

    @screen_when_error
    def assertText(self, *args, **kwds):
        target = args[1]
        expected = args[2]
        matched = False
        try:
            if len(re.findall("{{.+}}",args[2]))>0:
                expected = eval(args[2].replace('{{','self.global_variable[\'').replace('}}','\']'))
        except Exception,e:
            pass
        try:
            elem = self.find_element(target)
            actual = elem.text
            pattern = re.compile(expected)
            matched = pattern.match(actual)
        except:
            actual = u'元素未找到'
            
        msg = '预期: ' + expected + '实际: ' + actual
        if matched :
            return True, msg
        else:
            self.result[self.step] = (False,msg,self.cur_testcase)
            #screen when error
            return False, msg

    @save_to_global
    def get_currenturl(self, *args, **kwds):
        self.wait_for_pageload()
        return self.driver.current_url

    def check_url(self, *args, **kwd):
        target = args[1]
        try:
            if self.driver.current_url != target:
                msg = 'url ' + target + ' not found'
                raise Exception(msg)
        except Exception,e:
            self.result[self.step] = (False,'url check failed',self.cur_testcase)
            raise

    def goto_section(self, *args, **kwds):
        global global_cur_section
        target = args[1]
        flag = False
        if args[2] is None or len(args[2]) == 0: #不检查则默认跳转
            flag = True
        else:
            try:
                ia = args[2].replace('{{','self.global_variable[\'').replace('}}','\']')
                flag = eval(ia)
            except Exception,e:
                print 'error to section'
                flag = False
        if flag == True:
            global_cur_section = target

    @screen_when_error
    def assert_fn(self,method, *args, **kwds):
        res = False
        msg = ''
        a = args[0]
        b = args[1]
        #替换变量表达式，表达式暂不替换
        if method not in ('express',):
            if len(re.findall("{{.+}}",args[0]))>0:
                a = eval(args[0].replace('{{','self.global_variable[\'').replace('}}','\']'))
            if len(re.findall("{{.+}}",args[1]))>0:
                b = eval(args[1].replace('{{','self.global_variable[\'').replace('}}','\']'))
        #出去eq,express，默认为数字比较
        if method not in ('eq','express'):
            try:
                if len(re.findall('\.', a))>=2:
                    a = a.replace('.','')
                else:
                    a = a.replace(',','')
                    
                if len(re.findall('\.', b))>=2:
                    b = b.replace('.','')
                else:
                    b = b.replace(',','')

                tmpa = re.findall("[-+]?\d+[\.,]?\d*", a)
                tmpb = re.findall("[-+]?\d+[\.,]?\d*", b)
                if len(tmpa)>1:
                    a = ''
                    for ti in tmpa:
                        a +=''+ti
                else:
                    a = tmpa[0]

                if len(tmpb)>1:
                    b = ''      
                    for tj in tmpb:
                        b +=''+tj
                else:
                    b = tmpb[0]

                a = float(a)
                b = float(b)
            except Exception,e:
                print 'error convert'
                print e

        try:
            if method == 'express':
                ia = a.replace('{{','self.global_variable[\'').replace('}}','\']')
                a = ia
                res = eval(ia)
            elif method == 'gt':
                res = a > b
            elif method == 'lt':
                res = a < b
            elif method == 'le':
                res = a <= b
            elif method == 'ge':
                res = a >= b
            elif method =='eq' or method == 'numeq':
                res = a == b
        except Exception,e:
            msg = e
            res = False

        if res == True:
            self.result[self.step] = True
        else:
            res = False
            msg += '预期: ' + str(a) + ' ' + method + ' ' + str(b)
            self.result[self.step] = (False,msg,self.cur_testcase)

        return res
    def setbaseurl(self, *args, **kwds):
        target = args[1]
        #默认baseurl 最后去掉/，即http://buy.mi.com/->http://buy.mi.com
        self.baseurl = target.rstrip('/')

    def quit(self, *args, **kwds):
        self.driver.quit()
        self.driver.session_id = None

    def switch_to_context(self, *args, **kwds):
        target = args[0]
        if len(args) > 1:
            target = args[1]
        self.driver.switch_to.context(target)
        print 'switch to context: ' + self.driver.current_context

    def switch_to_webview(self, *args, **kwds):
        if self.native_context is not None:
            self.driver.switch_to.context(self.webview_context)

    def switch_to_native(self, *args, **kwds):
        if self.native_context is not None:
            self.driver.switch_to.context(self.native_context)
    
    def swipe(self, *args, **kwds):
        target = args[1].split(',')
        loop = 1
        if args[2] is None or len(args[2]) == 0:
            loop = 1
        else:
            if args[2]>1:
                loop = int(args[2])

        for i in range(1,loop):
            self.driver.swipe(target[0],target[1],target[2],target[3],500)

    def swipe_method(method, isfast=False):
        x = driver.get_window_size()['width']
        y = driver.get_window_size()['height']
        if method == 'left':
            self.driver.swipe(x*2/3,y/2,x/3,y/2,500)
        elif method == 'right':
            self.driver.swipe(x*1/3,y/2,x*2/3,y/2,500)
        elif method == 'down':
            self.driver.swipe(x/2,y/3,x/2,y*2/3,500)
        elif method == 'up':
            self.driver.swipe(x/2,y*2/3,x/2,y/3,500)
        if isfast == False:
            time.sleep(2)

    def swipe_to_left(self, *args, **kwds):
        self.swipe_method('left')
    def swipe_to_right(self, *args, **kwds):
        self.swipe_method('right')
    def swipe_to_down(self, *args, **kwds):
        self.swipe_method('down')
    def swipe_to_up(self, *args, **kwds):
        self.swipe_method('up')

    def process(self, testcase):
        if self.driver.session_id is None and self.isapp == False:
            self.createbrowser(self.driverhost, 'CHROME')

        self.cur_testcase = str(testcase)
        action = testcase[0].strip()
        target = value = ''
        if len(testcase) == 2:
            #target = testcase[1].strip()
            target = unicode(testcase[1].strip(),'utf-8')
        elif len(testcase) == 1:
            target = ''
            value = ''
        else:
            #target = testcase[1].strip()
            target = unicode(testcase[1].strip(),'utf-8')
            value = unicode(testcase[2].strip(),'utf-8')
            #value = testcase[2].strip()
        functions = {'url': self.openurl,
        'text':self.text,
        'click':self.click,
        'mouseover':self.mouseover,
        'assertText':self.assertText,
        'exec_script':self.exec_script,
        'save_js_variable':self.save_js_variable,
        'asyncexec_script':self.asyncexec_script,
        'get_js_variable': self.get_js_variable,
        'gettext':self.gettext,
        'getonlytext':self.gettext_withoutchild,
        'check_url':self.check_url,
        'get_currenturl':self.get_currenturl,
        'check_exists':self.check_exists,
        'goto_section':self.goto_section,
        'clickyes':self.clickyes,
        'clickno':self.clickno,
        'back':self.back,
        'forward':self.forward,
        'switch_to_context':self.switch_to_context,
        'swipe':self.swipe,
        'swipe_to_left':self.swipe_to_left,
        'swipe_to_right':self.swipe_to_right,
        'switch_to_webview':self.switch_to_webview,
        'switch_to_native':self.switch_to_native,
        'baseurl':self.setbaseurl,
        #'getattr_href':self.getattr_fn,
        'quit': self.quit}
        try:
            self.result[self.step] = True
            funcmap = action.split('_')
            if funcmap[0] =='assert':
                method = funcmap[1]
                if method not in ('express'):
                    self.assert_fn(method,target, value)
                    #self.assert_fn(method,self.global_variable[target].strip(),self.global_variable[value].strip())
                else:
                    self.assert_fn(method,target,value)
            elif funcmap[0] =='getattr':
                attr = funcmap[1]
                self.getattr_fn(attr, target, value)
            else:
                func = functions[action]
                func(action,target,value)
                try:
                    global ALWAYS_SAVE_FOLDER
                    if ALWAYS_SAVE_FOLDER:
                        global screen_folder
                        #临时使用，方便做实时同步,realtime
                        filename = screen_folder + 'real' + sep + str(self.SCREEN_ID) +'.png'
                        #切换到webview的时候有问题
                        if self.isapp:
                            tmp = self.driver.current_context
                            self.switch_to_native()
                            self.driver.get_screenshot_as_file(filename)
                            self.switch_to_context(tmp)
                        else:
                            self.driver.get_screenshot_as_file(filename)
                        self.SCREEN_ID +=1
                except Exception,e:
                    print 'save screen file error',e
        except MyException as e:
            raise e
        except Exception,e:
            if action.startswith('url'):
                if self.driver.session_id is not None:
                    self.driver.quit()
                    self.driver.session_id = None
                raise e

            self.result[self.step] = (False,e,self.cur_testcase)
        finally:
            self.step +=1


def RunTestCase(testcases, isfile=0, client='10.236.122.65'):
    #driver = UITestDriver.instance()
    global global_cur_section
    curtestcases = []
    testcase_suit = OrderedDict()
    testcase_sections = testcase_suit
    testcase_sections[global_cur_section] = curtestcases
    cur_section = global_cur_section
    t = __import__('time')
    start =t.strftime("%Y/%m/%d %H:%M:%S")
    testlist = ''
    isapp = False
    appcheck_flag = False
    appname = ''
    driver = None
    if isfile == 1:
        for file in testcases:
            testcase_sections = OrderedDict()
            testcase_suit[file] = testcase_sections
            cur_section = 'default'
            testcase_sections[cur_section] = []
            try:
                with open(file) as f:
                    lines = f.readlines()
                for test in lines:
                    test = test.strip()
                    if test is None:
                        continue
                    elif test.startswith('#;section_'):
                        i = test.index('_') + 1
                        cur_section = test[i:]
                        #cur_section = test.split('_')[1]
                        testcase_sections[cur_section] = [] #!! once here,init
                        continue
                    elif len(test)<=0 or test.startswith('#'):
                        continue
                    try:
                        #run once to check app
                        if appcheck_flag == False:
                            appinfo = eval(test)
                            if appinfo[0] == 'app':
                                appname = appinfo[1]
                                if path.isfile(PATH('../app/' + appname)) == True:
                                    isapp = True
                                    continue
                                else:
                                    return 'APP FILE NOT EXITS'
                        appcheck_flag = True

                        testcase_sections[cur_section].append(eval(test))
                    except Exception,e:
                        appcheck_flag = True
                        print 'eval error:' + test
                        print e
                        continue
            except:
                print 'read test case file:error'
            finally:
                pass
    else:
        testcase_sections = {}
        testcase_suit['selfdesign'] = testcase_sections
        testcase_sections['default'] = testcases
        curtestcases = testcases
    fail_result = {}

    #run testcase
    try:
        if isapp == False:
            driver = UITestDriver()
        else:
            driver = UITestDriver(isapp=True, appname= appname)
    except Exception,e:
        print 'run testcase runner driver failed'
        print e
        raise MyException('Failed to start driver')

    for suit in testcase_suit:
        #获取测试用例
        global_cur_section= 'default'
        cur_testcase_sections = testcase_suit[suit]
        testcase_sections = cur_testcase_sections
        for section in testcase_sections:  #TODO 以后这里更改成不限制顺序的
            if section not in (global_cur_section):
                continue
            cur_testcases = testcase_sections[section]
            isloop = False
            loopcnt = 1
            if section.startswith('loop_'):
                i = section.index('_')+1
                if i < len(section):
                    isloop = True
                    loopcnt = int(section[i:])
            testlist += 'now exe section ' + str(section) + ':<br><br>'
            print 'exec section: ' + section

            for ti in range(loopcnt):
                if section not in (global_cur_section):
                    break
                if ti > 0:
                    print 'exec section: ' + section + ' ' + str(ti+1) + ' time'

                for testcase in cur_testcases:
                    if section not in (global_cur_section):
                        break
                    try:
                        print testcase
                        try:
                            testlist += str(testcase) + '<br>'
                        except:
                            pass
                        driver.process(testcase)
                    except Exception,e:
                        print e
                        return fail_result

    #fail_result =  {k: v for k, v in driver.result.items() if v==False }
    result_flag = True
    end =t.strftime("%Y/%m/%d %H:%M:%S")
    msg = 'testcase starts: ' + start + '<br>' + 'testcase ends: ' + end + '<br>' + 'testcase from: ' + client + '<br>'  + 'testcase result: <br>' 
    
    count = len(driver.result) 
    errcount = 0
    errmsg = ''
    for k,v in driver.result.items():
        if v== False:
            fail_result[k] = '<br>'+str(v)
            errmsg += str(fail_result[k])
        elif type(v) == tuple:
            if v[0] == False:
                fail_result[k] = '<br>'+':'.join(map(str,v))
                errmsg += str(fail_result[k])
            

    if len(fail_result) == 0:
        fail_result = {'ALL':'OK'}
        msg += str(fail_result)
    else:
        errcount = len(fail_result)
        msg  = msg + 'Total : ' + str(count) + ' Times, Failed : ' + str(errcount) + ' times' + ' Passed: ' + str(count-errcount) + ' times<br>' + errmsg
        result_flag = False

    #if len(fail_result) == 0:
            #fail_result = {'ALL':'OK'}

    try:
            #end =t.strftime("%Y/%m/%d %H:%M:%S")
            #msg = 'testcase starts: ' + start + '\r\n' + 'testcase ends: ' + end + '\r\n' + 'testcase from: ' + client + '\r\n'  + 'testcase result: ' + str(fail_result) + '\r\n\r\n\r\n'
            #msg = 'testcase starts: ' + start + '<br>' + 'testcase ends: ' + end + '<br>' + 'testcase from: ' + client + '<br>'  + 'testcase result: <br>' + str(fail_result) + '<br><br><br>'
            msg += '<br><br>testsuit list is :' + '<br>'
            msg += str(testlist)  + '<br>'
            #from .mymail import mail
            if MAIL_OPEN == True:
                    mail = __import__('models.mymail',fromlist=['mail'])
                    mail.htmlmail(msg,result_flag)
            else:
                    pass
    except Exception,e:
            print e
            pass
    return fail_result

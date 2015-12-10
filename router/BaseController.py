import tornado.web
from models import TestCaseRunner
import json
from models import TestCases,TimeStamp


def check_user(func):
    def __check(req, *args):
        print 'check user '
        if not args:
            return func(req)
        else:
            return func(req, *args)
        
    return __check


class LoginHandler(tornado.web.RequestHandler):
    @check_user
    def get(self):
        self.render('login.html', title='login')
        
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', title='index')
class ShowRealHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('showreal.html', title='show real')
        
class ProductHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('product.html', title='product')

class TimestampHandler(tornado.web.RequestHandler):
    def get(self, *path):
        request = self.request
        #get action path
        path = [p.strip() for p in request.path.split('/') if p.strip()]
        action = getattr(self, "get_%s" % path[0])
        try:
            pathlen = len(path)
            if pathlen == 1:
                action()
            elif pathlen == 2:
                action(path[-1])
            else:
               self.write('404')     
        except Exception,e :
            print e
            self.write('404')
        
    def get_timetool(self):
        try:
            timetools = TimeStamp.TimeStamp()
            curtime = int(timetools.getservertime())
            self.render('timetools.html', title='timestamp',localtime=curtime)
        except:
            self.write('404')
    
    def get_gettimestamp(self):
        try:
            timetools = TimeStamp.TimeStamp()
            curtime = timetools.getservertime()
            self.write('var servertime='+curtime)
        except Exception,e:
            self.write('db connection failed')
    
    def get_settimestamp(self, value):
        try:
            timetools = TimeStamp.TimeStamp()
            curtime = timetools.changeservertime(value)
            self.redirect('/gettimestamp')
        except Exception,e:
            self.write('db connection failed')         
        
        
        
class SmokeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('smoke.html', title='smoketest')
        
class StockHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('stock.html', title='stock')

        
class NextHandler(tornado.web.RequestHandler):
    def get(self):
        isadmin = '0'
        testcases = []
        testcases = TestCases.TestCases().TestCases
        try:
            isadmin = self.get_argument('isadmin')
        except:
            pass
        headers = {}
        headers['css'] =("css/ui.multiselect.css",)
        headers['js'] =("js/libs/jquery-ui.js",)
        self.render('next.html', title='The Next', isadmin=isadmin, testcases = testcases, headers = headers)
        #self.render('next.html', title='The Next', isadmin=isadmin, testcases = testcases)

class TestCaseHandler(tornado.web.RequestHandler):
    def post(self):
        isok ,isfile = False, 0
        try:
            testcases, isfile = self.gen_testcases()
            fr = self.request.remote_ip
            isok = TestCaseRunner.RunTestCase(testcases, isfile, fr)
        except Exception, e:
            isok = False
            print e
        finally:
            self.set_header("Content-Type", "text/plain")
            self.set_header("charset", "UTF-8")
            if isok:
                result = {
                    'result' : isok
                }
                return self.write(json.dumps(result,ensure_ascii=False))
            else:
                return self.write(json.dumps({'result':False}))
    
    def gen_testcases(self):
        testcaselist = self.request.arguments.get("testcases[]")
        isfile = 0
        try:
            isfile = int(self.get_argument('isfile'))
        except:
            isfile = 0
            
        testcases = []
        for testcase in testcaselist:
            if isfile == 1:
                testcases.append(testcase)
            else:
                testcases.append(testcase.split(','))
        return testcases, isfile
       
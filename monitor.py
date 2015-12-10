import tornado.ioloop
import tornado.web
import os
from router.BaseController import *
        
    
class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        pass


    
class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "template_path": 'views',
            "static_path":  "public",
            "login_url": "/login",
            "xsrf_cookies": False,
            "cookie_secret": "myersguo",
            "gzipping": True,
            "debug": True,
        }
        handlers = [(r"/", IndexHandler),
        (r"/login", LoginHandler),
        (r"/next", NextHandler),
         (r"/product", ProductHandler),
         (r"/stock", StockHandler),
         (r"/timetool", TimestampHandler),
         (r"/gettimestamp", TimestampHandler),
         (r"/settimestamp/(\w+)",TimestampHandler),
         (r"/smoke", SmokeHandler),
         (r"/runtestcase",TestCaseHandler),
         (r"/showreal",ShowRealHandler),
          (r"/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    application = Application()
    application.listen(9090)
    tornado.ioloop.IOLoop.instance().start()
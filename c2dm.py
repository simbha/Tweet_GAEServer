_author_="Vipul A M"
_email_="vipul@byclor.org"


import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import logging

class Registration(db.Model):
    accountName=db.StringProperty()
    registrationId=db.StringProperty()

class Reset(webapp.RequestHandler):
    """This is used to reset the database"""
    def get(self):
        itemquery = db.GqlQuery("SELECT * FROM Registration ")
        items = itemquery.fetch(100, 0)
        for item in items:
            item.delete()
        self.response.out.write('Reset DataBase')
    
    def post(self):
        self.get()        
        
class StartPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<html>')
        self.response.out.write('<head>')
        self.response.out.write('<title>')
        self.response.out.write('Tweety')
        self.response.out.write('</title>')
        self.response.out.write('</head>')
        self.response.out.write('<style type=\"text/css\">body{background: #474A4B url(static/twig-bg.png) center 10px repeat-x;}h1{font-size: 8em;margin: 0;padding: 0;letter-spacing: -.05em;}</style>')
        self.response.out.write('<style type=\"text/css\">.button{width: 100%; height: 28px;line-height: 20px; border: 0;font-weight: bold; font-size: .8em; color: #fff; background: transparent url(static/button-bg.png) center no-repeat; margin: 10px 0;}p#desc{font-weight: bold;font-size: .8em; color: #fff; background: transparent url(http://twig.appspot.com/_assets/images/desc-bg.png) center no-repeat; padding: 1em; margin: 0;}</style>')
        self.response.out.write('<body><div align=center><br/><br/><br/><h1>Tweety</h1><br/><p id="desc">Push Notifications clone.</p><br/><br/>')
        self.response.out.write('<form action=\"/sender\" method=\"POST\">' )
        self.response.out.write('<select name=\"accountName\">' )
        self.response.out.write('<option value=\"-\">-</option>' )
        items = db.GqlQuery("SELECT * FROM Registration" )
        for r in items:
            self.response.out.write('<option value=\"'+r.accountName+'\">'+r.accountName+'</option>' )            
        self.response.out.write('</select>' )
        self.response.out.write('<br>')
        self.response.out.write('<input type=\"text\" name=\"text\" size=\"30\"/>')
        self.response.out.write('<br>')
        self.response.out.write('<input type=\"submit\" value=\"Send message\">')
        self.response.out.write('</form>')
        self.response.out.write('<br/><br/><br/><br/><br/><br/><br/><br/><div id=\"footer\">Powered by <a href=\"http://code.google.com/appengine/\">Google App Engine</a>')
        self.response.out.write('</div></body>')
        self.response.out.write('</html>')

class Sender(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.set_status( 500,"Server error" )
        self.response.out.write( "GET not supported" )

    def post(self):
        accountName = self.request.get( "accountName" )
        text = self.request.get( "text" )
        itemquery = db.GqlQuery("SELECT * FROM Registration WHERE accountName=:1",
                                accountName )
        items = itemquery.fetch(1)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.set_status( 200,"OK" )
        self.response.out.write('<html>')
        self.response.out.write('<head>')
        self.response.out.write('<title>')
        self.response.out.write('Tweety')
        self.response.out.write('</title>')
        self.response.out.write('</head>')
        self.response.out.write('<body>')
        self.response.out.write('<style type=\"text/css\">body{background: #474A4B url(http://twig.appspot.com/_assets/images/twig-bg.png) center 10px repeat-x;}h1{font-size: 8em;margin: 0;padding: 0;letter-spacing: -.05em;}</style>')
        self.response.out.write('<style type=\"text/css\">.button{width: 100%; height: 28px;line-height: 20px; border: 0;font-weight: bold; font-size: .8em; color: #fff; background: transparent url(http://twig.appspot.com/_assets/images/button-bg.png) center no-repeat; margin: 10px 0;}p#desc{font-weight: bold;font-size: .8em; color: #fff; background: transparent url(http://twig.appspot.com/_assets/images/desc-bg.png) center no-repeat; padding: 1em; margin: 0;}</style>')
        self.response.out.write('<body><div align=center><br/><br/><br/><h1>Tweety</h1><br/><p id="desc">Push Notifications clone.</p><br/><br/>')
        if len(items)>0:
            registration=items[0]
            registrationId=registration.registrationId
            status = self.sendMessage( accountName, registrationId, text )
            self.response.out.write('<p ><h3>  Message sent, status: '+status+'</h3></p>' )
        else:
            self.response.out.write( "<p ><h3>No registration for '"+accountName+"'</h3></p>" )
        self.response.out.write('<p id="desc"><a href=\"/\">Back to start page</a></p>' )
        self.response.out.write('</div></body>')
        self.response.out.write('</html>')
                    
    def sendMessage( self, accountName, registrationId, text ):
        global collapse_key
        global server_account_name
        #Probably the best place to use old authToken, 
        # Use fallback mechanism to reauth to handle a 401
        authToken = self.getAuthToken()
        if authToken=="":
            return "Cannot authenticate "+server_account_name 
        form_fields = {
            "registration_id": registrationId,
            "collapse_key": str(collapse_key),
            "data.message": text
        }
        logging.info( "authToken: "+authToken )
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url="http://android.apis.google.com/c2dm/send",
                        payload=form_data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded',
                                 'Authorization': 'GoogleLogin auth='+authToken
                                })
        collapse_key=collapse_key+1
        return result.content

    def getAuthToken(self):
        global server_account_name
        global server_account_password
        form_fields = {
            "accountType": "GOOGLE",
            "Email": "you@your-domain.com",
            "Passwd": "your-password",
            "service": "ac2dm",
            "source": "Company-App-Version"
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url="https://www.google.com/accounts/ClientLogin",
                        payload=form_data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'
                                })
        if result.status_code==200:
            logging.info( "Auth response: "+result.content )
            lines=result.content.split('\n')
            authToken=""
            for line in lines:
                if line.startswith( "Auth=" ):
                    authToken=line[5:len(line)]
            return authToken
        logging.error( "error code: "+str(result.status_code)+"; error message: "+result.content )
        return ""

class TokenService(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        accountName = self.request.get( "ac" )
        registrationId = self.request.get( "id" )
        logging.info( "TokenService, accountName: "+accountName+ \
                        "; registrationId: "+registrationId )
        self.updateOrInsertRegistration( accountName, registrationId )
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.set_status( 200,"Registration accepted" )
        self.response.out.write( "Registration accepted" )

    def updateOrInsertRegistration( self, accountName, registrationId ):
        itemquery = db.GqlQuery("SELECT * FROM Registration WHERE accountName=:1",
                                accountName )
        items = itemquery.fetch(1)
        if len(items)>0:
            registration=items[0]
            if registrationId=="":  # unregistration
                registration.delete()
            else:
                registration.registrationId=registrationId
                registration.put()
        else:
            registration=Registration()
            registration.accountName=accountName
            registration.registrationId=registrationId
            registration.put()

application = webapp.WSGIApplication(
                                     [('/', StartPage),
                                      ('/sender',Sender),
                                      ('/reset',Reset),
                                      ('/token',TokenService)],
                                     debug=True)

def main():
    global collapse_key
    collapse_key=1
    global server_account_name
    server_account_name="you@your-domain.com"
    global server_account_password
    server_account_password="your-password"
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

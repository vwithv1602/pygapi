YOUR_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com' 
YOUR_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxx' 
YOUR_SCOPE = 'https://www.googleapis.com/auth/contacts'
YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION = '/'

def gist_write(feed):
    target = open("entry.xml", 'a+')
    target.write("\n"+str(feed)+"\n")
    target.close()
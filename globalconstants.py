YOUR_CLIENT_ID = 'Your client id (eg: 123456789000-abc00def11abcdef0ab0a0abcdefghij.apps.googleusercontent.com'
YOUR_CLIENT_SECRET = 'your_client_secret'
YOUR_SCOPE = 'https://www.googleapis.com/auth/contacts'
YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION = '/'

def gist_write(feed):
    target = open("debug_log.txt", 'a+')
    target.write("\n"+str(feed)+"\n")
    target.close()
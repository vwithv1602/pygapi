YOUR_CLIENT_ID = '909547726371-lkc01ret91mahjuc6fe2k0ppcmlpuumj.apps.googleusercontent.com' # vwithv1602@gmail.com
YOUR_CLIENT_ID = '44903427330-pgr2c99htqn0n20lfefekcfvi34u8b29.apps.googleusercontent.com' # sales@usedyetnew.com
YOUR_CLIENT_SECRET = 'FV3pnlZwkr56_ykFtAxsELsa' # vwithv1602@gmail.com
YOUR_CLIENT_SECRET = 'WtBkANv9CDkOrXVg2aX6BXGa' # sales@usedyetnew.com
YOUR_SCOPE = 'https://www.googleapis.com/auth/contacts'
YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION = '/'

def gist_write(feed):
    target = open("entry.xml", 'a+')
    target.write("\n"+str(feed)+"\n")
    target.close()
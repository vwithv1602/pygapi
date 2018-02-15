import datetime
def vwrite(contenttowrite):
    target = open("vpygapilogfile.txt", 'a+')
    target.write("\n==========================="+str(datetime.datetime.now())+"===========================\n")
    target.write("\n"+str(contenttowrite)+"\n")
    target.close()

def ebaydebug(contenttowrite):
    target = open("debugpygapi.txt", 'a+')
    target.write("\n===========================" + str(datetime.datetime.now()) + "===========================\n")
    target.write("\n" + str(contenttowrite) + "\n")
    target.close()

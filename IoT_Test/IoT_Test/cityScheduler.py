import sched, time, datetime

def do_updates(s, theCity, seconds): 
    print "Update {} at {}".format(theCity.deviceId, datetime.datetime.now())
    theCity.update()
    s.enter(seconds, 1, do_updates, (s, theCity, seconds))

def repeat(theCityList, minutes):
    s = sched.scheduler(time.time, time.sleep)
    for i in range(len(theCityList)):
        s.enter(i + 1, 1, do_updates, (s, theCityList[i], minutes * 60))
    s.run()
#!/usr/bin/env python3
import sched, time, datetime, logging

def do_updates(s, theCity, seconds, logger): 
    logger.info("Update {} at {}".format(theCity.deviceId, datetime.datetime.now()))
    theCity.update()
    s.enter(seconds, 1, do_updates, (s, theCity, seconds, logger))

def repeat(minutes, *theCityList):
    s = sched.scheduler(time.time, time.sleep)
    logger = logging.getLogger(__name__)
    for i in range(len(theCityList)):
        s.enter(i + 1, 1, do_updates, (s, theCityList[i], minutes * 60, logger))
    s.run()
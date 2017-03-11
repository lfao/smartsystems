#!/usr/bin/env python3
import sched, time, datetime, logging

def repeat(minutes, *theCityList, citiesDelaySeconds = 1):
    """
    triggers update in each given city every given time interval
    Keyword arguments:
    minutes -- time delay between two updates in minutes
    theCityList -- the city objects to be updated
    """
    theScheduler = sched.scheduler(time.time, time.sleep)
    logger = logging.getLogger(__name__)

    def do_updates(theCity): 
        """
        triggers one update to the given city and enter a new time to scheduler
        Keyword arguments:
        theCity - city opject to be updated
        """

        logger.info("Update {} at {}".format(theCity.deviceId, datetime.datetime.now()))
        theCity.update()
        theScheduler.enter(minutes * 60, 1, do_updates, (theCity,))
    
    # start every city at the beginning with an offset of 1 second
    for i in range(len(theCityList)):
        theScheduler.enter((i + 1) * citiesDelaySeconds, 1, do_updates, (theCityList[i],))

    # start the scheduler to run forever
    theScheduler.run()
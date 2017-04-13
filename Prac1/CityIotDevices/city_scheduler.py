#!/usr/bin/env python3
import sched, time, datetime, logging

def repeat(minutes, *city_list, cities_delay_seconds = 1):
    """
    triggers update in each given city every given time interval
    Keyword arguments:
    minutes -- time delay between two updates in minutes
    theCityList -- the city objects to be updated
    """
    the_scheduler = sched.scheduler(time.time, time.sleep)
    logger = logging.getLogger(__name__)
    sumErrorCounter = 0
    currentErrorCounter = 0

    def do_updates(the_city): 
        """
        triggers one update to the given city and enter a new time to scheduler
        Keyword arguments:
        theCity - city opject to be updated
        """

        logger.info("Update {} at {}".format(the_city.device_id, datetime.datetime.now()))
        try:
            the_city.update()
            currentErrorCounter = 0
        except e:
            currentErrorCounter += 1
            sumErrorCounter += 1
            logger.error("Exception occured. Sum of all exceptions: {} Sum of continues exceptions: {}".format(sumErrorCounter, currentErrorCounter))
            logger.error(e)

        the_scheduler.enter(minutes * 60, 1, do_updates, (the_city,))
    
    # start every city at the beginning with an offset
    for i in range(len(city_list)):
        the_scheduler.enter(i * cities_delay_seconds, 1, do_updates, (city_list[i],))

    # start the scheduler to run forever
    the_scheduler.run()
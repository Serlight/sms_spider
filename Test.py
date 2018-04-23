# -*- coding:utf8 -*-

import sched
import time
from datetime import  datetime

s = sched.scheduler(time.time, time.sleep)


def print_time():
    dt = datetime.now()
    print "From print_time", dt.strftime('%H:%M:%S %f')


def print_some_times():
    print time.time()

    s.enter(5, 1, print_time, ())
    s.enter(10, 1, print_time, ())
    s.run()

    print time.time()



if __name__ == "__main__":
    #print_some_times()
    draw_str = "2018-04-13 16:00:00"
    draw_date = datetime.strptime(draw_str, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()

    if draw_date > current_date:
        seconds = int((draw_date - current_date).total_seconds())
        print "After ", seconds, "s can draw"
    else:
        print "draw coin"





    #schedule.every().day.at("06:30").do(print_time)

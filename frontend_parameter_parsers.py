import numpy as np
import re

def fix_day_time(dayRange, timeRange):
    print("here", dayRange, timeRange)
    day_map = {
        "Sun": "Sunday",
        "Mon": "Monday",
        "Tue": "Tuesday",
        "Wed": "Wednesday",
        "Thu": "Thursday",
        "Fri": "Friday",
        "Sat": "Saturday"
    }

    time_columns = ['8am', '9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm']
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


    hoursTableStartDayIndex = days_of_week.index(dayRange[0])
    hoursTableEndDayIndex = days_of_week.index(dayRange[-1])
    hoursTableStartTimeIndex = time_columns.index(timeRange[0])
    hoursTableEndTimeIndex = time_columns.index(timeRange[-1])-1 #Slider range from 8am-6pm means start at 8am-9am and end at 5pm-6pm

    dayRange = [day_map[i] for i in dayRange]
    newDays = []
    for i in range(0, len(timeRange)-1):
        # print(timeRange[i])
        newDays.append(f"{timeRange[i][:-2]}-{timeRange[i+1][:-2]} {timeRange[i+1][-2:].upper()}")
    # print(dayRange, newDays)
    return dayRange, newDays, [hoursTableStartDayIndex, hoursTableEndDayIndex, hoursTableStartTimeIndex, hoursTableEndTimeIndex]

def hours_table_parser(hoursTable, dayRange, timeRange, indices):
    hoursTable = hoursTable["dayTimeMinMax"]
    l_jk = np.zeros((len(dayRange), len(timeRange)))
    u_jk = np.zeros((len(dayRange), len(timeRange)))

    hoursTableStartDayIndex, hoursTableEndDayIndex, hoursTableStartTimeIndex, hoursTableEndTimeIndex = indices

    # print(hoursTableStartDayIndex, hoursTableEndDayIndex)
    # print(hoursTableStartTimeIndex, hoursTableEndTimeIndex)

    for j in range(hoursTableStartDayIndex, hoursTableEndDayIndex+1):
        for k in range(hoursTableStartTimeIndex, hoursTableEndTimeIndex+1):
            l_jk[j-hoursTableStartDayIndex][k-hoursTableStartTimeIndex] = hoursTable[j][k]["min"]
            u_jk[j-hoursTableStartDayIndex][k-hoursTableStartTimeIndex] = hoursTable[j][k]["max"]

    # print(l_jk)
    # print(u_jk)

    return l_jk, u_jk
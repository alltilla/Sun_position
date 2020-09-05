# -*- coding: utf-8 -*-
import math


def hour_to_time(time):  # tizedesjegyben kifejezve, ez kell?
    time_h = int(math.floor(time))
    time_m = int(math.floor((time-time_h)*60))
    time_s = int(math.floor((((time-time_h)*60)-time_m)*60))  # másodperc 2-ik tizedesjegyéig pontos
    return time_h, time_m, time_s


def day_to_time(time):  # tizedesjegyben kifejezve, ez kell?
    time_d = int(math.floor(time))
    time_h = int(math.floor((time-time_d)*24))
    time_m = int(math.floor((((time-time_d)*24)-time_h)*60))  # másodperc 2-ik tizedesjegyéig pontos
    time_s = int(math.floor((((((time-time_d)*24)-time_h)*60)-time_m)*60))
    return time_d, time_h, time_m, time_s


def JD(year, month, day, hour, minute):
    Y = year
    M = month
    D = day + float(hour)/24 + float(minute)/1440

    if M == 1 or M == 2:
        Y -= 1
        M += 12

    A = int(Y/100)

    x = Y*10000 + M*100 + D
    if x < 15821015:  # However, if the date is earlier than October 15, 1582 then B=0.
        B = 0
    else:
        B = 2-A+int(A/4)

    if Y < 0:
        C = int((365.25*Y)-0.75)
    else:
        C = int(365.25*Y)

    E = int(30.6001*(M+1))
    JD = B + C + D + E + 1720994.5

    return JD


def sun_position(julian_date, latitude, longitude, timezone, info):
    julian_date -= timezone/24  # JD helyi idő szerint definiálandó!

    n = julian_date - 2451545.0000000
    L = 280.460 + 0.9856474*n  # fok
    g = 357.528 + 0.9856003*n  # fok

    k = math.floor(L/360)
    m = math.floor(g/360)

    L = math.radians(L - k*360)  # radián
    g = math.radians(g - m*360)  # radián

    # Ekliptikus koordinátarendszer
    sun_lambda = L + math.radians(1.915)*math.sin(g) + math.radians(0.020)*math.sin(2*g)  # radián
    sun_beta = 0  # radián
    sun_distance = 1.00014 - 0.01671*math.cos(g) - 0.00014*math.cos(2*g)  # AU

    # Áttérés ekvatoriális koorináta rendszerre
    epsilon = math.radians(23.4393 - 0.0000004*n)  # 23.43699 fok - pillanatnyi érték, 22.1 és 24.5 között váltakozik 41000 éves ciklusban (radiánban kifejezve)
    RA = math.atan2(math.cos(epsilon)*math.sin(sun_lambda), math.cos(sun_lambda))  # radián
    DEC = math.asin(math.sin(epsilon)*math.sin(sun_lambda))  # radián

    # LST számítása
    JD_null = round(julian_date) - 0.5
    H = (julian_date - JD_null)*24
    D_null = JD_null - 2451545.0
    T = n/36525
    GST = 6.697374558 + 0.06570982441908*D_null + 1.00273790935*H + 0.000026*(T*T)  # órában
    o = math.floor(GST/24)
    GST = GST - o*24  # óra

    LST = GST + (longitude/15)
    p = math.floor(LST/24)
    LST = LST - p*24  # óra

    GST_h, GST_m, GST_s = hour_to_time(GST)
    LST_h, LST_m, LST_s = hour_to_time(LST)

    day_fraction = julian_date-int(math.floor(julian_date)) + 0.50000000
    UT_d, UT_h, UT_m, UT_s = day_to_time(day_fraction)

    # Áttérés horizontális koordinátarendszerbe
    h = math.radians(LST*15) - RA  # radián
    sun_elevation = math.asin(math.sin(latitude)*math.sin(DEC) + math.cos(latitude)*math.cos(DEC)*math.cos(h))

    a = -1*math.sin(latitude)*math.cos(DEC)*math.cos(h) + math.cos(latitude)*math.sin(DEC)
    b = math.cos(DEC)*math.sin(h)
    # sun_azimut = -1*math.atan2( -1*math.sin(latitude)*math.cos(DEC)*math.cos(h) + math.cos(latitude)*math.sin(DEC) , math.cos(DEC)*math.sin(h) )
    sun_azimut = -1*math.atan2(b, a)

    if sun_azimut < 0:
        sun_azimut = sun_azimut + 2*math.pi
    else:
        pass

    # LST_string = str(LST_h) + ":" + str(LST_m) + ":" + str(LST_s)
    UT_string = str(UT_h) + ":" + str(UT_m) + ":" + str(UT_s)
    sun_elevation_deg = math.degrees(sun_elevation)
    sun_azimut_deg = math.degrees(sun_azimut)

    if info is True:
        print("-- A " + str(julian_date) + " (JD) napon, a Nap ekliptikus koordinátái: --\n"
        # + "Number of days from epoch (n): " + str(n) +" d \n"
        # + "Mean longitude (L): " + str(math.degrees(L)) +"° \n"
        # + "Mean anomaly (g): " + str(math.degrees(g)) + "° \n"
        + "Ecliptic longitude (lambda): " + str(math.degrees(sun_lambda)) + "°\n"
        + "Ecliptic latitude (beta): " + str(math.degrees(sun_beta)) + "°\n"
        + "Earth-Sun distance (R): " + str(sun_distance) + " AU\n" + "\n"

        "-- A Nap ekvatoriális koordinátái: --\n"
        + "Right ascension (RA): " + str(math.degrees(RA)) + "°\n"
        + "Declination (DEC): " + str(math.degrees(DEC)) + "°\n" + "\n"

        "-- A Nap horizontális koordinátái: --\n"
        + "Magasság (a): " + str(math.degrees(sun_elevation)) + "°\n"
        + "Azimut (A): " + str(math.degrees(sun_azimut_deg)) + "°\n" + "\n"

        "-- További időadatok: --\n"
        + "Universal Time (UT): " + str(UT_h) + ":" + str(UT_m) + ":" + str(UT_s) + "\n"
        + "Greenwich Sidereal Time (GST): " + str(GST_h) + ":" + str(GST_m) + ":" + str(GST_s) + "\n"
        + "Local Sidereal Time (LST): " + str(LST_h) + ":" + str(LST_m) + ":" + str(LST_s) + "\n" + "\n"
        )

    else:
        pass

    return UT_string, sun_elevation_deg, sun_azimut_deg

# Teszteléshez
# curr_time = JD(2018, 2, 14, 12, 00, False) # Helyi idő szerint
# sun_position(curr_time, True)

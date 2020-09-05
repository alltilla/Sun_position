# -*- coding: utf-8 -*-
import sys
import math
import sun_position as SP

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout


def sun_energy(alt, azimut, delta_sec, panel_alt, panel_azimut):
    panel_area = 1.64 * 0.992  # m2
    efficiency = 1  # arbitrary

    azimut_diff = panel_azimut - azimut
    panel_diff = 90 - panel_alt - alt

    if alt > 0.5:  # Ha a Nap teljes terjedelmével a horizont felett van
        if abs(azimut_diff) < 90:  # Ha a napsugár és a panel szögkülönbsége kisebb mint 90°
            # intensity in kw/m2 = 1.35 * (1.00/1.35)^sec(angle of sun from zenith)
            i = 1.35 * math.pow((1.00/1.35), (1 / math.cos(math.radians(90-alt))))
            a = abs(math.cos(math.radians(panel_diff)))
            b = abs(math.cos(math.radians(azimut_diff)))

            energy = panel_area * delta_sec * a * b * i * efficiency  # kW/m2 * s * m2
        else:
            energy = 0
    else:
        energy = 0

    return energy


def energy_DAT(alt, azimut, delta_sec):
    global panel_power

    if alt > 0.5:  # Ha a Nap teljes terjedelmével a horizont felett van
        # intensity in kw/m2 = 1.35 * (1.00/1.35)^sec(angle of sun from zenith)
        i = 1.35 * math.pow((1.00/1.35), (1 / math.cos(math.radians(90-alt))))
        energy = (panel_power * delta_sec) * i / 1000  # kJ
    else:
        energy = 0

    return energy


def energy_fixed(alt, azimut, delta_sec, panel_alt, panel_azimut):
    global panel_power

    azimut_diff = panel_azimut - azimut
    panel_diff = (90 - panel_alt) - alt

    if alt > 0.5:  # Ha a Nap teljes terjedelmével a horizont felett van
        if abs(azimut_diff) < 90:  # Ha a napsugár és a panel szögkülönbsége kisebb mint 90°
            # intensity in kw/m2 = 1.35 * (1.00/1.35)^sec(angle of sun from zenith)
            i = 1.35 * math.pow((1.00/1.35), (1 / math.cos(math.radians(90-alt))))
            # a = math.cos(math.radians(panel_diff))
            # b = math.cos(math.radians(azimut_diff))

            r = 1
            # Sun coordinates
            x1 = r * math.cos(math.radians(alt)) * math.cos(math.radians(azimut))
            y1 = r * math.cos(math.radians(alt)) * math.sin(math.radians(azimut))
            z1 = r * math.sin(math.radians(alt))

            # Panel normal vector
            x2 = r * math.cos(math.radians(90 - panel_alt)) * math.cos(math.radians(panel_azimut))
            y2 = r * math.cos(math.radians(90 - panel_alt)) * math.sin(math.radians(panel_azimut))
            z2 = r * math.sin(math.radians(90 - panel_alt))

            aa = (x1 * x2) + (y1 * y2) + (z1 * z2)
            bb = math.sqrt(math.pow(x1, 2) + math.pow(y1, 2) + math.pow(z1, 2)) * math.sqrt(math.pow(x2, 2) + math.pow(y2, 2) + math.pow(z2, 2))
            cos_diff_angle = float(aa/bb)

            energy = panel_power * delta_sec * cos_diff_angle * i / 1000  # kJ
        else:
            energy = 0
    else:
        energy = 0

    return energy


def sun_daily_movement(date, resolution):
    date_s = date

    step_fraction = 0.00000000000
    steps = 24*60/resolution  # stepek száma egy napon (min)
    step_fraction = float(24/24) / float(steps)  # day / steps costant

    s = 0
    time_0_data = []
    elev_data = []
    alt_data = []

    date_0 = float(date_s)

    for s in range(0, steps):  # Sun position data
        UT_time_0, elev_0, azim_0 = SP.sun_position(date_0, False)
        time_0_data.append(UT_time_0)
        elev_data.append(elev_0)
        alt_data.append(azim_0)

        s += 1
        date_0 = float(date_0) + float(step_fraction)

    plot([Scatter(x=time_0_data, y=elev_data, name="Elevation"), Scatter(x=time_0_data, y=alt_data, name="Azimuth")])


def daily_energy_gain(date, resolution, print_plot):  # 38.82 fok dőlésszög esetén
    date_s = date
    panel_tilt = 38.82

    step_fraction = 0.00000000000
    steps = 24*60/resolution  # stepek száma egy napon (min)
    step_fraction = float(24/24) / float(steps)  # day / steps costant

    delta_T = resolution*60  # (s) lépésköz
    energy_DAT_data = 0
    energy_fix_data = 0
    sum_energy_DAT_data = 0
    sum_energy_fix_data = 0

    time_data = []
    DAT_data = []
    fix_data = []

    date_0 = float(date_s)

    for k in range(0, steps + 1):
        UT_time, elev, azim = SP.sun_position(date_0, False)

        # Energia adatok
        energy_DAT_data = energy_DAT(elev, azim, delta_T)  # kJ
        sum_energy_DAT_data += energy_DAT_data  # kJ

        energy_fix_data = energy_fixed(elev, azim, delta_T, panel_tilt, 180)  # kJ
        sum_energy_fix_data += energy_fix_data  # kJ

        time_data.append(UT_time)
        DAT_data.append(energy_DAT_data)
        fix_data.append(energy_fix_data)

        date_0 = float(date_0) + float(step_fraction)

    if print_plot is True:
        print("Kinyert összenergia (DAT): " + str(sum_energy_DAT_data) + " kJ")
        print("Kinyert összenergia (fixed at " + str(panel_tilt) + " deg): " + str(sum_energy_fix_data) + " kJ")

        graph_name = str("FIX" + str(panel_tilt))
        plot([Scatter(x=time_data, y=DAT_data, name="DAT"), Scatter(x=time_data, y=fix_data, name=graph_name)])
    else:
        pass

    return sum_energy_DAT_data, sum_energy_fix_data, panel_tilt


def daily_energy_gain_fixed(date, resolution, panel_tilt, print_plot):
    date_s = date

    step_fraction = 0.00000000000
    steps = 24*60/resolution  # stepek száma egy napon (min)
    step_fraction = float(24/24) / float(steps)  # day / steps costant

    delta_T = resolution*60  # (s) lépésköz
    energy_fix_data = 0
    sum_energy_fix_data = 0

    time_data = []
    fix_data = []

    date_0 = float(date_s)

    for k in range(0, steps + 1):
        UT_time, elev, azim = SP.sun_position(date_0, False)

        # Energia adatok
        energy_fix_data = energy_fixed(elev, azim, delta_T, panel_tilt, 180)  # kJ
        sum_energy_fix_data += energy_fix_data  # kJ

        time_data.append(UT_time)
        fix_data.append(energy_fix_data)

        date_0 = float(date_0) + float(step_fraction)

    if print_plot is True:
        print("Kinyert összenergia (fixed at " + str(panel_tilt) + " deg): " + str(sum_energy_fix_data) + " kJ")
        graph_name = str("FIX" + str(panel_tilt))
        plot([Scatter(x=time_data, y=fix_data, name=graph_name)])
    else:
        pass

    return sum_energy_fix_data


def interval_energy_gain(date, number_of_days):
    date_s = date

    sum_energy_DAT_data = 0
    sum_energy_fix_data = 0

    time_data = []
    DAT_data = []
    fix_data = []

    date_0 = date_s
    print("Iteration started!")

    for m in range(0, number_of_days + 1):
        DAT_energy, FIX_energy, panel_tilt = daily_energy_gain(date_0, 1, False)

        sum_energy_DAT_data += DAT_energy  # kJ
        sum_energy_fix_data += FIX_energy  # kJ

        time_data.append(m)
        DAT_data.append(DAT_energy)
        fix_data.append(FIX_energy)

        date_0 += 1

    print("Kinyert összenergia (DAT): " + str(sum_energy_DAT_data) + " kJ")
    print("Kinyert összenergia (fixed at " + str(panel_tilt) + " deg): " + str(sum_energy_fix_data) + " kJ")
    graph_name = str("FIX" + str(panel_tilt))
    plot([Scatter(x=time_data, y=DAT_data, name="DAT"), Scatter(x=time_data, y=fix_data, name=graph_name)])


def interval_energy_gain_optimum_calc(date, number_of_days, start_angle, end_angle, count):  # expected optimum angle: 38.82
    date_s = date
    angle_step = float(end_angle - start_angle)/float(count)

    angle_1 = 20
    angle_2 = 40
    angle_3 = 60
    day_data_1 = []
    day_data_2 = []
    day_data_3 = []
    daily_energy_data_1 = []
    daily_energy_data_2 = []
    daily_energy_data_3 = []

    sum_energy_fix_data = 0
    angle_data = []
    energy_data = []

    max_energy = 0
    optimal_tilt_angle = 0

    date_0 = date_s
    angle_0 = start_angle
    print("Iteration started!")

    for o in range(0, count + 1):
        for m in range(0, number_of_days + 1):
            FIX_energy = daily_energy_gain_fixed(date_0, 1, angle_0, False)
            sum_energy_fix_data += FIX_energy  # kJ

            if angle_0 == angle_1:
                day_data_1.append(m)
                daily_energy_data_1.append(FIX_energy)
            elif angle_0 == angle_2:
                day_data_2.append(m)
                daily_energy_data_2.append(FIX_energy)
            elif angle_0 == angle_3:
                day_data_3.append(m)
                daily_energy_data_3.append(FIX_energy)
            else:
                pass

            date_0 += 1

        angle_data.append(angle_0)
        energy_data.append(sum_energy_fix_data)

        if sum_energy_fix_data > max_energy:
            max_energy = sum_energy_fix_data
            optimal_tilt_angle = angle_0
        else:
            pass

        sum_energy_fix_data = 0
        print("Iteration " + str(o + 1) + "/" + str(count + 1) + " is ready!" + " Angle: " + str(angle_0) + "°.")
        date_0 = date_s
        angle_0 += angle_step

    efficiency_data = []
    for p in range(0, len(energy_data)):
        efficiency_data.append(energy_data[p]/max_energy)

    print("Max. energy yield with the optimal tilt angle (" + str(optimal_tilt_angle) + "): " + str(max_energy/1000/1000) + " GJ")
    # plot([Scatter(x=angle_data, y=energy_data, name="Fix_angle")])
    plot([Scatter(x=angle_data, y=efficiency_data, name="Fix_angle")])

    graph_name_1 = "FIX" + str(angle_1)
    graph_name_2 = "FIX" + str(angle_2)
    graph_name_3 = "FIX" + str(angle_3)
    # plot([Scatter(x=day_data_1, y=daily_energy_data_1, name=graph_name_1), Scatter(x=day_data_2, y=daily_energy_data_2, name=graph_name_2), Scatter(x=day_data_3, y=daily_energy_data_3, name=graph_name_3)])


# -- MAIN --
n_panel = 1760  # db
panel_power = 285  # W

# sun_daily_movement(SP.JD(2018, 2, 14, 0, 0, False), 1)
# daily_energy_gain(SP.JD(2018, 2, 14, 0, 0, False), 1, True)
# interval_energy_gain(SP.JD(2018, 2, 14, 0, 0, False), 365)

# daily_energy_gain_fixed(SP.JD(2018, 2, 14, 0, 0, False), 1, 40, True)
# daily_energy_gain_fixed(SP.JD(2018, 2, 14, 0, 0, False), 1, 45, True)
# daily_energy_gain_fixed(SP.JD(2018, 2, 14, 0, 0, False), 1, 50, True)
interval_energy_gain_optimum_calc(SP.JD(2018, 1, 1, 0, 0), 365, 15, 50, 35)

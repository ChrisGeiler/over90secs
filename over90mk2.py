import os
import datetime
import csv
import shutil


def closest_data(target, group):
    closest_delta = None
    closest_time = None

    for entry in group:
        (my_time, my_alt) = entry
        delta = abs(target - my_alt)

        if not closest_delta or delta < closest_delta:
            closest_delta = delta
            closest_time = my_time

        else:
            break

    return closest_time


def check_csv_greater(filename):
    csv_file = csv.reader(open(filename, "r"))
    print('"' + filename + '"')
    destination = "over90"
    window_top = 3000
    window_bottom = 2000
    window_target = 85
    exit_speed = 10
    target_buffer = 2

    csv_data = list(csv_file)
    ground_level = float(csv_data[-1][3])
    print("DZ elevation was " + str(round(ground_level)) + " above sea level. ")

    start_times = []
    stop_times = []
    exit_alt = []

    start_time = None
    stop_time = None
    exited_plane = False

    counter = 0

    for row in csv_data:
        counter += 1
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        if counter < 3:
            pass

        if counter > 2:
            counter += 1

            time = row[0]
            altitude = row[3]
            vert_speed = row[6]

            time = datetime.datetime.strptime(time, time_format)
            time = time.timestamp()
            altitude = float(altitude)
            altitude = altitude - ground_level
            vert_speed = float(vert_speed)

            if not exited_plane:
                if vert_speed > exit_speed:
                    exit_alt.append(altitude)
                    exited_plane = True
                    print("Exit altitude was " + str(round(exit_alt[0])) + " meters above ground level. ")

            if exited_plane:
                values = [time, altitude]

                if window_top - target_buffer < altitude < window_top + target_buffer:
                    start_times.append(values)

                elif window_bottom - target_buffer < altitude < window_bottom + target_buffer:
                    stop_times.append(values)

    if start_times and stop_times:
        start_time = closest_data(window_top, start_times)
        stop_time = closest_data(window_bottom, stop_times)

    if start_time and stop_time:
        window_time = stop_time - start_time
        print("Time inside competition window is " + str(window_time) + " seconds. ")

        if window_time > window_target:
            shutil.copy(filename, destination)
            print(f"Track is over {window_target} seconds for competition window located! ")

        if window_time < window_target:
            print(f"Track is lower than {window_target} seconds for competition window. ")
    print()


def run_me():
    mydir = "tracks"
    file_list = os.scandir(path=mydir)
    for file in file_list:
        file = file.name
        if ".csv" in file:
            filepath = os.path.join(mydir, file)
            check_csv_greater(filepath)


if __name__ == "__main__":
    run_me()


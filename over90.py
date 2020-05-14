import csv
import datetime
import shutil
import os


def closest(target, group):
    # target is a value close to window top or bottom
    # group is a list that looks like this: [(time, 3010.5), (time, 2999.9)]
    mylist = []
    for entry in group:
        (mytime, mymeters) = entry
        mylist.append([abs(target - mymeters), mymeters, mytime])

    mylist = sorted(mylist)

    result = mylist[0][2]
    # the result SHOULD be closest to target
    return result


def check_csv_greater_90(filename):
    csv_reader = csv.reader(open(filename, 'r'))
    dest = "over90"
    print('"' + filename + '"')

    # flysight data is raw elevation and needs to be corrected
    # competition definition of exit is when Vertical Speed exceeds 10m/s

    window_start = 3000.0
    window_stop = 2000.0
    target_time = 80.0
    buffer = 20.0
    vspeed_exit_signal = 10.0

    # find the ground level using the last entry in the csv_reader
    csv_reader = list(csv_reader)
    ground_level = csv_reader[-1][3]

    try:
        ground_level = float(ground_level)
    except:
        print("Failed to float: " + str(ground_level))

    print("New ground level: " + str(ground_level))

    start_times = []
    stop_times = []
    exit_alt = []

    start_time = None
    stop_time = None

    exit_started = False

    counter = 0

    for row in csv_reader:
        # need to remove header lines
        counter += 1
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        if counter < 3:
            pass
        elif counter > 2:
            counter += 1

            time = row[0]
            altitude = row[3]
            v_speed = row[6]

            # convert string into datetime
            time = datetime.datetime.strptime(time, time_format)
            time = time.timestamp()

            try:
                altitude = float(altitude)
                altitude = altitude - ground_level
            except:
                print("Failed to float: " + str(altitude))

            try:
                v_speed = float(v_speed)
            except:
                print("Failed to float: " + str(v_speed))

            if not exit_started:
                # check to see if exited
                # if exited, set boolean to True
                if v_speed > vspeed_exit_signal:
                    exit_alt.append(altitude)
                    exit_started = True
                    print(f"Exit Altitude was: " + str(exit_alt[0]) + "m above ground level.")

            if exit_started:
                values = [time, altitude, v_speed]
                # if altitude > window variable - 40.0 and altitude < window variable + 50.0
                # print(values)
                if altitude > window_start - buffer and altitude < window_start + buffer:
                    start_times.append((time, altitude))
                elif altitude > window_stop - buffer and altitude < window_stop + buffer:
                    stop_times.append((time, altitude))

    if start_times and stop_times:
        # print("Start time: " + (start_time))
        start_time = closest(window_start, start_times)
        # print("Start Time: " + str(start_time))
        stop_time = closest(window_stop, stop_times)

    if start_time and stop_time:
        windowtime = stop_time - start_time
        print("Window time: " + str(windowtime))
        if windowtime > target_time:
            print(f'Track over {target_time} seconds located!')
            # do something here to add the file to a special folder
            shutil.copy(filename, dest)
    print()


def run_me():
    mydir = "tracks"
    file_list = os.scandir(path=mydir)
    for file in file_list:
        file = file.name
        if ".csv" in file:
            filepath = os.path.join(mydir, file)
            # print(filepath)
            check_csv_greater_90(filepath)


if __name__ == '__main__':
    run_me()

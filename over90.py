import csv
import datetime
import shutil
import os


def first_closest(target, group):
    # closest delta is the closest current position to the target in meters (target-mymeters)
    closestdelta = None
    # closest time is the corresponding time stamp for the closest delta that has been found
    closesttime = None

    for entry in group:
        # entry is what's included in the group which gets checked each time in the for loop to find the closest delta
        (mytime, mymeters) = entry
        # delta is the current position that is being checked to see how close the target is when compared to mymeters
        delta = abs(target - mymeters)

        # if statement will create the first closestdelta so there will be a delta to check in the for loop
        # or delta less than will contine for loop while delta keeps getting smaller.
        if not closestdelta or delta < closestdelta:
            # for each subsequent entry, we set these variables if they are closer to target
            closestdelta = delta
            closesttime = mytime
        else:
            # else will cause break if delta becomes further from the target than previous loop
            break

    return closesttime


# def closest(target, group):
#     # target is a value close to window top or bottom
#     # group is a list that looks like this: [(time, 3010.5), (time, 2999.9)]
#     mylist = []
#
#     for entry in group:
#         (mytime, mymeters, myVspeed) = entry
#
#         if myVspeed > 0:
#             mylist.append([abs(target - mymeters), mymeters, mytime, myVspeed])
#
#     print(sorted(mylist))
#
#     result = mylist[0][2]
#     # the result SHOULD be closest to target
#     return result


def check_csv_greater_90(filename):
    # the file thas has been opened in a readable format using the reader function
    # from the csv module shall be named csv_reader
    csv_reader = csv.reader(open(filename, 'r'))
    # the detsination folder of copied files is set as over90
    dest = "over90"
    print('"' + filename + '"')

    # competition definition of exit is when Vertical Speed exceeds 10m/s

    # variables to call on within function
    window_start = 3000.0
    window_stop = 2000.0
    target_time = 90.0
    buffer = 5.0
    # competition definition of exit is when Vertical Speed exceeds 10m/s
    vspeed_exit_signal = 10.0

    csv_reader = list(csv_reader)
    # flysight data is raw elevation and needs to be corrected
    # ground level is the last entry of csv_reader in the 4th column
    ground_level = csv_reader[-1][3]

    try:
        # converting ground level to a float number instead of a string
        ground_level = float(ground_level)
    except:
        print("Failed to float: " + str(ground_level))

    print("Ground level for this file is: " + str(ground_level))

    start_times = []
    stop_times = []
    exit_alt = []

    start_time = None
    stop_time = None
    exit_started = False

    counter = 0

    for row in csv_reader:
        # need to remove the 3 header lines by passing rows until greater than 3 rows
        counter += 1
        # time format needs to be ISO for converting to time stamp
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        if counter < 3:
            pass
        elif counter > 2:
            counter += 1

            time = row[0]
            altitude = row[3]
            v_speed = row[6]

            # convert string of time into datetime time stamp
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
                # check to see if exited to make sure climb to altitude is not checked
                # if exited, set boolean to True
                if v_speed > vspeed_exit_signal:
                    exit_alt.append(altitude)
                    exit_started = True
                    print(f"Exit Altitude was: " + str(exit_alt[0]) + "m above ground level.")

            if exit_started:
                values = [time, altitude]

                if window_start - buffer < altitude < window_start + buffer:
                    start_times.append(values)

                elif window_stop - buffer < altitude < window_stop + buffer:
                    stop_times.append(values)

    if start_times and stop_times:
        # print("Start time: " + (start_time))
        # start_time loccated by using first_closest function with window_start and start_times
        start_time = first_closest(window_start, start_times)
        # print("Start Time: " + str(start_time))
        # stop time located by using first_closest functino with window-stop and stop_times
        stop_time = first_closest(window_stop, stop_times)

    if start_time and stop_time:
        # time in window is closest stop_time - closest start_time
        windowtime = stop_time - start_time
        print("Time inside competition window was: " + str(windowtime))
        if windowtime > target_time:
            print(f'Track over {target_time} seconds located!')
            # if closest start and stop time have been found, copy to destination folder
            shutil.copy(filename, dest)
        if windowtime < target_time:
            print(f"Track was lower than {target_time} seconds. ")
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

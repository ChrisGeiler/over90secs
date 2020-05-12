import csv

with open('CR++.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)

    for alt_time in csv_reader:
        i = alt_time[0]
        j = alt_time[3]
        if i.isdigit():
            i = int(i)
        elif j.isdigit():
            j = int(j)

    for window in csv_reader:







    # for row in csv_reader_dict:
        # window starts at 3000 and ends at 2000 hMSL
        # window = int(row['hMSL'])
        # if window >= 2000 <= 30001:
            # print(window)




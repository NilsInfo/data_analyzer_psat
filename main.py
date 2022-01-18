import json
from matplotlib import pyplot as plt
import numpy as np
def get_data(fileName):
    realNames = dict() # links between experiences and ids
    labels = dict() # links between lists and ids
    offsets = dict()
    count = 0
    data = []
    minLevel = 100
    f = open(fileName)
    lines = f.readlines()
    for index, l in enumerate(lines):
        if "exp" in l:
            jsonl = json.loads(lines[index+1])
            labels[jsonl["id"]] = count
            realNames[jsonl["id"]] = l.split('\"')[1]
            count += 1
            data.append([[],[],jsonl["id"]])
        else :
            if "id" in l: # checks if the syntax of the line is correct
                jsonl = json.loads(l)
                if jsonl["id"] in labels.keys(): # checks if it's a recorded id
                    if jsonl["id"] == "tr60_wifi4_lum0":
                        print("yo")
                    if jsonl["level"] != 1 : # We only take data when the battery reaches 99%
                        if len(data[labels[jsonl["id"]]][0]) == 0 : # add an offset for the timestamps to be relative
                            offsets[jsonl["id"]] = int(jsonl["ts"])

                        data[labels[jsonl["id"]]][0].append(int(jsonl["ts"]) - offsets[jsonl["id"]])
                        data[labels[jsonl["id"]]][1].append(jsonl["level"]*100)
    print(realNames)
    print(labels)
    print(data)
    return realNames, data

def plot_data(realNames, data):
    fig, ax = plt.subplots(1, figsize=(8, 6))
    minsTimesElapsed = []
    # calculate the experience with the minimum of time elapsed
    for i in range(len(data)):
        print(i)
        print(data[i])
        minsTimesElapsed.append(data[i][0][-1] - data[i][0][0])
    minTime = min(minsTimesElapsed)
    print(minsTimesElapsed)
    minsLevels = []
    # plot it
    for i in range(len(data)):
        minLen = int(minTime//20)
        if minLen >= len(data[i][0]) : # sometimes, the data is not wrote (there are holes)
            minLen = len(data[i][0] )- 1
        ax.plot(data[i][0][:minLen],data[i][1][:minLen], label = realNames[data[i][2]])
        minsLevels.append(min(data[i][1][:minLen])) # find the minimum level reached within the min time of exp
    # clean it
    ax.set_yticks(np.arange(min(minsLevels)-1,100, step=1))
    ax.set_xlabel("time (sec)")
    ax.set_ylabel("battery (%)")
    ax.grid(which = "major")
    plt.legend(loc="upper right", frameon=False)
    plt.show()

if __name__ == '__main__':
    realNames, data = get_data("exp_recurrence.txt")
    plot_data(realNames, data)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

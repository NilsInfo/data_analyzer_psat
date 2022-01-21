import json
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import linregress

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
                    # if jsonl["id"] == "tr60_wifi4_lum0":
                    #     print("yo")
                    if jsonl["level"] != 1 : # We only take data when the battery reaches 99%
                        if len(data[labels[jsonl["id"]]][0]) == 0 : # add an offset for the timestamps to be relative
                            offsets[jsonl["id"]] = int(jsonl["ts"])

                        data[labels[jsonl["id"]]][0].append(int(jsonl["ts"]) - offsets[jsonl["id"]])
                        data[labels[jsonl["id"]]][1].append(99-jsonl["level"]*100)
                        # data[labels[jsonl["id"]]][1].append(jsonl["level"]*100)
    # print(realNames)
    # print(labels)
    # print(data[0])
    minsTimesElapsed = []
    # calculate the experience with the minimum of time elapsed
    for i in range(len(data)):
        # print(i)
        # print(data[i])
        minsTimesElapsed.append(data[i][0][-1] - data[i][0][0])
    minTime = min(minsTimesElapsed)
    # print(minsTimesElapsed)
    return realNames, data, minTime

#returns the array with the percentage transition time, from 0% to 8% (of battery consumption)
def get_levels_array(data):
    totalLevels = []
    # print(data[0][0])
    for i in range(len(data)):
        expeLevels = [[],[]]
        for j in range(1,len(data[i][1])):
            if((data[i][1][j-1]!=data[i][1][j]) and data[i][1][j-1]<8):         #if percentage transition and percentage < 8
                expeLevels[1].append(data[i][1][j])         #appending the percentage value
                expeLevels[0].append(data[i][0][j]-10)      #appending the corresponding time, -10 to get the middle of the interval of time
        totalLevels.append(expeLevels)
    # print(totalLevels)
    return totalLevels

def get_average_levels(data):
    average_levels = [[],[]]
    for i in range(len(data[0][0])):
        sum=0
        for j in range(len(data)):
            sum+=data[j][0][i]
            average=sum/len(data)
        average_levels[0].append(average)
        average_levels[1].append(i+1)

    return average_levels

def get_standard_deviation(levels_array,average_levels):
    standard_deviations = [[],[]]

    for i in range(len(average_levels[0])):

        mean_value=average_levels[0][i]
        sum=0

        for j in range(len(levels_array)):
            sum+=(mean_value-levels_array[j][0][i])**2

        standard_deviations[0].append(np.sqrt(sum/len(levels_array)))
        standard_deviations[1].append(i+1)

    return standard_deviations , np.mean(standard_deviations[0])

def plot_bar_chart(realNames, data, minTime):
    labels = ['Le Figaro','Allociné', 'Le parisien', '20 minutes', 'Marmiton']
    web_with_ads = [int(7*3600*100/(1642693560-1642691040))/100] # values for lefigaro are hardcoded because of problems of measurements
    web_ads_blocked = [int(7*3600*100/(1642711560-1642704840))/100]
    minsLevels = []
    coefHour = minTime / 3600
    for i in range(len(data)):
        minLen = int(minTime//20)
        if minLen >= len(data[i][0]) : # sometimes, the data is not wrote (there are holes)
            minLen = len(data[i][0] )- 1
        if "blocked" in realNames[data[i][2]] :
            web_ads_blocked.append(int(((100-data[i][1][minLen])/coefHour)*10)/10)
        else :
            web_with_ads.append(int(((100-data[i][1][minLen])/coefHour)*10)/10)
        minsLevels.append(min(data[i][1][:minLen])) # find the minimum level reached within the min time of exp

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    with_ads = ax.bar(x - width / 2, web_with_ads, width, label='With ads')
    ads_blocked = ax.bar(x + width / 2, web_ads_blocked, width, label='ads_blocked')
    ax.errorbar(x - width/2, web_with_ads, 1.2, color='red', ecolor='red', fmt='o', elinewidth = 2, capsize=10)
    ax.errorbar(x + width/2, web_ads_blocked, 1.2, color='red', ecolor='red', fmt='o', elinewidth = 2, capsize=10)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Battery lost (%)')
    ax.set_title('Percentage of battery lost per hour')
    ax.set_xticks(x, labels)
    ax.set_yticks(np.arange(0,(102-min(minsLevels))//coefHour, step=1))

    ax.legend()

    ax.bar_label(with_ads, padding=3)
    ax.bar_label(ads_blocked, padding=3)
    ax.boxplot([2,10])

    fig.tight_layout()

    plt.show()

def get_uncertainty(yValues, minLen, redondantUncertainty):
    coeff_uncertainty = 0.38/yValues[minLen-1]*redondantUncertainty
    return ([y*coeff_uncertainty for y in yValues])

def get_standard_deviation2(x,y,yModeled):
    sum=0
    for i in range(len(x)):
        sum+=(yModeled[i]-y[i])**2
    
    return (np.sqrt(sum)/len(x))

def plot_data(realNames, data, minTime):
    fig, ax = plt.subplots(1, figsize=(8, 6))
    colors = ['red','blue','yellow','green','pink','magenta','orange']
    modelStderrs = []
    minsLevels = []
    # plot it
    for i in range(len(data)):
        minLen = int(minTime//20)
        if minLen >= len(data[i][0]) : # sometimes, the data is not wrote (there are holes)
            minLen = len(data[i][0] )- 1
        ax.plot(data[i][0][:minLen],data[i][1][:minLen], label = realNames[data[i][2]], color=colors[i])
        

        # model=np.polyfit(data[i][0][:minLen],data[i][1][:minLen],1)
        model=linregress(data[i][0][:minLen],data[i][1][:minLen])
        print(model.slope*3600)
        print(model.stderr*3600)
        yModelValues = [j*model.slope for j in data[i][0][:minLen]]+model.intercept
        uncertainty = get_uncertainty(yModelValues,minLen,model.stderr)

        modelStderrs.append(model.stderr)

        plt.fill_between(data[i][0][:minLen], 
                        [yModelValues[j]-uncertainty[j] for j in range(len(data[i][1][:minLen]))], 
                        [yModelValues[j]+uncertainty[j] for j in range(len(data[i][1][:minLen]))],
                        color=colors[i], alpha=0.2)
        minsLevels.append(min(data[i][1][:minLen])) # find the minimum level reached within the min time of exp
        
    # clean it
    ax.set_yticks(np.arange(0,12, step=1))
    ax.set_xlabel("time (sec)")
    ax.set_ylabel("battery consumed (%)")
    ax.grid(which = "major")
    plt.legend(loc="upper right", frameon=False)

    plt.show()

def display_standard_deviations(standard_deviations, mean):
    fig, ax = plt.subplots(1, figsize=(8, 6))

    ax.bar(standard_deviations[1],standard_deviations[0], label = "standard deviation")
    # ax.axhline(y=mean, color='r', linestyle='-', label= "mean standard deviation")
    # ax.set_xticks(np.arange(0,11, step=1))
    ax.set_yticks(np.arange(0,200, step=25))
    ax.set_ylabel("standard deviation of time measured (sec)")
    ax.set_xlabel("battery consumed (%)")
    ax.grid(which = "major")
    plt.legend(loc="upper right", frameon=False)
    plt.show()

def calculate_linear_regression(data):
    regression_coeffs = []
    for i in range(len(data)):
        model=np.polyfit(data[i][0],data[i][1],1)
        regression_coeffs.append(model[0]*3600)
    print(np.mean(regression_coeffs))
    sum=0
    for i in range(len(regression_coeffs)):
        sum+=(np.mean(regression_coeffs)-regression_coeffs[i])**2
    
    return regression_coeffs, np.sqrt(sum/len(regression_coeffs))

if __name__ == '__main__':
    realNames, data, minTime = get_data("exp_tr.txt")
    levels_array = get_levels_array(data)
    # print(levels_array)
    # average_levels = get_average_levels(levels_array)
    # standard_deviations, mean_standard_deviation = get_standard_deviation(levels_array,average_levels)
    # regression_coeffs, standard_deviation_coeffs = calculate_linear_regression(data)
    # print(regression_coeffs)
    # print(standard_deviation_coeffs)
    # print(standard_deviations)
    # print(mean_standard_deviation)
    # display_standard_deviations(standard_deviations, mean_standard_deviation)
    # print(realNames)
    plot_data(realNames, data, minTime)
    # print(data)
    # plot_bar_chart(realNames, data, minTime)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import xml.etree.ElementTree as ET
import csv
import matplotlib.pyplot as plt

'''
This class represents one Mushroom Type.
'''


class Mushroom:

    def __init__(self, attributes: dict):
        self.attr = attributes

    def time_value(self, cur_month):
        return self.attr["seasonStart"] <= cur_month <= self.attr["seasonEnd"]


def tree_value(mushroom, tree_type: str):
    com_fac = 1
    if mushroom.attr['commonness'] == "Selten":
        com_fac = 0.33
    hardwood = 0
    if tree_type == "Mischwaelder" or tree_type == "Laubwaelder":
        hardwood = 1
    softwood = 0
    if tree_type == "Mischwaelder" or tree_type == "Nadelwaelder":
        softwood = 1
    wt = mushroom.attr['woodtype']

    wood_type_factor = min(wt[0] * hardwood + wt[1] * softwood, 1)

    wiesen = ["Wiesen und Weiden", "Natuerliches Gruenland", "Heiden und Moorheiden", "Wald-Strauch-Uebergangsstadien"]
    if "wiese" in mushroom.attr['habitat'].lower() and tree_type in wiesen:
        wood_type_factor = 1.0

    # In the future, this could also consider specific trees
    return wood_type_factor * com_fac


def read_mushroom_XML(url):
    mushrooms = {}
    root = ET.parse(url).getroot()
    for type_tag in root.findall('mushroom'):
        shroom = {};
        for child in type_tag:
            if child.tag == "woodtype":
                shroom[child.tag] = (int("Hardwood" in child.text), int("Softwood" in child.text))
            elif child.tag == "trees":
                shroom[child.tag] = child.text.lower().split(",")
            else:
                shroom[child.tag] = child.text
        mushrooms[shroom["name"]] = Mushroom(shroom)
    return mushrooms


def temp_deviation(temp, opt_val):
    if temp < opt_val:
        return temp / opt_val
    elif temp > opt_val + 5:
        return opt_val / temp
    else:
        return 1.0


def environment_factor(rain, temperature, humidity):
    # The factorization of the values can be tweeked, it's just a gross estimation
    # First look at 28 days ago to 14 days ago
    ra = 0
    temp = 0
    hum = 0
    optimal_temp = 21
    for j in range(0, 14):
        # If 10mm is perfect amount, this measures the normalized contribution
        ra += 0.5 * min(rain[j], 25) / 14
        temp += 0.3 * temp_deviation(temperature[j], optimal_temp) / 14
        if humidity[j] is None:
            humidity[j] = 60
        hum += humidity[j] / 90 / 14
    # Emphasize 2-1 week ago
    for j in range(14, 21):
        ra += 3 * min(rain[j], 25) / 7
        temp += 0.75 * temp_deviation(temperature[j], optimal_temp) / 7
        if humidity[j] is None:
            humidity[j] = 60
        hum += humidity[j] / 90 / 7
    for j in range(21, 28):
        ra += 0.75 * min(rain[j], 25) / 7
        temp += 2 * temp_deviation(temperature[j], optimal_temp) / 7
        if humidity[j] is None:
            humidity[j] = 60
        hum += humidity[j] / 90 / 7
    norm_rain = 0.3 * (0.5 * 14 + 3 * 7 + 7 * 0.75)
    norm_temp = 3
    norm_hum = 1.0
    return min(ra / norm_rain, 3), min(temp / norm_temp, 3), hum / norm_hum


def sanity_test():
    # Deprecated, currently unused
    with open('rain.txt.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        rowcounter = 0
        val = []
        val2 = []
        ns = 0
        c = 0
        for row in spamreader:
            if c == 0:
                c += 1
                continue
            ns += float(row[3])
            rowcounter += 1
            c += 1
            if (rowcounter % 24) == 0:
                val.append((str(row[1])[0: len(str(row[1])) - 2], ns))
                val2.append(ns)
                rowcounter = 0
                ns = 0
        hum_res = []
        # for i in range(40, len(val2)):
        # hum_res.append(humidity_value(val2[i - 30:i], 0))
        curMonth = '10'
        res = []
        i = 0
        while i < len(val):
            con = 0
            while i < len(val) and val[i][0][4:6] == curMonth:
                con += float(val[i][1])
                i += 1
            if i >= len(val):
                break
            res.append((val[i][0][0:4] + '_' + curMonth, con))
            curMonth = val[i][0][4:6]
        yo = 0
        plt.plot(hum_res)
        plt.show()
        cnt = 0
        for i in range(len(hum_res)):
            if (hum_res[i] > 1):
                print(val[i][0])
                cnt += 1
        print(str(cnt) + " of " + str(len(hum_res)))

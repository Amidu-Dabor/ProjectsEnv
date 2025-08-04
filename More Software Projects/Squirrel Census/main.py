# with open("weather-data.csv", mode="r") as csv_file:
#     data = csv_file.readlines()
#     print(data)
import pandas
# import csv
#
# with open("weather-data.csv") as csv_file:
#     data = csv.reader(csv_file)
#     temperatures = []
#     for row in data:
#         tem_value = row[1]
#         if tem_value != "temp":
#             temperatures.append(int(tem_value))
#     print(temperatures)

import pandas as pd

# data = pd.read_csv("weather-data.csv")
# temp_list = data["temp"].to_list()
# average_temp = sum(temp_list) / len(temp_list)

# print(average_temp)
# print(data["temp"].mean())
# print(data.temp.max())
# print(data[data.day == "Thursday"])
# print(data[data.temp == data.temp.max()])
# monday = data[data.day == "Monday"]
# print(monday.temp)
#
# monday_F = (monday.temp * 9 / 5) + 32
# print(monday_F)

# data_dic = {
#     "students": ["Amy", "James", "Angela"],
#     "scores": [76, 56, 65],
#     "Program": ["Java", "Database", "CISCO"]
# }
#
# info = pandas.DataFrame(data_dic)
# info.to_csv("new_csv.csv")

# # print(info)
# print(info[info.students == "Angela"].scores)

data = pd.read_csv("228 2018-Central-Park-Squirrel-Census-Squirrel-Data.csv")
grey_squirrels_count = len(data[data["Primary Fur Color"] == "Gray"])
red_squirrels_count = len(data[data["Primary Fur Color"] == "Cinnamon"])
black_squirrels_count = len(data[data["Primary Fur Color"] == "Black"])

data_dic = {
    "Fur Colour": ["Gray", "Cinnamon", "Black"],
    "count": [grey_squirrels_count, red_squirrels_count, black_squirrels_count]
}

df = pd.DataFrame(data_dic)
df.to_csv("squirrel_count.csv")


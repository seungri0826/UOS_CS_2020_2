# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import requests
import json
import re
from json import loads
import datetime
import time
import pickle
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV
from sklearn import linear_model as lm
import xgboost as xgb
from scipy.stats import uniform, randint
import os

warnings.filterwarnings('ignore')
mpl.rcParams['axes.unicode_minus'] = False
plt.rcParams["font.family"] = 'NanumGothic'

app = Flask(__name__)


# 1. 동대문구 내 따릉이 대여소 ID 불러오기
with open('./bike_stop_data/Bike_Stop_ID.pickle', 'rb') as fr:
    Bike_Stop_ID = pickle.load(fr)

# 2. 다음 날의 유입 정도 예측
#### 2-1. XGBoost 모델 불러오기 (Model_Inflow, Model_Outflow)
dayofweek = ["요일_"+str(i) for i in range(7)]
features = ['월', '시간', '최저기온(°C)', '최고기온(°C)', '일강수량(mm)', '최대 풍속(m/s)', '평균 상대습도(%)'] + dayofweek
cols = ['월', '요일', '시간', '최저기온(°C)', '최고기온(°C)', '일강수량(mm)', '최대 풍속(m/s)', '평균 상대습도(%)']

dirs_in = os.getcwd() + '/model/Inflow'
files_in = os.listdir(dirs_in)
Model_Inflow = {}
in_pkl_path = "./model/Inflow/inflow_"
for id_stop in Bike_Stop_ID:
    Model_Inflow[str(id_stop)] = pickle.load(open(in_pkl_path+str(id_stop)+".pkl", "rb"))

dirs_out = os.getcwd() + '/model/Outflow'
files_out = os.listdir(dirs_out)
Model_Outflow = {}
out_pkl_path = "./model/Outflow/outflow_"
for id_stop in Bike_Stop_ID:
    Model_Outflow[str(id_stop)] = pickle.load(open(out_pkl_path+str(id_stop)+".pkl", "rb"))

#### 2-2. 일기예보 API 이용하여 input parameter 얻어오기
vilage_weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"
service_key = "33CwubzPkYtsaIF%2FC%2FcXBRHrNKfD2GczNC79ddAsLSmi7S7ZVvdt7A%2FzQWJQgbiSD5gu85leQwxOOgRjV%2BAgaA%3D%3D"
today = datetime.datetime.today()
if (100 * int(today.hour) + int(today.minute)) < 530:
    today = today - datetime.timedelta(1)
base_date = today.strftime("%Y%m%d") 
base_time = "0500" # 전날의 05시 이후에 동작해야 함

nx = "61"
ny = "127" # 동대문구의 좌표

# 1차 (데이터가 길어서 짤림)
payload1 = "serviceKey=" + service_key + "&" +\
    "numOfRows=50&" +\
    "pageNo=2&" +\
    "dataType=json" + "&" +\
    "base_date=" + base_date + "&" +\
    "base_time=" + base_time + "&" +\
    "nx=" + nx + "&" +\
    "ny=" + ny

# 값 요청
res1 = requests.get(vilage_weather_url + payload1)
data1 = res1.json()
fcst1 = pd.DataFrame(data1['response']['body']['items']['item'])

# 2차 (데이터가 길어서 짤림)
payload2 = "serviceKey=" + service_key + "&" +\
    "numOfRows=50&" +\
    "pageNo=3&" +\
    "dataType=json" + "&" +\
    "base_date=" + base_date + "&" +\
    "base_time=" + base_time + "&" +\
    "nx=" + nx + "&" +\
    "ny=" + ny

# 값 요청
res2 = requests.get(vilage_weather_url + payload2)
data2 = res2.json()
fcst2 = pd.DataFrame(data2['response']['body']['items']['item'])

# 1차, 2차 합치기
idx = list(range(32, 50))
fcst2 = fcst2.drop(idx)
fcst = pd.concat([fcst1, fcst2]).reset_index(drop=True).copy()
fcst = fcst.astype({'fcstValue': np.float})

# 최저기온 (0600에만 예보됨)
min_temp_tomorrow = float(fcst[fcst['category'] == 'TMN']['fcstValue'])

# 최고기온 (1500에만 예보됨)
max_temp_tomorrow = float(fcst[fcst['category'] == 'TMX']['fcstValue'])

# 일 강수량 (0000, 0600, 1200, 1800의 값들 모두 더하기)
r06 = fcst[fcst['category'] == 'R06']
rain_fall_tomorrow = float(r06['fcstValue'].sum())

# 풍속 (최댓값 구하기)
wsd = fcst[fcst['category'] == 'WSD']
wind_speed_tomorrow = float(wsd['fcstValue'].max())

# 습도 (평균 구하기)
reh = fcst[fcst['category'] == 'REH']
humidity_tomorrow = float(reh['fcstValue'].mean())

tomorrow = today + datetime.timedelta(1)
# 월
mon_tomorrow = tomorrow.month
# 요일
day_tomorrow = tomorrow.weekday()


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', mon_tomorrow=mon_tomorrow, day_tomorrow=day_tomorrow, min_temp_tomorrow=min_temp_tomorrow, 
        max_temp_tomorrow=max_temp_tomorrow, rain_fall_tomorrow=rain_fall_tomorrow, wind_speed_tomorrow=wind_speed_tomorrow, humidity_tomorrow=humidity_tomorrow, tomorrow = tomorrow.strftime("%Y-%m-%d-%A"))

    if request.method == 'POST':
        # input parameter
        mon = int(request.form['mon'])
        day = int(request.form['day'])
        min_temp = float(request.form['min_temp'])
        max_temp = float(request.form['max_temp'])
        rain_fall = float(request.form['rain_fall'])
        wind_speed = float(request.form['wind_speed'])
        humidity = float(request.form['humidity'])

        #### 2-3. parameter list로 만들기 (input_params)
        # 요일
        weekday = [0, 0, 0, 0, 0, 0, 0]
        weekday[day] = 1
        # 시간
        time_slot = list(range(5, 22))

        param = [mon, 0, min_temp, max_temp, rain_fall, wind_speed, humidity] + weekday
        params = []
        for i in time_slot:
            tmpp = param.copy()
            tmpp[1] = i
            params.append(tmpp)
        params = np.array(params)
        input_params = pd.DataFrame(params, columns = features)

        #### 2-4. Result_All 만들기
        alpha = 0.85
        Result_All = {}
        for stop_id in Bike_Stop_ID:
            Result_All[str(stop_id)] = {}
            for time in time_slot:
                inflow = Model_Inflow[str(stop_id)].predict(input_params)
                outflow = Model_Outflow[str(stop_id)].predict(input_params)
                delta = alpha * (inflow - outflow) + (1 - alpha) * inflow
                Result_All[str(stop_id)]['대여소ID'] = stop_id
                Result_All[str(stop_id)]['Time Slot'] = time_slot
                Result_All[str(stop_id)]['Inflow'] = inflow
                Result_All[str(stop_id)]['Outflow'] = outflow
                Result_All[str(stop_id)]['Delta'] = delta

        Result = pd.DataFrame(Result_All['600'])
        for id_stop in Bike_Stop_ID:
            if id_stop == 600:
                continue
            tmppp = pd.DataFrame(Result_All[str(id_stop)])
            Result = pd.concat([Result, tmppp])
            
        Result = Result.reset_index(drop = True)

        #### 2-5. heatmap 만들기
        Bike_Map = Result.pivot('대여소ID', 'Time Slot', 'Delta')
        plt.figure(figsize=(20,20))
        hm = sns.heatmap(Bike_Map, annot=True, fmt=".6f")
        plt.title('다음 날의 동대문구 내 따릉이 대여소의 시간대별 유입 정도', fontsize=20)
        fig = hm.get_figure()
        filename = 'img/heatmap/heatmap_' + str(int(datetime.datetime.now().timestamp())) + '.png'
        fig.savefig('./static/' + filename)


        # 3. 경로 추천
        #### 3-1. 이용량 TOP 13 대여소
        top_13 = []
        for stop_id in Bike_Stop_ID:
            sum = 0
            for delta in Result_All[str(stop_id)]['Delta']:
                sum += delta
            top_13.append((str(stop_id),str(sum)))
            
        top_13_sorted = sorted(top_13, key=lambda tup: float(tup[1]), reverse = True)
        top_13_sorted = top_13_sorted[0:13]

        #### 3-2. 대여소별 다녀간 횟수 저장
        visit_count = {}
        for stop_id in Bike_Stop_ID:
            visit_count[str(stop_id)] = 0

        #### 3-3. 각 대여소마다 유입정도 큰 순서로 (time slot: 05~20)
        desired_order = {}
        for stop_id in Bike_Stop_ID:
            desired_order[str(stop_id)] = []
            # 해당 대여소에서 delta가 큰 순서로 (시간, delta) 저장
            delta = Result_All[str(stop_id)]['Delta'].copy()
            
            delta_t = []
            for d, t in zip(delta, range(5, 22)):
                delta_t.append((str(t), d))
            delta_t = delta_t[0:16]
            
            delta_t_sorted = sorted(delta_t, key=lambda tup: float(tup[1]), reverse = True)
            desired_order[str(stop_id)] = delta_t_sorted

        #### 3-4. 시간대별 그 시간대가 제일 유입정도가 큰 대여소ID
        largest_stop = {}
        temp = []
        for stop_id in Bike_Stop_ID:
            temp.append(tuple(list([str(stop_id)]) + list(desired_order[str(stop_id)][0])))
        #temp
        for t in range(5, 21):
            largest_stop[str(t)] = []
            for tup in temp:
                if t == int(tup[1]):
                    largest_stop[str(t)].append((tup[0], tup[2]))
            largest_stop[str(t)] = sorted(largest_stop[str(t)], key=lambda tup: float(tup[1]), reverse = True)

        #### 3-5. 시간대별 대어소 배정 (w/ 대여소별 방문 횟수 카운팅) (team_A, team_B)
        ###### (1) 전 시간대에 제일 유입이 활발했던 대여소들 (최대 4개)
        ###### (2) 제일 유입이 활발했던 대여소의 개수가 4개가 넘는 시간대의 경우, 그 다음 시간대로 가득 채워가며 넘김
        ###### (3) 대여소별 방문 횟수가 0인 대여소 + TOP 13 대여소는 남는 시간대에 무작위로 방문
        visit_order = {}
        remainder = []
        for t in range(6, 22):
            visit_order[str(t)] = []
            if len(largest_stop[str(t-1)]) <= 4:
                for idx, val in largest_stop[str(t-1)]:
                    visit_order[str(t)].append(idx)
                    visit_count[idx] += 1
            else: # if len(largest_stop[str(t-1)]) > 4:
                i = 0
                for idx, val in largest_stop[str(t-1)]:
                    if i == 4:
                        break
                    visit_order[str(t)].append(idx)
                    visit_count[idx] += 1
                    i += 1
                remainder += largest_stop[str(t-1)][4:]
            
            remainder = sorted(remainder, key=lambda tup: tup[1], reverse = True)
            
            if len(visit_order[str(t)]) < 4 and len(remainder) != 0 :
                i = 0
                for i in range(4-len(visit_order[str(t)])):
                    if len(remainder) == 0:
                        break
                    idx = int(remainder.pop(0)[0])
                    visit_order[str(t)].append(str(idx))
                    visit_count[str(idx)] += 1
            
        remainder += top_13_sorted

        # visit_order[id] len가 4보다 작은 경우, remainder에서 하나씩 빼서 넣어줌 & visit_count[id]++
        for t in range(6, 22):
            if len(visit_order[str(t)]) >= 4:
                continue
            # if len(visit_order[str(t)])< 4:
            i = 0
            for i in range(4-len(visit_order[str(t)])):
                if len(remainder) == 0:
                    break
                idx = int(remainder.pop(0)[0])
                visit_order[str(t)].append(str(idx))
                visit_count[str(idx)] += 1

        # team_A와 team_B에게 배분
        team_A = {}
        team_B = {}

        for t in range(6, 22):
            team_A[str(t)] = []
            team_B[str(t)] = []
            team_A[str(t)].append(visit_order[str(t)][0])
            team_A[str(t)].append(visit_order[str(t)][2])
            team_B[str(t)].append(visit_order[str(t)][1])
            team_B[str(t)].append(visit_order[str(t)][3])


        # 4. 효용성 검증
        #### 4-1. 대여소별 거치대수 불러오기
        with open('./bike_stop_data/Bike_Stop_NUM.pickle', 'rb') as fr:
            bike_num = pickle.load(fr)

        #### 4-2. 예상 유효 소독 대수를 구함 (disinfected_day)
        disinfected = {}
        for stop_id, i in zip(Bike_Stop_ID, range(51)):
            t = 0
            for t in range(6, 22):
                if str(stop_id) in visit_order[str(t)]:
                    break
            disinfected_sum = float(bike_num[i][1])
            for l in range(t-5):
                disinfected_sum = disinfected_sum + Result_All[str(stop_id)]['Inflow'][l] - Result_All[str(stop_id)]['Outflow'][l]
            disinfected[str(stop_id)] = disinfected_sum

        disinfected_day = 0
        for stop_id in Bike_Stop_ID:
            if disinfected[str(stop_id)] > 0:
                disinfected_day += disinfected[str(stop_id)]
        disinfected_day = round(disinfected_day, 2)

        # heatmap, team_A, team_B, disinfected_day 넘기기
        return render_template('index.html', heatmap_path = filename, team_A = team_A, team_B = team_B, disinfected_day = disinfected_day, 
        mon_tomorrow=mon_tomorrow, day_tomorrow=day_tomorrow, min_temp_tomorrow=min_temp_tomorrow, 
        max_temp_tomorrow=max_temp_tomorrow, rain_fall_tomorrow=rain_fall_tomorrow, wind_speed_tomorrow=wind_speed_tomorrow, humidity_tomorrow=humidity_tomorrow, tomorrow = tomorrow.strftime("%Y-%m-%d-%A"))

if __name__ == '__main__':
    app.run(debug=True)
import requests
import json
import re
import pandas as pd

class Data: 
    """
    This module retrieves statistics of cases of the 2019 Novel Coronavirus. 
    Data Source: https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5
    
    ...

    Attributes
    ----------
    statistics : dict
        The raw data retrieved from the server.
    china : 
        Nation-level data of China. 
    province : pandas.DataFrame
        province-level data of China. 
    city : pandas.DataFrame
        city-level data of China
    international : pandas.DataFrame
        Data of foreign countries. 
    update_time : str
        Time of the last update. 
    

    """
    
    
    def __init__(self): 
        self.statistics = self._request_data()
        self.china = self._china_data()
        self.province = self._province_data()
        self.city = self._city_data()
        self.international = self._country_data()
        self.update_time = self._update_time_data()
        
        
    def _request_data(self): 
        data_request = requests.get('https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5')
        data_process = re.sub("^\\d+\\(", "", data_request.text)
        data_process = re.sub("\\)$", "", data_process)
        data_process_json = json.loads(data_process)
        data_json = json.loads(data_process_json['data'])
        return data_json
    
    
    def _province_data(self): 
        province_dict = {}
        for province in self.statistics['areaTree'][0]['children']: 
            province_dict[province['name']] = province
        
        # Make a list of multi-index
        province_key_list = []
        for province in province_dict.keys(): 
            for dimension in ['新增', '累计']: 
                province_key_list.append((province, dimension))
        index = pd.MultiIndex.from_tuples(province_key_list, names=['省/直辖市/自治区', '累计/新增'])
                
        # Make a array of data
        array_list = []
        for province in province_dict.keys(): 
            for dimension in ['today', 'total']: 
                array_list.append(pd.Series(data=province_dict[province][dimension]))
        
        # Put data in a DataFrame
        df = pd.DataFrame(data=array_list, index=index)
        df.rename(columns={'confirm': '确诊', 
                   'suspect': '疑似', 
                   'dead': '死亡', 
                   'heal': '治愈', 
                   'isUpdated': '数据已更新'}, 
          inplace=True)
        return df
    
    
    def _city_data(self):
        province_dict = {}
        for province in self.statistics['areaTree'][0]['children']: 
            province_dict[province['name']] = province
        
        # Make a list of multi-index
        county_key_list = []
        for province in province_dict.keys(): 
            for county in province_dict[province]['children']: 
                for dimension in ['新增', '累计']: 
                    county_key_list.append((province, county['name'], dimension))
        index = pd.MultiIndex.from_tuples(county_key_list, names=['省/直辖市/自治区', '行政区', '累计/新增'])
        
        # Make a array of data
        array_list = []
        for province in province_dict.keys(): 
            for county in province_dict[province]['children']: 
                for dimension in ['today', 'total']: 
                    array_list.append(pd.Series(data=county[dimension]))
        
        # Put data in a DataFrame
        df = pd.DataFrame(data=array_list, index=index)
        df.rename(columns={'confirm': '确诊', 
                   'suspect': '疑似', 
                   'dead': '死亡', 
                   'heal': '治愈', 
                   'isUpdated': '数据已更新'}, 
          inplace=True)
        return df
        
    def _country_data(self): 
        country_dict = {}
        for country in self.statistics['areaTree'][1:]: 
            country_dict[country['name']] = country

        country_key_list = []
        for country in country_dict.keys(): 
            for dimension in ['新增', '累计']: 
                country_key_list.append((country, dimension))
        index = pd.MultiIndex.from_tuples(country_key_list, names=['国家', '累计/新增'])

        array_list = []
        for country in country_dict.keys(): 
            for dimension in ['today', 'total']: 
                array_list.append(pd.Series(data=country_dict[country][dimension]))

        df = pd.DataFrame(data=array_list, index=index)
        df.rename(columns={'confirm': '确诊', 
                           'suspect': '疑似', 
                           'dead': '死亡', 
                           'heal': '治愈', 
                           'isUpdated': '数据已更新'}, 
                  inplace=True)
        return df
    
    
    def _china_data(self):
        china_total = pd.Series(self.statistics['chinaTotal'])
        china_add = pd.Series(self.statistics['chinaAdd'])
        df = pd.DataFrame([china_total, china_add], index=['累计', '新增'])
        df.rename(columns={'confirm': '确诊', 
                   'suspect': '疑似', 
                   'dead': '死亡', 
                   'heal': '治愈', 
                   'isUpdated': '数据已更新'}, 
                  inplace=True)
        return df
    
    
    def _update_time_data(self): 
        return self.statistics['lastUpdateTime']
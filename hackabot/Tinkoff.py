#!/usr/bin/env python
# coding: utf-8

# In[160]:


import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering

# matplotlib.style.use('ggplot')
# get_ipython().run_line_magic('matplotlib', 'inline')
#
#
# # # Соц.положение
# data_socdem = pd.read_csv('avk_hackathon_data_party_x_socdem.csv')
#
# # # Данные о изменеии баланса
#
# data_balance = pd.read_csv('avk_hackathon_data_account_x_balance.csv')
# data_balance = data_balance.dropna()
#
#
# # # Продукты
#
# data_products = pd.read_csv('avk_hackathon_data_party_products.csv')
#
# # # Логи
#
# data_logs = pd.read_csv('avk_hackathon_data_story_logs.csv')
#
#
# # # Тексты
#
#
# data_texts = pd.read_csv('avk_hackathon_data_story_texts.csv')
#
#
# # # Транзакции
#
# data_transactions = pd.read_csv('avk_hackathon_data_transactions.csv')
#
#
# # # Мёрджим таблицы по айдишнику клиента
#
#
# data_socdem_products = pd.merge(data_socdem, data_products, on='party_rk')
#
#
# # Заменим семейный статус на бинарный
# #
# # Женат/замужем - 1
# #
# # Холост/не замужем - 0
# #
# # Вдовец, вдова - 2
# #
# # Гражданский брак - 3
# #
# # Не проживает с супругом (ой) - 4
# #
# # Разведен (а) - 5
# #
# # Nan - 6
# #
# # --------------------
# #
# # Аналогично с полом
# #
# # M - 1
# #
# # F - 0 (да, да женщины - ноль, я ужасен, избейте меня, фемки)
#
#
# data_socdem_products['marital_status_desc'].replace({"Женат/замужем": 1,
#                                                      "Холост/не замужем": 0,
#                                                      "Вдовец, вдова":2,
#                                                      "Гражданский брак":3,
#                                                      "Не проживает с супругом (ой)":4,
#                                                      "Разведен (а)":5},
#                                                     inplace=True)
#
#
# data_socdem_products['gender_cd'].replace({"M": 1, "F": 0}, inplace=True)
# data_socdem_products = data_socdem_products.fillna(6)
#
# income_data = data_balance[data_balance['balance_chng'] > 0].groupby('party_rk').mean()
# income_data.reset_index(level=0, inplace=True)
# income_data.rename(columns={'balance_chng': 'income'}, inplace=True)
# income_data = income_data[['party_rk', 'income']]
#
# outcome_data = data_balance[data_balance['balance_chng'] < 0].groupby('party_rk').mean()
# outcome_data.reset_index(level=0, inplace=True)
# outcome_data.rename(columns={'balance_chng': 'outcome'}, inplace=True)
# outcome_data = outcome_data[['party_rk', 'outcome']]
#
#
# data_socdem_products_balance = data_socdem_products.merge(income_data,
#                                                           how='left',
#                                                           left_on='party_rk',
#                                                           right_on='party_rk')
# data_socdem_products_balance = data_socdem_products_balance.merge(outcome_data,
#                                                           how='left',
#                                                           left_on='party_rk',
#                                                           right_on='party_rk')
# data_socdem_products_balance = data_socdem_products_balance.fillna(0)
#
#
# data = data_socdem_products_balance[data_socdem_products_balance.columns[1:]]
#
#
# model = KMeans(n_clusters=5)
# model.fit(data)
#
#
# data_socdem_products_balance['label'] = model.labels_
#
#
# import operator
# dict_lab_categoty = {}
# for j in list(set(model.labels_)):
#     id_cl = data_socdem_products_balance[data_socdem_products_balance['label'] == j]['party_rk'].to_list()
#     df_cl = data_transactions[data_transactions['party_rk'].isin(id_cl)][data_transactions['transaction_type_desc'].isin(['Оплата услуг', 'Платеж', 'Покупка'])]
#     dict_ = {category: len(df_cl[df_cl['category'] == category]) for category in list(set(df_cl['category']))[1:]}
#
#     sorted_x = sorted(dict_.items(), key=operator.itemgetter(1))
#
#     reverse_sorted_x = []
#     dict_ = {}
#     for i in range(len(sorted_x)):
#         reverse_sorted_x.append(sorted_x[len(sorted_x)-i-1])
#     for value in reverse_sorted_x:
#         dict_[value[0]] = value[1]
#
#     dict_lab_categoty[j] = dict_

import json
dict_lab_categoty = json.load( open( "top_cat_lbl.json" ) )
data_socdem_products_balance = pd.read_csv('data_socdem_products_balance.csv', index_col = 0)

def id_to_label(_id):
    return(data_socdem_products_balance[data_socdem_products_balance['party_rk'] == _id]['label'].values[0])


def label_to_average_income(lbl):
    mean = data_socdem_products_balance[data_socdem_products_balance['label'] == lbl]['income'].mean()
    return(mean)


def label_to_average_outcome(lbl):
    mean = data_socdem_products_balance[data_socdem_products_balance['label'] == lbl]['outcome'].mean()
    return(mean)


def label_to_top_category(lbl):
    return(list(dict_lab_categoty[str(lbl)]))



def all_information(_id):
    _lbl = id_to_label(_id)
    av_income = label_to_average_income(_lbl)
    av_outcome = label_to_average_outcome(_lbl)
    top_categ = label_to_top_category(_lbl)


    return[av_income, av_outcome, top_categ]




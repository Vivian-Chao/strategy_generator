#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/20 上午11:29
# @Author : CaoV
# @File : Bin.py
# @Software: PyCharm

'''
单变量分箱
'''


import toad
import pandas as pd
import math

# method: 分箱方法，支持’chi’ (卡方分箱), ‘dt’ (决策树分箱), ‘kmean’ , ‘quantile’ (等频分箱), ‘step’ (等步长分箱)
# min_samples: 每箱至少包含样本量，可以是数字或者占比
# n_bins: 箱数，若无法分出这么多箱数，则会分出最多的箱数
# empty_separate: 是否将空箱单独分开


def auto_bins(data, target, method, min_samples = None, n_bins = None, empty_separate = True):
    c = toad.transform.Combiner()
    if method == 'quantile' :
        c.fit(data , y = target, method = method, n_bins = n_bins,  empty_separate = empty_separate)
    else:
        c.fit(data, y = target, method = method, n_bins = n_bins, min_samples = min_samples, empty_separate = empty_separate)

    data_bin = c.transform(data, labels=True)

    return data_bin


#
# # 手动分箱
#
#
#
# rule = {'day_dif': [1.0, 5.0, 17.0]}
# #
# #
# #
# c.set_rules(rule)
# data_bin = c.transform(data, labels=True)
#
#
#
#
#
#
# print('fraud_score_d1:',c.export()['fraud_score_d1'])




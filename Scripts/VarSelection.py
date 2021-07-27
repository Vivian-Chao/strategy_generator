#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/20 下午2:39
# @Author : CaoV
# @File : VarSelection.py
# @Software: PyCharm

'''
略略略略略😛
'''

import time
import numpy as np
import pandas as pd
# pd.set_option('max_columns',50)

import toad


# wrapper for debug
def cost_time(func_name):
    def inner(*args, **kwargs):
        st = time.time()
        rs = func_name(*args, **kwargs)
        ed = time.time()
        print('>>> %s, Cost Time(ms):%.2f'%(func_name.__name__, (ed - st)*100))
        return rs
    return inner


def format_percent(x, r, trans_percent = False):
    if trans_percent == True:
        x_processed = round(x * 100, r)
        y = str(x_processed) + '%'
    else:
        y = round(x, r)
    return y


def check_type(data, x):
    '''
    check var type
    :param data: dataframe
    :param x: str, variable name
    :return: str, 'num' or 'cat'
    '''
    try:
        if data[x].dtype in [int,float,'float32','float64','double']:
            rs = 'num'
        elif data[x].dtype in [object,str, bool]:
            rs = 'cat'
        else:
            pass
    except Exception as e :
        raise ValueError('>>>check \'%s\' type'%x, e)
    return rs



def cal_woe_iv(data , x_bin , target):
    '''
    懒得写后面补
    :param data:
    :param x_bin:
    :param target:
    :return:
    '''
    df = data.loc[:,[x_bin, target]]
    total_badrate = df[df[target]==1].shape[0]/df.shape[0]
    grouped = df.groupby(x_bin)[target]
    result_df = grouped.agg([('good', lambda y: (y == 0).sum()),
                             ('bad', lambda y: (y == 1).sum()),
                             ('total', 'count')])
    result_df['bad'] = result_df['bad'].apply(lambda x: 1 if x==0 else x)
    result_df['good'] = result_df['good'].apply(lambda x: 1 if x==0 else x)
    result_df['good_pct'] = result_df['good'] / result_df['good'].sum()
    result_df['bad_pct'] = result_df['bad'] / result_df['bad'].sum()
    result_df['total_pct'] = result_df['total'] / result_df['total'].sum()
    result_df['bad_rate'] = result_df['bad'] / result_df['total']
    result_df['lift'] = result_df['bad_rate']/total_badrate
    result_df['woe'] = np.log(result_df['bad_pct'] / result_df['good_pct'])
    result_df['iv'] = (result_df['bad_pct'] - result_df['good_pct']) * result_df['woe']
    result_df.drop(['good_pct', 'bad_pct'], axis = 1, inplace = True)
    return (result_df, result_df['iv'].sum())


def cal_woe_iv_2(data , x_bin , target, good_sum, bad_sum, total_sum, total_badrate):
    grouped = data.groupby(x_bin)[target]
    result_df = grouped.agg([('good', lambda y: (y == 0).sum()),
                             ('bad', lambda y: (y == 1).sum()),
                             ('total', 'count')])
    result_df['good_pct'] = result_df['good'] / good_sum
    result_df['bad_pct'] = result_df['bad'] / bad_sum
    result_df['total_pct'] = result_df['total'] / total_sum
    result_df['bad_rate'] = result_df['bad'] / result_df['total']
    result_df['lift'] = result_df['bad_rate']/total_badrate
    result_df['woe'] = np.log(result_df['bad_pct'] / result_df['good_pct'])
    result_df['iv'] = (result_df['bad_pct'] - result_df['good_pct']) * result_df['woe']
    result_df.drop(['good_pct', 'bad_pct'], axis = 1, inplace = True)
    return result_df

# IV
@cost_time
def var_select_iv(data, target, result_loc):
    '''
    :param data: dataframe, data, only include variables and target
    :param target: str, column name , means binary target(0/1)
    :return: dataframe, IV
    '''
    print('>>> Start...')
    df_iv = toad.quality(dataframe = data, target = target,iv_only=True, cpu_cores = -1)
    df_iv['iv'] = df_iv['iv'].apply(lambda x : format_percent(x,3))
    df_iv_out = df_iv.loc[:,['iv','unique']]
    if df_iv_out[df_iv_out['iv'] >= 1].shape[0] > 0 :
        print('>>> Those variables IV are unusual high, please check data type:',list(df_iv_out[df_iv_out['iv'] >= 1].index))
        print('>>> ...')
    else:
        pass
    df_iv_out.to_csv(result_loc + 'Var_IV.csv')
    print('>>> Finish, IV result also has been saved as csv file at \'%s\''%(result_loc + 'Var_IV.csv'))
    return df_iv_out


# 0%-10% head/tail LIFT > threshold
def var_select_lift(data, x, target, threshold):
    '''
    懒得写，以后补
    :param data:
    :param x:
    :param threshold:
    :return:
    '''
    # *params setting*
    # interrupt head/tail percent
    intr_pct = 10
    min_limit = np.min([500,round(data.shape[0]/100)])
    bad_limit = 5

    bad_sum  = data[data[target]==1].shape[0]
    good_sum = data[data[target]==0].shape[0]
    total_sum = data.shape[0]
    total_badrate = bad_sum/total_sum

    sort_col = ['var_name', 'value', 'good', 'bad', 'total', 'total_pct', 'bad_rate', 'lift', 'woe','iv']
    df_res = pd.DataFrame(columns= sort_col)

    # null value calculate metric
    if data[x].isna().sum() > 0:
        df_null = data[data[x].isna()]
        bad_cnt = df_null[df_null[target]==1].shape[0]
        if df_null.shape[0] >= min_limit and bad_cnt >= bad_limit and df_null.shape[0] <= data.shape[0]/intr_pct:
            null_badrate = bad_cnt/df_null.shape[0]
            null_lift = null_badrate/total_badrate
            if null_lift >= threshold or null_lift <= 1/threshold:
                df_null['%s_null_bin'%x] = 'null'
                df_selected = cal_woe_iv_2(data = df_null
                                           , x_bin = '%s_null_bin'%x
                                           , target =target
                                           , good_sum = good_sum
                                           , bad_sum = bad_sum
                                           , total_sum = total_sum
                                           , total_badrate = total_badrate
                                           ).reset_index()
                df_selected.rename(columns = {'%s_null_bin'%x : 'value'}, inplace = True)
                df_selected['var_name'] = x
                df_selected = df_selected[sort_col]
                df_res = df_res.append(df_selected)
            else:
                pass
    else:
        pass

    # drop null value rows
    data_notna = data[~data[x].isna()].reset_index(drop = True)
    x_unique_list = data_notna[x].unique()
    x_unique_list.sort()

    # select intr_pct%(like 10%) head/tail value
    x_unique_list_head = x_unique_list[:round(len(x_unique_list)/intr_pct)]
    x_unique_list_tail = x_unique_list[-round(len(x_unique_list)/intr_pct):]

    var_dtype = check_type(data, x)
    if var_dtype == 'cat':
        # 1.calculate value badrate,woe,iv,lift, extract value where lift over threshold
        df_lift = cal_woe_iv(data = data_notna , x_bin = x, target = target)[0]
        df_selected = df_lift[((df_lift['lift'] >= threshold) | (df_lift['lift'] <= 1/threshold))  # lift
                              & (df_lift['total'] >= min_limit)  # 总样本量
                              & (df_lift['bad'] >= bad_limit)   # bad样本量
                              ].reset_index()
        df_selected.rename(columns = {x : 'value'}, inplace = True)
        df_selected['var_name'] = x
        df_selected = df_selected[sort_col]
        # 2.append result dataframe
        df_res = df_res.append(df_selected)


    sort_col = ['var_name', 'value', 'good', 'bad', 'total', 'total_pct', 'bad_rate', 'lift', 'woe','iv']
    df_num_res = pd.DataFrame(columns= sort_col)

    if var_dtype =='num':
        # head_lift_dict = {}
        for i,val in enumerate(x_unique_list_head):
            df_bin = data[data[x] <= val]
            bad_cnt = df_bin[df_bin[target]==1].shape[0]
            # 当前切点分箱样本数 >= min_limit & bad个数 >= bad_limit & 只遍历到前intr_pct%(10%)
            if df_bin.shape[0] >= min_limit and bad_cnt >= bad_limit and df_bin.shape[0] <= data.shape[0]/intr_pct:
                bin_badrate = bad_cnt/df_bin.shape[0]
                bin_lift = bin_badrate/total_badrate
                # bin_lift >= threshold 找出坏人群，bin_lift <= 1/threshold 找出好人群
                if bin_lift >= threshold or bin_lift <= 1/threshold:
                    # head_lift_dict[val] = bin_lift
                    df_bin['%s_bin'%x] = '<=%s'%val
                    df_selected = cal_woe_iv_2(data = df_bin
                                               , x_bin = '%s_bin'%x
                                               , target =target
                                               , good_sum = good_sum
                                               , bad_sum = bad_sum
                                               , total_sum = total_sum
                                               , total_badrate = total_badrate
                                               ).reset_index()
                    df_selected.rename(columns = {'%s_bin'%x : 'value'}, inplace = True)
                    df_selected['var_name'] = x
                    df_selected = df_selected[sort_col]
                    # 2.append result dataframe
                    df_num_res = df_num_res.append(df_selected)
                else:
                    pass
            else:
                continue

        # tail_lift_dict = {}
        for i,val in enumerate(x_unique_list_tail):
            df_bin = data[data[x] >= val]
            bad_cnt = df_bin[df_bin[target]==1].shape[0]
            if df_bin.shape[0] >= min_limit and bad_cnt >= bad_limit and df_bin.shape[0] <= data.shape[0]/intr_pct:
                bin_badrate = bad_cnt/df_bin.shape[0]
                bin_lift = bin_badrate/total_badrate
                # bin_lift >= threshold 找出坏人群，bin_lift <= 1/threshold 找出好人群
                if bin_lift >= threshold or bin_lift <= 1/threshold:
                    # tail_lift_dict[val] = bin_lift
                    df_bin['%s_bin'%x] = '>=%s'%val
                    df_selected = cal_woe_iv_2(data = df_bin
                                               , x_bin = '%s_bin'%x
                                               , target =target
                                               , good_sum = good_sum
                                               , bad_sum = bad_sum
                                               , total_sum = total_sum
                                               , total_badrate = total_badrate
                                               ).reset_index()
                    df_selected.rename(columns = {'%s_bin'%x : 'value'}, inplace = True)
                    df_selected['var_name'] = x
                    df_selected = df_selected[sort_col]
                    # 2.append result dataframe
                    df_num_res = df_num_res.append(df_selected)
                else:
                    pass

        df_num_res_good = df_num_res[df_num_res['lift'] < 1]
        df_res = df_res.append(df_num_res_good[df_num_res_good['lift'] == df_num_res_good['lift'].min()])
        df_num_res_bad = df_num_res[df_num_res['lift'] > 1]
        df_res = df_res.append(df_num_res_bad[df_num_res_bad['lift'] == df_num_res_bad['lift'].max()])

        # for d in [head_lift_dict, tail_lift_dict]:
        #     if np.mean(list(d.values())) < 1:
        #         k_good = min(d, key= lambda k : d[k])
        #     elif np.mean(list(d.values())) > 1:
        #         k_bad = max(d, key= lambda k : d[k])
        #     else:
        #         pass
    return df_res


# organize LIFT variable selection loop
@cost_time
def var_select_lift_final(data, target, threshold, result_loc):
    '''
    :param data:
    :param target:
    :param threshold:
    :param result_loc:
    :return:
    '''

    sort_col = ['var_name', 'value', 'good', 'bad', 'total', 'total_pct', 'bad_rate', 'lift', 'woe','iv']
    df_res_tot = pd.DataFrame(columns= sort_col)

    x_list = data.drop(target, axis = 1).columns
    print('>>> Start...')
    for x in x_list:
        print('Processing %s...'%x)
        df_res = var_select_lift(data, x, target, threshold)
        df_res_tot = df_res_tot.append(df_res)

    df_res_tot.to_csv(result_loc + 'Var_LIFT.csv', index= False)
    print('>>> Finish, LIFT result also has been saved as csv file at \'%s\''%(result_loc + 'Var_LIFT'))

    return df_res_tot






#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/21 下午5:52
# @Author : CaoV
# @File : VarStatis.py
# @Software: PyCharm

import pandas as pd
import numpy as np


def cal_val_apply(data_bin, x, if_pas):
    grouped = data_bin.groupby(x)[if_pas]
    result_df = grouped.agg([('apply_cnt', 'count'),
                             ('accept_cnt', lambda y: (y == 1).sum()),
                             ])
    apply_sum = result_df['apply_cnt'].sum()
    accept_sum = result_df['accept_cnt'].sum()

    result_df.loc['总计',:] = result_df.sum(axis= 0)
    result_df['apply_pct'] = result_df['apply_cnt']/apply_sum
    result_df['accept_pct'] = result_df['accept_cnt']/accept_sum
    result_df['accept%'] = result_df['accept_cnt']/result_df['apply_cnt']
    return result_df


def cal_val_target(data_bin, x, target, prefix):
    grouped = data_bin.groupby(x)[target]
    result_df = grouped.agg([('%s_total'%prefix, 'count'),
                             ('%s_bad'%prefix, lambda y: (y == 1).sum()),
                             ])
    total_sum = result_df['%s_total'%prefix].sum()
    bad_sum = result_df['%s_bad'%prefix].sum()
    total_bad_rate = bad_sum/total_sum

    result_df.loc['总计',:] = result_df.sum(axis= 0)
    # result_df['total%'] = result_df['%s_total'%prefix]/total_sum
    # result_df['bad%'] = result_df['%s_bad'%prefix]/bad_sum
    result_df['%s_bad%%'%prefix] = result_df['%s_bad'%prefix]/result_df['%s_total'%prefix]
    result_df['%s_lift'%prefix] = result_df['%s_bad%%'%prefix]/total_bad_rate
    return result_df

def cal_val_target_amt(data_bin, x, prefix, rep_amt,ovd_amt):
    result_df = data_bin.groupby([x])[[rep_amt,ovd_amt]].sum()
    result_df.columns = ['%s_rep_amt'%prefix, '%s_ovd_amt'%prefix]
    rep_sum = result_df['%s_rep_amt'%prefix].sum()
    ovd_sum = result_df['%s_ovd_amt'%prefix].sum()
    total_bad_rate = ovd_sum/rep_sum
    result_df.loc['总计',:] = result_df.sum(axis= 0)
    result_df['%s_amt_bad%%'%prefix] = result_df['%s_ovd_amt'%prefix]/result_df['%s_rep_amt'%prefix]
    result_df['%s_amt_lift'%prefix] = result_df['%s_amt_bad%%'%prefix]/total_bad_rate
    return result_df



def combine_risk_metrics_table(data_bin, if_pas, x, params_list):
    '''
    :param data_bin: dataframe,全量分箱好的样本，包含交易未交易
    :param if_pas: str, 判断是否交易的字段名
    :param x: str,
    :param params_list: list,
        eg:[{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
            ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
            ]
    :return: dataframe
    '''

    df_apply = cal_val_apply(data_bin = data_bin, x = x, if_pas = if_pas)

    for i, params_dict in enumerate(params_list):
        # 去灰，如果不去灰，后面cal_val_....函数会报错
        data_model_bin = data_bin[(data_bin[params_dict['if_mob']] == 1) & (data_bin[params_dict['target']].isin([0,1]))]

        df_target = cal_val_target(data_bin = data_model_bin
                                   , x = x
                                   , target = params_dict['target']
                                   , prefix = params_dict['prefix']
                                   )
        df_target_amt = cal_val_target_amt(data_bin = data_model_bin
                                           , x = x
                                           , rep_amt = params_dict['rep_amt']
                                           , ovd_amt = params_dict['ovd_amt']
                                           , prefix = params_dict['prefix']
                                           )
        if i == 0 :
            df_target_res = pd.concat([df_target, df_target_amt],axis= 1)
        else:
            df_target_res = pd.concat([df_target_res, df_target, df_target_amt],axis= 1)

    df_res = pd.concat([df_apply, df_target_res], axis = 1)
    return df_res


def combine_stable_metrics_table(data_bin,  tim, x, target, freq):
    '''
    计算变量时间维度稳定指标
    :param data_bin:
    :param tim:
    :param x:
    :param target:
    :param freq: str, 'M' month or 'Q' quarter
    :return:
    '''

    data = data_bin.loc[:, [x, tim, target]]

    # check param 'freq'
    try:
        if freq =='M':
            data['by_tim'] = data[tim].str[2:7]
        elif freq == 'Q':
            data[tim] =pd.to_datetime(data[tim])
            data['by_tim'] = data[tim].apply(lambda x: str(x.year)[2:] +'-Q' + str(x.quarter))
        else:
            pass
    except Exception as e:
        ValueError('>>>check param \'freq\', use \'M\' or \'Q\' instead ',e)

    # groupby,  x col & tim(freq) col
    result_df_tot = pd.pivot_table(data, index= x, columns= 'by_tim', values= target, aggfunc = 'count').fillna(0)
    result_df_bad = pd.pivot_table(data, index= x, columns= 'by_tim', values= target, aggfunc = np.sum).fillna(0)

    # cal badrate
    result_df_bad.columns = ['%s_Bad'%col for col in result_df_tot.columns]
    result_df = pd.concat([result_df_bad, result_df_tot], axis = 1)
    result_df.loc['总计',:] = result_df.sum(axis= 0)
    # rename badrate col
    for col in result_df_tot.columns:
        result_df['%s_Bad%%'%col] = result_df['%s_Bad'%col]/(result_df[col])
    # PSI
    result_df_psi = result_df_tot
    for i,col in enumerate(result_df_tot.columns):
        # 把count = 0换成 1 ，避免计算psi时候分母为0的情况
        result_df_psi = result_df_psi.replace(0, 1)
        result_df_psi[col + '_pct'] = result_df_psi[col]/result_df_psi[col].sum()
        if col == result_df_psi.columns[0]:
            pass
        else:
            base_col = col + '_pct'
            comp_col = result_df_psi.columns[i-1] + '_pct'
            result_df_psi[col + '_psi'] = (result_df_psi[base_col] - result_df_psi[comp_col]) * np.log(result_df_psi[base_col] / (result_df_psi[comp_col]))

    result_df_psi.loc['总计',:] = result_df_psi.sum(axis= 0)
    # concat groupby table, badrate, psi
    keep_col = [col for col in result_df_psi.columns if 'psi' in col]
    result_df = pd.concat([result_df, result_df_psi.loc[:,keep_col]], axis =1).fillna(0)

    return result_df
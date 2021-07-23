#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/22 下午3:26
# @Author : CaoV
# @File : VisualReport.py
# @Software: PyCharm


import numpy as np
import xlsxwriter
from .VarStatis import combine_risk_metrics_table, combine_stable_metrics_table

#
# def var_metrics_visual(data_bin, if_pas, x_list, params_list, result_loc):
#     '''
#     save report at result_loc + 'var_report.xlsx', nothing return.
#     :param data_bin: dataframe
#     :param if_pas: str
#     :param x_list: list
#     :param params_list: str
#             eg:[{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
#             ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
#             ]
#     :param result_loc:
#     :return:
#     '''
#
#     workbook = xlsxwriter.Workbook(result_loc + 'var_report.xlsx')
#     # format 报告好看的关键！
#     # title format
#     title_formater = workbook.add_format({
#         'bold':True,
#         'align':'center',
#         'valign':'center',
#         'font_name': 'Arial',
#         'fg_color': '#5A81B8',
#         'font_color':'#F8F8FF',
#         'font_size': 14})
#
#     # header format
#     header_formater = workbook.add_format({
#         'bold': True,
#         'align':'center',
#         'valign':'center',
#         # 'text_wrap': True,  # 是否换行
#         'font_name': 'Arial',
#         'fg_color': '#5A81B8',
#         'font_color':'#F8F8FF',
#         'border': 1})
#     # main_format
#     main_formater = workbook.add_format({
#         # 'valign': 'top',
#         'font_name': 'Arial',
#         # 'border':1
#         'num_format':'0'
#     })
#     num_pct_formater =workbook.add_format({
#         'font_name': 'Arial',
#         'num_format':'0.0%'
#     })
#     num_float_formater =workbook.add_format({
#         'font_name': 'Arial',
#         'num_format':'0.00'
#     })
#
#
#     ws1 = workbook.add_worksheet('VariableMetrics')
#     ws1.hide_gridlines(option=2)  # 隐藏网格线
#     ws1.set_column(first_col = 0, last_col = 1, width=18)  # cell width
#     ws1.set_column(first_col = 1, last_col = 100, width=12)  # cell width
#
#     pen_row = 1  # 行指针
#
#     for x in x_list:
#         # 单变量各指标的表
#         df_metric_tmp = combine_metrics_table(data_bin = data_bin, if_pas = if_pas, x = x, params_list = params_list)
#
#         # write table title
#         ws1.write('A%d'%pen_row, x, title_formater)
#         # define table header
#         header_list = ['Bins'] + df_metric_tmp.columns.tolist()
#         column_settings = []
#         # format table
#         for header in header_list:
#             if header[-1] == '%' or header[-3:] == 'pct':
#                 d = {'header': header, 'header_format':main_formater, 'format': num_pct_formater}
#             elif header[-4:] == 'lift':
#                 d = {'header': header, 'header_format':main_formater, 'format': num_float_formater}
#             else:
#                 d = {'header': header, 'header_format':main_formater, 'format': main_formater}
#             column_settings.append(d)
#         # add table value
#         t_row, t_col  = df_metric_tmp.shape
#         res_array = np.c_[df_metric_tmp.index,df_metric_tmp.values,]
#         ws1.add_table(first_row = pen_row, first_col = 0, last_row = pen_row + t_row , last_col = t_col
#                       , options = {'data':res_array, 'columns': column_settings, 'style': 'Table Style Light 16'})  # style就是excel'套用表格格式'的排序序号！😐无语
#         pen_row = pen_row + t_row + 4 # 空两行
#
#     workbook.close()
#
#

# 重写

# format 报告好看的关键！
# title format
title_fmt = {
    'bold':True,
    'align':'center',
    'valign':'center',
    'font_name': 'Arial',
    'fg_color': '#5A81B8',
    'font_color':'#F8F8FF',
    'font_size': 14}
# header format
header_fmt = {
    'bold': True,
    'align':'center',
    'valign':'center',
    # 'text_wrap': True,  # 是否换行
    'font_name': 'Arial',
    'fg_color': '#5A81B8',
    'font_color':'#F8F8FF',
    'border': 1}
# main_format
main_fmt = {
    # 'valign': 'top',
    'font_name': 'Arial',
    # 'border':1
    'num_format':'0'
    }
num_pct_fmt ={
    'font_name': 'Arial',
    'num_format':'0.0%'
    }
num_float_fmt ={
    'font_name': 'Arial',
    'num_format':'0.00'
    }




class WriteDoc():
    def __init__(self, result_loc):
        self.result_loc = result_loc


    def open_workbook(self):
        workbook = xlsxwriter.Workbook(self.result_loc + 'Vars_Report.xlsx')

        global title_formater, header_formater, main_formater, num_pct_formater, num_float_formater
        title_formater =  workbook.add_format(title_fmt)
        header_formater =  workbook.add_format(header_fmt)
        main_formater =  workbook.add_format(main_fmt)
        num_pct_formater =  workbook.add_format(num_pct_fmt)
        num_float_formater =  workbook.add_format(num_float_fmt)
        return workbook

    def close_workbook(self,workbook):
        workbook.close()
        pass

    def open_worksheet(self, workbook):
        ws = workbook.add_worksheet('VariableMetrics')
        ws.hide_gridlines(option=2)  # 隐藏网格线
        ws.set_column(first_col = 0, last_col = 1, width=18)  # cell width
        ws.set_column(first_col = 1, last_col = 100, width=12)  # cell width
        return ws

    # def write_test(self,ws):
    #     ws.write('A1', 'Hello world')

    def var_risk_metrics_visual(self, ws, data_bin, if_pas, x_list, params_list):
        '''
        save report at result_loc + 'var_report.xlsx', nothing return.
        :param data_bin: dataframe
        :param if_pas: str
        :param x_list: list
        :param params_list: str
                eg:[{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
                ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
                ]
        :return:
        '''

        pen_row = 1  # 行指针
        for x in x_list:
            # 单变量各指标的表
            df_metric_tmp = combine_risk_metrics_table(data_bin = data_bin, if_pas = if_pas, x = x, params_list = params_list)

            # write table title
            ws.write('A%d'%pen_row, x, title_formater)
            # define table header
            header_list = ['Bins'] + df_metric_tmp.columns.tolist()
            column_settings = []
            # format table
            for header in header_list:
                if header[-1] == '%' or header[-3:] == 'pct':
                    d = {'header': header, 'header_format':main_formater, 'format': num_pct_formater}
                elif header[-4:] == 'lift':
                    d = {'header': header, 'header_format':main_formater, 'format': num_float_formater}
                else:
                    d = {'header': header, 'header_format':main_formater, 'format': main_formater}
                column_settings.append(d)
            # add table value
            t_row, t_col  = df_metric_tmp.shape
            res_array = np.c_[df_metric_tmp.index,df_metric_tmp.values,]
            ws.add_table(first_row = pen_row, first_col = 0, last_row = pen_row + t_row , last_col = t_col
                          , options = {'data':res_array, 'columns': column_settings, 'style': 'Table Style Light 16'})  # style就是excel'套用表格格式'的排序序号！😐无语
            pen_row = pen_row + t_row + 4 # 空两行


    def var_stable_metrics_visual(self, workbook, ws, data_bin,  x_list, params_list, if_mob, target, tim, freq):

        # 稳定性的表，只能指定一个y来计算
        data_model_bin = data_bin[(data_bin[if_mob] == 1) & (data_bin[target].isin([0,1]))]

        # 列指针
        if len(params_list) == 0 :
            pen_col = 0
        else:
            risk_metrics_table_width = 1 + 5 + len(params_list) * 8
            pen_col = risk_metrics_table_width + 1  # 空一列

        pen_row = 1  # 行指针
        for x in x_list:
            # 单变量各指标的表
            df_stable_tmp = combine_stable_metrics_table(data_bin = data_model_bin, tim = tim, x = x, target = target, freq = freq)
            # write table title
            ws.write(pen_row - 1, pen_col, x ,title_formater)
            # define table header
            header_list = ['Bins'] + df_stable_tmp.columns.tolist()
            column_settings = []
            # format table
            for header in header_list:
                if header[-1] == '%' or header[-3:] == 'pct':
                    d = {'header': header, 'header_format':main_formater, 'format': num_pct_formater}
                elif header[-3:] == 'psi':
                    d = {'header': header, 'header_format':main_formater, 'format': workbook.add_format({'font_name': 'Arial','num_format':'0.0000'})}
                else:
                    d = {'header': header, 'header_format':main_formater, 'format': main_formater}
                column_settings.append(d)
            # add table value
            t_row, t_col  = df_stable_tmp.shape
            res_array = np.c_[df_stable_tmp.index,df_stable_tmp.values,]
            ws.add_table(first_row = pen_row, first_col = pen_col, last_row = pen_row + t_row , last_col = pen_col + t_col
                         , options = {'data':res_array, 'columns': column_settings, 'style': 'Table Style Light 16'})  # style就是excel'套用表格格式'的排序序号！😐无语
            pen_row = pen_row + t_row + 4 # 空两行


if_pas = 'if_pas'
x_list  = ['cus_age',  'day_dif' ,'is_xin_mon']
params_list = [{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
    ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
               ]
tim = 'crt_tim'
if_mob = 'if_mob_d10'
target = 'flag_1_10'
freq ='Q'



def visual_var_report(result_loc, data_bin, if_pas, x_list, params_list,if_mob, target, tim, freq ,option = 'all'):

    doc = WriteDoc(result_loc = result_loc)
    workbook = doc.open_workbook()
    ws = doc.open_worksheet(workbook)
    if option == 'all':
        doc.var_risk_metrics_visual( ws = ws, data_bin = data_bin, if_pas = if_pas, x_list = x_list, params_list = params_list)
        doc.var_stable_metrics_visual(ws = ws, data_bin = data_bin,  x_list = x_list, params_list = params_list
                                      , if_mob = if_mob, target = target, tim = tim, freq = freq)
    elif option == 'risk':
        doc.var_risk_metrics_visual( ws = ws, data_bin = data_bin, if_pas = if_pas, x_list = x_list, params_list = params_list)
    elif option == 'stable':
        doc.var_stable_metrics_visual(workbook = workbook, ws = ws, data_bin = data_bin,  x_list = x_list, params_list = params_list
                                      , if_mob = if_mob, target = target, tim = tim, freq = freq)
    else:
        ValueError('>>>check param \'option\', use \'all\',\'risk\',\'stable\' instead')

    doc.close_workbook(workbook)









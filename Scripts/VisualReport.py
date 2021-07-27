#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/22 下午3:26
# @Author : CaoV
# @File : VisualReport.py
# @Software: PyCharm


import numpy as np
import xlsxwriter
from .VarStatis import combine_risk_metrics_table, combine_stable_metrics_table,cal_cross_var


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

# second title format
second_title_fmt = {
    'bold':True,
    'align':'center',
    'valign':'center',
    'font_name': 'Arial',
    'fg_color': '#5A81B8',
    'font_color':'#F8F8FF',
    }

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
        workbook = xlsxwriter.Workbook(self.result_loc + 'Vars_Report.xlsx'
                                       ,{'nan_inf_to_errors':True})

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


def visual_var_report(result_loc, data_bin, if_pas, x_list, params_list, if_mob = None, target = None, tim = None, freq = None ,option = 'risk'):
    '''
    :param result_loc: str, folder where save report file
    :param data_bin: dataframe , binned data
    :param if_pas: str, column name, value must be 1/0, mean order accept or not
    :param x_list: list, x variables columns name list
    :param params_list:dict, risk metrics table , can define more then one target.
    eg：{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
        * if_mob : str, value must be 1/0, 是否满足账期字段名
        * target :str, value must be 1/0, y字段名
        * ovd_amt :str, 逾期金额字段名
        * rep_amt :str, 本金字段名
        * prefix :str, 自定义前缀名，可以根据target的意思指定
    :param if_mob:是stable指标计算的字段，因为stable计算只能指定一个target，详细的不想写了就这样吧
    :param target:
    :param tim:
    :param freq:
    :param option:
    :return:
    '''

    doc = WriteDoc(result_loc = result_loc)
    workbook = doc.open_workbook()
    ws = doc.open_worksheet(workbook)
    print('>>> Start...')
    print('>>> %d variables will be calculated...'%len(x_list))
    if option == 'all':
        doc.var_risk_metrics_visual( ws = ws, data_bin = data_bin, if_pas = if_pas, x_list = x_list, params_list = params_list)
        doc.var_stable_metrics_visual(workbook = workbook,ws = ws, data_bin = data_bin,  x_list = x_list, params_list = params_list
                                      , if_mob = if_mob, target = target, tim = tim, freq = freq)
    elif option == 'risk':
        doc.var_risk_metrics_visual( ws = ws, data_bin = data_bin, if_pas = if_pas, x_list = x_list, params_list = params_list)
    elif option == 'stable':
        doc.var_stable_metrics_visual(workbook = workbook, ws = ws, data_bin = data_bin,  x_list = x_list, params_list = params_list
                                      , if_mob = if_mob, target = target, tim = tim, freq = freq)
    else:
        ValueError('>>>check param \'option\', use \'all\',\'risk\',\'stable\' instead')

    doc.close_workbook(workbook)
    print('>>> Finish, report has been saved at \'%s\''%(result_loc + 'Vars_Report.xlsx'))




class WriteDocCross():
    def __init__(self, result_loc):
        self.result_loc = result_loc


    def open_workbook(self):
        workbook = xlsxwriter.Workbook(self.result_loc + 'Cross_Matrix.xlsx'
                                       ,{'nan_inf_to_errors':True})

        global title_formater, second_title_formater, header_formater, main_formater, num_pct_formater, num_float_formater
        title_formater =  workbook.add_format(title_fmt)
        second_title_formater=  workbook.add_format(second_title_fmt)
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

    def cross_var_single_target_visual(self,ws, result_df, pen_row):
        '''
        :param ws:
        :param result_df:
        :param pen_row: 写入excel行指针
        :return: turple, dataframe.shape
        '''
        # define table header
        header_list = ['Bins'] + result_df.columns.tolist()
        column_settings = []
        # format table
        for header in header_list:
            if header[-1] == '%' or header[-3:] == 'pct':
                d = {'header': header, 'header_format':main_formater, 'format': num_pct_formater}
            else:
                d = {'header': header, 'header_format':main_formater, 'format': main_formater}
            column_settings.append(d)
        # add table value
        t_row, t_col  = result_df.shape
        res_array = np.c_[result_df.index,result_df.values,]
        ws.add_table(first_row = pen_row, first_col = 0, last_row = pen_row + t_row , last_col = t_col
                     , options = {'data':res_array, 'columns': column_settings, 'style': 'Table Style Light 16'})  # style就是excel'套用表格格式'的排序序号！😐无语

        return t_row, t_col


    def cross_var_loop_visual(self, ws, cross_var_list, data_bin, if_pas, params_list):
        doc = WriteDocCross(result_loc = self.result_loc)

        pen_row = 1  # 行指针
        for cross_var in cross_var_list :
            print('Processing %s...'%cross_var)

            # write first table title
            ws.write('A%d'%pen_row, '%s X %s'%(cross_var[0],cross_var[1]), title_formater)
            pen_row+=1

            # write second table title
            ws.write('A%d'%pen_row, '通过率', second_title_formater)

            # 通过率表
            df_apply = cal_cross_var(data = data_bin, cross_var = cross_var, target = if_pas, cal_pas = True)
            t_row, t_col = doc.cross_var_single_target_visual(ws = ws,  result_df = df_apply, pen_row = pen_row)
            pen_row = pen_row + t_row + 2

            # badrate表
            for i, params_dict in enumerate(params_list):
                # 去灰，如果不去灰，后面cal_val_....函数会报错
                data_model_bin = data_bin[(data_bin[params_dict['if_mob']] == 1) & (data_bin[params_dict['target']].isin([0,1]))]
                ws.write('A%d'%pen_row, params_dict['target'], second_title_formater)
                df_target = cal_cross_var(data = data_model_bin, cross_var = cross_var, target = params_dict['target'], cal_pas = False)
                t_row, t_col = doc.cross_var_single_target_visual(ws = ws,  result_df = df_target, pen_row = pen_row)
                pen_row = pen_row + t_row + 2

            pen_row += 2  # 空两行




def visual_cross_var_report(result_loc, data_bin, cross_var_list, if_pas, params_list):

    doc = WriteDocCross(result_loc = result_loc)
    workbook = doc.open_workbook()
    ws = doc.open_worksheet(workbook)
    print('>>> Start...')

    doc.cross_var_loop_visual(ws, cross_var_list, data_bin, if_pas, params_list)

    doc.close_workbook(workbook)
    print('>>> Finish, report has been saved at \'%s\''%(result_loc + 'Cross_Matrix.xlsx'))






if __name__ == '__main__':

    import os
    import pandas as pd
    import toad


    work_loc = './'
    result_loc = work_loc + 'result/'  # folder save output result
    if not os.path.exists(result_loc):
        os.mkdir(result_loc)

    file = '/Users/caowei/work/Risk/strategy_auto_tools/strategy_generator/data/testdata_sj.csv'
    data_raw = pd.read_csv(file,sep = '\t')

    # 是否满足账期的flag
    data_raw['if_mob_d10'] = data_raw['fst_rep_d10_amt'].notna()+0
    data_raw['if_mob_d30'] = data_raw['fst_rep_d30_amt'].notna()+0

    id_list = ['ord_no', 'uid','crt_tim']
    y_list  = ['if_pas','flag_1_30', 'flag_1_10', 'fst_ovr_due_d30_amt','fst_rep_d30_amt','fst_ovr_due_d10_amt','fst_rep_d10_amt']
    x_list = ['day_dif', 'acc_ord',  'is_xin','stt_rh', 'stt_xinyan', 'stt_bh','cus_sex', 'cus_age', 'cus_nat', 'usr_acd','lv2_pre_avl_lmt']


    # 03 bin
    c = toad.transform.Combiner()

    method = 'quantile'
    n_bins = 5
    min_samples = 0.02
    empty_separate = True
    target = 'flag_1_10'

    if method == 'quantile' :
        c.fit(X = data_raw[x_list + [target]] , y = target, method = method, n_bins = n_bins,  empty_separate = empty_separate)
    else:
        c.fit(X = data_raw[x_list + [target]] , y = target, method = method, n_bins = n_bins, min_samples = min_samples, empty_separate = empty_separate)

    # c.export()
    data_raw_bin =c.transform(data_raw, labels=True)



    result_loc =result_loc
    data_bin = data_raw_bin
    if_pas = 'if_pas'
    x_list  = ['cus_age',  'day_dif' ,'is_xin_mon']
    params_list = [{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
        ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
                   ]
    tim = 'crt_tim'
    if_mob = 'if_mob_d10'
    target = 'flag_1_10'
    freq ='Q'


    visual_var_report(result_loc, data_bin, if_pas, x_list, params_list,if_mob, target, tim, freq ,option = 'all')


    # cross matrix
    if_pas = 'if_pas'
    cross_var_list = [['cus_age','day_dif'],['modelscore_lendaudit2','day_dif']]
    cross_var = ['cus_age','day_dif']
    cross_x_list = []
    for cross_var in cross_var_list:
        cross_x_list.extend(cross_var)
    cross_x_list = list(set(cross_x_list)) # drop duplicates object

    target = 'flag_1_10'
    params_list = [{'if_mob':'if_mob_d10', 'target': 'flag_1_10', 'ovd_amt':'fst_ovr_due_d10_amt', 'rep_amt':'fst_rep_d10_amt', 'prefix':'FPD10'}
        ,{'if_mob':'if_mob_d30', 'target': 'flag_1_30', 'ovd_amt':'fst_ovr_due_d30_amt', 'rep_amt':'fst_rep_d30_amt', 'prefix':'FPD30'}
                   ]


    visual_cross_var_report(result_loc = result_loc
                            , data_bin = data_raw_bin
                            , cross_var_list = cross_var_list
                            , if_pas = if_pas
                            , params_list = params_list)

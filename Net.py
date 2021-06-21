from time import time
from base64 import b64encode
from copy import deepcopy
import streamlit as st
from numpy import linspace, array, interp
from pandas import DataFrame, read_csv
from DEFAULT import DRAW_LIST, DATA, SETTINGS
from Calculate import Analytic, Numerical

Setting_Mode = st.sidebar.selectbox("配置模式", ["默认模式", "专家模式"])

def main(data_cal, data_show, settings):
    settings['Method'] = 'Flux' if st.sidebar.selectbox(
        "燃耗方式", ["定通量燃耗", "定功率燃耗"]) == "定通量燃耗" else 'Power'
    if settings['Method'] == 'Flux':
        settings['Flux'] = st.sidebar.number_input(
            "中子通量（每平方厘米每秒）", min_value=0.0, format='%e', value=settings['Flux'], step=1e13)
        st.title("同位素成分随时间变化")
    else:
        settings['Power'] = st.sidebar.number_input(
            '比功率（兆瓦每吨）', min_value=0.0, format='%e', value=float(settings['Power']), help="单位质量的燃料可以放出的功率", step=50.0)
        st.title("同位素成分随燃耗变化")
    st.dataframe(data_show)

    draw_names_default = []
    SUM_INITIAL = 0

    settings['t'] = st.number_input(
        "运行时间（天）", min_value=0, format='%d', value=settings['t'], step=30)
    settings['DT'] = st.slider(
        "燃耗步长（天）", min_value=1 if settings['Method'] == 'Power' else 10, max_value=30, format='%d', value=settings['DT'])
    PLOT_ACCURACY = st.number_input("内步长精度", min_value=1e-8, value=settings['Accuracy'], format="%e", step=1e-4)

    for nuclide in data_show.iloc[:, 1]:
        if nuclide in DRAW_LIST.keys():
            draw_names_default.append(nuclide)
        if Setting_Mode == "专家模式" or nuclide in ['234U', '235U', '238U']:
            settings['Initial'][nuclide] = st.number_input(
                label=nuclide + "含量（千克每吨）", min_value=0.0, max_value=1000.0, value=float(settings['Initial'][nuclide]), format='%f', help=nuclide + "在单位质量燃料中的含量", step=1.0)
        
        SUM_INITIAL += settings['Initial'][nuclide]
        
    if SUM_INITIAL > 1000:
        st.warning("初始成分之和超出范围。请更正数值。")
    else:
        draw_names = st.multiselect("需要展示的核素", data_show.iloc[:, 1].to_list(), default=draw_names_default)
        draw_list = {}
        for nuclide in draw_names:
            draw_list[nuclide] = float(st.sidebar.number_input(nuclide + "缩放比例", min_value=0.0, format='%e', value=float(DRAW_LIST[nuclide] if nuclide in DRAW_LIST.keys() else 1), step=0.1))
            
        PLOT_MODE = st.selectbox("绘图方式", ["解析方法", "数值方法", "两种方法"])

        if PLOT_MODE in ["解析方法", "两种方法"]:
            start = time()
            analytic = Analytic(data_cal, settings)
            analytic.main(settings['t'] * 24 * 60 * 60, PLOT_ACCURACY)
            stop = time()
            if len(analytic.time_sequence) == 0:
                st.error("未能启动燃耗计算。可能的原因：定功率下可（易）裂变核素过少。")
            else:
                abscissa_title, plot_data = draw(analytic.numerical_result, analytic.time_sequence, draw_list, settings['Power'] if settings['Method'] == 'Power' else None)
                plot_info = {
                    "横坐标": str(abscissa_title),
                    "纵坐标": "同位素成分/(千克每吨)",
                    "计算方法": "解析方法",
                    "用时": "%.3e秒"%(stop - start)
                }
                st.write(plot_info)
                csv = plot_data.to_csv()
                b64 = b64encode(csv.encode(encoding='gbk')).decode(encoding='gbk')
                href = f'<a href="data:file/csv;base64,{b64}">下载燃耗计算结果</a> (右键点击链接并另存为csv格式)'
                st.markdown(href, unsafe_allow_html=True)
            
        if PLOT_MODE in ["数值方法", "两种方法"]:
            start = time()
            numerical = Numerical(data_cal, settings)
            numerical.main(settings['t'] * 24 * 60 * 60, PLOT_ACCURACY)
            stop = time()
            if len(numerical.time_sequence) == 0:
                st.error("未能启动燃耗计算。可能的原因：定功率下可（易）裂变核素过少。")
            else:
                abscissa_title, plot_data = draw(numerical.numerical_result, numerical.time_sequence, draw_list, settings['Power'] if settings['Method'] == 'Power' else None)
                plot_info = {
                    "横坐标": str(abscissa_title),
                    "纵坐标": "同位素成分/(千克每吨)",
                    "计算方法": "数值方法",
                    "用时": "%.3e秒"%(stop - start)
                }
                st.write(plot_info)
                csv = plot_data.to_csv()
                b64 = b64encode(csv.encode(encoding='gbk')).decode(encoding='gbk')
                href = f'<a href="data:file/csv;base64,{b64}">下载燃耗计算结果</a> (右键点击链接并另存为csv格式)'
                st.markdown(href, unsafe_allow_html=True)

def draw(numerical_result, time_sequence, draw_list, power=None):
    abscissa_title = ''
    plot_data = []
    plot_title = []
    time_sequence_new = linspace(time_sequence[0], time_sequence[-1], num=10000) if len(time_sequence) > 10000 else time_sequence
    for nuclide, nuclide_N in numerical_result.items():
        if nuclide in draw_list.keys():
            plot_data.append(nuclide_N * draw_list[nuclide] * int(nuclide[0:3]) * 1e-3)
            plot_data[-1] = interp(time_sequence_new, time_sequence, plot_data[-1])
            plot_title.append(nuclide if draw_list[nuclide] == 1 else nuclide + ' * %f'%draw_list[nuclide])

    if power is None:
        time_sequence_new /= (24 * 60 * 60)
        if time_sequence_new[-1] > 3650:
            time_sequence_new /= 365
            T_UNIT = '年'
        elif time_sequence_new[-1] > 300:
            time_sequence_new /= 30
            T_UNIT = '月'
        else:
            T_UNIT = '天'
        abscissa_title = "运行时间/(%s)"%T_UNIT
    else:
        time_sequence_new *= power * 1e-3 / (24 * 60 * 60)
        abscissa_title = "燃耗深度/(GW·天每吨)"

    plot_data = DataFrame(array(plot_data).T, time_sequence_new, plot_title)
    st.line_chart(plot_data)
    return abscissa_title, plot_data

if __name__ == '__main__':
    if Setting_Mode == "专家模式":
        csv = DATA.to_csv(index=False)
        b64 = b64encode(csv.encode(encoding='gbk')).decode(encoding='gbk')
        href = f'<a href="data:file/csv;base64,{b64}">下载燃耗链配置文件</a> (右键点击链接并另存为csv格式)'
        st.markdown(href, unsafe_allow_html=True)
        
        DATA_User = st.file_uploader("选择您的配置文件", type="csv", key='upload')
        if DATA_User is not None:
            data = read_csv(DATA_User, encoding='gbk')
            settings = deepcopy(SETTINGS)
            for nuclide in SETTINGS['Initial'].keys():
                if nuclide not in data.iloc[:, 1]:
                    del settings['Initial'][nuclide]
            settings_copy = deepcopy(settings)
            for nuclide in data.iloc[:, 1]:
                if nuclide not in settings_copy['Initial'].keys():
                    settings['Initial'][nuclide] = 0
            main(data.to_numpy(), data, settings)
    else:
        main(DATA.to_numpy(), DATA, SETTINGS)


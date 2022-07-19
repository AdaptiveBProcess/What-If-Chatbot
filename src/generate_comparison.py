# -*- coding: utf-8 -*-
import glob
import pandas as pd
from . import utils_chatbot as u
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

def execute_intent(bimp_path):
    scenarios = glob.glob('inputs/*/models/*.bpmn')
    
    available_scenarios = [x.split('\\')[-1] for x in scenarios]
    df_available_scenarios = pd.DataFrame(data = available_scenarios, columns = ['SCENARIOS'])
    
    print(df_available_scenarios.to_string())
    
    cond = True
    while cond:
        sim_scenario = input('which of the following scenarios do you want to compare? (write the number of scenarios separated by coma i.e. 1,2,4): ')
        sim_scenario = sim_scenario.split(',')
        if len(sim_scenario)>0:
            cond = False
        else:
            print('Please enter a valid number for scenarios!')
            
    comparison_scenarios = [scenarios[int(x)] for x in sim_scenario]
    
    scenario_paths = []
    for comparison_scenario in comparison_scenarios:
        csv_output_path = 'outputs/comparison/' + comparison_scenario.replace('bpmn', 'csv').split('\\')[-1]
        u.execute_simulator_simple(bimp_path, comparison_scenario, csv_output_path)
        scenario_paths.append([comparison_scenario, csv_output_path])
        
    df_res_util = pd.DataFrame(data = [], columns = ['Scenario', 'Resource', 'Utilization'])
    df_scenario_stats = pd.DataFrame(data = [], columns = ['Scenario','KPI', 'Min', 'Average', 'Max'])
    
    for scenario_path in scenario_paths:
        csv = scenario_path[1]
        
        ptt_s = 'Resource utilization'
        ptt_e = 'Individual task statistics' 
        res_u = u.extract_text(csv, ptt_s, ptt_e)
        
        data = [x.split(',') for x in res_u.split('\n') if x != '']
        df_tmp = pd.DataFrame(data = data[1:], columns=['Resource', 'Utilization'])
        df_tmp['Scenario'] = csv.split('/')[-1].split('.')[0]
        df_res_util = pd.concat([df_res_util, df_tmp[['Scenario', 'Resource', 'Utilization']]])
        
        ptt_s = 'Scenario statistics'
        ptt_e = 'Process Cycle Time (s) distribution' 
        scen_s = u.extract_text(csv, ptt_s, ptt_e)
        
        data = [x.split(',') for x in scen_s.split('\n') if x != '']
        df_tmp = pd.DataFrame(data = data[1:], columns=['KPI', 'Min', 'Average', 'Max'])
        df_tmp['Scenario'] = csv.split('/')[-1].split('.')[0]
        df_scenario_stats = pd.concat([df_scenario_stats, df_tmp[['Scenario', 'KPI', 'Min', 'Average', 'Max']]])
        
    scenarios = list(df_scenario_stats['Scenario'].drop_duplicates().values)
    
    df_res_util['Utilization'] = df_res_util['Utilization'].astype('float')
    df_scenario_stats[['Min', 'Average', 'Max']] = df_scenario_stats[['Min', 'Average', 'Max']].astype('float')
    
    plt.figure(figsize=(6, 6))
    ax1 = sns.barplot(data=df_res_util, x='Resource', y='Utilization', hue='Scenario', palette='Set2')
    ax1.grid()
    ax1.set_ylim([0, 100])
    plt.savefig('outputs/comparison/fig1.png', bbox_inches='tight')
    plt.clf()
    
    x_ticks = ['Process Cycle \nTime (s)', 'Process Cycle \n Time excluding \n out of timetable \nhours (s)',
               'Process Waiting \nTime (s)', 'Accumulated \nProcess \n Duration (s)', 'Cost']
    
    plt.figure(figsize=(6, 6))
    ax2 = sns.barplot(data=df_scenario_stats, x='KPI', y='Min', hue='Scenario', palette='Set2')
    plt.legend(bbox_to_anchor=(-0.4, -0.55), loc='upper left', ncol=3, borderaxespad=0)
    ax2.set_title('Minimun Stats')
    ax2.grid()
    ax2.set_xticklabels(x_ticks, rotation=90)
    plt.savefig('outputs/comparison/fig2.png', bbox_inches='tight')
    plt.clf()
    
    plt.figure(figsize=(6, 6))
    ax3 = sns.barplot(data=df_scenario_stats, x='KPI', y='Average', hue='Scenario', palette='Set2')
    plt.legend(bbox_to_anchor=(-0.4, -0.55), loc='upper left', ncol=3, borderaxespad=0)
    ax3.set_title('Average Stats')
    ax3.grid()
    ax3.set_xticklabels(x_ticks, rotation=90)
    plt.savefig('outputs/comparison/fig3.png', bbox_inches='tight')
    plt.clf()
    
    plt.figure(figsize=(6, 6))
    axs4 = sns.barplot(data=df_scenario_stats, x='KPI', y='Max', hue='Scenario', palette='Set2')
    plt.legend(bbox_to_anchor=(-0.4, -0.55), loc='upper left', ncol=3, borderaxespad=0)
    axs4.set_title('Maximum Stats')
    axs4.grid()
    axs4.set_xticklabels(x_ticks, rotation=90)
    plt.savefig('outputs/comparison/fig4.png', bbox_inches='tight')
    plt.clf()
    
    pdf_name = '_'.join(df_scenario_stats['Scenario'].drop_duplicates())
    pdf = FPDF(orientation = 'L', unit = 'mm', format='A4')
    pdf.add_page()
    pdf.set_font('arial', 'B', 11)
    pdf.cell(150, 10, 'Comparison of different scenarios', 0, 2, 'C')
    pdf.image('outputs/comparison/fig1.png')
    pdf.image('outputs/comparison/fig2.png')
    pdf.image('outputs/comparison/fig3.png')
    pdf.image('outputs/comparison/fig4.png')
    pdf.output('outputs/comparison/{}.pdf'.format(pdf_name))
    
    img_path = [os.remove(x) for x in glob.glob('outputs/comparison/*.png')]
    print('Analysis generated in {}'.format('outputs/comparison/{}.pdf'.format(pdf_name)))

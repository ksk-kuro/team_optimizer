import pandas as pd
import xlsxwriter
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
import jaconv
import re

DEBUG = False
DEBUG_inputprint = True

def count_common_elements(list1, list2):
    return len(set(list1) & set(list2))

def calculate_R(teams):
    R = []
    for i in range(len(teams) - 1):
        R.append(count_common_elements(teams[i][6], teams[i+1][6]))
    return R

def sum_R(R):
    return sum(R)

def convert_time_to_seconds(time):
    if time is None:
        return 0
    minutes = int(time)
    seconds = (time - minutes) * 100
    return int(minutes * 60 + seconds)

def str_to_timestr(input,option):
    string = str(input)
    time_list = re.split('[:：]',string)
    if option == 'startendtime':
        if len(time_list) == 2:
            return time_list[0].strip() + '.' + time_list[1].strip()
        elif len(time_list) == 3:
            return str(int(time_list[0])*60+int(time_list[1])).strip() + '.' + time_list[2].strip()
        else :
            return string
    elif option =='time':
        if len(time_list) == 1:
            return string
        else:
            if int(time_list[0]) != 0:
                return str(time_list[0]).strip() + '.' + time_list[1].strip()
            elif int(time_list[0]) == 0 and len(time_list) == 3:
                return str(time_list[1]).strip() + '.' + time_list[2].strip()

def format_timestamp(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"

def check_constraints(order, teams , showcase_starttime):
    total_seconds = showcase_starttime
    ignored_count = 0
    ignored_constraints = []
    for index, team_index in enumerate(order):
        start, end, starttime, endtime = teams[team_index][1:5]
        
        if isinstance(starttime, complex):
            start_seconds = convert_time_to_seconds(starttime.imag)
            if total_seconds < start_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority starttime constraint was ignored")
        elif starttime is not None and not np.isnan(starttime):
            start_seconds = convert_time_to_seconds(starttime)
            if total_seconds < start_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s starttime constraint was ignored")
        
        if isinstance(start, complex):
            if index + 1 < int(start.imag):
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority start constraint was ignored")
        elif start is not None and not np.isnan(start):
            if index + 1 < start:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s start constraint was ignored")
        
        if isinstance(endtime, complex):
            end_seconds = convert_time_to_seconds(endtime.imag)
            if total_seconds > end_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority endtime constraint was ignored")
        elif endtime is not None and not np.isnan(endtime):
            end_seconds = convert_time_to_seconds(endtime)
            if total_seconds > end_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s endtime constraint was ignored")
        
        if isinstance(end, complex):
            if index + 1 > int(end.imag):
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority end constraint was ignored")
        elif end is not None and not np.isnan(end):
            if index + 1 > end:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s end constraint was ignored")
        
        total_seconds += convert_time_to_seconds(teams[team_index][5])
    
    return ignored_count, ignored_constraints


def optimize_teams_order(teams,showcase_starttime):
    n = len(teams)
    dp = [(None, float('inf'), float('inf'), float('inf'))] * (1 << n)
    dp[0] = ([], 0, 0, 0)
    constraints_ignored = {i: [] for i in range(1 << n)}

    for mask in range(1 << n):
        for i in range(n):
            if not (mask & (1 << i)):
                new_mask = mask | (1 << i)
                for j in range(len(dp[mask][0]) + 1):
                    new_order = dp[mask][0][:j] + [i] + dp[mask][0][j:]
                    new_R = calculate_R([teams[k] for k in new_order])
                    new_sum_R = sum_R(new_R)
                    ignored_count, ignored_constraints = check_constraints(new_order, teams,showcase_starttime)
                    high_priority_ignored = sum(1 for c in ignored_constraints if "high priority" in c)
                    
                    if (high_priority_ignored < dp[new_mask][3]) or (
                        high_priority_ignored == dp[new_mask][3] and 
                        (ignored_count < dp[new_mask][2]) or 
                        (ignored_count == dp[new_mask][2] and new_sum_R < dp[new_mask][1])
                    ):
                        dp[new_mask] = (new_order, new_sum_R, ignored_count, high_priority_ignored)
                        constraints_ignored[new_mask] = ignored_constraints.copy()
    
    final_mask = (1 << n) - 1
    best_order = dp[final_mask][0]
    ignored_constraints = constraints_ignored[final_mask]
    
    return [teams[i] for i in best_order], ignored_constraints, dp[final_mask][1]


def gen_converter(gen):
    if isinstance(gen,int):
        return str(gen).rstrip()
    elif not gen:
        return str(gen).rstrip()
    elif isinstance(gen,str):
        return jaconv.z2h(gen, kana=False, ascii=False, digit=True).rstrip()
    else :
        return str(gen).rstrip()

def genre_converter(s):
    if not s:
        return s.rstrip()  # 空文字列の場合はそのまま返す
    
    # 先頭の文字を大文字に変換
    first_char = s[0].upper()
    # 残りの文字を小文字に変換
    rest = s[1:].rstrip().lower()
    
    return first_char + rest

def name_converter(text):
    return jaconv.h2z(text, kana=True, ascii=False, digit=False).rstrip()

def name_format(gen,genre,familyname,firstname):
    return gen+' '+genre+' '+familyname+' '+firstname

def read_teams_from_xlsx():
    root = tk.Tk()
    root.withdraw()  # GUIのメインウィンドウを非表示にします
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Select Excel File"
    )

    # ユーザーがキャンセルした場合、読み込みを中止
    if not file_path:
        print("File open operation cancelled.")
        return None

    xls = pd.ExcelFile(file_path)
    teams = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        team_name = df.iloc[0, 0]
        start = df.iloc[0, 2]
        end = df.iloc[0, 3]
        starttime = str_to_timestr(df.iloc[0, 4],'startendtime')
        endtime = str_to_timestr(df.iloc[0, 5],'startendtime')
        time = str_to_timestr(df.iloc[0, 1],'time')

        gen = df.iloc[3:, 0].dropna().tolist()
        genre = df.iloc[3:, 1].dropna().tolist()
        familyname = df.iloc[3:, 2].dropna().tolist()
        firstname = df.iloc[3:, 3].dropna().tolist()
        names = []
        for i in range(len(gen)):
            gen_converted = gen_converter(gen[i])
            genre_converted = genre_converter(genre[i])
            familyname_converted = name_converter(familyname[i])
            firstname_converted = name_converter(firstname[i])
            names.append(name_format(gen_converted,genre_converted,familyname_converted,firstname_converted))

        try:
            if isinstance(start, str) and 'j' in start:
                start = complex(start)
            else:
                start = int(start)
        except ValueError:
            start = None

        try:
            if isinstance(end, str) and 'j' in end:
                end = complex(end)
            else:
                end = int(end)
        except ValueError:
            end = None

        try:
            if isinstance(starttime, str) and 'j' in starttime:
                starttime = complex(starttime)
            else:
                starttime = float(starttime)
        except ValueError:
            starttime = None

        try:
            if isinstance(endtime, str) and 'j' in endtime:
                endtime = complex(endtime)
            else:
                endtime = float(endtime)
        except ValueError:
            endtime = None

        try:
            time = float(time)
        except ValueError:
            time = None

        teams.append([team_name, start, end, starttime, endtime, time, names])

    return teams



def export_to_xlsx(optimized_teams, ignored_constraints,showcase_starttime, default_file_name="optimized_schedule.xlsx"):
    # GUIで保存先ディレクトリを選択
    root = tk.Tk()
    root.withdraw()  # GUIのメインウィンドウを非表示にします
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=default_file_name,
        title="Save Optimized Schedule"
    )

    # ユーザーがキャンセルした場合、保存しない
    if not save_path:
        print("Save operation cancelled.")
        return

    with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
        df_main = pd.DataFrame(columns=['Timestamp', 'Team'])
        total_seconds = showcase_starttime

        for team in optimized_teams:
            timestamp = format_timestamp(total_seconds)
            df_main = pd.concat([df_main, pd.DataFrame([[timestamp, team[0]]], columns=['Timestamp', 'Team'])])
            total_seconds += convert_time_to_seconds(team[5])
        
        df_main.to_excel(writer, sheet_name='Main', index=False)

        for i in range(len(optimized_teams) - 1):
            common_members = set(optimized_teams[i][6]).intersection(set(optimized_teams[i + 1][6]))
            df_transition = pd.DataFrame(list(common_members), columns=['Common Members'])
            df_transition.to_excel(writer, sheet_name=f'Transition {i + 1}', index=False)
        
        # Summary sheet with ignored constraints content
        df_summary = pd.DataFrame(columns=['Ignored Constraints'])
        df_summary.loc[0] = [f"Ignored Constraints Count: {len(ignored_constraints)}"]
        df_summary.loc[1] = [f"Total R Value: {calculate_R(optimized_teams)}"]

        for i, constraint in enumerate(ignored_constraints):
            df_summary.loc[i + 2] = [constraint]
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

def remove_backslashes_and_trailing_spaces(input_string):
    # Remove backslashes
    cleaned_string = input_string.replace("\\", "")
    # Remove only trailing spaces
    cleaned_string = cleaned_string.rstrip()
    return cleaned_string

showcase_starttime_ex = 3671

# ファイルを読み込み、チームを最適化し、結果をエクスポートする例
if not DEBUG:
    teams = read_teams_from_xlsx()
    if teams is None:
        print("No file selected, terminating.")
        exit()
else:
    teams = [
        ["Break", 2, 3, -1, 3.0, 2.5, ["John", "Mike", "Akira", "Alex","An","George"]],
        ["Alpha", 1, 4, 1.0, -1, 1.3, ["Alex", "Mike", "Fumi", "Sam", "Ren","Bob"]],
        ["Beta", 1, 2, -1, 2.5, 0.7, ["Fumi", "Ren", "John", "Tom"]],
        ["Gamma", 3, 4, 2.0, -1, 1.2, ["Tom", "Mike", "Sara", "Fumi","Ken"]],
        ["Delta", -1, -1, -1, -1, 2.0, ["Sara", "Mike", "Nina", "Paul"]],
        ["Epsilon", 5, -1, 3.0, 10.5, 3.0, ["Paul", "Nina", "Akira", "John","Bob"]],
        ["Zeta", -1, 6, -1, 4.5, 1.5, ["Nina", "Alex", "John", "Sara"]],
        ["Eta", 4, 7, 4.5, -1, 2.1, ["Tom", "Fumi", "Paul", "Alex"]],
        ["Theta", 6, 9, -1, 8.0j, 1.9, ["Mike", "Sam", "John", "Nina","Bob"]],
        ["Iota", 7j, 10, 7.0, 10.5, 2.6, ["Ren", "Tom", "Sara", "Mike","Ken"]]
    ]
if DEBUG_inputprint:print(teams)
optimized_teams, ignored_constraints, _ = optimize_teams_order(teams,showcase_starttime_ex)

export_to_xlsx(optimized_teams, ignored_constraints,showcase_starttime_ex, 'optimized_schedule.xlsx')
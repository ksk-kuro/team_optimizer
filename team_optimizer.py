import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import jaconv
import re
import time_getter_gui as gui

DEBUG = False
DEBUG_inputprint = True

def count_common_elements(list1, list2):
    return len(set(list1) & set(list2))

def calculate_R(teams):
    R = []
    for i in range(len(teams) - 1):
        R.append(count_common_elements(teams[i][6], teams[i+1][6]))
    return R

def convert_time_to_seconds(time):
    if time is None:
        return 0
    minutes = int(time)
    seconds = (time - minutes) * 100
    return int(minutes * 60 + seconds)

def replace_hyphen(value, replace_at='-'):
   """
   全ハイフンをマイナスに置換
   :param value: 置換したい文字列
   :param replace_at: ハイフンの置換先の文字列
   :return: 置換した文字列
   """
   return re.sub('－|-|‐|−|‒|—|–|―|ｰ|─|━|ㅡ|ـ|⁻|₋', replace_at, value)

def convert_startend_to_str_ifneeded(input):
    if isinstance(input,str):
        string = str(jaconv.z2h(input,kana=False,ascii=True,digit=True)).replace(' ','')
        return replace_hyphen(string)
    else:
        return input
    
def calculate_total_performance_time(teams):
    total_seconds = 0
    for team in teams:
        performance_time = team[5]
        total_seconds += convert_time_to_seconds(performance_time)
    return total_seconds

def str_to_timestr(input,option):
    string = jaconv.z2h(str(input), kana=False, ascii=True, digit=True)
    time_list = re.split('[:]',string)
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

def check_constraints(order, teams , showcase_starttime,transition_seconds):
    total_seconds = showcase_starttime
    ignored_count = 0
    ignored_constraints = []
    n_teams = len(teams)

    for index, team_index in enumerate(order):
        start, end, starttime, endtime,time = teams[team_index][1:6]
        
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
            start_value = int(start.imag)
            if start_value < 0:
                start_value = n_teams + 1 + start_value
            if index + 1 < start_value:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority start constraint was ignored")
        elif start is not None and not np.isnan(start):
            if start < 0:
                start = n_teams + 1 + start
            if index + 1 < start:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s start constraint was ignored")


        if isinstance(endtime, complex):
            end_seconds = convert_time_to_seconds(endtime.imag)
            if total_seconds + convert_time_to_seconds(time)> end_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority endtime constraint was ignored")
        elif endtime is not None and not np.isnan(endtime):
            end_seconds = convert_time_to_seconds(endtime)
            if total_seconds + convert_time_to_seconds(time)> end_seconds:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s endtime constraint was ignored")
        
        if isinstance(end, complex):
            end_value = int(end.imag)
            if end_value < 0:
                end_value = n_teams + 1 + end_value
            if index + 1 > end_value:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s high priority end constraint was ignored")
        elif end is not None and not np.isnan(end):
            if end < 0:
                end = n_teams + 1 + end
            if index + 1 > end:
                ignored_count += 1
                ignored_constraints.append(f"Team {teams[team_index][0]}'s end constraint was ignored")
    
        total_seconds += convert_time_to_seconds(teams[team_index][5])
        total_seconds += transition_seconds
    
    return ignored_count, ignored_constraints


def optimize_teams_order(teams,showcase_starttime,transition_seconds):
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
                    new_sum_R = sum(new_R)
                    ignored_count, ignored_constraints = check_constraints(new_order, teams,showcase_starttime,transition_seconds)
                    high_priority_ignored = sum(1 for c in ignored_constraints if "high priority" in c)
                    
                    if (high_priority_ignored < dp[new_mask][3]) or (
                        high_priority_ignored == dp[new_mask][3] and 
                        (ignored_count < dp[new_mask][2]) or 
                        (ignored_count == dp[new_mask][2] and new_sum_R < dp[new_mask][1])
                    ):
                        dp[new_mask] = (new_order, new_sum_R, ignored_count, high_priority_ignored)
                        constraints_ignored[new_mask] = ignored_constraints.copy()
        print("\rprogress:",round(mask/(1 << n)*100,5),"%",end = '')
    
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
        return jaconv.z2h(gen, kana=False, ascii=False, digit=True).replace(' ','')
    else :
        return str(gen).rstrip()

def genre_converter(s):
    if not s:
        return s.rstrip()  # 空文字列の場合はそのまま返す
    s = jaconv.z2h(s, kana=False, ascii=True, digit=False).replace(' ','')
    # 先頭の文字を大文字に変換
    first_char = s[0].upper()
    # 残りの文字を小文字に変換
    rest = s[1:].lower()
    result = first_char +rest
    if result == "Hip":
        result = "Hiphop"
    return result

def name_converter(text):
    return jaconv.h2z(text, kana=True, ascii=False, digit=False).replace('　','')

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
        start = convert_startend_to_str_ifneeded(df.iloc[0, 2])
        end = convert_startend_to_str_ifneeded(df.iloc[0, 3])
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
            if isinstance(start, str) and ('j' in start or 'J' in start):
                start = complex(start)
            else:
                start = int(start)
        except ValueError:
            start = None

        try:
            if isinstance(end, str) and ('j' in end or 'J' in end):
                end = complex(end)
            else:
                end = int(end)
        except ValueError:
            end = None

        try:
            if isinstance(starttime, str) and ('j' in starttime or 'J' in starttime):
                starttime = complex(starttime)
            else:
                starttime = float(starttime)
        except ValueError:
            starttime = None

        try:
            if isinstance(endtime, str) and ('j' in endtime or 'J' in endtime):
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



def export_to_xlsx(optimized_teams, ignored_constraints, transition_seconds, showcase_starttime=0, default_file_name="optimized_schedule.xlsx"):
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
        df_main = pd.DataFrame(columns=['Timestamp', 'Team', 'showcase time', 'transition time'])
        total_seconds = showcase_starttime

        for team in optimized_teams:
            timestamp = format_timestamp(total_seconds)
            showcasetime = format_timestamp(convert_time_to_seconds(team[5]))
            transition_seconds_formatted = format_timestamp(transition_seconds)
            df_main = pd.concat([df_main, pd.DataFrame([[timestamp, team[0], showcasetime, transition_seconds_formatted]], columns=['Timestamp', 'Team', 'showcase time', 'transition time'])])
            total_seconds += convert_time_to_seconds(team[5])
            total_seconds += transition_seconds
        timestamp = format_timestamp(total_seconds)
        df_main = pd.concat([df_main, pd.DataFrame([[timestamp]], columns=['Timestamp'])])

        df_main.to_excel(writer, sheet_name='Main', index=False)

        for i in range(len(optimized_teams) - 1):
            common_members = set(optimized_teams[i][6]).intersection(set(optimized_teams[i + 1][6]))
            common_members_sorted = sorted(common_members)
            df_transition = pd.DataFrame(list(common_members_sorted), columns=[f'Common Members of {i + 1}: {optimized_teams[i][0]} -> {i + 2}: {optimized_teams[i + 1][0]} '])
            df_transition.to_excel(writer, sheet_name=f'Transition {i + 1}', index=False)

        # Summary sheet with ignored constraints content
        df_summary = pd.DataFrame(columns=['Ignored Constraints'])
        df_summary.loc[0] = [f"Ignored Constraints Count: {len(ignored_constraints)}"]
        df_summary.loc[1] = [f"Total R Value: {calculate_R(optimized_teams)}, {sum(calculate_R(optimized_teams))}"]

        for i, constraint in enumerate(ignored_constraints):
            df_summary.loc[i + 2] = [constraint]
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

        # 新しいシートの追加: names + チーム出席情報
        all_names = sorted({name for team in optimized_teams for name in team[6]})  # 全メンバー名をソートして取得
        df_names = pd.DataFrame(columns=['names'] + [team[0] for team in optimized_teams])  # 1列目: "names", 2列目以降: チーム名

        # 各メンバーの所属チーム情報を埋める
        for name in all_names:
            row = [name]  # 1列目: メンバー名
            count = 0  # ○の数を数えるためのカウンタ
            for team in optimized_teams:
                if name in team[6]:
                    row.append('○')
                    count += 1
                else:
                    row.append('')
            row.append(count)  # 最後の列に○の数を追加
            df_names = pd.concat([df_names, pd.DataFrame([row], columns=['names'] + [team[0] for team in optimized_teams] + ['count'])])

        df_names.to_excel(writer, sheet_name='Names Participation', index=False)

def remove_backslashes_and_trailing_spaces(input_string):
    # Remove backslashes
    cleaned_string = input_string.replace("\\", "")
    # Remove only trailing spaces
    cleaned_string = cleaned_string.rstrip()
    return cleaned_string



if __name__ == "__main__":

    initialize_start = gui.initialize_gui()

    if initialize_start:
        showcase_starttime = gui.get_showcasestarttime_from_gui()
        if DEBUG_inputprint:print("showcase start:",showcase_starttime)
    else:
        showcase_endtime = gui.get_showcaseendtime_from_gui()
        if DEBUG_inputprint:print("showcase start:",showcase_endtime)

    transition_seconds = gui.get_transitiontime_from_gui()
    if DEBUG_inputprint:print("transition time:",transition_seconds)

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

    if not initialize_start:
        total_time = calculate_total_performance_time(teams)+len(teams)*transition_seconds
        showcase_starttime = showcase_endtime - total_time
    
    if DEBUG_inputprint:
        print(teams)
        print(f'initial total R value = {sum(calculate_R(teams))}')
        initial_constraints_count,initial_constraints = check_constraints(list(range(len(teams))),teams,showcase_starttime,transition_seconds)
        print(f'the number of initial ignored constraints : {initial_constraints_count}')
        print(initial_constraints)

    exportmethod = gui.exportmethod_gui()
    print("valiable accepted")

    if exportmethod:
        print("optimization started")
        optimized_teams, ignored_constraints, _ = optimize_teams_order(teams,showcase_starttime,transition_seconds)
        print("optimization ended")
        export_to_xlsx(optimized_teams, ignored_constraints,transition_seconds,showcase_starttime, 'optimized_schedule.xlsx')
    else:
        print("export process started")
        optimized_teams = teams
        _ ,ignored_constraints = check_constraints(list(range(len(teams))),teams,showcase_starttime,transition_seconds)
        print("export process ended")
        export_to_xlsx(optimized_teams, ignored_constraints,transition_seconds,showcase_starttime, 'not_optimized_schedule.xlsx')
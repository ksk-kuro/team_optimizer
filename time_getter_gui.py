import tkinter as tk
from tkinter import messagebox

def create_button_gui():
    # ボタンが押されたときのコールバック関数
    def on_button_click(value):
        nonlocal result
        result = value
        root.destroy()  # ウィンドウを閉じる

    result = None

    # ウィンドウを作成
    root = tk.Tk()
    root.title("")
    root.configure(bg="white")
    root.geometry("800x220")

    #textfield
    textfield = tk.Frame(root,bg = "white")
    textfield_BOILED_label = tk.Label(textfield,text = "BOILED",font=('MS Gothic',35),bg='white')
    textfield_BOILED_label.pack()
    textfield_Team_Optimizer = tk.Label(textfield,text = "Team Optimizer",font=('MS Gothic',35),bg='white')
    textfield_Team_Optimizer.pack()
    textfield.pack()

    # ボタンAを作成
    button_a = tk.Button(root, text="開始時刻を指定して始める", command=lambda: on_button_click(True),bg="white")
    button_a.pack(pady=10)

    # ボタンBを作成
    button_b = tk.Button(root, text="終了時刻を指定して始める", command=lambda: on_button_click(False),bg="white")
    button_b.pack(pady=10)

    #自己顕示欲
    textfield2 = tk.Frame(root,bg = "white")
    textfield_name_label = tk.Label(textfield2,text = "developped by Kosuke,14th,sub head,break",font=('MS Gothic',15),bg='white')
    textfield_name_label.pack()
    textfield2.pack()

    # ウィンドウのメインループを開始
    root.mainloop()

    return result

def get_showcasestarttime_from_gui():
    def submit_time():
        try:
            hour = int(hour_entry.get())
            minute = int(minute_entry.get())
            second = int(second_entry.get())
            base_root.quit()  # GUIを終了する
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hour, minute, and second.")
            return

        global time_list
        time_list = [hour, minute, second]
        base_root.destroy()  # GUIを破棄する

    global time_list
    time_list = []

    # GUIを作成
    base_root = tk.Tk()
    base_root.title("ショーケース開始時刻")
    base_root.geometry("800x150")
    base_root.configure(bg = 'white')

    # ラベルと入力フィールドを作成

    textframe = tk.Frame(base_root,bg='white')
    description_label = tk.Label(textframe,text = "開始時刻を２４時間表記で入力してください。",font=('MS Gothic',30),bg='white')
    description_label.pack()
    textframe.pack()

    root = tk.Frame(base_root,bg='white')
    hour_label = tk.Label(root, text="時",font=('MS Gothic',30),bg = 'white')
    hour_label.grid(row=1, column=1)
    hour_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    hour_entry.grid(row=1, column=0)

    minute_label = tk.Label(root, text="分",font=('MS Gothic',30),bg='white')
    minute_label.grid(row=1, column=3)
    minute_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    minute_entry.grid(row=1, column=2)

    second_label = tk.Label(root, text="秒",font=('MS Gothic',30),bg = 'white')
    second_label.grid(row=1, column=5)
    second_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    second_entry.grid(row=1, column=4)
    root.pack()

    # ボタンを作成
    submit_button = tk.Button(root, text="Submit", command=submit_time,font=('MS Gothic',30),bg = 'white')
    submit_button.grid(row=3, columnspan=10)

    # GUIを実行
    base_root.mainloop()

    culculated_time = 3600*time_list[0] + 60*time_list[1] + time_list[2]
    return culculated_time

def get_showcaseendtime_from_gui():
    def submit_time():
        try:
            hour = int(hour_entry.get())
            minute = int(minute_entry.get())
            second = int(second_entry.get())
            base_root.quit()  # GUIを終了する
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hour, minute, and second.")
            return

        global time_list
        time_list = [hour, minute, second]
        base_root.destroy()  # GUIを破棄する

    global time_list
    time_list = []

    # GUIを作成
    base_root = tk.Tk()
    base_root.title("ショーケース終了時刻")
    base_root.geometry("800x150")
    base_root.configure(bg = 'white')

    # ラベルと入力フィールドを作成

    textframe = tk.Frame(base_root,bg='white')
    description_label = tk.Label(textframe,text = "終了時刻を２４時間表記で入力してください。",font=('MS Gothic',30),bg='white')
    description_label.pack()
    textframe.pack()

    root = tk.Frame(base_root,bg='white')
    hour_label = tk.Label(root, text="時",font=('MS Gothic',30),bg = 'white')
    hour_label.grid(row=1, column=1)
    hour_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    hour_entry.grid(row=1, column=0)

    minute_label = tk.Label(root, text="分",font=('MS Gothic',30),bg='white')
    minute_label.grid(row=1, column=3)
    minute_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    minute_entry.grid(row=1, column=2)

    second_label = tk.Label(root, text="秒",font=('MS Gothic',30),bg = 'white')
    second_label.grid(row=1, column=5)
    second_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    second_entry.grid(row=1, column=4)
    root.pack()

    # ボタンを作成
    submit_button = tk.Button(root, text="Submit", command=submit_time,font=('MS Gothic',30),bg = 'white')
    submit_button.grid(row=3, columnspan=10)

    # GUIを実行
    base_root.mainloop()

    culculated_time = 3600*time_list[0] + 60*time_list[1] + time_list[2]
    return culculated_time

def get_transitiontime_from_gui():
    def submit_time():
        try:
            minute = int(minute_entry.get())
            second = int(second_entry.get())
            base_root.quit()  # GUIを終了する
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for minute and second.")
            return

        global time_list
        time_list = [minute, second]
        base_root.destroy()  # GUIを破棄する

    global time_list
    time_list = []

    # GUIを作成
    base_root = tk.Tk()
    base_root.title("転換時間")
    base_root.geometry("800x150")
    base_root.configure(bg = 'white')

    # ラベルと入力フィールドを作成

    textframe = tk.Frame(base_root,bg = 'white')
    description_label = tk.Label(textframe,text = "転換時間を入力してください。",font=('MS Gothic',30),bg = 'white')
    description_label.pack()
    textframe.pack()

    root = tk.Frame(base_root,bg = 'white')

    minute_label = tk.Label(root, text="分",font=('MS Gothic',30),bg = 'white')
    minute_label.grid(row=1, column=1)
    minute_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    minute_entry.grid(row=1, column=0)

    second_label = tk.Label(root, text="秒",font=('MS Gothic',30),bg = 'white')
    second_label.grid(row=1, column=3)
    second_entry = tk.Entry(root,width=5,font=('MS Gothic',30))
    second_entry.grid(row=1, column=2)
    root.pack()

    # ボタンを作成
    submit_button = tk.Button(root, text="Submit", command=submit_time,font=('MS Gothic',30),bg = 'white')
    submit_button.grid(row=3, columnspan=10)

    # GUIを実行
    base_root.mainloop()

    culculated_time = 60*time_list[0] + time_list[1]
    return culculated_time

if __name__ == "__main__":
    # 関数を呼び出して結果を取得
    result = create_button_gui()
    print(result)
    #この関数を呼び出して時刻を取得
    time_values = get_showcasestarttime_from_gui()
    print("Entered time as list:", time_values)
    transition_time = get_transitiontime_from_gui()
    print('転換時間:',transition_time)

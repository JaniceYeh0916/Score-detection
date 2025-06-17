import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from datetime import datetime
import customtkinter as ctk
from CTkMenuBar import *
import pandas as pd
from PIL import Image, ImageTk
from classification import search_data
from ID_convert import id_detection
from formula_convert import digital_detection
from file_process import write_file, id_contrast


class SampleApp(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)
        # ctk.set_appearance_mode("Light")  # 主題模式：Light/Dark/System
        # ctk.set_default_color_theme("custom_theme.json")  # 主題顏色

        # Set main information
        self.title("Score Detection")
        self.configure(fg_color="white")
        self.iconbitmap("../icon/system_main.ico")

        # Set height & width
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()
        width = 800
        height = 750
        left = int((window_width - width) / 2)
        top = int((window_height - height) / 2)
        self.geometry(f"{width}x{height}+{left}+{0}")
        self.resizable(True, True)

        # Initialize the frame
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self.configure(bg_color="white")
        self._frame.pack()


class StartPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")

        self.menu()

        title = ctk.CTkLabel(self,
                             text="Welcome to Score Detection !",
                             font=("微軟正黑體", 20, "bold"),
                             bg_color="white",
                             text_color='#888')
        title.pack(side="top", fill="x", pady=30)

        grid_frame = ctk.CTkFrame(self, width=700, fg_color="white")
        grid_frame.pack(anchor="center", pady=15, fill="x")

        for i in range(5):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        for i in range(2):
            grid_frame.grid_rowconfigure(i, weight=1, uniform="equal")

        self.file_path_var = ctk.StringVar(value="尚未匯入檔案")
        self.loadStuBtn = ctk.CTkButton(grid_frame,
                                        text="匯入學生名冊",
                                        font=('微軟正黑體', 16),
                                        corner_radius=20,
                                        command=self.update_student,
                                        fg_color="#78c2ad",
                                        text_color="white",
                                        hover_color="#66a593")
        self.loadStuBtn.grid(row=0, column=1, columnspan=1, padx=10, pady=10)

        loadStuLabel = ctk.CTkLabel(grid_frame,
                                    textvariable=self.file_path_var,
                                    font=('微軟正黑體', 16),
                                    text_color='#888')
        loadStuLabel.grid(row=0, column=2, columnspan=3, padx=10, pady=10)

        examTitleLabel = ctk.CTkLabel(grid_frame,
                                  text="輸入測驗標題",
                                  font=('微軟正黑體', 16),
                                  text_color='#888')
        examTitleLabel.grid(row=1, column=1, columnspan=1, padx=10, pady=10)

        self.examTitleEntry = ctk.CTkEntry(grid_frame,
                                       font=("微軟正黑體", 16),
                                       width=200,
                                       text_color='#888')
        self.examTitleEntry.grid(row=1, column=2, columnspan=3, padx=10, pady=10)

        self.scan = ctk.CTkButton(self,
                                  text="開始掃描",
                                  font=('微軟正黑體', 16),
                                  command=self.image_processing,
                                  fg_color="#78c2ad",
                                  text_color="white",
                                  corner_radius=20,
                                  hover_color="#66a593")
        self.scan.pack(pady=10)

        self.enter_list = []
        self.wrong_list = []
        self.id_list = []
        self.name_list = []
        self.score_list = []
        self.test = 0

        self.create_table()

    def menu(self):
        menu = CTkMenuBar(self, bg_color="#78c2ad")

        option1 = menu.add_cascade("介紹",
                                   font=("微軟正黑體", 14, "bold"),
                                   text_color="white",
                                   bg_color="#78c2ad")
        dropdown1 = CustomDropdownMenu(widget=option1)
        dropdown1.add_option(option="操作介紹", command=self.introduction_window)
    
    def introduction_window(self):
        def update_content(step):
            if step == 1:
                rule = "點選「匯入學生名冊」按鈕設定檔案路徑\n輸入當次要填寫的測驗標題"
            elif step == 2:
                rule = "按下「開始掃描」按鈕進入登記程序"
            elif step == 3:
                rule = "鏡頭將會拍攝10張影像\n視窗左上方有拍攝每張影像的倒數秒數\n若中途要停止拍攝請按q鍵"
            elif step == 4:
                rule = "拍攝結束後將自動進入文字辨識流程，結果將會出現在視窗下方"
            elif step == 5:
                rule = "勾選要丟棄的資料，按下「確認輸入」按鈕後系統將會將資料填入excel中"
            else:
                rule = "此時，將會跳出彈跳視窗，詢問接下來的動作\n是：繼續登記當次測驗試卷\n否：回到系統中"

            self.content_label.configure(text=rule, font=("微軟正黑體", 14, "bold"),)

        intro_window = ctk.CTkToplevel(self, fg_color='white')
        intro_window.title("系統操作流程介紹")
        intro_window.geometry("600x500")
        intro_window.configure(bg="white")
        
        titleLabel = ctk.CTkLabel(intro_window, 
                                  text="流程說明", 
                                  font=("微軟正黑體", 20, "bold"),
                                  text_color='#888')
        titleLabel.pack(padx=5, pady=30)

        step_frame = ctk.CTkFrame(intro_window, fg_color='white')
        step_frame.pack(pady=5)

        for i in range(1, 7):
            button = ctk.CTkButton(step_frame, 
                                   text=f"步驟 {i}",
                                   width=30,
                                   corner_radius=20,
                                   font=("微軟正黑體", 14, "bold"),
                                   fg_color="#78c2ad",
                                   text_color="white",
                                   hover_color="#66a593",
                                   command=lambda i=i: update_content(i))
            button.grid(row=0, column=i-1, padx=5)

        self.content_frame = ctk.CTkFrame(intro_window, fg_color='white')
        self.content_frame.pack(pady=5)
        
        self.content_label = ctk.CTkLabel(self.content_frame, 
                                          text="請選擇一個步驟", 
                                          font=("微軟正黑體", 14, "bold"))
        self.content_label.pack(pady=10)
        
        self.content_image = ctk.CTkLabel(self.content_frame, text="")
        self.content_image.pack()

    def manual_input_window(self):
        manual_window = ctk.CTkToplevel(self, fg_color='white')
        manual_window.title("手動輸入分數")
        manual_window.geometry("400x200")
        manual_window.configure(bg="white")

        grid_frame = ctk.CTkFrame(manual_window, fg_color='white')
        grid_frame.pack(anchor="center", pady=15, fill="x")

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=2)

        IDLabel = ctk.CTkLabel(grid_frame, 
                               text="ID：", 
                               font=("微軟正黑體", 14, "bold"),
                               text_color='#888')
        IDLabel.grid(row=0, column=0, padx=5, pady=10)
        IDEntry = ctk.CTkEntry(grid_frame, 
                               font=("微軟正黑體", 14), 
                               text_color='#888')
        IDEntry.grid(row=0, column=1, padx=5, pady=10)

        ScoreLabel = ctk.CTkLabel(grid_frame, 
                                  text="Score：", 
                                  font=("微軟正黑體", 14, "bold"), 
                                  text_color='#888')
        ScoreLabel.grid(row=1, column=0, padx=5, pady=10)
        ScoreEntry = ctk.CTkEntry(grid_frame, 
                                  font=("微軟正黑體", 14), 
                                  text_color='#888')
        ScoreEntry.grid(row=1, column=1, padx=5, pady=10)

        def submit():
            student_id = IDEntry.get().strip()
            score = ScoreEntry.get().strip()

            if not student_id or not score:
                messagebox.showwarning("showwarning", "所有欄位均需填寫！")
                return
            
            result = id_contrast(self.file_path_var.get() , [[student_id,score]])
            _, id, name, score = map(list, zip(*result))
            
            row_index = len(self.id_list)
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.data_frame, fg_color="red", variable=var, text="", width=50)
            checkbox.grid(row=row_index + 1, column=0, padx=5, pady=3)
            self.checkbox_vars.append(var)

            id_label = ctk.CTkLabel(self.data_frame, text=id[0], font=('微軟正黑體', 14), width=100, anchor="center")
            id_label.grid(row=row_index + 1, column=1, padx=5, pady=3)

            id_label = ctk.CTkLabel(self.data_frame, text=name[0], font=('微軟正黑體', 14), width=100, anchor="center")
            id_label.grid(row=row_index + 1, column=2, padx=5, pady=3)

            score_label = ctk.CTkLabel(self.data_frame, text=str(score[0]), font=('微軟正黑體', 14), width=100, anchor="center")
            score_label.grid(row=row_index + 1, column=3, padx=3, pady=3)

            self.id_list = self.id_list + id
            self.name_list = self.name_list + name
            self.score_list = self.score_list + score

            manual_window.destroy()

        submitBtn = ctk.CTkButton(manual_window,
                                      text="提交",
                                      font=("微軟正黑體", 14),
                                      command=submit,
                                      fg_color="#78c2ad",
                                      text_color="white",
                                      corner_radius=20,
                                      hover_color="#66a593")
        submitBtn.pack(pady=10)

    def update_student(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                df = pd.read_excel(file_path)
                df.to_excel(file_path, index=False)
                self.file_path_var.set(file_path)
            except Exception as e:
                messagebox.showwarning("檔案被佔用", "選擇的檔案目前正被其他程式佔用，無法打開。")

    def create_table(self):
        header_frame = ctk.CTkFrame(self, fg_color="white")
        header_frame.pack(pady=30)

        headers = ["Trash", "ID", "Name", "Score"]
        widths = [50, 100, 100, 100]

        for col, (text, width) in enumerate(zip(headers, widths)):
            if text != "Trash":
                header = ctk.CTkLabel(header_frame, 
                                      fg_color="#6cc3d5", 
                                      text=text, 
                                      font=('微軟正黑體', 16),
                                      text_color="white", 
                                      corner_radius=20, 
                                      width=width, 
                                      anchor="center")
            else:
                header = ctk.CTkLabel(header_frame,
                                      fg_color="#FF2D2D",
                                      text=text, 
                                      font=('微軟正黑體', 16),
                                      text_color="white", 
                                      corner_radius=20, 
                                      width=width, 
                                      anchor="center")
            header.grid(row=0, column=col, padx=5, pady=3)

        table_frame = ctk.CTkFrame(self, fg_color="white", width=450)
        table_frame.pack(expand=True, pady=10)

        canvas = ctk.CTkCanvas(table_frame, bg="white", width=450, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=canvas.yview)

        self.data_frame = ctk.CTkFrame(canvas, fg_color="white", width=450)
        self.data_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        window_id = canvas.create_window((0, 0), window=self.data_frame, anchor="nw")

        def _on_mousewheel(event):
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            else:
                canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/Linux
        canvas.bind_all("<Button-4>", _on_mousewheel)    # macOS 滾動上
        canvas.bind_all("<Button-5>", _on_mousewheel)    # macOS 滾動下

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        button_frame = ctk.CTkFrame(self,fg_color="white")
        button_frame.pack()
        enterBtn = ctk.CTkButton(button_frame,
                               fg_color="#6cc3d5",
                               text="確認輸入",
                               font=('微軟正黑體', 16),
                               text_color="white",
                               corner_radius=20,
                               command=self.get_selected,
                               hover_color="#5ca6b5")
        enterBtn.grid(row=0, column=1, padx=5, pady=5)
        manualBtn = ctk.CTkButton(button_frame,
                               fg_color="#6cc3d5",
                               text="手動輸入",
                               font=('微軟正黑體', 16),
                               text_color="white",
                               corner_radius=20,
                               command=self.manual_input_window,
                               hover_color="#5ca6b5")
        manualBtn.grid(row=0, column=2, padx=5, pady=5)

    def insert_data(self):
        self.checkbox_vars = []
        for i in range(len(self.id_list)):
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.data_frame, fg_color="red", variable=var, text="", width=50)
            checkbox.grid(row=i + 1, column=0, padx=5, pady=3)
            self.checkbox_vars.append(var)

            id_label = ctk.CTkLabel(self.data_frame, text=self.id_list[i], font=('微軟正黑體', 14), width=100, anchor="center")
            id_label.grid(row=i + 1, column=1, padx=5, pady=3)

            id_label = ctk.CTkLabel(self.data_frame, text=self.name_list[i], font=('微軟正黑體', 14), width=100, anchor="center")
            id_label.grid(row=i + 1, column=2, padx=5, pady=3)

            score_label = ctk.CTkLabel(self.data_frame, text=str(self.score_list[i]), font=('微軟正黑體', 14), width=100, anchor="center")
            score_label.grid(row=i + 1, column=3, padx=3, pady=3)

    def get_selected(self):
        enter_list = []
        wrong_list = []
        for i in range(len(self.id_list)):
            if self.checkbox_vars[i].get():
                wrong_list.append((self.id_list[i], self.name_list[i], self.score_list[i]))
            else:
                if self.id_list[i] != "未偵測" and self.score_list[i] != -1:
                    enter_list.append((self.id_list[i], self.score_list[i]))
                else:
                    messagebox.showwarning('Warning', '無法填入未偵測到的資料!\n系統將自動跳過')

        self.enter_list = enter_list
        self.wrong_list = wrong_list

        if self.enter_list == []:
            choice = messagebox.askyesno('Warning', '未偵測到分數\n\n是否要手動輸入')

            if choice == True:
                print("手動輸入")
                self.manual_input_window()
            
        else:
            exam_title = self.examTitleEntry.get().strip()
            isDate = exam_title.find("/")
            if isDate != -1:
                month = exam_title[0:isDate]
                day = exam_title[isDate+1:]
                if month.isdigit() and day.isdigit():
                    exam_title = datetime.strptime(f"{datetime.now().year}/{self.examTitleEntry.get().strip()}", "%Y/%m/%d")

            data = write_file(self.file_path_var.get(), enter_list, exam_title)

        self.scan.configure(state=ctk.NORMAL)
        self.loadStuBtn.configure(state=ctk.NORMAL)

        self.enter_list = []
        self.id_list = []
        self.name_list = []
        self.score_list = []

        choice = messagebox.askyesno('Information', '輸入完成\n是否要繼續掃描？')
        if choice == True:
            self.image_processing()
        else:
            self.wrong_list = []

    def image_processing(self):
        self.scan.configure(state=ctk.DISABLED)
        self.loadStuBtn.configure(state=ctk.DISABLED)

        subprocess.run(['python', 'cache_img.py'])
        search_data()

        id = id_detection()
        score = digital_detection()
        print(id)
        print(score)
        
        enter_list = []
        for i in range(len(id)):
            enter_list.append([id[i], score[i]])
        result = id_contrast(self.file_path_var.get() , enter_list)
        _, id, name, score = map(list, zip(*result))
        
        self.id_list = ["未偵測" if x == "-1" else x for x in id]
        self.name_list = ["未偵測" if x == "-1" else x for x in name]
        self.score_list = score

        self.insert_data()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()

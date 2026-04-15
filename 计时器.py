import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime
import threading
import sys
from speak import speak_chinese, speak_english

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("倒计时器")
        
        # 设置窗口大小和位置居中
        window_width = 600
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 设置窗口背景颜色为白色
        self.root.configure(bg='#FFFFFF')
        
        # 设置字体
        self.title_font = ("Arial", 28, "bold")
        self.clock_font = ("Arial", 70, "bold")
        self.countdown_font = ("Arial", 70, "bold")
        self.button_font = ("Arial", 14)
        self.label_font = ("Arial", 16)
        
        # 倒计时变量
        self.remaining_seconds = 0
        self.is_running = False
        self.is_paused = False
        self.pause_time = 0
        self.total_seconds = 0
        self.already_announced_15min = False  # 标记15分钟提示是否已播报
        
        # 创建界面
        self.create_widgets()
        
        # 启动时间更新线程
        self.update_time()
        self.update_real_time()
    
    def create_widgets(self):
        # 主容器
        main_container = tk.Frame(self.root, bg='#FFFFFF')
        main_container.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        # 现实时间显示区域
        time_frame = tk.Frame(main_container, bg='#F8F9FA', relief=tk.RAISED, borderwidth=2)
        time_frame.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        tk.Label(time_frame, text="当前时间", font=("Arial", 16),
                bg='#F8F9FA', fg='#6C757D').pack(pady=(5, 2))
        
        self.real_time_label = tk.Label(time_frame, text="", font=self.clock_font, 
                                       bg='#F8F9FA', fg='#007BFF')
        self.real_time_label.pack(pady=(0, 5))
        
        # 当前日期标签
        self.date_label = tk.Label(time_frame, text="", font=("Arial", 14),
                                   bg='#F8F9FA', fg='#495057')
        self.date_label.pack(pady=(0, 5))
        
        # 倒计时显示区域
        countdown_frame = tk.Frame(main_container, bg='#F8F9FA', relief=tk.GROOVE, borderwidth=3)
        countdown_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(countdown_frame, text="倒计时剩余时间", font=("Arial", 18),
                bg='#F8F9FA', fg='#495057').pack(pady=(10, 5))
        
        self.time_display = tk.Label(countdown_frame, text="05:00", font=self.countdown_font, 
                                     bg='#F8F9FA', fg='#28A745')
        self.time_display.pack(expand=True)
        
        # 输入和控制区域
        control_frame = tk.Frame(main_container, bg='#FFFFFF')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 输入区域
        input_frame = tk.Frame(control_frame, bg='#FFFFFF')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(input_frame, text="设置倒计时时间（分钟）:", font=self.label_font, 
                bg='#FFFFFF', fg='#495057').pack(side=tk.LEFT, padx=(0, 10))
        
        self.time_entry = tk.Entry(input_frame, font=self.button_font, width=12,
                                   justify='center', bg='#FFFFFF', fg='#495057',
                                   relief=tk.SOLID, borderwidth=1)
        self.time_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.time_entry.insert(0, "5")
        
        # 控制按钮区域
        button_frame = tk.Frame(control_frame, bg='#FFFFFF')
        button_frame.pack(fill=tk.X)
        
        # 按钮容器，使按钮居中
        button_container = tk.Frame(button_frame, bg='#FFFFFF')
        button_container.pack()
        
        self.start_button = tk.Button(button_container, text="开始倒计时", font=self.button_font, 
                                      bg='#28A745', fg='white', padx=20, pady=8,
                                      command=self.start_timer, activebackground='#218838',
                                      activeforeground='white', relief=tk.RAISED, borderwidth=1)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(button_container, text="暂停", font=self.button_font, 
                                      bg='#FFC107', fg='white', padx=20, pady=8,
                                      command=self.pause_timer, state=tk.DISABLED, 
                                      activebackground='#E0A800', activeforeground='white',
                                      relief=tk.RAISED, borderwidth=1)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(button_container, text="重置", font=self.button_font, 
                                      bg='#DC3545', fg='white', padx=20, pady=8,
                                      command=self.reset_timer, activebackground='#C82333',
                                      activeforeground='white', relief=tk.RAISED, borderwidth=1)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", 
                       background='#28A745',
                       troughcolor='#E9ECEF',
                       bordercolor='#DEE2E6',
                       lightcolor='#28A745',
                       darkcolor='#28A745')
        
        self.progress_bar = ttk.Progressbar(main_container, length=500,
                                           style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态标签
        self.status_label = tk.Label(main_container, text="准备就绪，请输入倒计时时间", 
                                     font=("Arial", 12, "italic"),
                                     bg='#FFFFFF', fg='#6C757D')
        self.status_label.pack()
    
    def update_real_time(self):
        """更新现实时间和日期"""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y年%m月%d日 %A")
        
        # 将英文星期转换为中文
        weekday_map = {
            "Monday": "星期一",
            "Tuesday": "星期二",
            "Wednesday": "星期三",
            "Thursday": "星期四",
            "Friday": "星期五",
            "Saturday": "星期六",
            "Sunday": "星期日"
        }
        
        english_weekday = now.strftime("%A")
        chinese_weekday = weekday_map.get(english_weekday, english_weekday)
        current_date = now.strftime(f"%Y年%m月%d日 {chinese_weekday}")
        
        self.real_time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        
        # 每秒更新一次
        self.root.after(1000, self.update_real_time)
    
    def start_timer(self):
        if not self.is_running:
            try:
                minutes = int(self.time_entry.get())
                if minutes <= 0:
                    messagebox.showerror("错误", "请输入大于0的分钟数")
                    return
                if minutes > 999:
                    messagebox.showerror("错误", "倒计时时间过长，请输入小于1000的分钟数")
                    return
                
                self.remaining_seconds = minutes * 60
                self.total_seconds = self.remaining_seconds
                self.is_running = True
                self.is_paused = False
                self.already_announced_15min = False  # 重置15分钟提示标记
                
                # 更新按钮状态
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="暂停")
                self.time_entry.config(state=tk.DISABLED)
                
                # 更新状态
                self.status_label.config(text="倒计时进行中...")
                
                # 更新倒计时显示
                minutes_display = int(self.remaining_seconds // 60)
                seconds_display = int(self.remaining_seconds % 60)
                time_str = f"{minutes_display:02d}:{seconds_display:02d}"
                self.time_display.config(text=time_str, fg='#28A745')
                
                # 初始化进度条为满值，倒计时过程中逐渐减少
                self.progress_bar['value'] = 100
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
    
    def pause_timer(self):
        if self.is_running:
            if not self.is_paused:
                self.is_paused = True
                self.pause_button.config(text="继续")
                self.status_label.config(text="已暂停")
                self.pause_time = time.time()
                # 暂停时改变倒计时颜色
                self.time_display.config(fg='#FFC107')
            else:
                self.is_paused = False
                self.pause_button.config(text="暂停")
                self.status_label.config(text="倒计时进行中...")
                # 调整剩余时间，减去暂停期间的时间
                pause_duration = time.time() - self.pause_time
                self.remaining_seconds -= pause_duration
                # 恢复颜色
                if self.remaining_seconds > 60:
                    self.time_display.config(fg='#28A745')
                else:
                    self.time_display.config(fg='#DC3545')
    
    def reset_timer(self):
        self.is_running = False
        self.is_paused = False
        self.remaining_seconds = 0
        self.already_announced_15min = False  # 重置15分钟提示标记
        
        # 重置按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="暂停")
        self.time_entry.config(state=tk.NORMAL)
        
        # 重置显示
        self.time_display.config(text="05:00", fg='#28A745')
        self.status_label.config(text="已重置，请输入新的倒计时时间")
        self.progress_bar['value'] = 100
        
        # 重置输入框为默认值
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "5")
    
    def update_time(self):
        if self.is_running and not self.is_paused:
            # 检查是否需要播报15分钟提示
            if not self.already_announced_15min and self.remaining_seconds <= 900 and self.remaining_seconds > 895:
                speak_chinese("距考试结束还有十五分钟！", 200)
                self.already_announced_15min = True
            
            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
                
                # 计算分钟和秒
                minutes = int(self.remaining_seconds // 60)
                seconds = int(self.remaining_seconds % 60)
                
                # 更新显示
                time_str = f"{minutes:02d}:{seconds:02d}"
                self.time_display.config(text=time_str)
                
                # 更新进度条
                progress_value = 100 * self.remaining_seconds / self.total_seconds
                self.progress_bar['value'] = progress_value
                
                # 当时间少于1分钟时改变颜色
                if self.remaining_seconds < 60:
                    self.time_display.config(fg='#DC3545')
                else:
                    self.time_display.config(fg='#28A745')
                
                # 时间到
                if self.remaining_seconds <= 0:
                    self.time_display.config(text="00:00", fg='#DC3545')
                    self.status_label.config(text="时间到！")
                    speak_chinese("考试结束！请考生停止答卷！", 200)
                    self.progress_bar['value'] = 0
                    self.is_running = False
                    self.start_button.config(state=tk.NORMAL)
                    self.pause_button.config(state=tk.DISABLED)
                    self.time_entry.config(state=tk.NORMAL)
                    self.already_announced_15min = False  # 重置15分钟提示标记
                    
                    # 播放提示音（在控制台输出）
                    print("\a" * 3)
                    
                    # 时间到提示窗口
                    self.root.attributes('-topmost', True)
                    messagebox.showinfo("时间到", "倒计时结束！")
                    self.root.attributes('-topmost', False)
        
        # 每秒调用一次
        self.root.after(1000, self.update_time)

def main():
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
from tkinter import *
from tkinter import messagebox
import os
import imageio
import threading
import time
from PIL import Image, ImageTk
import cv2
from base_logger import getLogger
from win32api import GetSystemMetrics
import math


class VideoSelect:

    class VideoFrame:
        def __init__(self, root, max_width, max_height, filename: str='____.mp4', x: int=1, y: int=1):
            self.x, self.y = x + 1, y + 1
            self.max_width, self.max_height = max_width, max_height
            self.root = root
            self.filename = filename
            self.var_filename = StringVar()
            self.var_filename.set(self.filename)

            self.frame = LabelFrame(self.root, text=self.var_filename.get())
            # Label(self.frame, textvariable=self.var_filename).pack()
            self.initIamge = ImageTk.PhotoImage(Image.open('1.png'))
            self.panel = Label(self.frame, image=self.initIamge)
            self.panel.pack()
            self.thread = None

            self.will_exit = False

            # self.reader = imageio.get_reader(self.filename)

            self.toolbox = None
            # 单个的线程锁
            self.lock = threading.Lock()

            self.tool_s1 = None

            self.start_tool_thread()

        def toolbox_mainloop(self):
            self.toolbox.mainloop()

        def grid(self):
            # self.frame.grid(row=self.y, column=self.x)
            pass

        def start_pay_thread(self):
            if self.thread is not None:
                return
            self.thread = threading.Thread(target=self.play_thread)
            self.thread.setDaemon(True)
            self.thread.start()

        def start_tool_thread(self):
            retry = 0
            # 尝试5s，5s内没有初始化窗口就失败
            while retry <= 5000:
                if self.toolbox is None:
                    time.sleep(0.001)
                    retry += 1
                    continue
                t = threading.Thread(target=self.toolbox_mainloop)
                t.setDaemon(True)
                t.start()

        def play_thread(self):
            cap = cv2.VideoCapture(self.filename)
            pause = False
            ret, frame = cap.read()
            if ret is False:
                self.thread = None
                # 视频读取失败
                return

            width = int(cap.get(3))
            height = int(cap.get(4))
            # 帧率
            fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
            # 视频总帧数
            total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # 计算一下30s的跳转多少帧
            frame_count_30s = 30 * fps
            # 当前要读取的帧号。之前已经读取过一遍了
            frame_cnt = 1
            if width >= height:
                width_target = self.max_width
                height_target = self.max_height * height / width
            else:
                height_target = self.max_height
                width_target = self.max_width * width / height
            width_target, height_target = int(width_target), int(height_target)
            height_target += 48

            print('''########{filename}########
total frames count: {total}
fps per second: {fps}
'''.format(total=total_frame, fps=fps, filename=self.filename))

            # 在这里启动toolbox
            self.toolbox = Toplevel(self.root)
            self.toolbox.title("视频操作[%s]" % self.filename)

            self.tool_s1 = Scale(self.toolbox, from_=0, to=total_frame, orient=HORIZONTAL)
            self.tool_s1.pack()

            while cap.isOpened():
                cv2.namedWindow(self.filename, 0)
                # cv2.resizeWindow(self.filename, self.max_width, self.max_height)
                # cv2.resizeWindow(self.filename, width, height)
                cv2.resizeWindow(self.filename, width_target, height_target)
                # cv2.resizeWindow(self.filename, 1080 // 8, 720 // 8)
                cv2.moveWindow(self.filename, (self.x - 1) * self.max_width, (self.y - 1) * self.max_height)

                if not pause:
                    ret, frame = cap.read()
                cv2.imshow(self.filename, frame)
                k = cv2.waitKey(int(1000/fps))
                # q键退出
                if k & 0xff == ord('q'):
                    break
                if k & 0xff == ord('p'):
                    pause = not pause
                if self.will_exit is True:
                    break
            self.thread = None

    def __init__(self, filelist: list, root=None):
        self.root = root
        self.filelist = filelist
        self.screen_size = [GetSystemMetrics(0), GetSystemMetrics(1)]
        if self.root is None:
            self.root = Tk()
        split_list = [
            [], [1, 1], [2, 1], [3, 1], [2, 2], [3, 2], [3, 2], [3, 3], [3, 3], [3, 3],
        ]
        if len(filelist) > 9:
            messagebox.showerror('错误', '视频数量过多！别太贪心...')
            sys.exit(len(filelist))
        if len(filelist) == 0:
            messagebox.showerror('错误', '未打开视频！')
            sys.exit(1)
        self.width, self.height = split_list[len(filelist)]

        logger.info(str(split_list[len(filelist)]))

        self.title = '素材检录 - Lance Liang'
        self.root.title(self.title)
        # self.root.attributes('-fullscreen', 1)
        # self.root.attributes('-topmost', 0)

        # 初始化Frame
        self.video_frames = \
            [[self.VideoFrame(self.root, self.screen_size[0] // self.width, self.screen_size[1] // self.height,
                              filename=self.filelist[j * self.height + i], x=j, y=i) for i in range(self.height)]
             for j in range(self.width)]

        for x in range(len(self.video_frames)):
            for y in range(len(self.video_frames[x])):
                video_frame = self.video_frames[x][y]
                # video_frame.frame.grid(row=y, column=x)
                video_frame.grid()

    def mainloop(self):
        for x in range(len(self.video_frames)):
            for y in range(len(self.video_frames[x])):
                video_frame = self.video_frames[x][y]
                video_frame.start_pay_thread()
        self.root.mainloop()


logger = getLogger(__name__)


if __name__ == '__main__':
    _list = []
    for _file in os.listdir('.'):
        if _file.lower().endswith('.mp4'):
            _list.append(_file)
    logger.info('Open files: %s' % str(_list))
    _video = VideoSelect(_list)
    _video.mainloop()

from tkinter import *
import os
import imageio


class VideoSelect:

    class VideoFrame:
        def __init__(self, root, filename: str='____.mp4'):
            self.root = root
            self.filename = filename
            self.var_filename = StringVar()
            self.var_filename.set(self.filename)

            self.frame = LabelFrame(self.root, text=self.var_filename.get())
            Label(self.frame, textvariable=self.var_filename).pack()

    def __init__(self, filelist: list, root=None, width=1, height=1):
        self.root = root
        self.filelist = filelist
        if self.root is None:
            self.root = Tk()
        self.width, self.height = width, height

        self.title = '素材检录 - Lance Liang'
        self.root.title(self.title)

        # 初始化Frame
        self.video_frames = \
            [[self.VideoFrame(self.root, filename=self.filelist[j * self.height + i]) for i in range(self.height)]
             for j in range(self.width)]

        for x in self.video_frames:
            for y in x:
                y.frame.pack()

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    _list = []
    for _file in os.listdir('.'):
        if _file.lower().endswith('.mp4'):
            _list.append(_file)
    _video = VideoSelect(_list)
    _video.mainloop()

import os

import pyautogui
import win32con
import win32gui

# нужно ставить pywin32
import win32process

dt_process = None
chromedriver_main_process = None


def show_process():
    """Поиск окна программы в Windows, отображение его и активация, используется для чата"""
    global dt_process, chromedriver_main_process
    toplist = []
    winlist = []

    def enum_callback(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_callback, toplist)
    if dt_process is None or chromedriver_main_process is None:
        for hwnd, title in winlist:
            if 'DTMainWindow' in title:
                dt_process = hwnd
            if 'chromedriver' in title:
                chromedriver_main_process = hwnd
    win32gui.ShowWindow(dt_process, win32con.SW_NORMAL)
    pyautogui.press('alt')
    win32gui.SetForegroundWindow(dt_process)


def show_window(func):
    def show(*args, **kwargs):
        show_process()
        func(*args, **kwargs)
        show_process()

    return show


def hide_chrome_console():
    show_process()
    if chromedriver_main_process:
        win32gui.ShowWindow(chromedriver_main_process, win32con.SW_HIDE)


def close_all_chromedriver():
    import psutil

    chromedrivers = [item for item in psutil.process_iter() if item.name() == 'chromedriver.exe']
    for process in chromedrivers:
        process.terminate()

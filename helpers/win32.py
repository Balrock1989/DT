import pyautogui
import win32con
import win32gui
# нужно ставить pywin32 pip install pywin32
import psutil
#pip install psutil  (Необходма установка BuildTools C++)



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
    """Декоратор для функций который выводит окно программы на первый план до выполнения и после"""

    def show(*args, **kwargs):
        show_process()
        func(*args, **kwargs)
        show_process()

    return show


def hide_chrome_console():
    """Скрываем консоль от Chromedriver.exe при запуске приложения из exe"""
    show_process()
    if chromedriver_main_process:
        win32gui.ShowWindow(chromedriver_main_process, win32con.SW_HIDE)


def close_all_chromedriver():
    """При запуске программы закрывает все существующие процессы chromedriver.exe в windows"""

    chromedrivers = [item for item in psutil.process_iter() if item.name() == 'chromedriver.exe']
    for process in chromedrivers:
        process.terminate()


def hide_all_chromedriver():
    toplist = []
    winlist = []

    def enum_callback(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_callback, toplist)
    chromedrivers = [hwnd for hwnd, title in winlist if 'chromedriver' in title]
    for process in chromedrivers:
        win32gui.ShowWindow(process, win32con.SW_HIDE)

from PyQt5.QtCore import QThread
from pynput import keyboard

class GlobalHotKey(QThread):
    """Отдельный поток для глобального хоткея"""

    def __init__(self, mainwindow):
        super(GlobalHotKey, self).__init__()
        self.mainwindow = mainwindow

    def run(self):
        hotkey(self.mainwindow)


def hotkey(gui):
    """Слушаем в отдельном потоке глобальный хоткей"""
    COMBO_1 = [keyboard.Key.tab, keyboard.KeyCode(char='1')]
    COMBO_2 = [keyboard.Key.tab, keyboard.KeyCode(char='2')]
    COMBO_3 = [keyboard.Key.tab, keyboard.KeyCode(char='3')]
    COMBO_4 = [keyboard.Key.tab, keyboard.KeyCode(char='4')]
    current = set()

    def browser_checker(func):
        def check(*args, **kwargs):
            if gui.web_thread:
                gui.web_thread.web.exit = False
                func(*args, **kwargs)
            else:
                gui.chat_print_signal.emit('Браузер закрыт')
        return check

    @browser_checker
    def execute_tab1():
        try:
            gui.web_thread.web.start_data = gui.date_start.toPlainText()
            gui.web_thread.web.end_data = gui.date_end.toPlainText()
            gui.web_thread.web.url = gui.url.toPlainText()
            gui.web_thread.web.add_banner()
        except Exception as exc:
            gui.log.error('Возникла ошибка при загрузке баннеров')
            gui.log.error(exc)
        gui.log.info('\n *** Нажата комбинация клавиш: tab + 1 \n *** Должна вызваться функция :)')

    @browser_checker
    def execute_tab2():
        try:
            gui.web_thread.web.parser()
        except Exception as exc:
            gui.log.error('Возникла ошибка при выгрузке акций')
            gui.log.error(exc)
        gui.log.info('\n *** Нажата комбинация клавиш: tab + 2 \n *** Должна вызваться функция :)')

    @browser_checker
    def execute_tab3():
        try:
            gui.web_thread.web.download_banners()
        except Exception as exc:
            gui.log.error('Возникла ошибка при выгрузке баннеров')
            gui.log.error(exc)
        gui.log.info('\n *** Нажата комбинация клавиш: tab + 3 \n *** Должна вызваться функция :)')

    @browser_checker
    def execute_tab4():
        try:
            gui.web_thread.web.add_actions()
        except Exception as exc:
            gui.log.error('Возникла ошибка при загрузке акций')
            gui.log.error(exc)
        gui.log.info('\n *** Нажата комбинация клавиш: tab + 4 \n *** Должна вызваться функция :)')

    def get_key_name(key):
        """Определяем имя нажатой клавишы"""
        if isinstance(key, keyboard.KeyCode):
            return key.char
        else:
            return str(key)

    def on_press(key):
        """Проверка на комбинацию"""
        # key_name = get_key_name(key)
        if key == keyboard.Key.esc:
            # gui.log.info(f'--- Нажата клавиша: {key_name}')
            gui.set_exit_signal.emit()
        elif key == keyboard.Key.tab:
            current.add(key)
            # gui.log.info(f'--- Нажата клавиша: {key_name}')
        # elif (key == keyboard.KeyCode.from_char('1')) or (key == keyboard.KeyCode.from_char('2')) or \
        #         (key == keyboard.KeyCode.from_char('3')) or (key == keyboard.KeyCode.from_char('4')):
        #     gui.log.info(f'--- Нажата клавиша: {key_name}')
        else:
            # gui.log.info(f'Информационно. Вы нажали: {key_name}')
            current.clear()
        if any([key in COMBO_1 + COMBO_2 + COMBO_3 + COMBO_4]):
            current.add(key)
        if all(key in current for key in COMBO_1):
            execute_tab1()
            current.clear()
        elif all(key in current for key in COMBO_2):
            execute_tab2()
            current.clear()
        elif all(key in current for key in COMBO_3):
            execute_tab3()
            current.clear()
        elif all(key in current for key in COMBO_4):
            execute_tab4()
            current.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

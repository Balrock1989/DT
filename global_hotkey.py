from pynput import keyboard


def hotkey(gui):
    """Слушаем в отдельном потоке глобальный хоткей"""
    COMBO_1 = [keyboard.Key.space, keyboard.KeyCode(char='1')]
    COMBO_2 = [keyboard.Key.space, keyboard.KeyCode(char='2')]
    COMBO_3 = [keyboard.Key.space, keyboard.KeyCode(char='3')]
    COMBO_4 = [keyboard.Key.space, keyboard.KeyCode(char='4')]
    current = set()

    def execute_space1():
        gui.web_thread.web.exit = False
        gui.web_thread.web.start_data = gui.date_start.toPlainText()
        gui.web_thread.web.end_data = gui.date_end.toPlainText()
        gui.web_thread.web.url = gui.url.toPlainText()
        gui.web_thread.web.add_banner(gui=gui)
        gui.log.info('\n *** Нажата комбинация клавиш: space + 1 \n *** Должна вызваться функция :)')

    def execute_space2():
        gui.web_thread.web.parser(gui=gui) if not gui.web_thread.web.actions_data\
            else gui.web_thread.web.add_actions(gui=gui)
        gui.log.info('\n *** Нажата комбинация клавиш: space + 2 \n *** Должна вызваться функция :)')

    def execute_space3():
        gui.web_thread.web.download_banners(gui=gui)
        gui.log.info('\n *** Нажата комбинация клавиш: space + 3 \n *** Должна вызваться функция :)')

    def execute_space4():
        gui.log.info('\n *** Нажата комбинация клавиш: space + 4 \n *** Должна вызваться функция :)')

    def get_key_name(key):
        """Определяем имя нажатой клавишы"""
        if isinstance(key, keyboard.KeyCode):
            return key.char
        else:
            return str(key)

    def on_press(key):
        """Проверка на комбинацию"""
        key_name = get_key_name(key)
        if key == keyboard.Key.esc:
            gui.log.info(f'--- Нажата клавиша: {key_name}')
            try:
                gui.web_thread.web.exit = True
            except AttributeError:
                gui.log.exception('Объект web_thread еще не был создан')
            try:
                gui.sizer.exit = True
            except AttributeError:
                gui.log.exception('Объект sizer еще не был создан')
        elif key == keyboard.Key.space:
            current.add(key)
            gui.log.info(f'--- Нажата клавиша: {key_name}')
        elif (key == keyboard.KeyCode.from_char('1')) or (key == keyboard.KeyCode.from_char('2')) or \
                (key == keyboard.KeyCode.from_char('3')) or (key == keyboard.KeyCode.from_char('4')):
            gui.log.info(f'--- Нажата клавиша: {key_name}')
        else:
            gui.log.info(f'Информационно. Вы нажали: {key_name}')
            current.clear()
        if any([key in COMBO_1 + COMBO_2 + COMBO_3 + COMBO_4]):
            current.add(key)
        if all(key in current for key in COMBO_1):
            execute_space1()
            current.clear()
        elif all(key in current for key in COMBO_2):
            execute_space2()
            current.clear()
        elif all(key in current for key in COMBO_3):
            execute_space3()
            current.clear()
        elif all(key in current for key in COMBO_4):
            execute_space4()
            current.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

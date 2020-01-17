from pynput import keyboard


def hotkey(window):
    """Слушаем в отдельном потоке глобальный хоткей"""
    COMBO_1 = [keyboard.Key.space, keyboard.KeyCode(char='1')]
    COMBO_2 = [keyboard.Key.space, keyboard.KeyCode(char='2')]
    COMBO_3 = [keyboard.Key.space, keyboard.KeyCode(char='3')]
    COMBO_4 = [keyboard.Key.space, keyboard.KeyCode(char='4')]
    current = set()

    def execute_space1():
        window.web.exit = False
        window.web.start_data = window.date_start.toPlainText()
        window.web.end_data = window.date_end.toPlainText()
        window.web.url = window.url.toPlainText()
        window.web.add_banner(gui=window)
        window.log.info('\n *** Нажата комбинация клавиш: space + 1 \n *** Должна вызваться функция :)')

    def execute_space2():
        window.web.parser(gui=window) if not window.web.actions_data else window.web.add_actions(gui=window)
        window.log.info('\n *** Нажата комбинация клавиш: space + 2 \n *** Должна вызваться функция :)')

    def execute_space3():
        window.web.download_banners(gui=window)
        window.log.info('\n *** Нажата комбинация клавиш: space + 3 \n *** Должна вызваться функция :)')

    def execute_space4():
        window.web.parser_sephora(gui=window)
        window.log.info('\n *** Нажата комбинация клавиш: space + 4 \n *** Должна вызваться функция :)')

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
            window.log.info(f'--- Нажата клавиша: {key_name}')
            window.driver.exit = True
            window.sizer.exit = True
        elif key == keyboard.Key.space:
            current.add(key)
            window.log.info(f'--- Нажата клавиша: {key_name}')
        elif (key == keyboard.KeyCode.from_char('1')) or (key == keyboard.KeyCode.from_char('2')) or \
                (key == keyboard.KeyCode.from_char('3')) or (key == keyboard.KeyCode.from_char('4')):
            window.log.info(f'--- Нажата клавиша: {key_name}')
        else:
            window.log.info(f'Информационно. Вы нажали: {key_name}')
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

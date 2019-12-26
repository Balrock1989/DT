from pynput import keyboard


def show(window):
    COMBINATIONS_1 = [
        {keyboard.Key.shift_l, keyboard.KeyCode(char='!')},
        {keyboard.Key.shift_l, keyboard.Key.f1},
    ]

    COMBINATIONS_2 = [
        {keyboard.Key.shift_l, keyboard.KeyCode(char='@')},
        {keyboard.Key.shift_l, keyboard.KeyCode(char='"')},
        {keyboard.Key.shift_l, keyboard.Key.f2},
    ]

    current = set()

    def executeShiftF1():
        window.web.exit = False
        window.web.start_data = window.date_start.toPlainText()
        window.web.end_data = window.date_end.toPlainText()
        window.web.url = window.url.toPlainText()
        window.web.add_banner(gui=window)
        print("\n *** Нажата комбинация клавиш: Shift + F1 \n *** Должна вызваться функция :)")

    def executeShiftF2():
        window.web.add_actions(gui=window)
        window.web.parser(gui=window) if not window.web.actions_data else window.web.add_actions(gui=window)
        # print("\n *** Нажата комбинация клавиш: Shift + F2 \n *** Должна вызваться функция :)")

    def get_key_name(key):
        if isinstance(key, keyboard.KeyCode):
            return key.char
        else:
            return str(key)

    def on_press(key):
        key_name = get_key_name(key)
        if key == keyboard.Key.esc:
            print('--- Нажата клавиша: {}'.format(key_name))
            window.driver.exit = True
            window.sizer.exit = True
        elif key == keyboard.Key.shift_l:
            print('--- Нажата клавиша: {}'.format(key_name))

        elif (key == keyboard.KeyCode.from_char('f1')) or (key == keyboard.KeyCode.from_char('!')) \
                or (key == keyboard.KeyCode.from_char('@')) or (key == keyboard.KeyCode.from_char('f2')) \
                or (key == keyboard.KeyCode.from_char('"')):
            print('--- Нажата клавиша: {}'.format(key_name))
        else:
            print('Информационно. Вы нажали: {}'.format(key_name))
            current.clear()
        if any([key in COMBO for COMBO in COMBINATIONS_1]):
            current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS_1):
            executeShiftF1()
            current.clear()
        if any([key in COMBO for COMBO in COMBINATIONS_2]):
            current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS_2):
            executeShiftF2()
            current.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


from pynput import keyboard


def show(window):
    COMBINATIONS = [
        {keyboard.Key.shift_l, keyboard.KeyCode(char='!')},
        {keyboard.Key.shift_l, keyboard.Key.f1},
        {keyboard.Key.shift_l, keyboard.KeyCode(char='1')},
        {keyboard.Key.shift_r, keyboard.KeyCode(char='!')},
        {keyboard.Key.shift_r, keyboard.Key.f1},
        {keyboard.Key.shift_r, keyboard.KeyCode(char='1')}
    ]

    current = set()

    def executeShiftF1():
        window.add_banner()
        print("\n *** Нажата комбинация клавиш: Shift + F1 \n *** Должна вызваться функция :)")

    def get_key_name(key):
        """ Функцию get_key_name(), будет проверять тип ключа.
        Для нормального ключа он вернет key.char,
        у которого не будет дополнительных одинарных кавычек.
        Для других ключей он напечатает имя ключа (например, Key.cmd, Key.alt, Key.ctrl ...)
        """
        if isinstance(key, keyboard.KeyCode):
            return key.char
        else:
            return str(key)

    def on_press(key):
        key_name = get_key_name(key)

        if key == keyboard.Key.esc:
            print('--- Нажата клавиша: {}'.format(key_name))
            window.driver.exit = True
        elif key == keyboard.Key.shift_l:
            print('--- Нажата клавиша: {}'.format(key_name))

        elif (key == keyboard.KeyCode.from_char('f1')) or \
                (key == keyboard.KeyCode.from_char('1')):
            print('--- Нажата клавиша: {}'.format(key_name))

        else:
            print('Информационно. Вы нажали: {}'.format(key_name))
            current.clear()
        if any([key in COMBO for COMBO in COMBINATIONS]):
            current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            executeShiftF1()
            current.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


import os
import shutil

from PIL import Image


class Resizer:
    def __init__(self):
        self.basewidth = 0
        self.baseheight = 0
        self.w = 0
        self.h = 0
        self.exit = False
        self.count = ''

    def resize_image(self, gui, path, end_data):
        """Изменение размера изображений"""
        path = os.path.normpath(path)
        if path == '.' or not gui.path_window.toPlainText():
            gui.log.error('Необходимо указать путь до папки')
            gui.chat_print('Необходимо указать путь до папки')
            return
        for root, dirs, files in os.walk(path):
            gui.command_window.append(f'Всего папок {len(dirs)}')
            for i, file in enumerate(files):
                path = os.path.join(root, file)
                self.count = f'({i}/{len(files)})'
                gui.chat_print(f'всего файлов в текущей папке: {len(files)}  Всего обработано: {i}')
                try:
                    im = Image.open(path)
                except OSError:
                    gui.log.exception(f'SKIPPED Этот файл не картинка {path}')
                    gui.chat_print(f'SKIPPED "Этот файл не картинка {path}')
                    continue
                self.w, self.h = im.size
                gui.chat_print(f'мы работаем с файлом Ширина: {self.w} Высота: {self.h}')
                if self.w >= self.h:
                    gui.show_dialog_width()
                    if self.exit:
                        return
                    ratio = (self.basewidth / float(self.w))
                    height = int((float(self.h) * float(ratio)))
                    im = im.resize((self.basewidth, height), Image.LANCZOS)
                    im.save(path)
                    new_name = str(im.size[0]) + '__' + str(im.size[1]) + 'xxxxx' + str(end_data) + '_____' + str(
                        i) + path[-4:]
                    gui.chat_print(f'Новый размер баннера: {im.size[0]}x{im.size[1]}')
                    gui.chat_print('#' * 40)
                else:
                    gui.show_dialog_heigth()
                    if self.exit:
                        return
                    ratio = (self.baseheight / float(self.h))
                    width = int((float(self.w) * float(ratio)))
                    im = im.resize((width, self.baseheight), Image.LANCZOS)
                    im.save(path)
                    new_name = str(im.size[0]) + '__' + str(im.size[1]) + 'xxxxx' + str(end_data) + '_____' + str(
                        i) + path[-4:]
                    gui.chat_print(f'Новый размер баннера: {im.size[0]}x{im.size[1]}')
                    gui.chat_print('#' * 40)
                if not os.path.exists(os.path.join(path, new_name)):
                    shutil.move(path, os.path.join(root, new_name))
                else:
                    gui.log.error(f'не могу переместить это {os.path.join(root, file)}')
                    gui.chat_print(f'не могу переместить это {os.path.join(root, file)}')
                i += 1
        gui.chat_print('\nИзображения успешно обработаны')

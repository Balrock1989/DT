import os
import shutil
import zipfile
from random import randint

from PIL import Image
# Нужно ставить Pillow

class RenameImage:

    def rename_image(self, gui, end_data, checkbox):
        """Обработка загруженных баннеров, форматирование имени"""
        """
        :param gui:  MainWindow интерфейс
        :param path: Путь до папки из gui.path_window
        :param end_data: Дата окончания акции из gui.date_end
        :param checkbox: Чекбокс о слиянии в одну папку gui.rename_checbox
        :return: None
        """
        i = 1
        remove = 0
        path = gui.path_window.toPlainText()
        path_end_data = end_data.replace('.', '_')
        zip_target = os.path.join(path, f'do_{path_end_data}.zip')
        result = os.path.join(path, f'do_{path_end_data}')
        if len(path) == '.' or not gui.path_window.toPlainText():
            gui.chat_print_signal.emit('Необходимо указать путь до папки')
            return
        if not os.path.exists(result) and checkbox:
            os.mkdir(result)

        with zipfile.ZipFile(zip_target, 'w') as zip:
            for root, dirs, files in os.walk(path):
                dir_num = randint(1000000, 9999999)
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        im = Image.open(path)
                        if im.size[0] > 1000 or im.size[1] > 1000 or im.size[0] == im.size[1] and im.size[0] > 550:
                            im.close()
                            gui.command_window.append(f'{file} размером {im.size[0]}x{im.size[1]} был удалён')
                            os.remove(os.path.join(root, file))
                            remove += 1
                            continue
                    except OSError:
                        gui.chat_print_signal.emit(f'SKIPPED "Этот файл не картинка {path}')
                        continue
                    new_name = str(im.size[0]) + '__' + str(im.size[1]) + 'xxxxx' + str(end_data) + '_____' + str(
                        i) + path[-4:]
                    im.close()
                    if checkbox:
                        # С перетаскиванием в новую папку
                        if not os.path.exists(os.path.join(result, new_name)):
                            shutil.move(os.path.join(root, file), os.path.join(result, new_name))
                            zip.write(os.path.join(result, new_name), os.path.join(f'do_{path_end_data}', new_name))
                            i += 1
                        else:
                            gui.log.error(f'не могу переместить этот файл -> {os.path.join(root, file)}')
                            gui.chat_print_signal.emit(f'не могу переместить этот файл -> {os.path.join(root, file)}')
                            i += 1
                    else:
                        # Только переименовать
                        if not os.path.exists(os.path.join(path, new_name)):
                            shutil.move(path, os.path.join(root, new_name))
                            zip.write(os.path.join(root, new_name), os.path.join(str(dir_num), new_name))
                            i += 1
                        else:
                            gui.chat_print_signal.emit(f'не могу переместить этот файл {os.path.join(root, file)}')
            gui.chat_print_signal.emit(f'Процесс успешно завершен. Удалено {remove} файлов')
            gui.chat_print_signal.emit(f'Всего было обработано {i - 1} файлов')

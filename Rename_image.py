import os
import shutil
import zipfile
from PIL import Image


class Rename:
    """Обработка загруженных баннеров, форматирование имени"""

    def rename_image(self, gui, path, end_data, checkbox):
        i = 1
        remove = 0
        path = os.path.normpath(path)
        path_end_data = end_data.replace('.', '_')
        zip_target = os.path.join(path, f'do_{path_end_data}.zip')
        result = os.path.join(path, f'do_{path_end_data}')
        if path == '.' or not gui.path_window.toPlainText():
            gui.command_window.append('Необходимо указать путь до папки')
            return
        if not os.path.exists(result) and checkbox:
            os.mkdir(result)
        dir_num = 1
        with zipfile.ZipFile(zip_target, 'w') as zip:
            for root, dirs, files in os.walk(path):
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
                        gui.command_window.append(f'SKIPPED "Этот файл не картинка{path}')
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
                            gui.command_window.append(f'не могу переместить это {os.path.join(root, file)} '
                                                      f'сюда с таким именем {os.path.join(result, new_name)}')
                            i += 1
                    else:
                        # Только переименовать
                        if not os.path.exists(os.path.join(path, new_name)):
                            shutil.move(path, os.path.join(root, new_name))
                            zip.write(os.path.join(root, new_name), os.path.join(str(dir_num), new_name))
                            i += 1
                        else:
                            gui.command_window.append(f'не могу переместить это {os.path.join(root, file)}')
                dir_num += 1
            gui.command_window.append(f'Было удалено {remove} файлов')
            gui.command_window.append(f'Всего обработано {i - 1} файлов')

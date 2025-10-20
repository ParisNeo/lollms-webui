from lollms.utilities import find_first_available_file_index, discussion_path_to_url
from lollms.client_session import Client
import pipmaster as pm
from functools import partial


def take_screenshot(client: Client, use_ui: bool = False, use_a_single_photo_at_a_time= True):

    if not pm.is_installed("pyautogui"):
        pm.install("pyautogui")
    if not pm.is_installed("PyQt5"):
        pm.install("PyQt5")

    import pyautogui
    from PyQt5 import QtWidgets, QtGui
    import sys

    class ScreenshotWindow(QtWidgets.QWidget):
        def __init__(self, client, screenshot, fn_view, fn, use_a_single_photo_at_a_time= True):
            super().__init__()
            self.client = client
            self.screenshot = screenshot
            self.fn_view = fn_view
            self.fn = fn
            self.use_a_single_photo_at_a_time = use_a_single_photo_at_a_time
            
            self.initUI()

        def initUI(self):
            self.setWindowTitle('Screenshot Viewer')
            self.layout = QtWidgets.QVBoxLayout()
            
            self.label = QtWidgets.QLabel(self)
            self.pixmap = QtGui.QPixmap(self.screenshot)
            self.label.setPixmap(self.pixmap)
            self.layout.addWidget(self.label)
            
            self.ok_button = QtWidgets.QPushButton('OK')
            self.ok_button.clicked.connect(self.save_and_close)
            self.layout.addWidget(self.ok_button)
            
            self.setLayout(self.layout)
            
        def save_and_close(self):
            self.screenshot.save(self.fn_view)
            self.screenshot.save(self.fn)
            self.client.discussion.image_files.append(self.fn)
            if self.use_a_single_photo_at_a_time:
                self.client.discussion.image_files = [self.client.discussion.image_files[-1]]

            self.close()


    screenshot = pyautogui.screenshot()
    view_image = client.discussion.discussion_folder / "view_images"
    image = client.discussion.discussion_folder / "images"
    index = find_first_available_file_index(view_image, "screen_shot_", ".png")
    fn_view = view_image / f"screen_shot_{index}.png"
    fn = image / f"screen_shot_{index}.png"

    if use_ui:
        app = QtWidgets.QApplication(sys.argv)
        window = ScreenshotWindow(client, screenshot, fn_view, fn, use_a_single_photo_at_a_time)
        window.show()
        app.exec_()
        return f'<img src="{discussion_path_to_url(fn_view)}" width="80%"></img>'
    else:
        screenshot.save(fn_view)
        screenshot.save(fn)
        client.discussion.image_files.append(fn)
        if use_a_single_photo_at_a_time:
            client.discussion.image_files = [client.discussion.image_files[-1]]

        return f'<img src="{discussion_path_to_url(fn_view)}" width="80%"></img>'

def take_screenshot_function(client, use_ui=True, use_a_single_photo_at_a_time= True):
    return {
            "function_name": "take_screenshot",
            "function": partial(take_screenshot, client=client, use_ui = use_ui, use_a_single_photo_at_a_time= use_a_single_photo_at_a_time),
            "function_description": "Takes a screenshot of the current screen.",
            "function_parameters": []                
        }
import os
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from worldmor.worldmor import Worldmor
from worldmor.constants import CELL_SIZE, MAX_CELL_SIZE, MIN_CELL_SIZE, ZOOM_CELL_STEP


class GridWidget(QtWidgets.QWidget):

    def __init__(self, worldmor):
        super().__init__()
        # TODO: constants
        self.cell_size = CELL_SIZE
        self.worldmor = worldmor
        self.setMinimumSize(*self.logical_to_pixels(3, 3))

    def pixels_to_logical(self, x, y):
        """
        Convert pixels to logical size of the field.
        :return: number of the field in the game
        """
        return y // self.cell_size, x // self.cell_size

    def logical_to_pixels(self, row, column):
        """
        Convert from a logical field in the game to the pixel to paint color or image.
        :return: pixels in grid
        """
        return column * self.cell_size, row * self.cell_size

    # TODO: some logic to do moves, discrete time

    def paintEvent(self, event):
        """
        The event called when changing the game map or when the size of the game is change.
        """
        row_max, col_max = self.pixels_to_logical(self.width(), self.height())
        row_max += 1
        col_max += 1

        painter = QtGui.QPainter(self)

        # TODO: do part of get map, if big changes get new map, not always

        for row in range(0, row_max):
            for column in range(0, col_max):

                # get place in map to color
                x, y = self.logical_to_pixels(row, column)

                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                # render some color
                painter.fillRect(rect, QtGui.QColor(min(255, (row+column)*2),
                                                    min(255, (row+column)*2),
                                                    min(255, (row+column)*2)))

    def wheelEvent(self, event):
        """
        Method called when the user uses the wheel. Need check ctrl for zoom.
        """
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # check scroll wheel direction
            if event.angleDelta().y() < 0:
                if not self.cell_size < MIN_CELL_SIZE:
                    self.cell_size -= ZOOM_CELL_STEP
                    self.update()
            else:
                if not self.cell_size > MAX_CELL_SIZE:
                    self.cell_size += ZOOM_CELL_STEP
                    self.update()


class myWindow(QtWidgets.QMainWindow):
    """
    Main application window.
    """

    def __init__(self):
        super().__init__()
        self.grid = None
        self.worldmor = None

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.grid.tick()


class App:
    """Class of the main loop of PyQt application."""

    def __init__(self):
        """
        Init class - create the window and load layout for it.
        - create game instance
        - create grid widget to display game
        - load dialogs and images
        """
        self.app = QtWidgets.QApplication([])

        self.worldmor = Worldmor()

        self.window = myWindow()
        self.window.setWindowIcon(QtGui.QIcon(App.get_img_path("worldmor.svg")))

        # load layout
        with open(App.get_gui_path('mainwindow.ui')) as f:
            uic.loadUi(f, self.window)

        # create and add grid
        self.grid = GridWidget(self.worldmor)
        self.window.grid = self.grid
        self.window.setCentralWidget(self.grid)

        # TODO: bind action for save, new, load, etc...
        # TODO: need for do fullscreen mode
        # self.window.showFullScreen()
        # self.window.showMaximized()
        self.window.menuBar().setVisible(True)

    @staticmethod
    def get_gui_path(file_name):
        """
        Create a complete path for gui part file.
        :param file_name: name of the *.ui part to import
        :return: complete path to gui part *.ui
        """
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'gui', file_name))

    @staticmethod
    def get_img_path(file_name):
        """
        Create a complete path for image file specific to import to the application.
        :param file_name: name of the picture to import
        :return: the complete path to the image
        """
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'img', file_name))

    def run(self):
        """
        Displaying the initialized window and preparing the game.
        """
        self.window.show()
        return self.app.exec()


def main():
    app = App()
    app.run()
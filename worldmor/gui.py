import os
from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg, uic
from worldmor.worldmor import Worldmor
from worldmor.constants import CELL_SIZE, MAX_CELL_SIZE, MIN_CELL_SIZE, ZOOM_CELL_STEP, PICTURES
from worldmor.about import ABOUT


# TODO: thread which will do time moments in this app. This app only set the move need or gun.

class GridWidget(QtWidgets.QWidget):

    def __init__(self, worldmor, images):
        super().__init__()
        self.images = images
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
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        print(painter.renderHints())

        # TODO: do part of get map, if big changes get new map, not always
        w_map = self.worldmor.get_map(row_max, col_max)

        for row in range(0, row_max):
            for column in range(0, col_max):

                # get place in map to color
                x, y = self.logical_to_pixels(row, column)

                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)
                # TODO: render picture based on codes in map.
                # render some color
                if w_map[row, column] == 0:
                    ...
                    painter.drawImage(rect, self.images['grass']);
                    #self.images['grass'].render(painter, rect)
                elif w_map[row, column] == 1:
                    ...
                    painter.drawImage(rect, self.images['grass']);
                    painter.drawImage(rect, self.images['wall']);
                    #self.images['grass'].render(painter, rect)
                    #self.images['wall'].render(painter, rect)
                elif w_map[row, column] == 2:
                    ...
                    painter.drawImage(rect, self.images['grass']);
                    #self.images['grass'].render(painter, rect)
                elif w_map[row, column] == 3:
                    ...
                    painter.drawImage(rect, self.images['grass']);
                    painter.drawImage(rect, self.images['e4']);
                    painter.drawImage(QtCore.QRectF(x+30, y+30, self.cell_size-30, self.cell_size-30), self.images['g5']);
                    #self.images['grass'].render(painter, rect)
                    #self.images['e4'].render(painter, rect)
                    # TODO: render smaller guns
                    #self.images['g5'].render(painter, QtCore.QRectF(x+30, y+30, self.cell_size-30, self.cell_size-30))
                    # TODO: render live bar, use in code
                else:
                    print("Error")
                    exit(-1)
                #painter.drawImage(QtCore.QPointF(0, 0), self.images['blood']);
                #self.images['blood'].render(painter)
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
        """Catch key press event and do move."""
        if e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_A:
            self.worldmor.left()
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_D:
            self.worldmor.right()
        if e.key() == QtCore.Qt.Key_Up or e.key() == QtCore.Qt.Key_W:
            self.worldmor.up()
        if e.key() == QtCore.Qt.Key_Down or e.key() == QtCore.Qt.Key_S:
            self.worldmor.down()
        self.grid.update()

    def show_score_and_live(self, score, live):
        """
        Show score and live in status bar.
        """
        self.statusBar.showMessage("Score: %s    Live: %s" % (int(score), int(live)))


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

        # TODO: how big create on init
        self.worldmor = Worldmor(1000, 1000, 500, 500)

        self.window = myWindow()
        self.window.setWindowIcon(QtGui.QIcon(App.get_img_path("worldmor.svg")))

        # load layout
        with open(App.get_gui_path('mainwindow.ui')) as f:
            uic.loadUi(f, self.window)

        self.images = {}
        for i in PICTURES:
            self.images[i] = App.create_as_qt_svg(i + ".svg")

        # create and add grid
        self.grid = GridWidget(self.worldmor, images=self.images)
        self.window.grid = self.grid
        self.window.worldmor = self.worldmor
        self.window.setCentralWidget(self.grid)

        self.action_bind('actionNew', lambda: self.new_dialog())
        self.action_bind('actionLoad', lambda: self.load_dialog())
        self.action_bind('actionSave', lambda: self.save_dialog())
        self.action_bind('actionSave_As', lambda: self.save_as_dialog())
        self.action_bind('actionExit', lambda: self.exit_dialog())

        self.action_bind('actionFullscreen', lambda: self.fullscreen())

        self.action_bind('actionAbout', lambda: self.about_dialog())




        # TODO: need dialog after game, some with score or leader bord maybe?

        self.window.menuBar().setVisible(True)
        self.window.show_score_and_live(0,0)

    def new_dialog(self):
        """
        Show question dialog if you really want create new game and eventually create it.
        """
        reply = QtWidgets.QMessageBox.question(self.window, 'New?',
                                               'Are you really want new game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.worldmor = Worldmor(1000, 1000, 500, 500)
            self.grid.worldmor = self.worldmor
            self.window.worldmor = self.worldmor
            self.grid.update()

    def load_dialog(self):
        print("load dialog")
        # TODO: normal load file dialog - check format

    def save_dialog(self):
        print("save dialog")
        # TODO: save if file is known, or open file save dialog as save as

    def save_as_dialog(self):
        print("save as dialog")
        # TODO: save dialog

    def exit_dialog(self):
        """
        Show question dialog if you really want to exit and eventually end the application.
        """
        reply = QtWidgets.QMessageBox.question(self.window, 'Exit?',
                                               'Are you really want exit the game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.window.close()

    def fullscreen(self):
        print("fullscrean")
        # self.window.showFullScreen()
        # self.window.showMaximized()
        self.window.menuBar().setVisible(True)
        # TODO: switch to fullscreen mode

    def about_dialog(self):
        """
        Show about dialog save in about.py.
        """
        QtWidgets.QMessageBox.about(self.window, "WorldMor", ABOUT)

    def action_bind(self, name, func):
        """
        Find function in QMAinWindow layout as child and bind to it the action.

        :param name: name of child in gui
        :param func: function to bind
        """
        action = self.window.findChild(QtWidgets.QAction, name)
        action.triggered.connect(func)

    @staticmethod
    def create_as_qt_svg(file_name):
        # TODO: render svg is too slow need only paint pixels
        return QtGui.QIcon(App.get_img_path(file_name)).pixmap(QtCore.QSize(300, 300)).toImage()
        #return QtSvg.QSvgRenderer(App.get_img_path(file_name))

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

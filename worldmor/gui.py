import os
import threading
import time
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from worldmor.worldmor import *
from worldmor.about import ABOUT
from worldmor.constants import *

PICTURES = {"grass": GRASS, "wall": WALL, "blood": BLOOD, "player": PLAYER, "bullet": BULLET,
            "health": HEALTH, "e1": ENEMY_B, "e2": ENEMY_1, "e3": ENEMY_2, "e4": ENEMY_E,
            "g1": GUN_B, "g2": GUN_1, "g3": GUN_2, "g4": GUN_3, "g5": GUN_E}


class TickThread(QtCore.QThread):
    """Tick thread class is class do the time moments in the game. In each time moment can move, shoot or both.
    AI runs too on this time moments. The timer can be paused and resume to stopping the game."""

    # Signal for update
    signal_update = QtCore.pyqtSignal()
    # Signal for set score bar
    signal_score = QtCore.pyqtSignal(int, int, int)

    def __init__(self, worldmor, tick_time, parent=None):
        """Init ticking class for do time moment. After init it is need set the grid for updates after time moment."""
        super(TickThread, self).__init__(parent)
        self.worldmor = worldmor
        self.daemon = True
        # start out paused.
        self.paused = True
        # condition for pausing and resume
        self.state = threading.Condition()
        # end kill the daemon thread
        self.kill = False
        # one step tick time
        self.tick_time = tick_time
        # Add to status bar
        self.score = 0
        self.health = 0
        self.bullets = 0

    def run(self):
        """Run thread, run as pause and resume when rendering window."""
        self.resume()
        while True:
            with self.state:
                if self.paused:
                    # block execution until notified.
                    self.state.wait()
            if self.kill:
                return

            self.worldmor.do_one_time_moment()
            # emit update signal to main thread
            self.signal_update.emit()
            # emit score signal to main thread
            self.signal_score.emit(self.score, self.health, self.bullets)
            time.sleep(self.tick_time)

    def resume(self):
        """Resume ticker -> resume game"""
        with self.state:
            self.paused = False
            # Unblock self if waiting.
            self.state.notify()

    def pause(self):
        """Pause time ticking thread, AI not moves."""
        with self.state:
            self.paused = True  # Block self.

    def set_kill(self):
        """Set kill flag to kill daemon thread, when wake up in one time moment."""
        self.kill = True
        self.resume()


class GridWidget(QtWidgets.QWidget):
    """GridWidget is class for render the part of map to window."""

    def __init__(self, worldmor, images, tick_thread):
        super().__init__()
        self.images = images
        self.cell_size = CELL_SIZE
        self.worldmor = worldmor
        self.tick_thread = tick_thread
        self.setMinimumSize(*self.logical_to_pixels(3, 3))
        self.tick_thread.resume()
        self.lock = threading.Lock()

    def pixels_to_logical(self, x, y):
        """Convert pixels to logical size of the field.

        :return: number of the field in the game
        """
        return y // self.cell_size, x // self.cell_size

    def logical_to_pixels(self, row, column):
        """Convert from a logical field in the game to the pixel to paint color or image.

        :return: pixels in grid
        """
        return column * self.cell_size, row * self.cell_size

    def paintEvent(self, event):
        """The event called when changing the game map or when the size of the game is change."""

        row_max, col_max = self.pixels_to_logical(self.width(), self.height())

        row_max += 1
        col_max += 1

        painter = QtGui.QPainter(self)

        w_map = self.worldmor.get_map(row_max, col_max)

        for row in range(0, row_max):
            for column in range(0, col_max):

                # get place in map to color
                x, y = self.logical_to_pixels(row, column)

                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                # Get code for rendering
                code = w_map[row, column] % 100
                # Get visible -> what render
                visible = int(w_map[row, column] / 100) % 10

                # Grass render on whole map
                painter.drawImage(rect, self.images[GRASS])
                # Render black where is not visibility
                if visible == 0:
                    painter.fillRect(rect, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                    continue
                # Render only map in "fog"
                if visible == 2:
                    if code == WALL:
                        painter.drawImage(rect, self.images[WALL])
                    painter.fillRect(rect, QtGui.QBrush(QtGui.QColor(0, 0, 0, 200)))
                    continue
                # Render pictures
                if code == WALL:
                    painter.drawImage(rect, self.images[WALL])
                elif code == BLOOD:
                    painter.drawImage(rect, self.images[BLOOD])
                elif code == PLAYER:
                    painter.drawImage(rect, self.images[PLAYER])
                    painter.drawImage(QtCore.QRectF(x + self.cell_size / 3, y + self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 3),
                                      self.images[(int(w_map[row, column] / 100000000000)) % 100])  # get gun from code
                    self.tick_thread.health = (int(w_map[row, column] / 1000)) % 1000  # get health
                    self.tick_thread.bullets = (int(w_map[row, column] / 1000000)) % 1000  # get bullets
                    # TODO: render live bar, use in code
                elif code == BULLET:
                    # render three bullets
                    painter.drawImage(QtCore.QRectF(x, y, self.cell_size, self.cell_size), self.images[BULLET])
                    painter.drawImage(QtCore.QRectF(x - self.cell_size / 4, y, self.cell_size, self.cell_size),
                                      self.images[BULLET])
                    painter.drawImage(QtCore.QRectF(x + self.cell_size / 4, y, self.cell_size, self.cell_size),
                                      self.images[BULLET])
                elif code == HEALTH:
                    # render health
                    painter.drawImage(QtCore.QRectF(x + self.cell_size / 3, y + self.cell_size / 2,
                                                    self.cell_size - self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 2),
                                      self.images[HEALTH])
                elif code == ENEMY_B:
                    painter.drawImage(rect, self.images[ENEMY_B])
                elif code == ENEMY_1:
                    painter.drawImage(rect, self.images[ENEMY_1])
                elif code == ENEMY_2:
                    painter.drawImage(rect, self.images[ENEMY_2])
                elif code == ENEMY_E:
                    painter.drawImage(rect, self.images[ENEMY_E])
                elif code == GUN_B:
                    painter.drawImage(rect, self.images[GUN_B])
                elif code == GUN_1:
                    painter.drawImage(rect, self.images[GUN_1])
                elif code == GUN_2:
                    painter.drawImage(rect, self.images[GUN_2])
                elif code == GUN_3:
                    painter.drawImage(rect, self.images[GUN_3])
                elif code == GUN_E:
                    painter.drawImage(rect, self.images[GUN_E])


    def wheelEvent(self, event):
        """Method called when the user uses the wheel. Need check ctrl for zoom."""
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


class MyWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, tick_thread):
        super().__init__()
        self.grid = None
        self.tick_thread = tick_thread
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
        if e.key() == QtCore.Qt.Key_Space or e.key() == QtCore.Qt.Key_0:
            self.worldmor.shoot()

    def update_status_bar(self, score, live, bullets):
        """Show score, live and number of bullets in status bar."""
        self.statusBar.showMessage("Score: %s    Live: %s   Bullets: %s" % (int(score), int(live), int(bullets)))

    def closeEvent(self, event):
        self.tick_thread.set_kill()


class App:
    """Class of the main loop of PyQt application."""

    def __init__(self):
        """Init class - create the window and load layout for it.

        - create game instance
        - create grid widget to display game
        - load dialogs and images
        """
        self.app = QtWidgets.QApplication([])

        self.worldmor = None
        self.create_new_world()
        # create daemon thread for do time in the WorldMor
        self.tick_thread = TickThread(self.worldmor, TICK_TIME)
        self.tick_thread.start()

        self.window = MyWindow(self.tick_thread)
        self.window.setWindowIcon(QtGui.QIcon(App.get_img_path("worldmor.svg")))
        # load layout
        with open(App.get_gui_path('mainwindow.ui')) as f:
            uic.loadUi(f, self.window)

        self.images = {}
        for i in PICTURES:
            self.images[PICTURES[i]] = App.render_pixmap_from_svg(str(i) + ".svg", RENDER_RECT_SIZE)

        # create and add grid
        self.grid = GridWidget(self.worldmor, images=self.images, tick_thread=self.tick_thread)
        self.window.grid = self.grid
        self.window.worldmor = self.worldmor
        self.window.setCentralWidget(self.grid)

        # bind menu actions
        self.action_bind('actionNew', lambda: self.new_dialog())
        self.action_bind('actionLoad', lambda: self.load_dialog())
        self.action_bind('actionSave', lambda: self.save_dialog())
        self.action_bind('actionSave_As', lambda: self.save_as_dialog())
        self.action_bind('actionExit', lambda: self.exit_dialog())

        self.action_bind('actionFullscreen', lambda: self.fullscreen())

        self.action_bind('actionAbout', lambda: self.about_dialog())

        # TODO: need dialog after game, some with score or leader bord maybe?
        self.window.menuBar().setVisible(True)
        # connect signal from thread for update
        self.tick_thread.signal_update.connect(self.update_signal)
        # connect score signal from thread for update
        self.tick_thread.signal_score.connect(self.update_status_bar)

    def update_signal(self):
        """Connected function to signal in ticking thread for correct updates."""
        self.grid.update()

    def update_status_bar(self, score, health, bullets):
        """Connected function to signal in ticking thread for correct updates of score bar."""
        self.window.update_status_bar(score, health, bullets)

    def new_dialog(self):
        """Show question dialog if you really want create new game and eventually create it."""
        self.tick_thread.pause()
        reply = QtWidgets.QMessageBox.question(self.window, 'New?',
                                               'Are you really want new game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.create_new_world()
            self.grid.worldmor = self.worldmor
            self.window.worldmor = self.worldmor
            self.tick_thread.worldmor = self.worldmor
            self.grid.update()
        self.tick_thread.resume()

    def load_dialog(self):
        print("load dialog")
        # TODO: normal load file dialog - check format
        # TODO: pause time deamon

    def save_dialog(self):
        print("save dialog")
        # TODO: save if file is known, or open file save dialog as save as
        # TODO: pause time deamon

    def save_as_dialog(self):
        print("save as dialog")
        # TODO: save dialog
        # TODO: pause time deamon

    def exit_dialog(self):
        """Show question dialog if you really want to exit and eventually end the application."""
        self.tick_thread.pause()
        reply = QtWidgets.QMessageBox.question(self.window, 'Exit?',
                                               'Are you really want exit the game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.tick_thread.set_kill()
            self.window.close()
        if reply == QtWidgets.QMessageBox.No:
            self.tick_thread.resume()

    def fullscreen(self):
        print("fullscreen")
        # self.window.showFullScreen()
        # self.window.showMaximized()
        self.window.menuBar().setVisible(True)
        # TODO: switch to fullscreen mode

    def create_new_world(self):
        """Create WorldMor map with specific parameters for generating map."""
        self.worldmor = Worldmor(rows=START_MAP_SIZE, bullets_exponent=BULLETS_EXPONENT,
                                 bullets_multiply=BULLETS_MULTIPLY, bullets_max_prob=BULLETS_MAX_PROB,
                                 health_exponent=HEALTH_EXPONENT, health_multiply=HEALTH_MULTIPLY,
                                 health_max_prob=HEALTH_MAX_PROB, enemy_start_probability=ENEMY_START_PROBABILITY,
                                 enemy_distance_divider=ENEMY_DISTANCE_DIVIDER, enemy_max_prob=ENEMY_MAX_PROB,
                                 guns_exponent=GUNS_EXPONENT, guns_multiply=GUNS_MULTIPLY, guns_max_prob=GUNS_MAX_PROB)

    def about_dialog(self):
        """Show about dialog save in about.py."""
        self.tick_thread.pause()
        QtWidgets.QMessageBox.about(self.window, "WorldMor", ABOUT)
        self.tick_thread.resume()

    def action_bind(self, name, func):
        """Find function in QMAinWindow layout as child and bind to it the action.

        :param name: name of child in gui
        :param func: function to bind
        """
        action = self.window.findChild(QtWidgets.QAction, name)
        action.triggered.connect(func)

    @staticmethod
    def render_pixmap_from_svg(file_name, render_quality):
        """Render pixmaps from svg for fast render in game.

        SVG images rendered slowly if there were a lot of them.
        :param file_name: file name of svg picture
        :param render_quality: size in pixel to render from SVG
        :return: QImage with pixmap with render_quality size
        """
        return QtGui.QIcon(App.get_img_path(file_name)).pixmap(QtCore.QSize(render_quality,
                                                                            render_quality)).toImage()

    @staticmethod
    def get_gui_path(file_name):
        """Create a complete path for gui part file.

        :param file_name: name of the *.ui part to import
        :return: complete path to gui part *.ui
        """
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'gui', file_name))

    @staticmethod
    def get_img_path(file_name):
        """Create a complete path for image file specific to import to the application.

        :param file_name: name of the picture to import
        :return: the complete path to the image
        """
        return os.path.normpath(os.path.join(os.path.dirname(__file__), 'img', file_name))

    def run(self):
        """Displaying the initialized window and preparing the game."""
        self.window.show()
        return self.app.exec()


def main():
    app = App()
    app.run()

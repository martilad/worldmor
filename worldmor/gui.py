import os
import threading
import time
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from worldmor.worldmor import *
from worldmor.about import ABOUT
from worldmor.constants import *

PICTURES = {"grass": GRASS, "wall": WALL, "blood": BLOOD, "player": PLAYER, "bullet": BULLET,
            "health": HEALTH, "e1": ENEMY_B, "e2": ENEMY_1, "e3": ENEMY_2, "e4": ENEMY_E,
            "g1": GUN_B, "g2": GUN_1, "g3": GUN_2, "g4": GUN_3, "g5": GUN_E, 'ex': EXPLODE}


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

            #TODO: score collect and show
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
        self.health_pen_size = 2

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
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0)), self.health_pen_size))

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
                    painter.fillRect(rect, QtGui.QBrush(QtGui.QColor(0, 0, 0, 150)))
                    continue
                # Render pictures
                if code == WALL:
                    painter.drawImage(rect, self.images[WALL])
                elif code == BLOOD:
                    painter.drawImage(rect, self.images[BLOOD])
                elif code == PLAYER:
                    painter.drawImage(rect, self.images[PLAYER])
                    health = (int(w_map[row, column] / 1000)) % 1000
                    self.tick_thread.health = health  # get health
                    self.tick_thread.bullets = (int(w_map[row, column] / 1000000)) % 1000  # get bullets
                    self.drawHealth(x, y, health, painter)
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
                if visible > 2:
                    painter.drawImage(rect, self.images[EXPLODE])
                if ENEMY_B <= code <= ENEMY_E or code == PLAYER:
                    health = (int(w_map[row, column] / 1000)) % 1000
                    self.drawHealth(x, y, health, painter)
                    gun = (int(w_map[row, column] / 100000000000)) % 100
                    if GUN_B <= gun <= GUN_E:
                        painter.drawImage(QtCore.QRectF(x + self.cell_size / 3, y + self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 3),
                                      self.images[gun])

    def drawHealth(self, x, y, health, painter):
        """Draw health bar for characters."""
        painter.drawRect(QtCore.QRectF(x + self.cell_size / 20, y,
                                       self.cell_size - self.cell_size / 10,
                                       self.cell_size / 7))
        painter.fillRect(QtCore.QRectF(x + self.health_pen_size / 2 + self.cell_size / 20, y + self.health_pen_size / 2,
                                       (self.cell_size - self.cell_size / 10 - self.health_pen_size) * (health / 100),
                                       self.cell_size / 7 - self.health_pen_size),
                         QtGui.QBrush(QtGui.QColor(200, 0, 0, 200)))

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

    def __init__(self, tick_thread, app):
        super().__init__()
        self.grid = None
        self.tick_thread = tick_thread
        self.worldmor = None
        self.app = app

    def keyPressEvent(self, e):
        """Catch key press event and do move."""
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_A:
            self.worldmor.left()
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_D:
            self.worldmor.right()
        if e.key() == QtCore.Qt.Key_Up or e.key() == QtCore.Qt.Key_W:
            self.worldmor.up()
        if e.key() == QtCore.Qt.Key_Down or e.key() == QtCore.Qt.Key_S:
            if modifiers == QtCore.Qt.ControlModifier:
                self.app.save_dialog()
            elif modifiers == (QtCore.Qt.ControlModifier |
                               QtCore.Qt.ShiftModifier):
                self.app.save_as_dialog()
            else:
                self.worldmor.down()
        if e.key() == QtCore.Qt.Key_Space or e.key() == QtCore.Qt.Key_0:
            self.worldmor.shoot()
        if e.key() == QtCore.Qt.Key_N:
            if modifiers == QtCore.Qt.ControlModifier:
                self.app.new_dialog()
        if e.key() == QtCore.Qt.Key_E:
            if modifiers == QtCore.Qt.ControlModifier:
                self.app.exit_dialog()
        if e.key() == QtCore.Qt.Key_O:
            if modifiers == QtCore.Qt.ControlModifier:
                self.app.load_dialog()
        if e.key() == QtCore.Qt.Key_Escape:
            self.app.fullscreen_dialog()
        if e.key() == QtCore.Qt.Key_Return:
            if modifiers == QtCore.Qt.AltModifier:
                self.app.fullscreen()

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

        self.full_screen = False
        self.worldmor = None
        self.create_new_world()
        # create daemon thread for do time in the WorldMor
        self.tick_thread = TickThread(self.worldmor, TICK_TIME)
        self.tick_thread.start()

        self.window = MyWindow(self.tick_thread, self)
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
        App.action_bind(self.window, 'actionNew', lambda: self.new_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionLoad', lambda: self.load_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionSave', lambda: self.save_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionSave_As', lambda: self.save_as_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionExit', lambda: self.exit_dialog(), QtWidgets.QAction)

        App.action_bind(self.window, 'actionFullscreen', lambda: self.fullscreen(), QtWidgets.QAction)

        App.action_bind(self.window, 'actionAbout', lambda: self.about_dialog(), QtWidgets.QAction)

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
        """Switch to fullscreen or back"""
        if self.full_screen:
            self.window.showNormal()
            self.full_screen = False
            self.window.menuBar().setVisible(True)
        else:
            self.window.showFullScreen()
            self.full_screen = True
            self.window.menuBar().setVisible(False)

    def fullscreen_dialog(self):
        """Load buttons dialog if have game fullscreen. Can be use shortcuts too."""
        if not self.full_screen:
            return
        # Pause game
        self.tick_thread.pause()
        dialog = QtWidgets.QDialog(self.window)
        with open(App.get_gui_path('fullscreen_dialog.ui')) as f:
            uic.loadUi(f, dialog)
        dialog.setWindowFlag(QtCore.Qt.SplashScreen)
        # Bind the buttons to actions
        App.button_bind(dialog, 'New', lambda: self.dialog_close(dialog, self.new_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'Load', lambda: self.dialog_close(dialog, self.load_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'Save', lambda: self.dialog_close(dialog, self.save_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'Save_as', lambda: self.dialog_close(dialog, self.save_as_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'Exit', lambda: self.dialog_close(dialog, self.exit_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'Back', lambda: self.dialog_close(dialog, dialog.close),
                        QtWidgets.QPushButton)

        dialog.exec()

    def dialog_close(self, dialog, call):
        """Manage fullscreen dialog push buttons to resume ticker and close dialog."""
        dialog.close()
        call()
        self.tick_thread.resume()
        return

    def create_new_world(self):
        """Create WorldMor map with specific parameters for generating map."""
        self.worldmor = Worldmor(rows=START_MAP_SIZE, random_seed=time.time(), bullets_exponent=BULLETS_EXPONENT,
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

    @staticmethod
    def action_bind(parent, name, func, what):
        """Find function in QMAinWindow layout as child and bind to it the action.

        :param parrent: name of parent where look for items
        :param name: name of child in gui
        :param func: function to bind
        """
        action = parent.findChild(what, name)
        action.triggered.connect(func)

    @staticmethod
    def button_bind(parrent, name, func, what):
        """Find function in QMAinWindow layout as child and bind to it the action.

        :param parrent: name of parrent where look for items
        :param name: name of child in gui
        :param func: function to bind
        """
        action = parrent.findChild(what, name)
        action.clicked.connect(func)

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

import os
import threading
import time
import json
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from worldmor.about import ABOUT
from worldmor.constants import *
from worldmor.game.game import *

PICTURES = {"grass": GRASS, "wall": WALL, "blood": BLOOD, "player": PLAYER, "bullet": BULLET,
            "health": HEALTH, "e1": ENEMY_B, "e2": ENEMY_1, "e3": ENEMY_2, "e4": ENEMY_E,
            "g1": GUN_B, "g2": GUN_1, "g3": GUN_2, "g4": GUN_3, "g5": GUN_E, 'ex': EXPLODE}

class TickThread(QtCore.QThread):
    """Tick thread class is class do the time moments in the game. In each time moment can move, shoot or both.
    AI runs too on this time moments. The timer can be paused and resume to stopping the game."""

    # Signal for update
    signal_update = QtCore.pyqtSignal()
    # Signal for game over
    signal_game_over = QtCore.pyqtSignal()
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
        while True:
            with self.state:
                if self.paused:
                    # block execution until notified.
                    self.state.wait()
            if self.kill:
                return

            back = self.worldmor.do_one_time_moment()

            if back == -1:
                # signalize end game
                self.signal_game_over.emit()
            else:
                self.score += back
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
        self.health_pen_size = 2
        self.started = False

    def pixels_to_logical(self, x, y):
        """Convert pixels to logical size of the field.

        :return: number of the field in the game
        """
        return y // self.cell_size, x // self.cell_size

    def logical_to_pixels(self, row_c, column_c):
        """Convert from a logical field in the game to the pixel to paint color or image.

        :return: pixels in grid
        """
        return column_c * self.cell_size, row_c * self.cell_size

    def paintEvent(self, event):
        """The event called when changing the game map or when the size of the game is change."""

        row_max_r, col_max_r = self.pixels_to_logical(self.width(), self.height())

        row_max_r += 1
        col_max_r += 1

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0)), self.health_pen_size))

        w_map = self.worldmor.get_map(row_max_r, col_max_r)

        for row_r in range(0, row_max_r):
            for column_r in range(0, col_max_r):

                # get place in map to color
                x, y = self.logical_to_pixels(row_r, column_r)

                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                # Get code for rendering
                code = w_map[row_r, column_r] % 100
                # Get visible -> what render
                visible = int(w_map[row_r, column_r] / 100) % 10

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
                if code == PLAYER:
                    painter.drawImage(rect, self.images[PLAYER])
                    health = self.worldmor.get_health(w_map[row_r, column_r])
                    self.tick_thread.health = health  # get health
                    self.tick_thread.bullets = self.worldmor.get_bullets(w_map[row_r, column_r])
                    self.draw_health(x, y, health, painter)
                elif code == BULLET:
                    # render three bullets
                    painter.drawImage(QtCore.QRectF(x, y, self.cell_size, self.cell_size), self.images[BULLET])
                    painter.drawImage(QtCore.QRectF(x - self.cell_size / 4, y, self.cell_size, self.cell_size),
                                      self.images[BULLET])
                    painter.drawImage(QtCore.QRectF(x + self.cell_size / 4, y, self.cell_size, self.cell_size),
                                      self.images[BULLET])
                elif code == HEALTH:
                    # render health
                    painter.drawImage(QtCore.QRectF(x + self.cell_size / 6, y + self.cell_size / 4,
                                                    self.cell_size - self.cell_size / 3,
                                                    self.cell_size - self.cell_size / 2),
                                      self.images[HEALTH])
                else:
                    painter.drawImage(rect, self.images[code])
                if visible > 2:
                    painter.drawImage(rect, self.images[EXPLODE])
                if ENEMY_B <= code <= ENEMY_E or code == PLAYER:
                    health = self.worldmor.get_health(w_map[row_r, column_r])
                    self.draw_health(x, y, health, painter)
                    gun = self.worldmor.get_gun(w_map[row_r, column_r])
                    if GUN_B <= gun <= GUN_E:
                        painter.drawImage(QtCore.QRectF(x + self.cell_size / 3, y + self.cell_size / 3,
                                                        self.cell_size - self.cell_size / 3,
                                                        self.cell_size - self.cell_size / 3),
                                          self.images[gun])
        if not self.started:
            self.draw_start_text()

    def draw_start_text(self):
        """Draw the start text to press enter to start the game."""
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QColor(0, 0, 0, 180))
        font = QtGui.QFont("Times", self.cell_size / 3.3, QtGui.QFont.Bold)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(self.width() / 2 - self.cell_size * 5 / 2, self.height() / 2 - self.cell_size * 5 / 2,
                          self.cell_size * 5, self.cell_size * 5), QtCore.Qt.AlignLeft,
            START_GAME_TEXT)

    def draw_health(self, x, y, health, painter):
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
        """Catch key press event and do corresponding actions."""
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if (e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_A) and self.grid.started:
            self.worldmor.left()
        if (e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_D) and self.grid.started:
            self.worldmor.right()
        if (e.key() == QtCore.Qt.Key_Up or e.key() == QtCore.Qt.Key_W) and self.grid.started:
            self.worldmor.up()
        if (e.key() == QtCore.Qt.Key_Down or e.key() == QtCore.Qt.Key_S) and self.grid.started:
            if modifiers == QtCore.Qt.ControlModifier:
                self.app.save_dialog()
            elif modifiers == (QtCore.Qt.ControlModifier |
                               QtCore.Qt.ShiftModifier):
                self.app.save_as_dialog()
            else:
                self.worldmor.down()
        if (e.key() == QtCore.Qt.Key_Space or e.key() == QtCore.Qt.Key_0) and self.grid.started:
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
            elif modifiers == QtCore.Qt.NoModifier and not self.grid.started:
                self.grid.started = True
                self.resume()

    def update_status_bar(self, score, live, bullets):
        """Show score, live and number of bullets in status bar."""
        self.statusBar.showMessage("%s: %s    %s: %s   %s: %s" % (SCORE_TEXT, int(score), HEALTH_TEXT,
                                                                  int(live), BULLETS_TEXT, int(bullets)))

    def resume(self):
        """Resume the game using the pause the ticker."""
        if self.grid.started:
            self.tick_thread.resume()

    def pause(self):
        """Pause the game using the pause the ticker."""
        if self.grid.started:
            self.tick_thread.pause()

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
        self.save_file = None

        # bind menu actions
        App.action_bind(self.window, 'actionNew', lambda: self.new_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionLoad', lambda: self.load_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionSave', lambda: self.save_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionSave_As', lambda: self.save_as_dialog(), QtWidgets.QAction)
        App.action_bind(self.window, 'actionExit', lambda: self.exit_dialog(), QtWidgets.QAction)

        App.action_bind(self.window, 'actionFullscreen', lambda: self.fullscreen(), QtWidgets.QAction)

        App.action_bind(self.window, 'actionAbout', lambda: self.about_dialog(), QtWidgets.QAction)

        self.window.menuBar().setVisible(True)
        # connect signal from thread for update
        self.tick_thread.signal_update.connect(self.update_signal)
        # connect score signal from thread
        self.tick_thread.signal_score.connect(self.update_status_bar)
        # connect game over signal from thread
        self.tick_thread.signal_game_over.connect(self.game_over)

        # do levels
        self.level1 = self.window.findChild(QtWidgets.QAction, "level_1")
        self.level2 = self.window.findChild(QtWidgets.QAction, "level_2")
        self.level3 = self.window.findChild(QtWidgets.QAction, "level_3")
        self.worldmor.set_how_fast_ai_is(LEVEL_1_AI_FAST)
        self.worldmor.set_ai_how_far_see(LEVEL_1_AI_SIGHT)
        self.level1.triggered.connect(lambda: self.level_set(self.level1, LEVEL_1_AI_SIGHT, LEVEL_1_AI_FAST))
        self.level2.triggered.connect(lambda: self.level_set(self.level2, LEVEL_2_AI_SIGHT, LEVEL_2_AI_FAST))
        self.level3.triggered.connect(lambda: self.level_set(self.level3, LEVEL_3_AI_SIGHT, LEVEL_3_AI_FAST))

    def level_set(self, action, how_far_ai_see, how_ai_fast):
        """Check checkbox and set values for the level."""
        self.level1.setChecked(False)
        self.level2.setChecked(False)
        self.level3.setChecked(False)
        action.setChecked(True)
        self.worldmor.set_how_fast_ai_is(how_ai_fast)
        self.worldmor.set_ai_how_far_see(how_far_ai_see)

    def game_over(self):
        """Show dialog when the game end."""
        self.window.pause()

        # Set the dialog window and show
        dialog = QtWidgets.QDialog(self.window)
        dialog.setWindowOpacity(.7)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(0, 0, 300, 300), 20, 20)

        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        dialog.setMask(mask)
        with open(App.get_gui_path('game_over.ui')) as f:
            uic.loadUi(f, dialog)
        dialog.setWindowFlag(QtCore.Qt.SplashScreen)
        # Bind the buttons to actions
        App.button_bind(dialog, 'new_2', lambda: self.dialog_close(dialog, self.new_dialog),
                        QtWidgets.QPushButton)
        App.button_bind(dialog, 'exit', lambda: self.window.close(),
                        QtWidgets.QPushButton)

        # Cant be tab order in game over dialog because for fast click the dialog can be clicked out.
        # Work the shortcuts.
        exit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_E), dialog)
        exit_shortcut.activated.connect(lambda: self.dialog_close(dialog, self.exit_dialog))
        new_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_N), dialog)
        new_shortcut.activated.connect(lambda: self.dialog_close(dialog, self.new_dialog))

        dialog.findChild(QtWidgets.QLabel, "score_label").setText("Score: %s" % self.tick_thread.score)

        dialog.exec()

    def update_signal(self):
        """Connected function to signal in ticking thread for correct updates."""
        self.grid.update()

    def update_status_bar(self, score, health, bullets):
        """Connected function to signal in ticking thread for correct updates of score bar."""
        self.window.update_status_bar(score, health, bullets)

    def new_dialog(self):
        """Show question dialog if you really want create new game and eventually create it."""
        self.window.pause()
        reply = QtWidgets.QMessageBox.question(self.window, 'New?',
                                               'Are you really want new game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.create_new_world()
            self.grid.worldmor = self.worldmor
            self.window.worldmor = self.worldmor
            self.tick_thread.worldmor = self.worldmor
            self.grid.started = False
            self.grid.update()
        self.window.resume()

    def load_dialog(self):
        """Load game from file."""
        self.window.pause()
        # load from file dialog
        file = QtWidgets.QFileDialog.getOpenFileName(self.window)
        try:
            file = open(file[0], 'r+')
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.window, "Open error", e.strerror)
        else:
            with file:
                try:
                    loaded = file.readlines()
                    score, how_far_ai, ai_fast, mid_row, mid_col, pos_row, pos_col = loaded[0].strip().split(",")
                    self.tick_thread.score = int(score)
                    self.worldmor.set_ai_how_far_see(int(how_far_ai))
                    self.worldmor.set_how_fast_ai_is(int(ai_fast))
                    self.worldmor.set_mid_row(int(mid_row))
                    self.worldmor.set_mid_col(int(mid_col))
                    self.worldmor.set_pos_row(int(pos_row))
                    self.worldmor.set_pos_col(int(pos_col))
                    self.worldmor.put_map_to_game(np.array(json.loads(loaded[1])).astype(np.int64))
                    self.grid.started = False
                    self.grid.update()
                except (TypeError, ValueError) as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self.window, "File format error", "Bad format.")

    def save_dialog(self):
        """Save game to last file."""
        self.window.pause()
        if self.save_file is not None:
            try:
                file_open = open(self.save_file[0], 'w')
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.window, "Save game error", e.strerror)
            else:
                with file_open:
                    self.save_game(file_open)
                QtWidgets.QMessageBox.information(self.window, "Save game", "Game saved.")
            self.window.resume()
        else:
            self.save_as_dialog()

    def save_as_dialog(self):
        """Save game to file."""
        self.window.pause()

        file = QtWidgets.QFileDialog.getSaveFileName(self.window)
        try:
            file_open = open(file[0], 'w')
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.window, "Save game error", e.strerror)
        else:
            with file_open:
                self.save_game(file_open)
                self.save_file = file
        self.window.resume()

    def save_game(self, file):
        """Save game to opened file.

        :param file: open file to write
        """
        file.write("%s,%s,%s,%s,%s,%s,%s \n" % (self.tick_thread.score, self.worldmor.get_ai_how_far_see(),
                                                self.worldmor.get_how_fast_ai_is(), self.worldmor.get_mid_row(),
                                                self.worldmor.get_mid_col(), self.worldmor.get_pos_row(),
                                                self.worldmor.get_pos_col()))
        file.write(json.dumps(self.worldmor.get_map_to_save().tolist()))

    def exit_dialog(self):
        """Show question dialog if you really want to exit and eventually end the application."""
        self.window.pause()
        reply = QtWidgets.QMessageBox.question(self.window, 'Exit?',
                                               'Are you really want exit the game?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.tick_thread.set_kill()
            self.window.close()
        if reply == QtWidgets.QMessageBox.No:
            self.window.resume()

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
        self.window.pause()
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
        self.window.resume()
        return

    def create_new_world(self):
        """Create WorldMor map with specific parameters for generating map."""
        self.worldmor = Worldmor(rows=START_MAP_SIZE, random_seed=time.time(), bullets_exponent=BULLETS_EXPONENT,
                                 bullets_multiply=BULLETS_MULTIPLY, bullets_max_prob=BULLETS_MAX_PROB,
                                 health_exponent=HEALTH_EXPONENT, health_multiply=HEALTH_MULTIPLY,
                                 health_max_prob=HEALTH_MAX_PROB, enemy_start_probability=ENEMY_START_PROBABILITY,
                                 enemy_distance_divider=ENEMY_DISTANCE_DIVIDER, enemy_max_prob=ENEMY_MAX_PROB,
                                 guns_exponent=GUNS_EXPONENT, guns_multiply=GUNS_MULTIPLY, guns_max_prob=GUNS_MAX_PROB,
                                 how_far_see_ai=HOW_FAR_SEE_AI, how_long_between_turn_ai=HOW_LONG_BETWEEN_TURN_AI,
                                 go_for_player_ai_prob=GO_FOR_PLAYER_AI_PROB, go_for_gun_ai_prob=GO_FOR_GUN_AI_PROB,
                                 go_for_health_ai_prob=GO_FOR_HEALTH_AI_PROB, view_range=VIEW_RANGE,
                                 go_for_bullets_ai_prob=GO_FOR_BULLETS_AI_PROB, check_range=CHECK_RANGE)

    def about_dialog(self):
        """Show about dialog save in about.py."""
        self.window.pause()
        QtWidgets.QMessageBox.about(self.window, "WorldMor", ABOUT)
        self.window.resume()

    @staticmethod
    def action_bind(parent, name, func, what):
        """Find function in QMAinWindow layout as child and bind to it the action.

        :param parent: name of parent where look for items
        :param name: name of child in gui
        :param func: function to bind
        :param what: what element need to find
        """
        action = parent.findChild(what, name)
        action.triggered.connect(func)

    @staticmethod
    def button_bind(parent, name, func, what):
        """Find function in QMAinWindow layout as child and bind to it the action.

        :param parent: name of parent where look for items
        :param name: name of child in gui
        :param func: function to bind
        :param what: what element need to find
        """
        action = parent.findChild(what, name)
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

import random
import sys
import ctypes
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter, QCursor, QColor, QTransform, QMovie, QGuiApplication
from PySide6.QtCore import Qt, QTimer, QPoint, QSize, QPointF


@dataclass
class CursorPetState:
    image_path: Optional[str] = None
    color: Optional[QColor] = None
    size: Optional[Tuple[int, int]] = None  # (width, height)
    offset: Optional[Tuple[int, int]] = None  # (dx, dy)
    rotation: Optional[float] = 0
    is_gif: bool = False
    movie: Optional["QMovie"] = None


class CursorPetOverlay(QWidget):
    def __init__(self, update_interval_ms: int = 16, parent=None):
        super().__init__(parent)

        # --- Оформление окна ---
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # --- Состояния ---
        self._states: Dict[str, CursorPetState] = {}
        self._pixmaps: Dict[str, QPixmap] = {}
        self._current_state_name: Optional[str] = None

        # Геометрия отрисовки
        self._current_pixmap: Optional[QPixmap] = None
        self._current_color: Optional[QColor] = None
        self._current_size: QSize = QSize(32, 32)
        self._current_offset: QPoint = QPoint(-16, -16)

        # Плавное смещение (для интерполяции)
        self._smooth_offset = QPointF(self._current_offset)

        # Позиция питомца и его скорость -- для инерции
        start_pos = QCursor.pos()
        self._pet_pos = QPointF(start_pos)  # реальная позиция окна
        self._velocity = QPointF(0.0, 0.0)

        # Для мини-ИИ
        self._idle_ms = 0  # сколько времени мышь почти не двигается
        self._ai_mode = "follow"  # "follow" или "play"
        self._ai_target_offset = QPointF(self._current_offset)  # цель в режиме "play"

        # Для оценки "скорости" курсора при желании
        self._last_cursor_pos = QCursor.pos()

        # Настроение
        self._mood = "neutral"  # neutral / happy / bored / sleepy / excited

        # Пинок курсора
        self._is_pushing = False
        self._push_dir = QPointF(0.0, 0.0)
        self._push_steps = 0
        self._push_cooldown_ms = 0

        # Таймер обновления позиции и отрисовки
        self._timer = QTimer(self)
        self._timer.setInterval(update_interval_ms)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start()

        # WinAPI click-through
        self._click_through_enabled = False

    # ========== ПУБЛИЧНЫЙ API ==========

    def register_state(
            self,
            name: str,
            image_path: Optional[str] = None,
            color: Optional[QColor] = None,
            size: Optional[Tuple[int, int]] = None,
            offset: Optional[Tuple[int, int]] = None,
            rotation=0
    ):
        """
        Регистрирует или обновляет состояние питомца курсора.

        name       - имя состояния (строка).
        image_path - путь к изображению (PNG с альфой идеально).
        color      - QColor для подложки/эффекта.
        size       - (width, height) для скейла изображения.
        offset     - (dx, dy) смещение относительно позиции курсора.
        """

        state = CursorPetState(
            image_path=image_path,
            color=color,
            size=size,
            offset=offset,
            rotation=rotation
        )

        if image_path:
            if image_path.lower().endswith(".gif"):
                state.is_gif = True
                movie = QMovie(image_path)
                movie.setCacheMode(QMovie.CacheAll)
                movie.start()
                movie.jumpToFrame(0)
                state.movie = movie
            else:
                pm = QPixmap(image_path)
                if pm.isNull():
                    pm = QPixmap(32, 32)
                    pm.fill(Qt.red)
                self._pixmaps[name] = pm

        self._states[name] = state

        # Если это первое зарегистрированное состояние - сразу активируем
        if self._current_state_name is None:
            self.set_state(name)

    def set_state(self, name: str):
        """
        Переключает текущее состояние.
        """
        if name not in self._states:
            return

        # отключаем старый GIF, если он был
        if self._current_state_name:
            old = self._states[self._current_state_name]
            if old.is_gif and old.movie:
                try:
                    old.movie.frameChanged.disconnect(self._gif_update)
                except:
                    pass
                try:
                    old.movie.updated.disconnect(self._gif_update)
                except:
                    pass

        self._current_state_name = name
        st = self._states[name]

        # connect gif
        if st.is_gif and st.movie:
            st.movie.frameChanged.connect(self._gif_update)
            st.movie.updated.connect(self._gif_update)

            # BUGFIX #2 — после смены состояния GIF должен сразу показать первый кадр
            QTimer.singleShot(0, lambda: self._apply_gif_state(st))

        self._apply_state()

    def _gif_update(self, *args):
        # Принудительная перерисовка
        self._apply_state()
        self.update()

    def _apply_gif_state(self, st):
        # Иногда movie.currentPixmap остаётся пустым → второй фрейм помогает
        if st.movie:
            st.movie.jumpToFrame(st.movie.currentFrameNumber())
        self._apply_state()
        self.update()

    def get_state(self) -> Optional[str]:
        """
        Возвращает имя текущего состояния.
        """
        return self._current_state_name

    # ========== ВНУТРЕННЯЯ ЛОГИКА ==========

    def _apply_state(self):
        """
        Применяет настройки текущего состояния:
        - картинка
        - цвет
        - размер
        - смещение
        """
        if self._current_state_name is None:
            return

        state = self._states[self._current_state_name]

        # --- Получаем pixmap ---
        if state.is_gif and state.movie:
            pixmap = state.movie.currentPixmap()
            if pixmap.isNull():
                return
        else:
            pixmap = self._pixmaps.get(self._current_state_name)
            if pixmap is None:
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.green)

        # --- Маштаб ---
        if state.size:
            w, h = state.size
            pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._current_size = QSize(w, h)
        else:
            self._current_size = pixmap.size()

        # --- Поворот ---
        if state.rotation and not pixmap.isNull():
            tr = QTransform()
            tr.rotate(state.rotation)
            pixmap = pixmap.transformed(tr, Qt.SmoothTransformation)

        # --- Цвет ---
        self._current_color = state.color

        # --- Смещение ---
        if state.offset:
            dx, dy = state.offset
            self._current_offset = QPoint(dx, dy)
        else:
            self._current_offset = QPoint(
                -self._current_size.width() // 2,
                -self._current_size.height() // 2
            )

        self._current_pixmap = pixmap
        self.resize(self._current_size)
        self.update()

    def _compute_dynamic_offset(self, cursor_pos: QPoint, base_offset: QPoint) -> QPoint:
        """
        Возвращает смещение с учётом того, что пони должна оставаться в пределах экрана.
        Берём базовый self._current_offset, но корректируем, если уходим за край.
        Корректирует смещение так, чтобы пони оставалась в пределах экрана.
        base_offset — уже "переосмысленное" смещение (например, с учётом направления),
        возвращаем итоговое смещение относительно курсора.
        """
        dx, dy = base_offset.x(), base_offset.y()

        screen = QGuiApplication.primaryScreen().availableGeometry()
        pet_w, pet_h = self._current_size.width(), self._current_size.height()

        # Позиция окна, если использовать base_offset
        target_x = cursor_pos.x() + dx
        target_y = cursor_pos.y() + dy

        margin = 5

        # Горизонталь
        if target_x < screen.left() + margin:
            target_x = screen.left() + margin
        if target_x + pet_w > screen.right() - margin:
            target_x = screen.right() - margin - pet_w

        # Вертикаль
        if target_y < screen.top() + margin:
            target_y = screen.top() + margin
        if target_y + pet_h > screen.bottom() - margin:
            target_y = screen.bottom() - margin - pet_h

        return QPoint(target_x - cursor_pos.x(), target_y - cursor_pos.y())

    def _update_mood(self, speed: float, move_threshold: float):
        """
        Простая модель настроения на основе активности мыши и времени простоя.
        """
        if speed > move_threshold * 4:
            new_mood = "excited"
        elif speed > move_threshold * 2:
            new_mood = "happy"
        elif self._idle_ms > 120000:
            new_mood = "sleepy"
        elif self._idle_ms > 50000:
            new_mood = "bored"
        else:
            new_mood = "neutral"

        self._mood = new_mood

    def _apply_mood_to_state(self, desired_state: str) -> str:
        """
        При желании можно подменять состояние в зависимости от настроения,
        если заранее зарегистрировать такие состояния.
        """
        # Sleepy — если есть специальная анимация сна
        if self._mood == "sleepy" and "sleep" in self._states:
            return "sleep"

        # Bored — скучающая анимация
        if self._mood == "bored" and "bored" in self._states:
            return "bored"

        # Happy / excited — более активная анимация
        if self._mood in ("happy", "excited") and "happy" in self._states:
            return "happy"

        return desired_state

    def _on_timer(self):
        """
        Обновление позиции и поведения:
        - определяем направление движения мыши;
        - режимы: follow (преследует курсор) и play (играет вокруг него);
        - настроения: neutral / happy / bored / sleepy / excited;
        - инерция движения питомца;
        - иногда подлетает и "толкает" курсор.
        """
        pos = QCursor.pos()
        dx = pos.x() - self._last_cursor_pos.x()
        dy = pos.y() - self._last_cursor_pos.y()
        speed = abs(dx) + abs(dy)

        interval_ms = self._timer.interval()
        move_threshold = 4
        idle_threshold_ms = 2500  # через сколько мс тишины включаем mini-AI

        # Обновляем idle-счётчик и режим AI
        if speed > move_threshold:
            self._idle_ms = 0
            self._ai_mode = "follow"
        else:
            self._idle_ms += interval_ms
            if self._idle_ms > idle_threshold_ms:
                self._ai_mode = "play"
            else:
                self._ai_mode = "follow"

        # Обновляем настроение
        self._update_mood(speed, move_threshold)

        desired_state = self._current_state_name
        flip_x = None  # если нет отдельных спрайтов left/right — будем зеркалить offset

        # --- РЕЖИМ FOLLOW ---
        if self._ai_mode == "follow":
            if speed > move_threshold:
                if abs(dx) >= abs(dy):
                    # Горизонтальное движение
                    if dx > 0:
                        # движение вправо
                        if "move_right" in self._states:
                            desired_state = "move_right"
                        elif "move" in self._states:
                            desired_state = "move"
                            flip_x = False
                        elif "move_left" in self._states:
                            desired_state = "move_left"
                    else:
                        # движение влево
                        if "move_left" in self._states:
                            desired_state = "move_left"
                        elif "move" in self._states:
                            desired_state = "move"
                            flip_x = True
                        elif "move_right" in self._states:
                            desired_state = "move_right"
                else:
                    # Вертикальное движение
                    if dy < 0 and "move_up" in self._states:
                        desired_state = "move_up"
                    elif dy > 0 and "move_down" in self._states:
                        desired_state = "move_down"
            else:
                # почти без движения
                if "idle" in self._states:
                    desired_state = "idle"

            # базовое смещение
            base = QPoint(self._current_offset)

            # зеркалим по X только если у нас один общий спрайт "move"
            if flip_x is not None or desired_state == "move":
                if flip_x:
                    base.setX(-abs(base.x()))
                else:
                    base.setX(abs(base.x()))

            # плавная интерполяция смещения
            alpha = 0.05
            self._smooth_offset.setX(
                self._smooth_offset.x() + (base.x() - self._smooth_offset.x()) * alpha
            )
            self._smooth_offset.setY(
                self._smooth_offset.y() + (base.y() - self._smooth_offset.y()) * alpha
            )

            target_offset = QPoint(int(self._smooth_offset.x()), int(self._smooth_offset.y()))

        # --- РЕЖИМ PLAY (mini-AI) ---
        else:
            # иногда выбираем новую "игровую" цель вокруг курсора
            if random.random() < 0.02:
                # радиус зависит от настроения
                if self._mood == "sleepy":
                    r = 64
                elif self._mood == "bored":
                    r = 128
                else:
                    r = 512

                rx = random.randint(-r, r)
                ry = random.randint(-r // 2, r)

                self._ai_target_offset = QPointF(rx, ry)

                # подменяем состояние под настроение
                if "play" in self._states:
                    desired_state = "play"
                elif "idle" in self._states:
                    desired_state = "idle"

            # плавно движемся к игровой цели
            alpha_ai = 0.01
            self._smooth_offset.setX(
                self._smooth_offset.x() + (self._ai_target_offset.x() - self._smooth_offset.x()) * alpha_ai
            )
            self._smooth_offset.setY(
                self._smooth_offset.y() + (self._ai_target_offset.y() - self._smooth_offset.y()) * alpha_ai
            )

            target_offset = QPoint(int(self._smooth_offset.x()), int(self._smooth_offset.y()))

        # Применяем настроение к состоянию (если есть спец-состояния)
        desired_state = self._apply_mood_to_state(desired_state)

        # Переключаем состояние при необходимости
        if desired_state != self._current_state_name and desired_state in self._states:
            self.set_state(desired_state)

        # Учитываем края экрана
        effective_offset = self._compute_dynamic_offset(pos, target_offset)

        # --------- ИНЕРЦИЯ ПОЛЁТА ПИТОМЦА ---------
        target_x = pos.x() + effective_offset.x()
        target_y = pos.y() + effective_offset.y()

        dt = interval_ms / 1000.0
        accel_k = 12.0 * dt
        friction = 0.75

        dir_x = target_x - self._pet_pos.x()
        dir_y = target_y - self._pet_pos.y()

        self._velocity.setX(self._velocity.x() + dir_x * accel_k)
        self._velocity.setY(self._velocity.y() + dir_y * accel_k)

        self._velocity.setX(self._velocity.x() * friction)
        self._velocity.setY(self._velocity.y() * friction)

        self._pet_pos.setX(self._pet_pos.x() + self._velocity.x())
        self._pet_pos.setY(self._pet_pos.y() + self._velocity.y())

        self.move(int(self._pet_pos.x()), int(self._pet_pos.y()))

        # --------- ПИНОК КУРСОРА ---------
        # обновляем кулдаун
        if self._push_cooldown_ms > 0:
            self._push_cooldown_ms = max(0, self._push_cooldown_ms - interval_ms)

        # вероятность "тычка" — только в режиме play или при активном движении
        if not self._is_pushing and self._push_cooldown_ms == 0 and self._ai_mode in ("play", "follow") and self._mood == "sleepy":
            # расстояние между пони и курсором
            dist2 = (pos.x() - self._pet_pos.x()) ** 2 + (pos.y() - self._pet_pos.y()) ** 2
            if dist2 < (40 ** 2) and random.random() < 0.05:
                vx = pos.x() - self._pet_pos.x()
                vy = pos.y() - self._pet_pos.y()
                length = (vx * vx + vy * vy) ** 0.5 or 1.0
                # направление "от себя" — чуть дальше от пони
                self._push_dir = QPointF(vx / length * 3.0, vy / length * 3.0)
                self._is_pushing = True
                self._push_steps = 3
                self._push_cooldown_ms = 1600  # мс до следующего пинка

        if self._is_pushing and self._push_steps > 0:
            cur = QCursor.pos()
            QCursor.setPos(
                int(cur.x() + self._push_dir.x()),
                int(cur.y() + self._push_dir.y())
            )
            self._push_steps -= 1
            if self._push_steps <= 0:
                self._is_pushing = False

        self._last_cursor_pos = pos
        self.update()

    # --- WinAPI click through ---

    def _enable_click_through(self):
        if self._click_through_enabled:
            return

        hwnd = int(self.winId())

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020

        user32 = ctypes.windll.user32
        get_window_long = user32.GetWindowLongW
        set_window_long = user32.SetWindowLongW

        ex_style = get_window_long(hwnd, GWL_EXSTYLE)
        ex_style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        set_window_long(hwnd, GWL_EXSTYLE, ex_style)

        self._click_through_enabled = True

    def showEvent(self, event):
        super().showEvent(event)
        self._enable_click_through()

    # --- отрисовка ---

    def paintEvent(self, event):
        if self._current_pixmap is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # цветовая подложка для наглядности (если задана)
        if self._current_color is not None:
            painter.setBrush(self._current_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                0,
                0,
                self._current_size.width(),
                self._current_size.height(),
            )

        # картинка поверх
        painter.drawPixmap(0, 0, self._current_pixmap)

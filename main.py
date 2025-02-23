import atexit
import itertools
import threading
import queue
import requests
import time
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Line, Color
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ColorProperty
from kivy.properties import StringProperty

def draw_border_and_bg(self, bg_color, border_color): # Функция, рисующая границы и фон элементу

    def update_border(self, *args):
        self.bg.pos =self.pos
        self.bg.size =self.size
        self.border.rectangle = (self.x,self.y,self.width,self.height)

    with self.canvas.before:
        Color(*hex_to_rgba(bg_color, 0.5))  # фон
        self.bg = Rectangle(pos=self.pos, size=self.size)

        Color(*hex_to_rgba(border_color)) # граница
        self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

    self.bind(pos=update_border, size=update_border) # Ставим, чтобы при изменении размера или положения границы и фон перерисовывались

def hex_to_rgba(hex_color, alpha=1.0): # Функция для перевода hex в rgba
    """Преобразует цвет из HEX в RGBA."""
    hex_color = hex_color.lstrip("#")  # Убираем #
    if len(hex_color) == 6:  # Формат #RRGGBB
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    elif len(hex_color) == 3:  # Формат #RGB (короткий)
        r, g, b = [int(hex_color[i] * 2, 16) for i in range(3)]
    else:
        raise ValueError("Неверный формат HEX. Используйте #RRGGBB или #RGB")
    
    return r / 255, g / 255, b / 255, alpha  # Возвращаем нормализованные значения (0-1)

class Body(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Режим клавиатуры (обычно 'system' для настольных приложений)
        Window.keyboard_mode = 'system'
    
    # def keyboard_on_key_down(self, window, keycode, text, modifiers):
    #     # keycode: (key_number, key_string)
    #     key = keycode[1]
    #     if key == 'down':
    #         self.focus_next_child()
    #         return True
    #     elif key == 'up':
    #         self.focus_previous_child()
    #         return True
    #     return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def focus_next_child(self):
        # Перебираем детей, которые поддерживают фокус
        focusable = [child for child in self.children if hasattr(child, 'focus')]
        # Так как children хранится в обратном порядке (последний добавленный имеет индекс 0)
        focusable = sorted(focusable, key=lambda w: w.y)
        current = None
        for child in focusable:
            if child.focus:
                current = child
                break
        if not focusable:
            return
        if current is None:
            # Если ни один не имеет фокуса, установить фокус на первый (в порядке сверху вниз)
            focusable[0].focus = True
        else:
            idx = focusable.index(current)
            # Переключаем фокус на следующий, если достигли конца, переходим к первому
            current.focus = False
            next_child = focusable[(idx + 1) % len(focusable)]
            next_child.focus = True

    def focus_previous_child(self):
        focusable = [child for child in self.children if hasattr(child, 'focus')]
        focusable = sorted(focusable, key=lambda w: w.y)
        current = None
        for child in focusable:
            if child.focus:
                current = child
                break
        if not focusable:
            return
        if current is None:
            focusable[-1].focus = True
        else:
            idx = focusable.index(current)
            current.focus = False
            prev_child = focusable[(idx - 1) % len(focusable)]
            prev_child.focus = True

# class CustomTextInput(TextInput, FocusBehavior):

#     def __init__(self, **kwargs):
#         super(CustomTextInput, self).__init__(**kwargs)

#         self.background_normal = ''
#         self.background_active = ''
#         self.background_color = (0, 0, 0, 0)
#         self.foreground_color = (0.2, 0.2, 0.2, 1)
#         self.padding = (10, 10)
#         self.hint_text_color = (0.6, 0.6, 0.6, 1)

#         with self.canvas.before:
#             self.border_color = Color(0.7, 0.8, 1, 1)
#             self.border_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20, 20, 20, 20])

#         self.bind(pos=self.update_rect, size=self.update_rect, focus=self.animate_focus)





#     def keyboard_on_key_down(self, window, keycode, text, modifiers):
#         # keycode имеет вид (key_number, key_string)
#         if keycode[1] in ('left', 'right'):
#             # Снимаем фокус с текущего виджета
#             self.focus = False
#             parent = self.parent
#             if parent:
#                 # Получаем всех детей, поддерживающих фокус (у которых есть атрибут focus)
#                 focusable = [child for child in parent.children if hasattr(child, 'focus')]
#                 # Для горизонтальной навигации сортируем по координате x
#                 focusable = sorted(focusable, key=lambda w: w.x)
#                 try:
#                     idx = focusable.index(self)
#                 except ValueError:
#                     idx = 0
#                 if keycode[1] == 'left':
#                     # При нажатии на стрелку влево переходим к следующему (если дошли до конца, переходим к первому)
#                     next_idx = (idx + 1) % len(focusable)
#                 else:  # 'right'
#                     # При нажатии на стрелку вправо переходим к предыдущему (если дошли до начала, переходим к последнему)
#                     next_idx = (idx - 1) % len(focusable)
#                 focusable[next_idx].focus = True
#             return True
#         else:
#             return super().keyboard_on_key_down(window, keycode, text, modifiers)
        
#     def update_rect(self, *args):
#         self.border_rect.pos = self.pos
#         self.border_rect.size = self.size
 

#     def animate_focus(self, instance, focused):
#         if focused:
#             anim = Animation(rgba=(0.3, 0.5, 1, 1), duration=0.2)
#             anim.start(self.border_color)
#         else:
#             anim = Animation(rgba=(0.7, 0.8, 1, 1), duration=0.2)
#             anim.start(self.border_color)

class CustomTextInput(TextInput):
    border_color = ColorProperty((1, 0, 0, 1))  # <--- Определите border_color как ColorProperty
    border_width = NumericProperty(2)  # <--- Определите border_width как NumericProperty (если используете)
    animated_text = StringProperty('')
    def __init__(self, **kwargs):
        # Если не задано, ставим однострочный режим
        kwargs.setdefault('multiline', False)
        super().__init__(**kwargs)
        # Убираем стандартные фоны
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        # Стили
        self.foreground_color = kwargs.get('foreground_color', hex_to_rgba("#C0C0C0"))
        self.hint_text_color = kwargs.get('hint_text_color', (0.6, 0.6, 0.6, 1))
        # self.padding = kwargs.get('padding', (10, 10))
        # Фиксируем размер по вертикали, чтобы не было "прыжков"
        self.font_size = Window.height * 0.057
        # self.size_hint_y = None
        # df
        # self.pos_hint={'center_x': 0.5, 'y': -0.2}
        # self.height = self.fixed_height
        self.bind(text=lambda inst, val: setattr(inst, 'height', self.fixed_height))
        
        self.padding_x = 20
        # Фиксированный размер по вертикали:
        # self.size_hint_y = None
        # Сохраним начальное значение font_size (оно уже установлено через kwargs или по умолчанию)
        self.height = self.font_size + 20
        self.fixed_height = self.height
        # self.height = self.fixed_height
        # Начинаем в режиме только для чтения (readonly) – навигационный режим
        self.readonly = True
        # Скрываем курсор (он не нужен в навигационном режиме)
        self.cursor_color = (0, 0, 0, 0)
        self._cursor_blink = False  # Отключаем стандартное мигание
        # self.size_hint= None
        # Не даём высоте изменяться при вводе текста
        # self.bind(text=lambda inst, val: setattr(inst, 'height', self.fixed_height))
        self.animation_duration = 0.3
        self.typing_speed = 0.05
        self.erasing_speed = 0.05
        self.bind(focus=self.on_focus)

    def on_focus(self, instance, focused):
        if focused:
            Animation(rgba=(0.392, 0.58, 0.929, 0.5), duration=0.2).start(self.parent.border_color)
            Animation(foreground_color=(1, 1, 1, 1), duration=0.2).start(self)
        else:
            Animation(rgba=(0.2, 0.2, 0.2, 1), duration=0.2).start(self.parent.border_color)
            Animation(foreground_color=(0.75, 0.75, 0.75, 1), duration=0.2).start(self)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            if self.readonly:
                self.readonly = False
                self.hint_text = ''
                Animation(rgba=(0.392, 0.58, 0.929, 0.8), duration=0.2).start(self.parent.border_color)
                self.cursor_color = (1,1,1,1)
                self.cursor_width = 2
            else:
                self.readonly = True
                # self.focus = False
                Animation(rgba=(0.392, 0.58, 0.929, 0.5), duration=0.2).start(self.parent.border_color)
                self.cursor_color = (0,0,0,0)
            return True

        elif keycode[1] in ('left', 'right') and self.readonly:
            # Снимаем фокус с текущего виджета
            self.focus = False
            parent = self.parent.parent
            if parent:
                # Получаем всех детей, поддерживающих фокус (у которых есть атрибут focus)
                focusable = [child for child in parent.children if hasattr(child, 'focus')]
                # Для горизонтальной навигации сортируем по координате x
                focusable = sorted(focusable, key=lambda w: w.x)
                try:
                    idx = focusable.index(self)
                except ValueError:
                    idx = 0
                if keycode[1] == 'left':
                    # При нажатии на стрелку влево переходим к следующему (если дошли до конца, переходим к первому)
                    next_idx = (idx + 1) % len(focusable)
                else:  # 'right'
                    # При нажатии на стрелку вправо переходим к предыдущему (если дошли до начала, переходим к последнему)
                    next_idx = (idx - 1) % len(focusable)
                focusable[next_idx].focus = True
            return True
        else:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)
        # return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def animate_hint_text(self, hint_text):
        self.clear_hint_text(lambda: self.type_hint_text(hint_text))

    def clear_hint_text(self, on_complete=None):
        def erase_char(dt):
            if not self.hint_text:
                if on_complete:
                    on_complete()
                return False
            self.hint_text = self.hint_text[:-1]
            Clock.schedule_once(erase_char, self.erasing_speed)
            return False

        Clock.schedule_once(erase_char, self.erasing_speed)

    def type_hint_text(self, hint_text):
        def add_char(dt):
            if len(self.hint_text) == len(hint_text):
                return False
            self.hint_text += hint_text[len(self.hint_text)]
            Clock.schedule_once(add_char, self.typing_speed)
            return False

        Clock.schedule_once(add_char, self.typing_speed)

    def fade_in(self):
        Animation(opacity=1, duration=self.animation_duration).start(self)

    def fade_out(self, on_complete=None):
        anim = Animation(opacity=0, duration=self.animation_duration)
        if on_complete:
            anim.bind(on_complete=lambda *args: on_complete())
        anim.start(self)

class CustomTextInputContainer(FocusBehavior, BoxLayout):
    def __init__(self, **kwargs):
        container_kwargs = {}
        textinput_kwargs = {}
        # Отделяем параметры, предназначенные для текстового поля
        textinput_props = ['font_size', 'text', 'hint_text', 'foreground_color', 'padding', 'hint_text_color', 'multiline']
        for key, value in kwargs.items():
            if key in textinput_props:
                textinput_kwargs[key] = value
            else:
                container_kwargs[key] = value

        super().__init__(**container_kwargs)

        # Рисуем фон с закруглёнными углами
        with self.canvas.before:
            self.border_color = Color(0.2, 0.2, 0.2, 1.0)
            rounding = self.height * 0.3
            self.border_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[rounding, rounding, rounding, rounding])
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Создаём внутреннее текстовое поле с сохранением стилей
        self.text_input = CustomTextInput(
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            **textinput_kwargs
        )
        self.add_widget(self.text_input)
        
        # Проксируем событие фокуса: анимация будет запускаться при изменении фокуса внутреннего поля
        # self.text_input.bind(focus=self._on_inner_focus)

        Window.bind(on_resize=self.update_text_size)
        # Флаг режима редактирования
        self.editing = False

        
    def update_text_size(self, *args):
        self.text_input.font_size = Window.height * 0.057
        self.height = Window.height * 0.1
        self.text_input.height = Window.height * 0.1

    def _update_rect(self, *args):
        self.border_rect.pos = self.pos
        self.border_rect.size = self.size

    @property
    def focus(self):
        return self.text_input.focus

    @focus.setter
    def focus(self, value):
        self.text_input.focus = value



        
class HoverButton(Button, FocusBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(focus=self.on_focus)
        Window.bind(mouse_pos=self.on_mouse_pos)
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # keycode имеет вид (key_number, key_string)
        if keycode[1] in ('left', 'right'):
            # Снимаем фокус с текущего виджета
            self.focus = False
            parent = self.parent
            if parent:
                # Получаем всех детей, поддерживающих фокус (у которых есть атрибут focus)
                focusable = [child for child in parent.children if hasattr(child, 'focus')]
                # Для горизонтальной навигации сортируем по координате x
                focusable = sorted(focusable, key=lambda w: w.x)
                try:
                    idx = focusable.index(self)
                except ValueError:
                    idx = 0
                if keycode[1] == 'left':
                    # При нажатии на стрелку влево переходим к следующему (если дошли до конца, переходим к первому)
                    next_idx = (idx + 1) % len(focusable)
                else:  # 'right'
                    # При нажатии на стрелку вправо переходим к предыдущему (если дошли до начала, переходим к последнему)
                    next_idx = (idx - 1) % len(focusable)

                focusable[next_idx].focus = True
            return True
        elif keycode[1] == "enter":
            # Снимаем фокус с текущего виджета
            
            print('Нажата кнопка')
            return True
        else:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)
    def on_focus(self, instance, value):

        if value:  # Если фокусируется
            self.width = self.width*1.3
            Animation(background_color=hex_to_rgba("#6495ED"), duration=0.3).start(self)  # Голубая граница
        else:  # Если теряет фокус
            self.width = self.width/1.3
            Animation(background_color=hex_to_rgba("#333333"), duration=0.3).start(self)  # Серый цвет
    def on_mouse_pos(self, window, pos):
        # Если курсор над кнопкой
        if self.collide_point(*pos):
            Animation(background_color=(0.13, 0.65, 0.95, 1), duration=0.2).start(self)
            Window.set_system_cursor("hand")  # Меняем курсор на "руку"
        else:
            Animation(background_color=(0.13, 0.65, 0.95, 0.41), duration=0.2).start(self)
            Window.set_system_cursor("arrow")  # Возвращаем стандартный курсор (стрелка)


class MyApp(App):
    
    def build(self):
        self.body = Body(orientation="vertical", padding=10, spacing=10) # Главный родитель
        Window.clearcolor = hex_to_rgba("#1E1E1E", 0.6) # Цвет фона

        scroll_view = ScrollView(size_hint=(1, 1)) # Контейнер для прокрутки

        self.main_space = GridLayout(padding = 20, spacing = 10, size_hint_y = None) # Контейнер для размещения карточек фильмов

        # draw_border_and_bg(main_space, "#1E1E1E", "#FFCA08")
        self.body.add_widget(scroll_view)

        input_container = BoxLayout(orientation="horizontal", spacing = 10, size_hint = (1, 0.1)) # Контейнер для ввода
        
        button= HoverButton(text="Поиск",  size_hint = (0.4,1), font_size = Window.height * 0.05)
        self.text_input = CustomTextInputContainer()
        Clock.schedule_once(lambda dt: self.text_input.text_input.animate_hint_text('Поиск'), 2)  # Задержка перед началом анимации
        button.focus = True
        input_container.add_widget(self.text_input)
        input_container.add_widget(button)

        self.body.add_widget(input_container)

        return self.body
if __name__ == '__main__':
    MyApp().run()


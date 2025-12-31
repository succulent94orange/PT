import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen
import os

# --- COLORS ---
COLOR_MENU = get_color_from_hex('#2C3E50')    # Dark Blue
COLOR_SPRINT = get_color_from_hex('#27AE60')  # Green
COLOR_REST = get_color_from_hex('#C0392B')    # Red
COLOR_DONE = get_color_from_hex('#F39C12')    # Orange
COLOR_BTN_GRAY = get_color_from_hex('#7F8C8D')

# --- AUDIO MANAGER ---
class SoundManager:
    def __init__(self):
        self.sound_path = '/storage/emulated/0/Download/'
        self.sounds = {}
        try:
            self.sounds['beep'] = SoundLoader.load(os.path.join(self.sound_path, 'beep.wav'))
            self.sounds['buzzer'] = SoundLoader.load(os.path.join(self.sound_path, 'buzzer.wav'))
        except Exception as e:
            print(f"Error loading sounds: {e}")

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            try:
                if sound.state == 'play':
                    sound.stop()
                sound.play()
            except:
                pass

audio_manager = None

# ==========================================
# SCREEN 1: MAIN MENU
# ==========================================
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        with layout.canvas.before:
            Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))

        title = Label(text="WORKOUT SELECTOR", font_size='40sp', bold=True, size_hint=(1, 0.3))
        
        btn_airbike = Button(
            text="AIR BIKE\n(7-4-2-1-1)",
            font_size='30sp',
            bold=True,
            background_normal='',
            background_color=COLOR_SPRINT
        )
        btn_airbike.bind(on_press=self.go_airbike)

        btn_30s = Button(
            text="LOOP TIMER\n(Default: 30s/2s)",
            font_size='30sp',
            bold=True,
            background_normal='',
            background_color=COLOR_DONE
        )
        btn_30s.bind(on_press=self.go_30s)

        layout.add_widget(title)
        layout.add_widget(btn_airbike)
        layout.add_widget(btn_30s)
        self.add_widget(layout)

    def go_airbike(self, instance):
        self.manager.current = 'airbike'

    def go_30s(self, instance):
        self.manager.current = 'loop30'

# ==========================================
# SCREEN 2: AIR BIKE TIMER (UPDATED)
# ==========================================
class AirBikeScreen(Screen):
    def __init__(self, **kwargs):
        super(AirBikeScreen, self).__init__(**kwargs)
        self.routine = self._build_routine()
        self.current_step_index = 0
        self.time_remaining = 0
        self.timer_event = None

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Back Button
        btn_back = Button(text="< BACK TO MENU", size_hint=(1, 0.1), background_color=COLOR_BTN_GRAY)
        btn_back.bind(on_press=self.go_back)

        self.lbl_status = Label(text="7-4-2-1-1 INTERVALS", font_size='35sp', bold=True, size_hint=(1, 0.15))
        self.lbl_info = Label(text="Tap Start", font_size='25sp', size_hint=(1, 0.1), color=(0.9, 0.9, 0.9, 1))
        self.lbl_timer = Label(text="18:20", font_size='100sp', bold=True, size_hint=(1, 0.4))

        controls = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.25))
        self.btn_prev = Button(text="<<", font_size='25sp', background_color=COLOR_BTN_GRAY)
        self.btn_prev.bind(on_press=self.go_prev)
        self.btn_main = Button(text="START", font_size='30sp', bold=True, background_normal='', background_color=COLOR_SPRINT)
        self.btn_main.bind(on_press=self.toggle_timer)
        self.btn_next = Button(text=">>", font_size='25sp', background_color=COLOR_BTN_GRAY)
        self.btn_next.bind(on_press=self.go_next)

        controls.add_widget(self.btn_prev)
        controls.add_widget(self.btn_main)
        controls.add_widget(self.btn_next)

        self.layout.add_widget(btn_back)
        self.layout.add_widget(self.lbl_status)
        self.layout.add_widget(self.lbl_info)
        self.layout.add_widget(self.lbl_timer)
        self.layout.add_widget(controls)
        self.add_widget(self.layout)

    def _build_routine(self):
        r = []
        r.append(("READY", 5, "GET READY"))
        
        # Set 1: 7 Reps
        for i in range(1, 8):
            lbl = f"SET 1 / 5   |   REP {i} / 7"
            r.append(("SPRINT", 10, lbl))
            r.append(("REST", 30, lbl))
            
        # Set 2: 4 Reps
        for i in range(1, 5):
            lbl = f"SET 2 / 5   |   REP {i} / 4"
            r.append(("SPRINT", 20, lbl))
            r.append(("REST", 60, lbl))
            
        # Set 3: 2 Reps
        for i in range(1, 3):
            lbl = f"SET 3 / 5   |   REP {i} / 2"
            r.append(("SPRINT", 30, lbl))
            r.append(("REST", 90, lbl))
            
        # Set 4: 1 Rep
        lbl = "SET 4 / 5   |   REP 1 / 1"
        r.append(("SPRINT", 60, lbl))
        r.append(("REST", 180, lbl))
        
        # Set 5: Final
        lbl = "SET 5 / 5   |   FINAL"
        r.append(("SPRINT", 20, lbl))
        r.append(("DONE", 0, "COMPLETE"))
        return r

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_back(self, instance):
        self.finish_workout()
        self.manager.current = 'menu'

    def toggle_timer(self, instance):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            self.btn_main.text = "RESUME"
            self.btn_main.background_color = COLOR_SPRINT
        else:
            if self.btn_main.text == "START":
                audio_manager.play('beep')
            self.btn_main.text = "STOP"
            self.btn_main.background_color = COLOR_REST
            if self.current_step_index == 0 and self.time_remaining == 0:
                self.load_step()
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def load_step(self):
        step_type, duration, info_text = self.routine[self.current_step_index]
        self.time_remaining = duration
        self.lbl_info.text = info_text
        
        if step_type == "READY":
            self.bg_color.rgba = COLOR_MENU
            self.lbl_status.text = "GET READY"
        elif step_type == "SPRINT":
            self.bg_color.rgba = COLOR_SPRINT
            # Shows duration in title: SPRINT (10s)
            self.lbl_status.text = f"SPRINT ({duration}s)"
        elif step_type == "REST":
            self.bg_color.rgba = COLOR_REST
            # Shows duration in title: REST (30s)
            self.lbl_status.text = f"REST ({duration}s)"
        elif step_type == "DONE":
            self.bg_color.rgba = COLOR_DONE
            self.lbl_status.text = "COMPLETE"
            self.lbl_timer.text = "00:00"
            self.finish_workout()
            return
        self.update_timer_label()

    def update_timer(self, dt):
        self.time_remaining -= 1
        if self.time_remaining < 0:
            self.go_next(None)
        else:
            self.update_timer_label()

    def update_timer_label(self):
        mins, secs = divmod(self.time_remaining, 60)
        self.lbl_timer.text = f"{mins:02d}:{secs:02d}"

    def go_next(self, instance):
        if self.current_step_index < len(self.routine) - 1:
            self.current_step_index += 1
            audio_manager.play('beep')
            self.load_step()

    def go_prev(self, instance):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            audio_manager.play('beep')
            self.load_step()

    def finish_workout(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.btn_main.text = "RESET"
        self.btn_main.background_color = COLOR_SPRINT
        self.current_step_index = 0

# ==========================================
# SCREEN 3: CUSTOM LOOP TIMER
# ==========================================
class Loop30Screen(Screen):
    def __init__(self, **kwargs):
        super(Loop30Screen, self).__init__(**kwargs)
        self.running = False
        self.timer_event = None
        self.phase = "WORK" # WORK or BREAK
        self.time_remaining = 30
        
        # Default Durations
        self.default_work = 30
        self.default_rest = 2
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # 1. Back Button
        btn_back = Button(text="< BACK TO MENU", size_hint=(1, 0.1), background_color=COLOR_BTN_GRAY)
        btn_back.bind(on_press=self.go_back)

        # 2. Settings Row (Inputs)
        settings_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.15))
        
        # Work Setting
        work_box = BoxLayout(orientation='vertical', spacing=5)
        lbl_work = Label(text="Work (sec):", font_size='20sp', halign='center', valign='bottom')
        lbl_work.bind(size=lbl_work.setter('text_size'))
        self.input_work = TextInput(text=str(self.default_work), input_filter='int', multiline=False, font_size='30sp', halign='center', padding_y=(10, 10))
        work_box.add_widget(lbl_work)
        work_box.add_widget(self.input_work)
        
        # Rest Setting
        rest_box = BoxLayout(orientation='vertical', spacing=5)
        lbl_rest = Label(text="Rest (sec):", font_size='20sp', halign='center', valign='bottom')
        lbl_rest.bind(size=lbl_rest.setter('text_size'))
        self.input_rest = TextInput(text=str(self.default_rest), input_filter='int', multiline=False, font_size='30sp', halign='center', padding_y=(10, 10))
        rest_box.add_widget(lbl_rest)
        rest_box.add_widget(self.input_rest)

        settings_layout.add_widget(work_box)
        settings_layout.add_widget(rest_box)

        # 3. Status and Timer
        self.lbl_status = Label(text="LOOP READY", font_size='40sp', bold=True, size_hint=(1, 0.2))
        self.lbl_timer = Label(text="00:30", font_size='100sp', bold=True, size_hint=(1, 0.35))

        # 4. Start Button
        self.btn_main = Button(
            text="START LOOP", 
            font_size='35sp', 
            bold=True, 
            background_normal='', 
            background_color=COLOR_SPRINT,
            size_hint=(1, 0.2)
        )
        self.btn_main.bind(on_press=self.toggle_timer)

        self.layout.add_widget(btn_back)
        self.layout.add_widget(settings_layout)
        self.layout.add_widget(self.lbl_status)
        self.layout.add_widget(self.lbl_timer)
        self.layout.add_widget(self.btn_main)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_back(self, instance):
        self.stop_timer()
        self.manager.current = 'menu'

    def get_user_settings(self):
        try:
            w = int(self.input_work.text)
        except:
            w = 30
        try:
            r = int(self.input_rest.text)
        except:
            r = 2
        return w, r

    def toggle_timer(self, instance):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.running = True
        self.btn_main.text = "STOP"
        self.btn_main.background_color = COLOR_REST
        
        w, r = self.get_user_settings()
        
        self.phase = "WORK"
        self.time_remaining = w
        self.update_visuals()
        
        audio_manager.play('beep')
        self.timer_event = Clock.schedule_interval(self.update_loop, 1)

    def stop_timer(self):
        self.running = False
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = None
        
        w, r = self.get_user_settings()
        
        self.btn_main.text = "START LOOP"
        self.btn_main.background_color = COLOR_SPRINT
        self.lbl_timer.text = f"{w:02d}"
        self.bg_color.rgba = COLOR_MENU
        self.lbl_status.text = "LOOP STOPPED"

    def update_loop(self, dt):
        self.time_remaining -= 1
        
        if self.time_remaining < 0:
            w, r = self.get_user_settings()
            if self.phase == "WORK":
                self.phase = "BREAK"
                self.time_remaining = r
                audio_manager.play('buzzer') 
            else:
                self.phase = "WORK"
                self.time_remaining = w
                audio_manager.play('beep') 
        
        self.update_visuals()

    def update_visuals(self):
        if self.phase == "WORK":
            self.bg_color.rgba = COLOR_SPRINT
            self.lbl_status.text = "WORK!"
        else:
            self.bg_color.rgba = COLOR_REST
            self.lbl_status.text = "RESET..."

        mins, secs = divmod(self.time_remaining, 60)
        self.lbl_timer.text = f"{mins:02d}:{secs:02d}"

# ==========================================
# APP BUILDER
# ==========================================
class WorkoutApp(App):
    def build(self):
        global audio_manager
        audio_manager = SoundManager()

        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(AirBikeScreen(name='airbike'))
        sm.add_widget(Loop30Screen(name='loop30'))
        return sm

if __name__ == '__main__':
    WorkoutApp().run()

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
import os

# Configuration for colors
COLOR_BG_READY = get_color_from_hex('#2C3E50')  # Dark Blue
COLOR_BG_SPRINT = get_color_from_hex('#27AE60') # Green
COLOR_BG_REST = get_color_from_hex('#C0392B')   # Red
COLOR_BG_DONE = get_color_from_hex('#F39C12')   # Orange

class WorkoutTimerApp(App):
    def build(self):
        # 1. Build Routine with "Set/Rep" Labels
        # Format: (Type, Duration, Label_Text)
        self.routine = []
        
        # --- 5-Second Warning Phase ---
        self.routine.append(("READY", 5, "GET READY"))
        
        # Set 1: 7 Reps (10s sprint, 30s rest)
        for i in range(1, 8):
            lbl = f"SET 1: REP {i} / 7"
            self.routine.append(("SPRINT", 10, lbl))
            self.routine.append(("REST", 30, lbl))
            
        # Set 2: 4 Reps (20s sprint, 1:00 rest)
        for i in range(1, 5):
            lbl = f"SET 2: REP {i} / 4"
            self.routine.append(("SPRINT", 20, lbl))
            self.routine.append(("REST", 60, lbl))
            
        # Set 3: 2 Reps (30s sprint, 1:30 rest)
        for i in range(1, 3):
            lbl = f"SET 3: REP {i} / 2"
            self.routine.append(("SPRINT", 30, lbl))
            self.routine.append(("REST", 90, lbl))
            
        # Set 4: 1 Rep (60s sprint, 3:00 rest)
        lbl = "SET 4: REP 1 / 1"
        self.routine.append(("SPRINT", 60, lbl))
        self.routine.append(("REST", 180, lbl))
        
        # Set 5: 1 Rep (20s sprint, DONE)
        lbl = "SET 5: FINAL SPRINT"
        self.routine.append(("SPRINT", 20, lbl))
        self.routine.append(("DONE", 0, "COMPLETE"))

        # App State
        self.current_step_index = 0
        self.time_remaining = 0
        self.timer_event = None
        
        # --- AUDIO SETUP ---
        sound_path = '/storage/emulated/0/Download/'
        self.sounds = {}
        try:
            self.sounds['beep'] = SoundLoader.load(os.path.join(sound_path, 'beep.wav'))
            self.sounds['buzzer'] = SoundLoader.load(os.path.join(sound_path, 'buzzer.wav'))
        except Exception as e:
            print(f"Error loading sounds: {e}")

        # --- UI LAYOUT ---
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_BG_READY)
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # 1. Status Label (SPRINT / REST)
        self.lbl_status = Label(
            text="7-4-2-1-1 INTERVALS",
            font_size='40sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2)
        )

        # 2. Set/Rep Info Label (NEW)
        self.lbl_info = Label(
            text="Tap Start to Begin",
            font_size='25sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.1)
        )
        
        # 3. Big Timer
        self.lbl_timer = Label(
            text="18:20",
            font_size='110sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.4)
        )

        # 4. Control Buttons (Horizontal Layout)
        self.controls = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))
        
        # Previous Button
        self.btn_prev = Button(
            text="<< PREV",
            font_size='20sp',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        self.btn_prev.bind(on_press=self.go_prev)

        # Start/Stop Button
        self.btn_main = Button(
            text="START",
            font_size='30sp',
            bold=True,
            background_normal='',
            background_color=(0, 0.8, 0, 1) # Green
        )
        self.btn_main.bind(on_press=self.toggle_timer)

        # Next Button
        self.btn_next = Button(
            text="NEXT >>",
            font_size='20sp',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        self.btn_next.bind(on_press=self.go_next)

        self.controls.add_widget(self.btn_prev)
        self.controls.add_widget(self.btn_main)
        self.controls.add_widget(self.btn_next)

        self.layout.add_widget(self.lbl_status)
        self.layout.add_widget(self.lbl_info)
        self.layout.add_widget(self.lbl_timer)
        self.layout.add_widget(self.controls)

        return self.layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def toggle_timer(self, instance):
        if self.timer_event:
            # STOP ACTION
            self.timer_event.cancel()
            self.timer_event = None
            self.btn_main.text = "RESUME"
            self.btn_main.background_color = (0, 0.8, 0, 1) # Green
            
            # Stop any sound playing
            for sound in self.sounds.values():
                if sound and sound.state == 'play':
                    sound.stop()
        else:
            # START ACTION
            if self.btn_main.text == "START":
                self.play_sound('beep') # Initial beep
                
            self.btn_main.text = "STOP"
            self.btn_main.background_color = (0.9, 0, 0, 1) # Red
            
            # If starting fresh
            if self.current_step_index == 0 and self.time_remaining == 0:
                self.load_step()
                
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def load_step(self):
        step_type, duration, info_text = self.routine[self.current_step_index]
        
        # Only reset time if we aren't resuming (checked via logic elsewhere, but here we usually load full duration on step change)
        self.time_remaining = duration
        self.lbl_info.text = info_text
        
        if step_type == "READY":
            self.bg_color.rgba = COLOR_BG_READY
            self.lbl_status.text = f"GET READY"
        elif step_type == "SPRINT":
            self.bg_color.rgba = COLOR_BG_SPRINT
            self.lbl_status.text = f"SPRINT!"
        elif step_type == "REST":
            self.bg_color.rgba = COLOR_BG_REST
            self.lbl_status.text = f"REST..."
        elif step_type == "DONE":
            self.bg_color.rgba = COLOR_BG_DONE
            self.lbl_status.text = "COMPLETE"
            self.lbl_timer.text = "00:00"
            self.finish_workout()
            return

        self.update_timer_label()

    def update_timer(self, dt):
        self.time_remaining -= 1
        if self.time_remaining < 0:
            self.go_next(None) # Auto advance
        else:
            self.update_timer_label()

    def update_timer_label(self):
        mins, secs = divmod(self.time_remaining, 60)
        self.lbl_timer.text = f"{mins:02d}:{secs:02d}"

    def go_next(self, instance):
        if self.current_step_index < len(self.routine) - 1:
            self.current_step_index += 1
            
            step_type, _, _ = self.routine[self.current_step_index]
            
            # Sound Logic
            if step_type == "DONE":
                self.play_sound('buzzer')
            else:
                self.play_sound('beep')
                
            self.load_step()
        else:
            # Already at end
            pass

    def go_prev(self, instance):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.play_sound('beep')
            self.load_step()

    def finish_workout(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.btn_main.text = "RESET"
        self.btn_main.background_color = (0, 0.8, 0, 1)
        self.current_step_index = 0

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if sound:
            try:
                if sound.state == 'play':
                    sound.stop()
                sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

if __name__ == '__main__':
    WorkoutTimerApp().run()

import json
import os
import time
import math
import re

# --- KIVY CORE ---
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex, platform
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.audio import SoundLoader
from kivy.animation import Animation

# ==========================================
# 1. THEME & COLORS (NEO-BRUTALIST NATURE)
# ==========================================
C_BG_MAIN   = "#050505"      # OLED Void
C_BG_SEC    = "#0F120F"      # Nature Dark Green/Black
C_CARD      = "#181A18"      # Card Grey-Green
C_BORDER    = "#2D332D"      # Muted Moss
C_PRIMARY   = "#CCFF00"      # ACID LIME (Accents)
C_SECONDARY = "#9D4EDD"      # ELECTRIC PURPLE
C_TEXT      = "#FFFFFF"      # Pure White
C_SUB       = "#889988"      # Sage
C_ALERT     = "#FF3333"      # Neo Red

COLOR_SPRINT_HEX = '#00FF41'
COLOR_REST_HEX   = '#FF0055'
COLOR_DONE_HEX   = '#FFD700'
COLOR_BTN_BLUE_HEX = '#00CCFF'

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mma_profile_kivy.json")

# ==========================================
# 2. AUDIO & DATA MANAGERS
# ==========================================
class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            paths = ['/storage/emulated/0/Download/', './']
            for p in paths:
                beep = os.path.join(p, 'beep.wav')
                buzzer = os.path.join(p, 'buzzer.wav')
                if os.path.exists(beep): self.sounds['beep'] = SoundLoader.load(beep)
                if os.path.exists(buzzer): self.sounds['buzzer'] = SoundLoader.load(buzzer)
        except: pass

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            try:
                if sound.state == 'play': sound.stop()
                sound.play()
            except: pass

audio_manager = None

default_profile = {
    "current_week": 1,
    "maxes": {
        "Hack Squat": 95, "Trap Bar Farmers Walk": 125, "Dumbbell Bench Press": 50,
        "Cable Row": 35, "Unilateral Leg Press": 50, "Tricep Pushdowns": 25,
        "Cable Woodchoppers": 20, "Leg Extension": 35, "Seated Leg Curl": 35,
        "Cable Face Pulls": 25
    }
}

user_profile = default_profile.copy()

def load_data():
    global user_profile
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                user_profile = json.load(f)
        except: pass

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(user_profile, f)
        return True
    except: return False

def parse_duration(text):
    if "Air Bike" in text or "Assault Bike" in text: return "AIRBIKE"
    if "Side Plank" in text: return "SIDEPLANK"
    text = text.lower()
    match = re.search(r'\((\d+)\s*(m|min|mins|sec|s)\)', text)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if 'm' in unit: return val * 60
        return val
    return None

# ==========================================
# 3. EXERCISE DATABASE
# ==========================================
exercise_db = {
    "Bird Dog": {"desc": "Hands/knees. Brace core. Extend opposite limbs.", "cue": "Punch heel back. Keep spine stiff."},
    "Side Plank": {"desc": "Lie on side. Lift hips. Hold.", "cue": "Focus on breathing. Complete both sides."},
    "Pallof Press": {"desc": "Kneel on one knee. Press band forward.", "cue": "Don't let the band pull you sideways."},
    "Glute Bridge": {"desc": "Back on floor. Lift hips.", "cue": "Squeeze glutes BEFORE lifting."},
    "Cat-Cow": {"desc": "Arch/Round spine slowly.", "cue": "Move one vertebrae at a time."},
    "90/90 Hip Flow": {"desc": "Sit with legs 90-deg. Lean forward/back.", "cue": "Focus on tight hip restrictions."},
    "Adductor Rock Back": {"desc": "One leg out to side. Rock back.", "cue": "Deep stretch in groin/inner thigh."},
    "Couch Stretch": {"desc": "Knee near wall. Squeeze glute.", "cue": "Don't arch back. 30s each side."},
    "Malasana Squat": {"desc": "Deep squat. Breathe.", "cue": "Visualize pelvic floor dropping/relaxing."},
    "Relaxation Breathing": {"desc": "1. Lie on back. Hand on belly.\n2. Inhale DEEP expanding BELLY.\n3. Visualize floor bulging down.\n4. Exhale passively.", "cue": "Down-regulates pelvic tone."},
    "Hack Squat": {"desc": "Feet shoulder width. Lower.", "cue": "Limit depth if hip clicks."},
    "Box Jumps": {"desc": "Explosive jump. STEP DOWN.", "cue": "Land soft. Protect pelvic floor."},
    "Trap Bar Farmers Walk": {"desc": "Lift bar. Walk short steps.", "cue": "Stay vertical. Targets QL."},
    "Dumbbell Bench Press": {"desc": "Press DBs up.", "cue": "45-degree arm angle."},
    "Cable Row": {"desc": "Seated row. Pull to stomach.", "cue": "Squeeze shoulder blades."},
    "Tricep Pushdowns": {"desc": "Push rope down.", "cue": "Lockout elbows."},
    "Cable Face Pulls": {"desc": "Pull rope to forehead.", "cue": "Thumbs back."},
    "Unilateral Leg Press": {"desc": "One leg. Lower slowly.", "cue": "Fix Right Hip imbalance."},
    "Leg Extension": {"desc": "Extend legs fully.", "cue": "Control the top."},
    "Seated Leg Curl": {"desc": "Curl heels to butt.", "cue": "Squeeze hamstrings."},
    "Cable Woodchoppers": {"desc": "High to low. Rotate torso.", "cue": "Rotate from ribs."},
    "Split Squat": {"desc": "Lunge stance. Drop knee.", "cue": "Use plate under heel if hip clicks."},
    "Lower Body Warm-Up": {"desc": "10 Squats + 5 Lunges.", "cue": "Open hips before walking on mats."},
    "Air Bike Protocol": {"desc": "20-minute interval routine.", "cue": "Use the integrated timer."},
    "Static Plank": {"desc": "Hold body straight.", "cue": "Squeeze glutes."},
    "Push-Ups": {"desc": "Standard push-up. Chest to floor.", "cue": "Keep core tight."},
    "Swiss Ball Bridge": {"desc": "Heels on ball. Lift hips. Hold.", "cue": "Static hold."},
    "Clam Shells": {"desc": "Lie on side, knees bent. Lift top knee.", "cue": "Squeeze glute medius. 15 per side."}
}

def get_weight(exercise):
    if exercise not in user_profile["maxes"]: return ""
    try:
        one_rm = float(user_profile["maxes"][exercise])
        w_num = user_profile["current_week"]
        val = int((one_rm * 0.80) + ((w_num - 1) * 2.5))
        return f"@ {val} lbs"
    except: return ""

def get_workout(day):
    w = get_weight
    if day == "Monday":
        return ["MORNING ROUTINE", "Push-Ups (30 reps)", "Side Plank (1 min)", "Static Plank (1 min)", "Swiss Ball Bridge (1 min)", "Clam Shells (2 sets x 15/side)",
                "WARMUP", "Cat-Cow (30 reps)", "Glute Bridge (2x15)",
                "SUPERSET A", f"Hack Squat (3x8) {w('Hack Squat')}", "Box Jumps (3x5)",
                "SUPERSET B", f"Trap Bar Farmers Walk (3x40yds) {w('Trap Bar Farmers Walk')}", "Air Bike Protocol (See Timer)",
                "FINISHER", f"Seated Leg Curl (3x15) {w('Seated Leg Curl')}", "COOL DOWN", "90/90 Hip Flow (2 mins)"]
    elif day == "Wednesday":
        return ["MORNING ROUTINE", "Push-Ups (30 reps)", "Side Plank (1 min)", "Static Plank (1 min)", "Swiss Ball Bridge (1 min)", "Clam Shells (2 sets x 15/side)",
                "WARMUP", "Pallof Press (3x10/side)",
                "SUPERSET A", f"Dumbbell Bench Press (3x10) {w('Dumbbell Bench Press')}", f"Cable Row (3x12) {w('Cable Row')}",
                "SUPERSET B", f"Tricep Pushdowns (3x15) {w('Tricep Pushdowns')}", f"Cable Face Pulls (3x15) {w('Cable Face Pulls')}",
                "CARDIO", "Air Bike Protocol (See Timer)"]
    elif day == "Friday":
        return ["MORNING ROUTINE", "Push-Ups (30 reps)", "Side Plank (1 min)", "Static Plank (1 min)", "Swiss Ball Bridge (1 min)", "Clam Shells (2 sets x 15/side)",
                "WARMUP", "Bird Dog (3x10/side)", "Split Squat BW (2x5/side)",
                "CIRCUIT", f"1. Unilateral Leg Press (10/side) {w('Unilateral Leg Press')}", f"2. Cable Woodchoppers (12/side) {w('Cable Woodchoppers')}",
                f"3. Leg Extension (15 reps) {w('Leg Extension')}", "4. Plank (1 min)", "COOL DOWN", "Couch Stretch (3x30s/side)"]
    elif day in ["Tuesday", "Thursday", "Saturday"]:
        return ["PRE-COMBAT", "Lower Body Warm-Up (1 Round)", "Adductor Rock Back (1 min)", "ACTIVITY", "BJJ / Kickboxing Class", "POST-COMBAT", "Relaxation Breathing (5 mins)", "Malasana Squat (2 mins)"]
    return ["Active Recovery", "Walk 45 Mins", "Meal Prep"]

# ==========================================
# 4. NEO-BRUTALIST UI COMPONENTS
# ==========================================

class SectionHeader(Label):
    def __init__(self, text, **kwargs):
        super().__init__(text=text.upper(), **kwargs)
        self.font_size = dp(12)
        self.color = get_color_from_hex(C_PRIMARY)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(40)
        self.text_size = (Window.width - dp(40), None)
        self.halign = 'left'
        self.valign = 'bottom'
        with self.canvas.before:
            Color(*get_color_from_hex(C_PRIMARY))
            self.line_instr = Rectangle(pos=self.pos, size=(dp(25), dp(2)))
        self.bind(pos=self.update_ui, size=self.update_ui)
    def update_ui(self, *args):
        self.line_instr.pos = (self.x + dp(20), self.y + dp(5))

class NeoCard(BoxLayout):
    def __init__(self, command=None, bg_color=get_color_from_hex(C_CARD), border_color=get_color_from_hex(C_BORDER), **kwargs):
        super().__init__(**kwargs)
        self.command = command
        self.orientation = 'horizontal'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(90)
        self.bg_val = bg_color
        self.press_pos = None
        with self.canvas.before:
            Color(0, 0, 0, 1) # Shadow
            self.shadow = Rectangle(pos=(self.x + dp(4), self.y - dp(4)), size=self.size)
            self.rect_color = Color(*self.bg_val)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*border_color)
            self.border_instr = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(pos=self.update_ui, size=self.update_ui)
    def update_ui(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size
        self.shadow.pos = (self.x + dp(4), self.y - dp(4)); self.shadow.size = self.size
        self.border_instr.rectangle = (self.x, self.y, self.width, self.height)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.press_pos = touch.pos
            self.rect_color.rgba = get_color_from_hex("#252525")
            self.rect.pos = (self.x + dp(2), self.y - dp(2))
            return super().on_touch_down(touch)
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.press_pos:
            if math.hypot(touch.x - self.press_pos[0], touch.y - self.press_pos[1]) < dp(20):
                for child in self.walk():
                    if isinstance(child, Button) and child.collide_point(*touch.pos):
                        self.reset_vis(); return super().on_touch_up(touch)
                if self.command: self.command()
        self.reset_vis()
        return super().on_touch_up(touch)
    def reset_vis(self):
        self.rect_color.rgba = self.bg_val; self.rect.pos = self.pos; self.press_pos = None

class NeoButton(Button):
    def __init__(self, **kwargs):
        bg_hex = kwargs.pop('background_color_hex', C_CARD)
        fg_hex = kwargs.pop('color_hex', C_TEXT)
        super().__init__(**kwargs)
        self.background_normal = ''; self.background_down = ''; self.background_color = (0,0,0,0)
        self.bg_val = get_color_from_hex(bg_hex)
        self.color = get_color_from_hex(fg_hex)
        self.bold = True
        with self.canvas.before:
            Color(0, 0, 0, 1) # Shadow
            self.shadow = Rectangle(pos=(self.x+dp(3), self.y-dp(3)), size=self.size)
            self.rect_c = Color(*self.bg_val)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*get_color_from_hex(C_BORDER))
            self.border_instr = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
        self.bind(pos=self.update_ui, size=self.update_ui, state=self.on_state)
    def update_ui(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size
        self.shadow.pos = (self.x+dp(3), self.y-dp(3)); self.shadow.size = self.size
        self.border_instr.rectangle = (self.x, self.y, self.width, self.height)
    def on_state(self, instance, value):
        if value == 'down': self.rect.pos = (self.x+dp(2), self.y-dp(2))
        else: self.rect.pos = self.pos

# ==========================================
# 5. SCREENS & NAVIGATION
# ==========================================

class SwipeManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_start_x = 0
        self.last_exit = 0
    def on_touch_down(self, touch): self.touch_start_x = touch.x; return super().on_touch_down(touch)
    def on_touch_up(self, touch):
        dx = touch.x - self.touch_start_x
        if dx > Window.width * 0.25 and abs(touch.dy) < dp(50):
            if self.current != 'home': self.transition = SlideTransition(direction='right'); self.current = 'home'
            else:
                if time.time() - self.last_exit < 2.0: App.get_running_app().stop()
                else: self.last_exit = time.time()
        return super().on_touch_up(touch)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG_MAIN)); Rectangle(pos=self.pos, size=self.size)
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10), spacing=dp(10))
        btn_prev = NeoButton(text="<", size_hint_x=None, width=dp(50), background_color_hex=C_CARD)
        btn_prev.bind(on_release=self.prev_week)
        self.lbl_week = Label(text="WEEK 1", font_size=dp(24), bold=True, color=get_color_from_hex(C_PRIMARY))
        btn_next = NeoButton(text=">", size_hint_x=None, width=dp(50), background_color_hex=C_CARD)
        btn_next.bind(on_release=self.next_week)
        btn_edit = NeoButton(text="PRO", size_hint_x=None, width=dp(60), background_color_hex=C_BG_SEC)
        btn_edit.bind(on_release=lambda x: setattr(self.manager, 'current', 'edit'))
        header.add_widget(btn_prev); header.add_widget(self.lbl_week); header.add_widget(btn_next); header.add_widget(btn_edit)
        self.layout.add_widget(header)
        scroll = ScrollView(); list_l = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        list_l.bind(minimum_height=list_l.setter('height'))
        for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            card = NeoCard(command=lambda day=d: self.go_day(day))
            card.add_widget(Label(text=d.upper(), font_size=dp(18), bold=True, halign='left', size_hint_x=0.8))
            card.add_widget(Label(text="→", font_size=dp(24), color=get_color_from_hex(C_PRIMARY), size_hint_x=0.2))
            list_l.add_widget(card)
        list_l.add_widget(SectionHeader(text="UTILITIES"))
        btn_ab = NeoCard(command=lambda: setattr(self.manager, 'current', 'airbike'), bg_color=get_color_from_hex("#1A2226"))
        btn_ab.add_widget(Label(text="AIR BIKE TIMER", bold=True)); list_l.add_widget(btn_ab)
        btn_lp = NeoCard(command=lambda: setattr(self.manager, 'current', 'loop30'), bg_color=get_color_from_hex("#1A2226"))
        btn_lp.add_widget(Label(text="LOOP TIMER", bold=True)); list_l.add_widget(btn_lp)
        scroll.add_widget(list_l); self.layout.add_widget(scroll); self.add_widget(self.layout)
    def on_pre_enter(self): self.lbl_week.text = f"WEEK {user_profile['current_week']}"
    def next_week(self, *a): user_profile['current_week'] = (user_profile['current_week'] % 6) + 1; save_data(); self.on_pre_enter()
    def prev_week(self, *a): user_profile['current_week'] = 6 if user_profile['current_week'] == 1 else user_profile['current_week']-1; save_data(); self.on_pre_enter()
    def go_day(self, d): self.manager.get_screen('day').load_day(d); self.manager.transition.direction='left'; self.manager.current='day'

class DayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG_MAIN)); Rectangle(pos=self.pos, size=self.size)
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="< BACK", size_hint_x=None, width=dp(80)); btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        self.lbl_title = Label(text="DAY", font_size=dp(24), bold=True); header.add_widget(btn_back); header.add_widget(self.lbl_title)
        self.layout.add_widget(header)
        self.scroll = ScrollView(); self.content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, padding=dp(15))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content); self.layout.add_widget(self.scroll); self.add_widget(self.layout)
    def load_day(self, day):
        self.lbl_title.text = day.upper(); self.content.clear_widgets()
        for line in get_workout(day):
            if any(x in line for x in ["WARMUP", "SUPERSET", "COOL", "COMBAT", "FINISHER", "CIRCUIT", "CARDIO", "MORNING"]):
                self.content.add_widget(SectionHeader(text=line))
            else:
                ex_key = next((k for k in exercise_db if k in line), None)
                dur = parse_duration(line)
                card = NeoCard(command=(lambda x=ex_key, l=line: self.go_detail(x, l)) if ex_key else None)
                card.add_widget(Label(text=line, font_size=dp(14), halign='left', text_size=(Window.width-dp(120), None)))
                if dur:
                    t_btn = NeoButton(text="TIME", size_hint_x=None, width=dp(60), background_color_hex=C_PRIMARY, color_hex="#000000")
                    if dur == "AIRBIKE": t_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'airbike'))
                    elif dur == "SIDEPLANK": t_btn.bind(on_release=lambda x: self.go_timer(60, "SIDEPLANK"))
                    else: t_btn.bind(on_release=lambda x, t=dur: self.go_timer(t))
                    card.add_widget(t_btn)
                self.content.add_widget(card)
    def go_detail(self, k, l): self.manager.get_screen('detail').load_ex(k, l); self.manager.current='detail'
    def go_timer(self, s, m="SIMPLE"): self.manager.get_screen('simple_timer').set_time(s, m); self.manager.current='simple_timer'

class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG_MAIN)); Rectangle(pos=self.pos, size=self.size)
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="< BACK", size_hint_x=None, width=dp(80)); btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'day'))
        self.lbl_title = Label(text="TECHNIQUE", bold=True); header.add_widget(btn_back); header.add_widget(self.lbl_title)
        self.layout.add_widget(header)
        scroll = ScrollView(); content = GridLayout(cols=1, spacing=dp(20), size_hint_y=None, padding=dp(20))
        content.bind(minimum_height=content.setter('height'))
        self.lbl_assign = Label(markup=True, size_hint_y=None, color=get_color_from_hex(C_PRIMARY))
        self.lbl_desc = Label(markup=True, size_hint_y=None, color=get_color_from_hex(C_TEXT))
        self.lbl_cue = Label(markup=True, size_hint_y=None, color=get_color_from_hex(C_ALERT))
        content.add_widget(SectionHeader(text="ASSIGNMENT")); content.add_widget(self.lbl_assign)
        content.add_widget(SectionHeader(text="EXECUTION")); content.add_widget(self.lbl_desc)
        content.add_widget(SectionHeader(text="CUE")); content.add_widget(self.lbl_cue)
        scroll.add_widget(content); self.layout.add_widget(scroll); self.add_widget(self.layout)
    def load_ex(self, k, l):
        d = exercise_db.get(k)
        self.lbl_assign.text = f"[b]{l}[/b]"; self.lbl_assign.text_size=(Window.width-dp(40), None); self.lbl_assign.texture_update(); self.lbl_assign.height=self.lbl_assign.texture_size[1]+dp(10)
        self.lbl_desc.text = d['desc']; self.lbl_desc.text_size=(Window.width-dp(40), None); self.lbl_desc.texture_update(); self.lbl_desc.height=self.lbl_desc.texture_size[1]+dp(10)
        self.lbl_cue.text = f"[b]CUE:[/b] {d['cue']}"; self.lbl_cue.text_size=(Window.width-dp(40), None); self.lbl_cue.texture_update(); self.lbl_cue.height=self.lbl_cue.texture_size[1]+dp(10)

class SimpleTimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            self.bg_color = Color(*get_color_from_hex(C_CARD)); self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="< BACK", size_hint_x=None, width=dp(80)); btn_back.bind(on_release=lambda x: self.stop_go_back())
        self.lbl_status = Label(text="TIMER", bold=True); header.add_widget(btn_back); header.add_widget(self.lbl_status)
        self.layout.add_widget(header)
        self.lbl_timer = Label(text="00:00", font_size=dp(100), bold=True)
        self.layout.add_widget(self.lbl_timer)
        controls = BoxLayout(size_hint_y=None, height=dp(120), padding=dp(20), spacing=dp(20))
        self.btn_main = NeoButton(text="START", background_color_hex=COLOR_SPRINT_HEX, color_hex="#000000")
        self.btn_main.bind(on_release=self.toggle); controls.add_widget(self.btn_main)
        self.layout.add_widget(controls); self.add_widget(self.layout)
        self.total = 0; self.curr = 0; self.running = False; self.event = None; self.mode = "SIMPLE"; self.phase = 0
    def set_time(self, s, m="SIMPLE"):
        self.total = s; self.mode = m; self.curr = s; self.running = False; self.phase = 0
        if self.event: self.event.cancel()
        self.lbl_status.text = "SIDE 1 (L)" if m == "SIDEPLANK" else "TIMER"; self.update_display()
    def toggle(self, *a):
        if self.running: self.running = False; self.btn_main.text = "RESUME"; self.event.cancel()
        else: self.running = True; self.btn_main.text = "PAUSE"; self.event = Clock.schedule_interval(self.update, 1)
    def update(self, dt):
        self.curr -= 1
        if self.curr <= 0:
            if self.mode == "SIDEPLANK" and self.phase == 0:
                self.phase = 1; self.curr = 10; self.lbl_status.text = "BREAK"
                if audio_manager: audio_manager.play('buzzer')
            elif self.mode == "SIDEPLANK" and self.phase == 1:
                self.phase = 2; self.curr = self.total; self.lbl_status.text = "SIDE 2 (R)"
                if audio_manager: audio_manager.play('beep')
            else:
                self.running = False; self.event.cancel(); self.lbl_status.text = "DONE"
                if audio_manager: audio_manager.play('beep')
        self.update_display()
    def update_display(self): m, s = divmod(self.curr, 60); self.lbl_timer.text = f"{m:02d}:{s:02d}"
    def stop_go_back(self):
        if self.event: self.event.cancel()
        self.manager.current = 'day'

class AirBikeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            self.bg_color = Color(*get_color_from_hex(C_CARD)); self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="<", size_hint_x=None, width=dp(50)); btn_back.bind(on_release=lambda x: self.stop_go_back())
        header.add_widget(btn_back); header.add_widget(Label(text="AIR BIKE", bold=True)); self.layout.add_widget(header)
        self.lbl_info = Label(text="READY?", font_size=dp(20), color=get_color_from_hex(C_PRIMARY))
        self.lbl_timer = Label(text="20:00", font_size=dp(80), bold=True)
        self.layout.add_widget(self.lbl_info); self.layout.add_widget(self.lbl_timer)
        controls = BoxLayout(size_hint_y=None, height=dp(100), padding=dp(20), spacing=dp(20))
        self.btn_main = NeoButton(text="START", background_color_hex=COLOR_SPRINT_HEX, color_hex="#000000")
        self.btn_main.bind(on_release=self.toggle); controls.add_widget(self.btn_main)
        self.layout.add_widget(controls); self.add_widget(self.layout)
        self.routine = self._build(); self.idx = 0; self.curr = 0; self.event = None
    def _build(self):
        r = [("READY", 5, "GET READY"), ("WARMUP", 150, "WARM UP: BUILD (50-60%)"), ("SPRINT", 5, "SPRINT: 80-90%")]
        r += [("WARMUP", 25, "WARM UP"), ("SPRINT", 5, "SPRINT"), ("WARMUP", 25, "WARM UP"), ("SPRINT", 5, "SPRINT"), ("WARMUP", 25, "WARM UP")]
        r += [("WORK", 90, "PHASE 1: 70% THRESHOLD"), ("SPRINT", 15, "PHASE 1: 90% SPRINT"), ("WORK", 75, "PHASE 1: 70%")]
        r += [("SPRINT", 15, "ARMS ONLY"), ("WORK", 45, "HEAVY GRIND"), ("SPRINT", 15, "ARMS ONLY"), ("WORK", 45, "HEAVY GRIND")]
        for i in range(1, 5): r += [("SPRINT", 20, f"PHASE 3: SPRINT {i}/4"), ("WARMUP", 10, f"PHASE 3: CRUISE")]
        r += [("REST", 120, "RECOVERY: 40%")]
        for i in range(1, 5): r += [("SPRINT", 20, f"INTERVAL {i}/4 MAX"), ("REST", 40, f"REST")]
        r += [("WARMUP", 180, "COOLDOWN: LIGHT FLUSH"), ("DONE", 0, "COMPLETE")]
        return r
    def toggle(self, *a):
        if self.event: self.event.cancel(); self.event=None; self.btn_main.text="RESUME"
        else:
            self.btn_main.text="STOP"
            if self.curr == 0: self.load_step()
            self.event = Clock.schedule_interval(self.update, 1)
    def load_step(self):
        t, d, i = self.routine[self.idx]; self.curr = d; self.lbl_info.text = i; self.update_display()
    def update(self, dt):
        self.curr -= 1
        if self.curr < 0:
            self.idx += 1
            if self.idx < len(self.routine):
                self.load_step()
                if audio_manager: audio_manager.play('beep')
            else: self.event.cancel(); self.lbl_info.text="DONE"
        self.update_display()
    def update_display(self): m, s = divmod(self.curr, 60); self.lbl_timer.text = f"{m:02d}:{s:02d}"
    def stop_go_back(self):
        if self.event: self.event.cancel()
        self.manager.current = 'home'

class Loop30Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            self.bg_color = Color(*get_color_from_hex(C_CARD)); self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="< BACK", size_hint_x=None, width=dp(80)); btn_back.bind(on_release=lambda x: self.stop_go_back())
        self.lbl_title = Label(text="LOOP TIMER", bold=True); header.add_widget(btn_back); header.add_widget(self.lbl_title)
        self.layout.add_widget(header)
        inputs = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(20))
        self.in_work = TextInput(text="30", multiline=False, input_filter='int', background_color=(0,0,0,1), foreground_color=(1,1,1,1))
        self.in_rest = TextInput(text="2", multiline=False, input_filter='int', background_color=(0,0,0,1), foreground_color=(1,1,1,1))
        inputs.add_widget(Label(text="W:")); inputs.add_widget(self.in_work); inputs.add_widget(Label(text="R:")); inputs.add_widget(self.in_rest)
        self.layout.add_widget(inputs)
        self.lbl_timer = Label(text="00:30", font_size=dp(80), bold=True); self.layout.add_widget(self.lbl_timer)
        controls = BoxLayout(size_hint_y=None, height=dp(100), padding=dp(20))
        self.btn_main = NeoButton(text="START", background_color_hex=COLOR_SPRINT_HEX, color_hex="#000000")
        self.btn_main.bind(on_release=self.toggle); controls.add_widget(self.btn_main)
        self.layout.add_widget(controls); self.add_widget(self.layout)
        self.curr = 30; self.running = False; self.event = None; self.phase = "WORK"
    def toggle(self, *a):
        if self.running: self.running = False; self.event.cancel(); self.btn_main.text = "RESUME"
        else: self.running = True; self.btn_main.text = "STOP"; self.event = Clock.schedule_interval(self.update, 1)
    def update(self, dt):
        self.curr -= 1
        if self.curr < 0:
            if self.phase == "WORK":
                self.phase = "REST"
                self.curr = int(self.in_rest.text)
                if audio_manager: audio_manager.play('buzzer')
            else:
                self.phase = "WORK"
                self.curr = int(self.in_work.text)
                if audio_manager: audio_manager.play('beep')
        m, s = divmod(self.curr, 60); self.lbl_timer.text = f"{m:02d}:{s:02d}"
    def stop_go_back(self):
        if self.event: self.event.cancel()
        self.manager.current = 'home'

class EditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(*get_color_from_hex(C_BG_MAIN)); Rectangle(pos=self.pos, size=self.size)
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        btn_back = NeoButton(text="<", size_hint_x=None, width=dp(50)); btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        btn_save = NeoButton(text="SAVE", background_color_hex=C_PRIMARY, color_hex="#000000")
        btn_save.bind(on_release=self.save)
        header.add_widget(btn_back); header.add_widget(Label(text="PROFILE")); header.add_widget(btn_save); self.layout.add_widget(header)
        scroll = ScrollView(); content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(20))
        content.bind(minimum_height=content.setter('height')); self.inputs = {}
        content.add_widget(SectionHeader(text="WEEK")); self.in_w = TextInput(text=str(user_profile['current_week']), multiline=False, size_hint_y=None, height=dp(40))
        content.add_widget(self.in_w)
        for k, v in user_profile['maxes'].items():
            content.add_widget(Label(text=k, color=get_color_from_hex(C_SUB), size_hint_y=None, height=dp(20), halign='left'))
            inp = TextInput(text=str(v), multiline=False, size_hint_y=None, height=dp(40)); self.inputs[k] = inp; content.add_widget(inp)
        scroll.add_widget(content); self.layout.add_widget(scroll); self.add_widget(self.layout)
    def save(self, *a):
        try:
            user_profile['current_week'] = int(self.in_w.text)
            for k, i in self.inputs.items(): user_profile['maxes'][k] = float(i.text)
            save_data(); self.manager.current = 'home'
        except: pass

class RehabApp(App):
    def build(self):
        global audio_manager; audio_manager = SoundManager()
        load_data(); sm = SwipeManager()
        sm.add_widget(HomeScreen(name='home')); sm.add_widget(DayScreen(name='day'))
        sm.add_widget(DetailScreen(name='detail')); sm.add_widget(EditScreen(name='edit'))
        sm.add_widget(AirBikeScreen(name='airbike')); sm.add_widget(SimpleTimerScreen(name='simple_timer'))
        sm.add_widget(Loop30Screen(name='loop30'))
        return sm
    def on_stop(self): save_data()

if __name__ == '__main__':
    RehabApp().run()

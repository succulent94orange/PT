import json
import os
import time
import math
import re
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
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader

# ==========================================
# 1. THEME & COLORS
# ==========================================
C_BG      = "#000000"
C_BG_SEC  = "#121212"
C_CARD    = "#1E1E1E"
C_CARD_HIT = "#333333"
C_PRIMARY = "#A020F0"
C_SEC     = "#00E5FF"
C_TEXT    = "#FFFFFF"
C_SUB     = "#AAAAAA"
C_ALERT   = "#FF5252"

COLOR_MENU_HEX   = '#2C3E50'
COLOR_SPRINT_HEX = '#27AE60'
COLOR_REST_HEX   = '#C0392B'
COLOR_DONE_HEX   = '#F39C12'
COLOR_BTN_BLUE_HEX = '#2980B9'

COLOR_MENU   = get_color_from_hex(COLOR_MENU_HEX)
COLOR_SPRINT = get_color_from_hex(COLOR_SPRINT_HEX)
COLOR_REST   = get_color_from_hex(COLOR_REST_HEX)
COLOR_DONE   = get_color_from_hex(COLOR_DONE_HEX)
COLOR_BTN_BLUE = get_color_from_hex(COLOR_BTN_BLUE_HEX)
COLOR_CTRL_BG = (0, 0, 0, 0.6)

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
        print("Data Saved")
        return True
    except: return False

def parse_duration(text):
    if "Air Bike" in text or "Assault Bike" in text:
        return "AIRBIKE"
    text = text.lower()
    match = re.search(r'\((\d+)\s*(m|min|mins|sec|s)\)', text)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if 'm' in unit: return val * 60
        return val
    return None

# ==========================================
# 3. EXERCISE LOGIC
# ==========================================
exercise_db = {
    "Bird Dog": {"desc": "Hands/knees. Brace core. Extend opposite limbs.", "cue": "Punch heel back. Keep spine stiff."},
    "Side Plank": {"desc": "Lie on side. Lift hips. Hold.", "cue": "Push floor away. Concave side focus."},
    "Pallof Press": {"desc": "Kneel on one knee. Press band forward.", "cue": "Kneel on 'Tight Right' knee."},
    "Glute Bridge": {"desc": "Back on floor. Lift hips.", "cue": "Squeeze glutes BEFORE lifting."},
    "Cat-Cow": {"desc": "Arch/Round spine slowly.", "cue": "Move one vertebrae at a time."},
    "90/90 Hip Flow": {"desc": "Sit with legs 90-deg. Lean forward/back.", "cue": "Focus on Right Hip restriction."},
    "Adductor Rock Back": {"desc": "One leg out to side. Rock back.", "cue": "ESSENTIAL before BJJ."},
    "Couch Stretch": {"desc": "Knee near wall. Squeeze glute.", "cue": "Don't arch back. 30s each."},
    "Malasana Squat": {"desc": "Deep squat. Breathe.", "cue": "Visualize pelvic floor dropping."},
    "Relaxation Breathing": {
        "desc": "1. Lie on your back, knees bent. Hand on belly.\n2. Inhale DEEP expanding BELLY (not chest).\n3. Visualize pelvic floor bulging downward (like pushing out urine gently).\n4. Exhale passively. Do NOT push hard.",
        "cue": "Down-regulates pelvic tone. Essential for recovery."
    },
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
    "Assault Bike Sprint": {"desc": "Max effort sprint.", "cue": "Do cool-down immediately after."},
    "Plank": {"desc": "Hold body straight.", "cue": "Squeeze glutes."}
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
    if day == "Monday":
        return ["WARMUP", "Cat-Cow (30 reps)", "Glute Bridge (2 sets x 15 reps)", 
                "SUPERSET A", f"Hack Squat (3 sets x 8 reps) {get_weight('Hack Squat')}", "Box Jumps (3 sets x 5 reps)",
                "SUPERSET B", f"Trap Bar Farmers Walk (3 sets x 40 yds) {get_weight('Trap Bar Farmers Walk')}", "Air Bike Protocol (See Timer)",
                "FINISHER", f"Seated Leg Curl (3 sets x 15 reps) {get_weight('Seated Leg Curl')}", "COOL DOWN", "90/90 Hip Flow (2 mins)"]
    elif day == "Wednesday":
        return ["WARMUP", "Pallof Press (3 sets x 10/side)", "Side Plank (3 sets x 60s/side)",
                "SUPERSET A", f"Dumbbell Bench Press (3 sets x 10 reps) {get_weight('Dumbbell Bench Press')}", f"Cable Row (3 sets x 12 reps) {get_weight('Cable Row')}",
                "SUPERSET B", f"Tricep Pushdowns (3 sets x 15 reps) {get_weight('Tricep Pushdowns')}", f"Cable Face Pulls (3 sets x 15 reps) {get_weight('Cable Face Pulls')}",
                "CARDIO", "Air Bike Protocol (See Timer)"]
    elif day == "Friday":
        return ["WARMUP", "Bird Dog (3 sets x 10/side)", "Split Squat BW (2 sets x 5/side)",
                "CIRCUIT (3 Rounds)", f"1. Unilateral Leg Press (10 reps/side) {get_weight('Unilateral Leg Press')}", f"2. Cable Woodchoppers (12 reps/side) {get_weight('Cable Woodchoppers')}",
                f"3. Leg Extension (15 reps) {get_weight('Leg Extension')}", "4. Plank (1 min)", "COOL DOWN", "Couch Stretch (3 sets x 30s/side)"]
    elif day in ["Tuesday", "Thursday", "Saturday"]:
        return ["PRE-COMBAT", "Lower Body Warm-Up (1 Round)", "Adductor Rock Back (1 min)", "ACTIVITY", "BJJ / Kickboxing Class", "POST-COMBAT", "Relaxation Breathing (5 mins)", "Malasana Squat (2 mins)"]
    return ["Active Recovery", "Walk 45 Mins", "Meal Prep"]

# ==========================================
# 4. KIVY UI COMPONENTS
# ==========================================

class SectionHeader(Label):
    def __init__(self, text, **kwargs):
        super().__init__(text=text, **kwargs)
        self.font_size = dp(14)
        self.color = get_color_from_hex(C_SEC)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(40)
        self.text_size = (Window.width - dp(30), None)
        self.halign = 'left'
        self.valign = 'middle' # Center vertically

class SmartCard(BoxLayout):
    def __init__(self, command=None, bg_color=get_color_from_hex(C_CARD), **kwargs):
        super().__init__(**kwargs)
        self.command = command
        self.orientation = 'horizontal'
        self.padding = dp(15) # Increased padding
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(90) # Taller cards for better spacing
        self.bg_color = bg_color
        self.default_color = bg_color
        self.hit_color = get_color_from_hex(C_CARD + "AA")
        self.press_pos = None

        with self.canvas.before:
            self.rect_color = Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.press_pos = touch.pos
            self.rect_color.rgba = self.hit_color
            return super().on_touch_down(touch)
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.press_pos:
            dist = math.hypot(touch.x - self.press_pos[0], touch.y - self.press_pos[1])
            if dist < dp(20): 
                # Check children first
                for child in self.walk():
                    if isinstance(child, Button) and child.collide_point(*touch.pos):
                        self.rect_color.rgba = self.default_color
                        return super().on_touch_up(touch)
                
                if self.command: self.command()
        
        self.rect_color.rgba = self.default_color
        self.press_pos = None
        return super().on_touch_up(touch)

class TouchScroll(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_type = ['bars', 'content']
        self.bar_width = dp(4)

# ==========================================
# 5. GESTURE & SCREENS
# ==========================================

class SwipeManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_start_x = 0
        self.last_exit_attempt = 0
        self.toast_label = None

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        dx = touch.x - self.touch_start_x
        if dx > Window.width * 0.25 and abs(touch.dy) < dp(50):
            self.handle_back_gesture()
        return super().on_touch_up(touch)

    def handle_back_gesture(self):
        try:
            current = self.current
            if current == 'home':
                now = time.time()
                if now - self.last_exit_attempt < 2.0:
                    self.exit_app()
                else:
                    self.show_toast("Swipe again to exit")
                    self.last_exit_attempt = now
            elif current != 'home':
                self.transition = SlideTransition(direction='right')
                self.current = 'home'
        except: pass

    def show_toast(self, text):
        if not self.toast_label:
            self.toast_label = Label(text=text, size_hint=(None, None), size=(dp(200), dp(50)),
                                     pos_hint={'center_x': 0.5, 'y': 0.1}, color=get_color_from_hex(C_TEXT))
            with self.toast_label.canvas.before:
                Color(0.2, 0.2, 0.2, 0.9)
                self.rect = Rectangle(size=self.toast_label.size, pos=self.toast_label.pos)
            self.toast_label.bind(pos=self.update_rect, size=self.update_rect)
            Window.add_widget(self.toast_label)
            Clock.schedule_once(self.remove_toast, 2)
            
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def remove_toast(self, dt):
        if self.toast_label:
            Window.remove_widget(self.toast_label)
            self.toast_label = None

    def exit_app(self):
        save_data()
        App.get_running_app().stop()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(5), spacing=dp(5))
        btn_prev = Button(text="<", size_hint_x=None, width=dp(50), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_prev.bind(on_release=self.prev_week)
        self.lbl_week = Label(text=f"WEEK {user_profile['current_week']}", font_size=dp(20), bold=True, color=get_color_from_hex(C_PRIMARY))
        btn_next = Button(text=">", size_hint_x=None, width=dp(50), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_next.bind(on_release=self.next_week)
        btn_edit = Button(text="PROFILE", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_edit.bind(on_release=self.go_edit)
        
        self.header.add_widget(btn_prev)
        self.header.add_widget(self.lbl_week)
        self.header.add_widget(btn_next)
        self.header.add_widget(btn_edit)
        self.layout.add_widget(self.header)
        
        # Scroll List
        self.scroll = TouchScroll()
        self.list_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        subs = ["Lifting & Rehab", "Combat & Recovery", "Lifting & Rehab", "Combat & Recovery", "Lifting & Rehab", "Combat & Recovery", "Rest"]
        
        for i, day in enumerate(days):
            card = SmartCard(command=lambda d=day: self.go_day(d))
            # Text Content
            txt_box = BoxLayout(orientation='vertical', size_hint_x=0.8) # Give text more room
            txt_box.add_widget(Label(text=day, font_size=dp(20), bold=True, halign='left', valign='bottom', color=get_color_from_hex(C_TEXT), size_hint_y=0.6, text_size=(Window.width*0.7, None)))
            txt_box.add_widget(Label(text=subs[i], font_size=dp(14), color=get_color_from_hex(C_SUB), size_hint_y=0.4, halign='left', valign='top', text_size=(Window.width*0.7, None)))
            
            card.add_widget(txt_box)
            # Arrow
            card.add_widget(Label(text=">", font_size=dp(24), bold=True, size_hint_x=0.2, color=get_color_from_hex(C_SEC), halign='center', valign='middle'))
            self.list_layout.add_widget(card)
            
        # Timers
        self.list_layout.add_widget(SectionHeader(text="TIMERS"))
        
        btn_ab = SmartCard(command=self.go_airbike)
        # Vertical alignment for timer card content
        ab_box = BoxLayout(orientation='vertical', size_hint_x=1)
        ab_box.add_widget(Label(text="AIR BIKE TIMER", font_size=dp(18), bold=True, color=get_color_from_hex(C_TEXT), halign='left', valign='middle', text_size=(Window.width*0.8, None)))
        ab_box.add_widget(Label(text="20 Min Interval Routine", font_size=dp(14), color=get_color_from_hex(C_SUB), halign='left', valign='middle', text_size=(Window.width*0.8, None)))
        btn_ab.add_widget(ab_box)
        self.list_layout.add_widget(btn_ab)
        
        btn_lp = SmartCard(command=self.go_loop)
        lp_box = BoxLayout(orientation='vertical', size_hint_x=1)
        lp_box.add_widget(Label(text="LOOP TIMER", font_size=dp(18), bold=True, color=get_color_from_hex(C_TEXT), halign='left', valign='middle', text_size=(Window.width*0.8, None)))
        lp_box.add_widget(Label(text="Custom Interval (Default 30s/2s)", font_size=dp(14), color=get_color_from_hex(C_SUB), halign='left', valign='middle', text_size=(Window.width*0.8, None)))
        btn_lp.add_widget(lp_box)
        self.list_layout.add_widget(btn_lp)
            
        self.scroll.add_widget(self.list_layout)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.lbl_week.text = f"WEEK {user_profile['current_week']}"

    def next_week(self, instance):
        if user_profile['current_week'] < 6: user_profile['current_week'] += 1
        else: user_profile['current_week'] = 1
        save_data()
        self.lbl_week.text = f"WEEK {user_profile['current_week']}"

    def prev_week(self, instance):
        if user_profile['current_week'] > 1: user_profile['current_week'] -= 1
        else: user_profile['current_week'] = 6
        save_data()
        self.lbl_week.text = f"WEEK {user_profile['current_week']}"

    def go_day(self, day):
        self.manager.get_screen('day').load_day(day)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'day'

    def go_edit(self, instance):
        self.manager.transition = SlideTransition(direction='up')
        self.manager.current = 'edit'
        
    def go_airbike(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'airbike'
        
    def go_loop(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'loop30'

class DayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_back = Button(text="< BACK", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_back.bind(on_release=self.go_back)
        self.lbl_title = Label(text="DAY", font_size=dp(20), bold=True)
        header.add_widget(btn_back)
        header.add_widget(self.lbl_title)
        self.layout.add_widget(header)
        self.scroll = TouchScroll()
        self.content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def load_day(self, day):
        self.lbl_title.text = day.upper()
        self.content.clear_widgets()
        workout = get_workout(day)
        for line in workout:
            if line.isupper() and " " not in line: 
                self.content.add_widget(SectionHeader(text=line))
            elif any(x in line for x in ["WARMUP", "SUPERSET", "COOL", "COMBAT", "FINISHER", "CIRCUIT", "CARDIO", "ACCESSORY"]):
                 self.content.add_widget(SectionHeader(text=line))
            else:
                # Workout Item Row
                ex_key = None
                for k in exercise_db:
                    if k in line: ex_key = k
                
                # If timer is needed
                duration = parse_duration(line)
                
                # Card Container
                # If we have a timer, the card logic needs to be careful not to overlap the button
                # So we make the card just a layout, and add a button for details and a button for timer
                
                card_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=dp(5))
                
                # Main Details Area (Clickable)
                details_btn = Button(
                    text=line,
                    background_normal='',
                    background_color=get_color_from_hex(C_CARD) if ex_key else get_color_from_hex(C_BG),
                    color=get_color_from_hex(C_TEXT if ex_key else C_SUB),
                    halign='left',
                    valign='middle',
                    text_size=(Window.width - (dp(100) if duration else dp(40)), None) # Adjust text width based on if timer exists
                )
                
                if ex_key:
                    details_btn.bind(on_release=lambda x, k=ex_key, l=line: self.go_detail(k, l))
                
                card_layout.add_widget(details_btn)

                # Timer Button (Purple)
                if duration:
                    t_btn = Button(
                        text="TIMER", 
                        size_hint_x=None, 
                        width=dp(70), 
                        background_normal='', 
                        background_color=get_color_from_hex(C_PRIMARY), 
                        bold=True
                    )
                    if duration == "AIRBIKE":
                        t_btn.bind(on_release=lambda x: self.go_airbike())
                    else:
                        t_btn.bind(on_release=lambda x, t=duration: self.go_simple_timer(t))
                    card_layout.add_widget(t_btn)

                self.content.add_widget(card_layout)

    def go_detail(self, key, line):
        if key == "Air Bike Protocol":
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'airbike'
        else:
            self.manager.get_screen('detail').load_ex(key, line)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'detail'

    def go_simple_timer(self, seconds):
        self.manager.get_screen('simple_timer').set_time(seconds)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'simple_timer'

    def go_airbike(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'airbike'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_back = Button(text="< BACK", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_back.bind(on_release=self.go_back)
        self.lbl_title = Label(text="DETAILS", font_size=dp(20), bold=True)
        header.add_widget(btn_back)
        header.add_widget(self.lbl_title)
        self.layout.add_widget(header)
        self.scroll = TouchScroll()
        self.content = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(20))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.lbl_assign = Label(text="", markup=True, size_hint_y=None, text_size=(Window.width-dp(40), None), color=get_color_from_hex(C_PRIMARY))
        self.lbl_desc = Label(text="", markup=True, size_hint_y=None, text_size=(Window.width-dp(40), None))
        self.lbl_cue = Label(text="", markup=True, size_hint_y=None, text_size=(Window.width-dp(40), None), color=get_color_from_hex(C_ALERT))
        self.content.add_widget(SectionHeader(text="ASSIGNMENT"))
        self.content.add_widget(self.lbl_assign)
        self.content.add_widget(SectionHeader(text="TECHNIQUE"))
        self.content.add_widget(self.lbl_desc)
        self.content.add_widget(SectionHeader(text="MEDICAL CUE"))
        self.content.add_widget(self.lbl_cue)
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def load_ex(self, key, line):
        data = exercise_db.get(key)
        self.lbl_assign.text = f"[b]{line}[/b]"
        self.lbl_assign.texture_update()
        self.lbl_assign.height = self.lbl_assign.texture_size[1] + dp(10)
        self.lbl_desc.text = data['desc']
        self.lbl_desc.texture_update()
        self.lbl_desc.height = self.lbl_desc.texture_size[1] + dp(10)
        self.lbl_cue.text = data['cue']
        self.lbl_cue.texture_update()
        self.lbl_cue.height = self.lbl_cue.texture_size[1] + dp(10)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'day'

class SimpleTimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_back = Button(text="< BACK", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_back.bind(on_release=self.go_back)
        self.lbl_status = Label(text="TIMER", font_size=dp(20), bold=True)
        header.add_widget(btn_back)
        header.add_widget(self.lbl_status)
        self.layout.add_widget(header)
        self.lbl_timer = Label(text="00:00", font_size=dp(100), bold=True)
        self.layout.add_widget(self.lbl_timer)
        controls = BoxLayout(size_hint_y=None, height=dp(100), padding=dp(20), spacing=dp(20))
        self.btn_main = Button(text="START", background_normal='', background_color=COLOR_SPRINT, font_size=dp(24), bold=True)
        self.btn_main.bind(on_release=self.toggle)
        btn_reset = Button(text="RESET", background_normal='', background_color=COLOR_BTN_BLUE)
        btn_reset.bind(on_release=self.reset)
        controls.add_widget(self.btn_main)
        controls.add_widget(btn_reset)
        self.layout.add_widget(controls)
        self.add_widget(self.layout)
        self.total_time = 0
        self.current_time = 0
        self.running = False
        self.event = None

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def set_time(self, seconds):
        self.total_time = seconds
        self.reset(None)

    def toggle(self, instance):
        if self.running:
            self.running = False
            if self.event: self.event.cancel()
            self.btn_main.text = "RESUME"
            self.btn_main.background_color = COLOR_SPRINT
        else:
            self.running = True
            self.btn_main.text = "PAUSE"
            self.btn_main.background_color = COLOR_REST
            self.event = Clock.schedule_interval(self.update, 1)

    def reset(self, instance):
        self.running = False
        if self.event: self.event.cancel()
        self.current_time = self.total_time
        self.update_display()
        self.btn_main.text = "START"
        self.btn_main.background_color = COLOR_SPRINT
        self.bg_color.rgba = COLOR_MENU

    def update(self, dt):
        self.current_time -= 1
        if self.current_time <= 0:
            self.current_time = 0
            self.running = False
            if self.event: self.event.cancel()
            if audio_manager: audio_manager.play('beep')
            self.bg_color.rgba = COLOR_DONE
            self.btn_main.text = "DONE"
        self.update_display()

    def update_display(self):
        m, s = divmod(self.current_time, 60)
        self.lbl_timer.text = f"{m:02d}:{s:02d}"

    def go_back(self, instance):
        if self.event: self.event.cancel()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'day'

class EditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_cancel = Button(text="CANCEL", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_cancel.bind(on_release=self.go_back)
        btn_save = Button(text="SAVE", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_PRIMARY))
        btn_save.bind(on_release=self.save)
        header.add_widget(btn_cancel)
        header.add_widget(Label(text="PROFILE", bold=True))
        header.add_widget(btn_save)
        self.layout.add_widget(header)
        self.scroll = TouchScroll()
        self.content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(20))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.content.add_widget(SectionHeader(text="CURRENT WEEK"))
        self.in_week = TextInput(text=str(user_profile['current_week']), multiline=False, size_hint_y=None, height=dp(40))
        self.content.add_widget(self.in_week)
        self.content.add_widget(SectionHeader(text="1RM INPUTS (LBS)"))
        self.inputs = {}
        for k, v in user_profile['maxes'].items():
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70))
            box.add_widget(Label(text=k, color=get_color_from_hex(C_SUB), size_hint_y=None, height=dp(20), halign='left', text_size=(Window.width-dp(40), None)))
            inp = TextInput(text=str(v), multiline=False, size_hint_y=None, height=dp(40))
            box.add_widget(inp)
            self.content.add_widget(box)
            self.inputs[k] = inp
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def save(self, instance):
        try:
            user_profile['current_week'] = int(self.in_week.text)
            for k, inp in self.inputs.items():
                user_profile['maxes'][k] = float(inp.text)
            save_data()
            self.go_back(None)
        except: pass

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='down')
        self.manager.current = 'home'

class AirBikeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_back = Button(text="< BACK", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_back.bind(on_release=self.go_back)
        self.lbl_status = Label(text="AIR BIKE WORKOUT", font_size=dp(20), bold=True)
        header.add_widget(btn_back)
        header.add_widget(self.lbl_status)
        self.layout.add_widget(header)
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.lbl_timer = Label(text="20:00", font_size=dp(80), bold=True)
        self.lbl_info = Label(text="Tap Start", font_size=dp(20))
        self.lbl_step = Label(text="", font_size=dp(16), color=get_color_from_hex(C_SEC))
        content.add_widget(self.lbl_info)
        content.add_widget(self.lbl_step)
        content.add_widget(self.lbl_timer)
        self.layout.add_widget(content)
        controls = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(10))
        btn_prev = Button(text="PREV", background_normal='', background_color=COLOR_BTN_BLUE)
        btn_prev.bind(on_release=self.go_prev)
        self.btn_main = Button(text="START", background_normal='', background_color=COLOR_SPRINT, font_size=dp(20), bold=True)
        self.btn_main.bind(on_release=self.toggle_timer)
        btn_next = Button(text="SKIP", background_normal='', background_color=COLOR_BTN_BLUE)
        btn_next.bind(on_release=self.go_next)
        controls.add_widget(btn_prev)
        controls.add_widget(self.btn_main)
        controls.add_widget(btn_next)
        self.layout.add_widget(controls)
        self.add_widget(self.layout)
        self.routine = self._build_routine()
        self.current_step_index = 0
        self.time_remaining = 0
        self.timer_event = None

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _build_routine(self):
        r = []
        r.append(("READY", 5, "GET READY"))
        r.append(("WARMUP", 150, "WARM UP: BUILD (50-60%)"))
        r.append(("SPRINT", 5, "SPRINT: 80-90% EFFORT"))
        r.append(("WARMUP", 25, "WARM UP: 60% EFFORT"))
        r.append(("SPRINT", 5, "SPRINT: 80-90% EFFORT"))
        r.append(("WARMUP", 25, "WARM UP: 60% EFFORT"))
        r.append(("SPRINT", 5, "SPRINT: 80-90% EFFORT"))
        r.append(("WARMUP", 25, "WARM UP: 60% EFFORT"))
        r.append(("WORK", 90, "PHASE 1: 70% THRESHOLD")) 
        r.append(("SPRINT", 15, "PHASE 1: 90% SPRINT")) 
        r.append(("WORK", 75, "PHASE 1: 70% THRESHOLD")) 
        r.append(("SPRINT", 15, "ARMS ONLY: MAX EFFORT")) 
        r.append(("WORK", 45, "HEAVY RESISTANCE GRIND"))
        r.append(("SPRINT", 15, "ARMS ONLY: MAX EFFORT")) 
        r.append(("WORK", 45, "HEAVY RESISTANCE GRIND"))
        for i in range(1, 5):
            r.append(("SPRINT", 20, f"PHASE 3: SPRINT {i}/4"))
            r.append(("WARMUP", 10, f"PHASE 3: CRUISE {i}/4"))
        r.append(("REST", 120, "RECOVERY: 40%"))
        for i in range(1, 5):
            r.append(("SPRINT", 20, f"INTERVAL {i}/4 MAX"))
            r.append(("REST", 40, f"INTERVAL {i}/4 REST"))
        r.append(("WARMUP", 180, "COOLDOWN: LIGHT FLUSH"))
        r.append(("DONE", 0, "WORKOUT COMPLETE"))
        return r

    def go_back(self, instance):
        if self.timer_event: self.timer_event.cancel()
        self.manager.transition = SlideTransition(direction='right')
        # We need to know where we came from, but for now home/day
        self.manager.current = 'home'

    def toggle_timer(self, instance):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            self.btn_main.text = "RESUME"
            self.btn_main.background_color = COLOR_SPRINT
        else:
            self.btn_main.text = "STOP"
            self.btn_main.background_color = COLOR_REST
            if self.current_step_index == 0 and self.time_remaining == 0:
                self.load_step()
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def load_step(self):
        step_type, duration, info = self.routine[self.current_step_index]
        self.time_remaining = duration
        self.lbl_info.text = info
        self.lbl_step.text = f"STEP {self.current_step_index+1}/{len(self.routine)}"
        
        c = COLOR_MENU
        if step_type == "SPRINT": c = COLOR_SPRINT
        elif step_type == "REST": c = COLOR_REST
        elif step_type == "DONE": c = COLOR_DONE
        self.bg_color.rgba = c
        self.update_label()

    def update_timer(self, dt):
        self.time_remaining -= 1
        if self.time_remaining < 0:
            self.go_next(None)
        else:
            self.update_label()

    def update_label(self):
        m, s = divmod(self.time_remaining, 60)
        self.lbl_timer.text = f"{m:02d}:{s:02d}"

    def go_next(self, instance):
        if self.current_step_index < len(self.routine)-1:
            self.current_step_index += 1
            if audio_manager: audio_manager.play('beep')
            self.load_step()

    def go_prev(self, instance):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.load_step()

class Loop30Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        with self.layout.canvas.before:
            self.bg_color = Color(*COLOR_MENU)
            self.rect = Rectangle(size=(5000, 5000), pos=(0, 0))
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10))
        btn_back = Button(text="< MENU", size_hint_x=None, width=dp(80), background_normal='', background_color=get_color_from_hex(C_CARD))
        btn_back.bind(on_release=self.go_back)
        self.lbl_status = Label(text="LOOP TIMER", font_size=dp(20), bold=True)
        header.add_widget(btn_back)
        header.add_widget(self.lbl_status)
        self.layout.add_widget(header)

        inputs = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(20))
        self.in_work = TextInput(text="30", multiline=False, input_filter='int')
        self.in_rest = TextInput(text="2", multiline=False, input_filter='int')
        inputs.add_widget(Label(text="Work (s):"))
        inputs.add_widget(self.in_work)
        inputs.add_widget(Label(text="Rest (s):"))
        inputs.add_widget(self.in_rest)
        self.layout.add_widget(inputs)

        self.lbl_timer = Label(text="00:30", font_size=dp(80), bold=True)
        self.lbl_set = Label(text="SET: 1", font_size=dp(24), color=get_color_from_hex(C_SEC))
        self.layout.add_widget(self.lbl_set)
        self.layout.add_widget(self.lbl_timer)

        controls = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(10))
        self.btn_main = Button(text="START", background_normal='', background_color=COLOR_SPRINT, font_size=dp(20), bold=True)
        self.btn_main.bind(on_release=self.toggle)
        btn_skip = Button(text="SKIP", background_normal='', background_color=COLOR_BTN_BLUE)
        btn_skip.bind(on_release=self.skip)
        
        controls.add_widget(self.btn_main)
        controls.add_widget(btn_skip)
        self.layout.add_widget(controls)
        
        self.add_widget(self.layout)
        self.running = False
        self.phase = "WORK"
        self.time = 30
        self.event = None
        self.sets = 1

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_back(self, instance):
        if self.event: self.event.cancel()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def toggle(self, instance):
        if self.running:
            self.running = False
            if self.event: self.event.cancel()
            self.btn_main.text = "RESUME"
            self.btn_main.background_color = COLOR_SPRINT
        else:
            self.running = True
            self.btn_main.text = "STOP"
            self.btn_main.background_color = COLOR_REST
            self.event = Clock.schedule_interval(self.update, 1)

    def skip(self, instance):
        self.time = 0
        self.update(0)

    def update(self, dt):
        self.time -= 1
        if self.time < 0:
            if self.phase == "WORK":
                self.phase = "REST"
                self.time = int(self.in_rest.text)
                self.bg_color.rgba = COLOR_REST
                self.lbl_status.text = "REST"
                if audio_manager: audio_manager.play('buzzer')
            else:
                self.phase = "WORK"
                self.time = int(self.in_work.text)
                self.bg_color.rgba = COLOR_SPRINT
                self.lbl_status.text = "WORK"
                self.sets += 1
                self.lbl_set.text = f"SET: {self.sets}"
                if audio_manager: audio_manager.play('beep')
        
        m, s = divmod(self.time, 60)
        self.lbl_timer.text = f"{m:02d}:{s:02d}"

# ==========================================
# APP BUILDER
# ==========================================
class RehabApp(App):
    def build(self):
        global audio_manager
        audio_manager = SoundManager()
        Window.clearcolor = get_color_from_hex(C_BG)
        load_data()
        sm = SwipeManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DayScreen(name='day'))
        sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(EditScreen(name='edit'))
        sm.add_widget(AirBikeScreen(name='airbike'))
        sm.add_widget(Loop30Screen(name='loop30'))
        sm.add_widget(SimpleTimerScreen(name='simple_timer'))
        return sm
        
    def on_stop(self):
        save_data()
    
    def on_start(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Activity = PythonActivity.mActivity
                View = autoclass('android.view.View')
                Activity.getWindow().addFlags(View.KEEP_SCREEN_ON)
            except: pass

if __name__ == '__main__':
    RehabApp().run()
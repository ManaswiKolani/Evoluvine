import os

# Screen settings
WIDTH = 800
HEIGHT = 600
FPS = 70
TILE_SIZE = 20

# Game behavior
ORB_COUNT = 6
DANGER_RELOCATE_INTERVAL = 5000  
DEATH_DELAY = 1000 

# Asset paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
BG_PATH = os.path.join(ASSETS_DIR, "background.PNG")
ICON_PATH = os.path.join(ASSETS_DIR, "danger_sprite2.PNG")
TITLE_CARD_PATH = os.path.join(ASSETS_DIR, "title_screen.PNG")
MUSIC_PATH = os.path.join(ASSETS_DIR, "serenity_sound.mp3")
SNAKE_LIVE_PATH = os.path.join(ASSETS_DIR, "snake_live.PNG")
SNAKE_DEAD_PATH = os.path.join(ASSETS_DIR, "snake_dead.PNG")


# Models Path
BRAIN_DIR = os.path.join(BASE_DIR, "..", "src", "Brain")
MODEL_DIR = os.path.join(BRAIN_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.pkl")


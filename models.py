import random
import json
import os
import sys

COLS, ROWS = 3, 3
NUM_SPRITES = 4
STATS_FILE = "assets/stats.json"
IS_WEB = sys.platform == "emscripten"


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.current_sprite = random.randint(0, NUM_SPRITES - 1)
        self.spinning = False
        self.spin_timer = 0.0
        self.spin_duration = 0.0
        self.elapsed = 0.0
        self.display_sprite = self.current_sprite
        self.target_sprite = self.current_sprite

    def start_spin(self):
        if self.spinning:
            return
        self.spinning = True
        self.spin_timer = 0.0
        self.spin_duration = random.uniform(2.0, 4.0)
        self.elapsed = 0.0
        self.target_sprite = random.randint(0, NUM_SPRITES - 1)

    def update(self, dt):
        if not self.spinning:
            return
        self.elapsed += dt
        p = min(self.elapsed / self.spin_duration, 1.0)
        interval = 0.125 + p * p * 0.5
        self.spin_timer += dt
        if self.spin_timer >= interval:
            self.spin_timer -= interval
            self.display_sprite = (self.display_sprite + 1) % NUM_SPRITES
        if self.elapsed >= self.spin_duration:
            self.spinning = False
            self.display_sprite = self.target_sprite
            self.current_sprite = self.target_sprite


class StatsManager:
    def __init__(self):
        self.games_played = 0
        self.total_clicks = 0
        self.clicks_history = []
        self.times_history = []
        self.cell_clicks = [0] * 9
        self.sprite_wins = [0] * NUM_SPRITES
        self.current_streak = 0
        self.best_streak = 0
        self.total_play_time = 0.0
        self.load()

    @property
    def avg_clicks(self):
        return self.total_clicks / self.games_played if self.games_played else 0.0

    @property
    def max_clicks(self):
        return max(self.clicks_history) if self.clicks_history else 0

    @property
    def min_clicks(self):
        return min(self.clicks_history) if self.clicks_history else 0

    @property
    def avg_time(self):
        return self.total_play_time / self.games_played if self.games_played else 0.0

    @property
    def fastest_win(self):
        return min(self.times_history) if self.times_history else 0.0

    @property
    def slowest_win(self):
        return max(self.times_history) if self.times_history else 0.0

    def record_game(self, clicks, time_sec, cell_clicks, win_sprite):
        self.games_played += 1
        self.total_clicks += clicks
        self.clicks_history.append(clicks)
        self.times_history.append(time_sec)
        for i in range(9):
            self.cell_clicks[i] += cell_clicks[i]
        self.sprite_wins[win_sprite] += 1
        self.current_streak += 1
        self.best_streak = max(self.best_streak, self.current_streak)
        self.total_play_time += time_sec
        self.save()

    def load(self):
        try:
            if IS_WEB:
                import platform
                raw = platform.window.localStorage.getItem("michislot_stats")
                if raw is None:
                    return
                d = json.loads(raw)
            else:
                if not os.path.exists(STATS_FILE):
                    return
                with open(STATS_FILE) as f:
                    d = json.load(f)
            self.games_played = d.get('games_played', 0)
            self.total_clicks = d.get('total_clicks', 0)
            self.clicks_history = d.get('clicks_history', [])
            self.times_history = d.get('times_history', [])
            self.cell_clicks = d.get('cell_clicks', [0] * 9)
            self.sprite_wins = d.get('sprite_wins', [0] * NUM_SPRITES)
            self.current_streak = d.get('current_streak', 0)
            self.best_streak = d.get('best_streak', 0)
            self.total_play_time = d.get('total_play_time', 0.0)
        except Exception:
            pass

    def save(self):
        d = {
            'games_played': self.games_played,
            'total_clicks': self.total_clicks,
            'clicks_history': self.clicks_history,
            'times_history': self.times_history,
            'cell_clicks': self.cell_clicks,
            'sprite_wins': self.sprite_wins,
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'total_play_time': self.total_play_time,
        }
        if IS_WEB:
            import platform
            platform.window.localStorage.setItem("michislot_stats", json.dumps(d))
        else:
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            with open(STATS_FILE, 'w') as f:
                json.dump(d, f, indent=2)


def all_same(cells):
    return all(c.current_sprite == cells[0].current_sprite for c in cells)


def all_stopped(cells):
    return all(not c.spinning for c in cells)


def fmt_time(secs):
    if secs >= 60:
        m = int(secs // 60)
        return f"{m}:{secs % 60:05.2f}"
    return f"{secs:.1f}s"

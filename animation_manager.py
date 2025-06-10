# animation_manager.py

from matplotlib.animation import FuncAnimation

class AnimationManager:
    def __init__(self, fig, update_func, frames_range, interval_ms=100):
        self.animation = None
        self.is_running = False
        self.fig = fig
        self.update_func = update_func
        self.frames_range = frames_range
        self.interval_ms = interval_ms

    def start(self):
        if self.is_running:
            return
        self.animation = FuncAnimation(
            self.fig,
            self.update_func,
            frames=self.frames_range,
            interval=self.interval_ms,
            blit=True,
            repeat=False
        )
        self.is_running = True
        self.fig.canvas.draw_idle() 

    def pause(self):
        if self.animation and self.is_running:
            # self.animation.event_source.stop()
            self.is_running = False

    def stop(self):
        if self.animation:
            # self.animation.event_source.stop()
            self.animation = None
            self.is_running = False
        

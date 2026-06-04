from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.core.window import Window
import math

Window.size = (1280, 720)

WORLD = [
    "111111111111111",
    "1.............1",
    "1..2222.......1",
    "1.............1",
    "1.....3333....1",
    "1.............1",
    "1...4444......1",
    "1.............1",
    "1.............1",
    "111111111111111"
]


class RaycastGame(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player_x = 2.5
        self.player_y = 2.5
        self.player_angle = 0

        

        self.player_radius = 0.2

        self.move_speed = 3.0

        self.fov = math.pi / 3
        self.num_rays = 160
        self.max_depth = 16

        self.joy_radius = 80
        self.knob_radius = 35

        self.look_sensitivity = 0.01

        self.show_settings = False

        self.joy_x = 130
        self.joy_y = 130

        self.joy_dx = 0
        self.joy_dy = 0

        self.dragging_joystick = False

        Clock.schedule_interval(self.update, 1 / 60)

    def is_wall(self, tile):
        return tile != "."

    def can_move(self, x, y):

        corners = [
            (x - self.player_radius, y - self.player_radius),
            (x + self.player_radius, y - self.player_radius),
            (x - self.player_radius, y + self.player_radius),
            (x + self.player_radius, y + self.player_radius)
        ]

        for px, py in corners:

            mx = int(px)
            my = int(py)

            if mx < 0 or my < 0:
                return False

            if my >= len(WORLD):
                return False

            if mx >= len(WORLD[0]):
                return False

            if self.is_wall(WORLD[my][mx]):
                return False

        return True

    def on_touch_down(self, touch):

        if math.hypot(
            touch.x - self.joy_x,
            touch.y - self.joy_y
        ) <= self.joy_radius:

            self.dragging_joystick = True
            return True
        if (
    self.width - 160 <= touch.x <= self.width - 20 and
    self.height - 80 <= touch.y <= self.height - 20
    ):
            
            self.change_sensitivity()
        return True
            

        touch.ud["camera"] = True
        return True
    def change_sensitivity(self):

        if self.look_sensitivity == 0.01:
            self.look_sensitivity = 0.02

        elif self.look_sensitivity == 0.02:
            self.look_sensitivity = 0.05

        else:
            self.look_sensitivity = 0.01


    def on_touch_move(self, touch):

        if self.dragging_joystick:

            dx = touch.x - self.joy_x
            dy = touch.y - self.joy_y

            dist = math.hypot(dx, dy)

            if dist > self.joy_radius:
                dx *= self.joy_radius / dist
                dy *= self.joy_radius / dist

            self.joy_dx = dx / self.joy_radius
            self.joy_dy = dy / self.joy_radius

        else:
            self.player_angle += touch.dx * self.look_sensitivity


        return True

    def on_touch_up(self, touch):

        self.dragging_joystick = False

        self.joy_dx = 0
        self.joy_dy = 0

        return True

    def update(self, dt):

        forward = self.joy_dy
        strafe = -self.joy_dx

        fx = math.cos(self.player_angle)
        fy = math.sin(self.player_angle)

        sx = math.cos(self.player_angle + math.pi / 2)
        sy = math.sin(self.player_angle + math.pi / 2)

        nx = self.player_x + (
            fx * forward +
            sx * strafe
        ) * self.move_speed * dt

        ny = self.player_y + (
            fy * forward -
            sy * strafe
        ) * self.move_speed * dt

        if self.can_move(nx, self.player_y):
            self.player_x = nx

        if self.can_move(self.player_x, ny):
            self.player_y = ny

        self.render()

    def render(self):

        self.canvas.clear()

        width = self.width
        height = self.height

        with self.canvas:

            # sky
            Rectangle(
    pos=(0, height / 2 ),
    size=(width, height)
)
                # SETTINGS BUTTON
            Color(1, 1, 0)

            Rectangle(
        pos=(width - 160, height - 80),
        size=(140, 60)
            )
            # floor
            Color(0.25, 0.25, 0.25)
            Rectangle(
                pos=(0, 0),
                size=(width, height / 2)
            )

            for ray in range(self.num_rays):

                ray_angle = (
                    self.player_angle
                    - self.fov / 2
                    + self.fov * ray / self.num_rays
                )

                distance = 0
                wall_type = "1"

                while distance < self.max_depth:

                    tx = (
                        self.player_x
                        + math.cos(ray_angle) * distance
                    )

                    ty = (
                        self.player_y
                        + math.sin(ray_angle) * distance
                    )

                    mx = int(tx)
                    my = int(ty)

                    if (
                        mx < 0 or
                        my < 0 or
                        my >= len(WORLD) or
                        mx >= len(WORLD[0])
                    ):
                        break

                    tile = WORLD[my][mx]

                    if self.is_wall(tile):
                        wall_type = tile
                        break

                    distance += 0.05

                distance *= math.cos(
                    ray_angle - self.player_angle
                )

                wall_height = min(
                    height,
                    850 / (distance + 0.001)
                )

                shade = max(
                    40,
                    255 - int(distance * 18)
                )

                if wall_type == "1":
                    Color(shade / 255, 0, 0)

                elif wall_type == "2":
                    Color(0, shade / 255, 0)

                elif wall_type == "3":
                    Color(0, 0, shade / 255)

                else:
                    Color(
                        shade / 255,
                        0,
                        shade / 255
                    )

                x = ray * width / self.num_rays

                Rectangle(
    pos=(
        x,
        height / 2 - wall_height / 2 
    ),
    size=(
        width / self.num_rays + 2,
        wall_height
    )
)
                

                


            # ======================
            # CROSSHAIR
            # ======================

            Color(1, 1, 1)

            Rectangle(
                pos=(width / 2 - 2, height / 2 - 15 ),
                size=(4, 30)
            )

            Rectangle(
                pos=(width / 2 - 15, height / 2 - 2 ),
                size=(30, 4)
            )


            # minimap
            tile_size = 15

            for y, row in enumerate(WORLD):
                for x, cell in enumerate(row):

                    if cell == ".":
                        Color(0.9, 0.9, 0.9)

                    elif cell == "1":
                        Color(1, 0, 0)

                    elif cell == "2":
                        Color(0, 1, 0)

                    elif cell == "3":
                        Color(0, 0, 1)

                    else:
                        Color(1, 0, 1)

                    Rectangle(
                        pos=(
                            x * tile_size,
                            height - (y + 1) * tile_size
                        ),
                        size=(tile_size, tile_size)
                    )

            Color(1, 1, 0)
            Ellipse(
                pos=(
                    self.player_x * tile_size - 4,
                    height - self.player_y * tile_size - 4
                ),
                size=(8, 8)
            )

            # joystick base
            Color(0.3, 0.3, 0.3)
            Ellipse(
                pos=(
                    self.joy_x - self.joy_radius,
                    self.joy_y - self.joy_radius
                ),
                size=(
                    self.joy_radius * 2,
                    self.joy_radius * 2
                )
            )

            # joystick knob
            Color(0.85, 0.85, 0.85)
            Ellipse(
                pos=(
                    self.joy_x
                    + self.joy_dx * self.joy_radius
                    - self.knob_radius,

                    self.joy_y
                    + self.joy_dy * self.joy_radius
                    - self.knob_radius
                ),
                size=(
                    self.knob_radius * 2,
                    self.knob_radius * 2
                )
            )


class GameApp(App):
    def build(self):
        return RaycastGame()


if __name__ == "__main__":
    GameApp().run()

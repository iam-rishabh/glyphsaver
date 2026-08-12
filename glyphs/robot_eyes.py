import random
import tkinter as tk

from .base import Glyph


# ============================================================
# EYE HOUSING
#
# A chunky rounded-rectangle, drawn as a pixel mask - the
# classic OLED robot-eye silhouette (RoboEyes / Vector style).
# ============================================================

EYE_GRID = [
    "001111111100",
    "011111111110",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "111111111111",
    "011111111110",
    "001111111100",
]

EYE_COLS = len(EYE_GRID[0])
EYE_ROWS = len(EYE_GRID)

# ----------------------------------------------------
# The pupil is a separate solid block overlaid on top of
# the housing grid. It's positioned in housing-grid cells
# (not pixels), and rides along with the housing's own
# blink/squash transform, so it "closes" together with
# the lid instead of floating independently.
# ----------------------------------------------------

PUPIL_W = 4
PUPIL_H = 5

PUPIL_BASE_COL = (EYE_COLS - PUPIL_W) // 2
PUPIL_BASE_ROW = (EYE_ROWS - PUPIL_H) // 2

MAX_COL_OFFSET = PUPIL_BASE_COL - 1
MAX_ROW_OFFSET = PUPIL_BASE_ROW - 2


# ============================================================
# MOUTHS
# Small, centered, visually subordinate to the eyes.
# ============================================================

MOUTHS = {
    "smile": [
        "110000011",
        "011111110",
        "001111100",
    ],

    "grin": [
        "110000011",
        "111111111",
        "011111110",
    ],

    "small": [
        "0110110",
        "0011100",
    ],

    "flat": [
        "011111110",
    ],

    "o": [
        "0111110",
        "1111111",
        "1111111",
        "0111110",
    ],

    "smirk_l": [
        "111000000",
        "011111100",
        "001111111",
    ],

    "smirk_r": [
        "000000111",
        "001111110",
        "111111100",
    ],

    "pout": [
        "001111100",
        "011111110",
        "011000110",
    ],
}


# ============================================================
# DISCRETE GAZE GRID
#
# Eye tracking snaps between fixed points on a grid, like a
# scanner sweeping a matrix, rather than drifting continuously.
# ============================================================

GAZE_STEPS_X = (-1.0, -0.5, 0.0, 0.5, 1.0)
GAZE_STEPS_Y = (-0.6, -0.3, 0.0, 0.3, 0.6)

JITTER_STEPS = (-0.02, 0.0, 0.02)


# ============================================================
# EXPRESSION TIMELINE
#
#   neutral -> anticipation -> overshoot -> settle -> hold
#            -> rebound -> neutral
#
# Anticipation is a small move in the OPPOSITE direction right
# before the real move. Overshoot punches past the actual
# target, then settles back to it and holds. Rebound is a small
# bounce past neutral on the way back out.
# ============================================================

KEYFRAME_TIMES = (0.0, 0.10, 0.38, 0.52, 0.78, 0.90, 1.0)
KEYFRAME_KINDS = (
    "neutral",
    "anticipation",
    "overshoot",
    "target",
    "target",
    "rebound",
    "neutral",
)

ANTICIPATION_FACTOR = -0.22
OVERSHOOT_FACTOR = 1.30
REBOUND_FACTOR = -0.16

# Safety bounds so overshoot/anticipation can't invert a scale
# or fling a housing off the canvas.
BOUNDS = {
    "left_scale": (0.02, 1.9),
    "right_scale": (0.02, 1.9),
    "mouth_scale": (0.05, 2.1),
    "left_x": (-0.55, 0.55),
    "right_x": (-0.55, 0.55),
    "left_y": (-0.55, 0.55),
    "right_y": (-0.55, 0.55),
    "gaze_x": (-1.2, 1.2),
    "gaze_y": (-1.2, 1.2),
    "mouth_y": (-0.35, 0.35),
}


class RobotEyesGlyph(Glyph):

    name = "robot-eyes"

    description = (
        "Rounded-rectangle robot eye housings with a real moving "
        "pupil/eyeball, digital/stepped transitions, and bold "
        "anticipation-overshoot expressions"
    )

    # ========================================================
    # ARGUMENTS
    # ========================================================

    @classmethod
    def add_arguments(cls, parser):

        super().add_arguments(parser)

        parser.add_argument(
            "--eye-color",
            default="#00e5ff",
            help="Eye housing (sclera) color",
        )

        parser.add_argument(
            "--pupil-color",
            default="#081018",
            help="Pupil color",
        )

        parser.add_argument(
            "--mouth-color",
            default=None,
            help="Mouth color, defaults to eye color",
        )

        parser.add_argument(
            "--mouth",
            action="store_true",
            help="Enable animated mouth",
        )

        parser.add_argument(
            "--screen-fill",
            type=float,
            default=0.85,
            help="Target percentage of screen width used",
        )

        parser.add_argument(
            "--gap",
            type=float,
            default=0.035,
            help="Eye gap as fraction of screen width",
        )

        parser.add_argument(
            "--expression-interval",
            type=float,
            default=2.5,
            help="Average delay between expressions",
        )

        parser.add_argument(
            "--expression-speed",
            type=int,
            default=420,
            help="Approximate time in ms for a full expression beat",
        )

        parser.add_argument(
            "--transition-steps",
            type=int,
            default=3,
            help="Discrete levels each beat snaps through (lower = blockier)",
        )

        parser.add_argument(
            "--glitch-chance",
            type=float,
            default=0.04,
            help="Chance a pixel drops out per frame during a transition",
        )

        parser.add_argument(
            "--gaze-speed",
            type=float,
            default=0.08,
            help="Step size (grid units per tick) for eye-tracking motion",
        )

        parser.add_argument(
            "--clock-color",
            default="#606060",
            help="Clock color",
        )

        parser.add_argument(
            "--clock-size",
            type=int,
            default=18,
            help="Clock size",
        )

    # ========================================================
    # SETUP
    # ========================================================

    def setup(
        self,
        root,
        canvas,
        width,
        height,
    ):

        self.root = root
        self.canvas = canvas

        self.width = width
        self.height = height

        self.left_pixels = []
        self.right_pixels = []
        self.mouth_pixels = []

        self.clock_id = None

        self.state = self._neutral()

        self.event = None

        self.event_frame = 0
        self.event_frames = 1

        self.event_poses = []

        self.mouth_shape_current = "smile"
        self.mouth_shape_target = "smile"

        self.gaze_target_x = 0.0
        self.gaze_target_y = 0.0

        self.jitter_x = 0.0

        self._redraw()

        self._update_clock()

        self.root.after(
            20,
            self._tick,
        )

        self._schedule_expression()
        self._schedule_gaze()
        self._schedule_jitter()

        self.root.bind(
            "<Configure>",
            self._on_resize,
        )

    def _on_resize(self, event):
        if event.width < 100 or event.height < 100:
            return

        self.width = event.width
        self.height = event.height

        self._redraw()

    # ========================================================
    # NEUTRAL STATE
    # ========================================================

    def _neutral(self):

        return {
            "left_scale": 1.0,
            "right_scale": 1.0,

            "left_x": 0.0,
            "right_x": 0.0,

            "left_y": 0.0,
            "right_y": 0.0,

            "gaze_x": 0.0,
            "gaze_y": 0.0,

            "mouth_scale": 1.0,
            "mouth_y": 0.0,
        }

    NUMERIC_KEYS = (
        "left_scale",
        "right_scale",
        "left_x",
        "right_x",
        "left_y",
        "right_y",
        "gaze_x",
        "gaze_y",
        "mouth_scale",
        "mouth_y",
    )

    # ========================================================
    # LAYOUT
    # ========================================================

    def _layout(self):

        cols = EYE_COLS
        rows = EYE_ROWS

        gap = (
            self.width *
            self.args.gap
        )

        target_width = (
            self.width *
            self.args.screen_fill
        )

        pixel_by_width = (
            target_width - gap
        ) / (
            cols * 2
        )

        pixel_by_height = (
            self.height * 0.58
        ) / rows

        pixel = max(
            2,
            int(
                min(
                    pixel_by_width,
                    pixel_by_height,
                )
            ),
        )

        eye_width = cols * pixel
        eye_height = rows * pixel

        total_width = (
            eye_width * 2 +
            gap
        )

        center_x = self.width / 2

        left_x = (
            center_x -
            total_width / 2
        )

        right_x = (
            left_x +
            eye_width +
            gap
        )

        center_y = (
            self.height * 0.40
        )

        top_y = (
            center_y -
            eye_height / 2
        )

        return {
            "pixel": pixel,
            "eye_width": eye_width,
            "eye_height": eye_height,
            "left_x": left_x,
            "right_x": right_x,
            "top_y": top_y,
        }

    # ========================================================
    # EYE (housing + pupil, drawn together so the pupil rides
    # along with the housing's own blink/squash transform)
    # ========================================================

    def _draw_eye(
        self,
        x0,
        y0,
        pixel,
        scale,
        x_shift,
        y_shift,
        pupil_col0,
        pupil_row0,
        glitch=False,
    ):

        items = []

        rows = EYE_ROWS

        center_row = (
            rows - 1
        ) / 2

        scale = max(
            0.02,
            scale,
        )

        for row, data in enumerate(
            EYE_GRID
        ):

            transformed_row = (
                center_row +
                (
                    row -
                    center_row
                ) * scale
            )

            y = (
                y0 +
                transformed_row *
                pixel +
                y_shift
            )

            in_pupil_row = (
                pupil_row0
                <= row
                < pupil_row0 + PUPIL_H
            )

            for col, cell in enumerate(
                data
            ):

                if cell != "1":
                    continue

                # Matrix-style flicker: pixels drop out at
                # random during a transition, never at rest.
                if (
                    glitch
                    and random.random() <
                    self.args.glitch_chance
                ):
                    continue

                x = (
                    x0 +
                    col * pixel +
                    x_shift
                )

                gap = max(
                    1,
                    int(
                        pixel *
                        0.045
                    ),
                )

                in_pupil = (
                    in_pupil_row
                    and pupil_col0
                    <= col
                    < pupil_col0 + PUPIL_W
                )

                color = (
                    self.args.pupil_color
                    if in_pupil
                    else self.args.eye_color
                )

                items.append(
                    self.canvas.create_rectangle(
                        x + gap,
                        y + gap,
                        x + pixel - gap,
                        y + pixel - gap,
                        fill=color,
                        outline="",
                    )
                )

        return items

    # ========================================================
    # MOUTH
    # ========================================================

    def _draw_mouth(
        self,
        layout,
    ):

        if not self.args.mouth:
            return []

        grid = MOUTHS[
            self.mouth_shape_current
        ]

        pixel = layout["pixel"]

        mouth_pixel = max(
            2,
            int(
                pixel *
                0.82 *
                self.state["mouth_scale"]
            ),
        )

        width = (
            len(grid[0]) *
            mouth_pixel
        )

        x0 = (
            self.width / 2 -
            width / 2
        )

        y0 = (
            layout["top_y"] +
            layout["eye_height"] +
            pixel * 0.28 +
            self.state["mouth_y"] * pixel
        )

        color = (
            self.args.mouth_color
            or self.args.eye_color
        )

        items = []

        for row, data in enumerate(
            grid
        ):

            for col, cell in enumerate(
                data
            ):

                if cell != "1":
                    continue

                x = (
                    x0 +
                    col *
                    mouth_pixel
                )

                y = (
                    y0 +
                    row *
                    mouth_pixel
                )

                gap = max(
                    1,
                    int(
                        mouth_pixel *
                        0.06
                    ),
                )

                items.append(
                    self.canvas.create_rectangle(
                        x + gap,
                        y + gap,
                        x + mouth_pixel - gap,
                        y + mouth_pixel - gap,
                        fill=color,
                        outline="",
                    )
                )

        return items

    # ========================================================
    # REDRAW
    # ========================================================

    def _redraw(self):

        for group in (
            self.left_pixels,
            self.right_pixels,
            self.mouth_pixels,
        ):

            for item in group:
                self.canvas.delete(item)

        self.left_pixels = []
        self.right_pixels = []
        self.mouth_pixels = []

        layout = self._layout()

        pixel = layout["pixel"]

        glitch = self.event is not None

        # Pupil position in housing-grid cells, shared by both
        # eyes so they track the same point - this is the part
        # that actually reads as "eyeballs" rather than a
        # shifting shape.
        gaze_x = max(
            -1.0,
            min(
                1.0,
                self.state["gaze_x"],
            ),
        )

        gaze_y = max(
            -1.0,
            min(
                1.0,
                self.state["gaze_y"],
            ),
        )

        pupil_col0 = (
            PUPIL_BASE_COL
            + round(gaze_x * MAX_COL_OFFSET)
        )

        pupil_col0 = max(
            0,
            min(
                EYE_COLS - PUPIL_W,
                pupil_col0,
            ),
        )

        pupil_row0 = (
            PUPIL_BASE_ROW
            + round(gaze_y * MAX_ROW_OFFSET)
        )

        pupil_row0 = max(
            0,
            min(
                EYE_ROWS - PUPIL_H,
                pupil_row0,
            ),
        )

        self.left_pixels = (
            self._draw_eye(
                layout["left_x"],
                layout["top_y"],
                pixel,
                self.state["left_scale"],
                self.state["left_x"] * pixel,
                self.state["left_y"] * pixel,
                pupil_col0,
                pupil_row0,
                glitch=glitch,
            )
        )

        self.right_pixels = (
            self._draw_eye(
                layout["right_x"],
                layout["top_y"],
                pixel,
                self.state["right_scale"],
                self.state["right_x"] * pixel,
                self.state["right_y"] * pixel,
                pupil_col0,
                pupil_row0,
                glitch=glitch,
            )
        )

        self.mouth_pixels = (
            self._draw_mouth(
                layout
            )
        )

    # ========================================================
    # STEPPED TRANSITIONS
    # ========================================================

    @staticmethod
    def _stepped(t, steps):

        t = max(
            0.0,
            min(
                1.0,
                t,
            ),
        )

        if steps <= 1:
            return round(t)

        return (
            round(t * steps) / steps
        )

    @staticmethod
    def _step_toward(current, target, step):

        if abs(target - current) <= step:
            return target

        if target > current:
            return current + step

        return current - step

    # ========================================================
    # STATE SNAP
    # ========================================================

    def _interpolate_state(
        self,
        a,
        b,
        t,
    ):

        for key in self.NUMERIC_KEYS:

            self.state[key] = (
                a[key] +
                (
                    b[key] -
                    a[key]
                ) * t
            )

    # ========================================================
    # POSE SCALING (anticipation / overshoot / rebound)
    # ========================================================

    def _scaled_pose(self, target, factor):

        neutral = self._neutral()

        pose = {}

        for key in self.NUMERIC_KEYS:

            value = (
                neutral[key] +
                (
                    target[key] -
                    neutral[key]
                ) * factor
            )

            lo, hi = BOUNDS[key]

            pose[key] = max(
                lo,
                min(
                    hi,
                    value,
                ),
            )

        return pose

    def _build_keyframe_poses(self, target):

        poses = []

        for kind in KEYFRAME_KINDS:

            if kind == "neutral":
                poses.append(self._neutral())

            elif kind == "target":
                poses.append(target)

            elif kind == "anticipation":
                poses.append(
                    self._scaled_pose(
                        target,
                        ANTICIPATION_FACTOR,
                    )
                )

            elif kind == "overshoot":
                poses.append(
                    self._scaled_pose(
                        target,
                        OVERSHOOT_FACTOR,
                    )
                )

            elif kind == "rebound":
                poses.append(
                    self._scaled_pose(
                        target,
                        REBOUND_FACTOR,
                    )
                )

        return poses

    # ========================================================
    # EXPRESSION TARGETS
    # ========================================================

    def _expression(
        self,
        name,
    ):

        state = self._neutral()

        if name == "blink":

            state.update(
                left_scale=0.02,
                right_scale=0.02,
                mouth_scale=0.92,
            )

        elif name == "wink_left":

            state.update(
                left_scale=0.02,
                right_scale=1.05,
                gaze_x=0.14,
            )

        elif name == "wink_right":

            state.update(
                left_scale=1.05,
                right_scale=0.02,
                gaze_x=-0.14,
            )

        elif name == "side_left":

            state.update(
                left_scale=0.70,
                right_scale=0.78,
                gaze_x=-1.0,
                left_x=-0.10,
                right_x=-0.06,
                left_y=0.04,
                right_y=-0.03,
                mouth_scale=0.80,
            )

        elif name == "side_right":

            state.update(
                left_scale=0.78,
                right_scale=0.70,
                gaze_x=1.0,
                left_x=0.06,
                right_x=0.10,
                left_y=-0.03,
                right_y=0.04,
                mouth_scale=0.80,
            )

        elif name == "look_left":

            state.update(
                left_scale=0.85,
                right_scale=0.90,
                gaze_x=-1.0,
            )

        elif name == "look_right":

            state.update(
                left_scale=0.90,
                right_scale=0.85,
                gaze_x=1.0,
            )

        elif name == "skeptical":

            state.update(
                left_scale=0.36,
                right_scale=1.08,
                gaze_x=0.6,
                left_y=-0.22,
                right_y=0.16,
                mouth_scale=0.75,
            )

        elif name == "confused":

            state.update(
                left_scale=0.95,
                right_scale=0.32,
                gaze_x=-0.3,
                left_y=-0.24,
                right_y=0.22,
                mouth_y=0.15,
                mouth_scale=0.70,
            )

        elif name == "happy":

            state.update(
                left_scale=0.52,
                right_scale=0.53,
                gaze_y=-0.15,
                mouth_scale=1.45,
            )

        elif name == "laugh":

            state.update(
                left_scale=0.26,
                right_scale=0.28,
                gaze_y=-0.25,
                mouth_scale=1.65,
            )

        elif name == "sleepy":

            state.update(
                left_scale=0.28,
                right_scale=0.22,
                gaze_y=0.6,
                mouth_scale=0.58,
            )

        elif name == "surprised":

            state.update(
                left_scale=1.40,
                right_scale=1.40,
                gaze_y=-0.3,
                mouth_scale=1.35,
            )

        elif name == "shy":

            state.update(
                gaze_x=-0.6,
                gaze_y=0.6,
                left_scale=0.58,
                right_scale=0.72,
                mouth_scale=0.52,
                mouth_y=-0.09,
            )

        elif name == "pout":

            state.update(
                gaze_y=0.3,
                left_scale=0.76,
                right_scale=0.78,
                mouth_scale=0.78,
                mouth_y=-0.05,
            )

        elif name == "disappointed":

            state.update(
                left_scale=0.42,
                right_scale=0.38,
                gaze_y=0.6,
                mouth_scale=0.46,
                mouth_y=0.11,
            )

        elif name == "excited":

            state.update(
                left_scale=1.30,
                right_scale=1.26,
                gaze_y=-0.35,
                mouth_scale=1.55,
            )

        elif name == "look_up":

            state.update(
                left_scale=0.84,
                right_scale=0.80,
                gaze_y=-1.0,
            )

        elif name == "look_down":

            state.update(
                left_scale=0.80,
                right_scale=0.84,
                gaze_y=1.0,
            )

        elif name == "deadpan":

            state.update(
                left_scale=0.54,
                right_scale=0.52,
                gaze_x=0.1,
                mouth_scale=0.55,
            )

        return state

    # ========================================================
    # CHOOSE EXPRESSION
    # ========================================================

    EXPRESSIONS = (
        "blink",
        "blink",
        "blink",

        "wink_left",
        "wink_right",

        "side_left",
        "side_right",

        "look_left",
        "look_right",

        "skeptical",
        "confused",

        "happy",
        "laugh",

        "sleepy",

        "surprised",
        "shy",
        "pout",

        "disappointed",
        "excited",

        "look_up",
        "look_down",

        "deadpan",
    )

    EXPRESSION_WEIGHTS = (
        26,
        23,
        20,

        4,
        4,

        5,
        5,

        3,
        3,

        4,
        4,

        4,
        3,

        2,

        2,
        2,
        2,

        1,
        2,

        1,
        1,

        2,
    )

    MOUTH_FOR_EXPRESSION = {
        "happy": "grin",
        "laugh": "grin",
        "surprised": "o",
        "skeptical": "smirk_r",
        "side_left": "smirk_l",
        "side_right": "smirk_r",
        "look_left": "smirk_l",
        "look_right": "smirk_r",
        "wink_left": "small",
        "wink_right": "small",
        "pout": "pout",
        "confused": "small",
        "sleepy": "small",
        "shy": "small",
        "deadpan": "flat",
    }

    def _choose_expression(self):

        return random.choices(
            self.EXPRESSIONS,
            weights=self.EXPRESSION_WEIGHTS,
            k=1,
        )[0]

    # ========================================================
    # START EXPRESSION
    # ========================================================

    def _start_expression(self):

        if self.event is not None:
            self._schedule_expression()
            return

        self.event = (
            self._choose_expression()
        )

        self.event_frame = 0

        base_frames = max(
            12,
            self.args.expression_speed // 20,
        )

        self.event_frames = (
            base_frames +
            random.randint(-2, 2)
        )

        if self.event in (
            "sleepy",
            "shy",
            "disappointed",
        ):

            self.event_frames = int(
                self.event_frames * 1.4
            )

        target = self._expression(
            self.event
        )

        self.event_poses = (
            self._build_keyframe_poses(
                target
            )
        )

        if self.args.mouth:

            self.mouth_shape_target = (
                self.MOUTH_FOR_EXPRESSION.get(
                    self.event,
                    "smile",
                )
            )

            self.mouth_shape_current = (
                "smile"
            )

        self._animate_expression()

    # ========================================================
    # ANIMATE EXPRESSION
    # ========================================================

    def _animate_expression(self):

        total = self.event_frames

        progress = (
            self.event_frame /
            max(1, total - 1)
        )

        steps = self.args.transition_steps

        segment = len(KEYFRAME_TIMES) - 2

        for i in range(len(KEYFRAME_TIMES) - 1):

            if progress <= KEYFRAME_TIMES[i + 1]:
                segment = i
                break

        t0 = KEYFRAME_TIMES[segment]
        t1 = KEYFRAME_TIMES[segment + 1]

        span = t1 - t0

        local_t = (
            0.0
            if span <= 0
            else (progress - t0) / span
        )

        local_t = self._stepped(
            local_t,
            steps,
        )

        self._interpolate_state(
            self.event_poses[segment],
            self.event_poses[segment + 1],
            local_t,
        )

        if (
            self.args.mouth
            and progress >= KEYFRAME_TIMES[2]
            and self.mouth_shape_current
            != self.mouth_shape_target
        ):

            self.mouth_shape_current = (
                self.mouth_shape_target
            )

        self._redraw()

        if self.event_frame < total - 1:

            self.event_frame += 1

            self.root.after(
                20,
                self._animate_expression,
            )

        else:

            self.state = self._neutral()

            self.mouth_shape_current = "smile"

            self.event = None

            self._redraw()

            self._schedule_expression()

    # ========================================================
    # EVENT SCHEDULER
    # ========================================================

    def _schedule_expression(self):

        delay = random.uniform(
            self.args.expression_interval
            * 0.45,

            self.args.expression_interval
            * 1.35,
        )

        self.root.after(
            int(
                delay *
                1000
            ),
            self._start_expression,
        )

    # ========================================================
    # EYE TRACKING
    # ========================================================

    def _schedule_gaze(self):

        delay = random.uniform(0.6, 2.2)

        self.root.after(
            int(delay * 1000),
            self._pick_gaze_target,
        )

    def _pick_gaze_target(self):

        self.gaze_target_x = random.choice(
            GAZE_STEPS_X
        )

        self.gaze_target_y = random.choice(
            GAZE_STEPS_Y
        )

        self._schedule_gaze()

    def _schedule_jitter(self):

        delay = random.uniform(1.5, 4.0)

        self.root.after(
            int(delay * 1000),
            self._pick_jitter,
        )

    def _pick_jitter(self):

        self.jitter_x = random.choice(
            JITTER_STEPS
        )

        self._schedule_jitter()

    def _idle(self):

        if self.event is not None:
            return

        self.state["gaze_x"] = self._step_toward(
            self.state["gaze_x"],
            self.gaze_target_x,
            self.args.gaze_speed,
        )

        self.state["gaze_y"] = self._step_toward(
            self.state["gaze_y"],
            self.gaze_target_y,
            self.args.gaze_speed,
        )

        self.state["left_x"] = self.jitter_x
        self.state["right_x"] = -self.jitter_x

        self._redraw()

    # ========================================================
    # MASTER LOOP
    # ========================================================

    def _tick(self):

        self._idle()

        self.root.after(
            20,
            self._tick,
        )

    # ========================================================
    # CLOCK
    # ========================================================

    def _update_clock(self):

        if self.clock_id is None:

            self.clock_id = (
                self.canvas.create_text(
                    self.width / 2,
                    self.height - 24,
                    text="",
                    fill=self.args.clock_color,
                    font=(
                        "TkFixedFont",
                        self.args.clock_size,
                    ),
                    anchor="s",
                )
            )

        current_time = self.root.tk.call(
            "clock",
            "format",
            self.root.tk.call(
                "clock",
                "seconds",
            ),
            "-format",
            "%H:%M",
        )

        self.canvas.itemconfigure(
            self.clock_id,
            text=current_time,
        )

        self.canvas.coords(
            self.clock_id,
            self.width / 2,
            self.height - 24,
        )

        self.root.after(
            1000,
            self._update_clock,
        )
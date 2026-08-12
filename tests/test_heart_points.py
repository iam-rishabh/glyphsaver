"""Tests for glyphs.heart_eyes.

Pure geometry/state-machine math — no Tk window needed, so this runs
headless in CI. Exercises the pixel-grid data, the stepped/step-toward
easing primitives, and the expression/keyframe pose system, without
touching anything that requires an actual canvas.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from glyphs.heart_eyes import (  # noqa: E402
    BOUNDS,
    HEART_GRID,
    KEYFRAME_KINDS,
    MOUTHS,
    HeartEyesGlyph,
)


def make_glyph():
    """Build a HeartEyesGlyph without running Glyph.__init__/setup.

    Every method under test here is pure state math - it never touches
    self.args, self.root, or self.canvas - so we only need self.state
    seeded to neutral.
    """
    glyph = HeartEyesGlyph.__new__(HeartEyesGlyph)
    glyph.state = glyph._neutral()
    return glyph


# ============================================================
# HEART_GRID / MOUTHS data shape
# ============================================================

def test_heart_grid_rows_are_equal_width():
    width = len(HEART_GRID[0])
    assert all(len(row) == width for row in HEART_GRID)


def test_heart_grid_is_binary():
    for row in HEART_GRID:
        assert set(row) <= {"0", "1"}


def test_heart_grid_has_filled_pixels():
    assert any("1" in row for row in HEART_GRID)


def test_mouths_rows_are_binary_and_rectangular():
    for name, grid in MOUTHS.items():
        width = len(grid[0])
        for row in grid:
            assert len(row) == width, f"{name} has ragged rows"
            assert set(row) <= {"0", "1"}, f"{name} has non-binary cell"


# ============================================================
# _stepped: quantizes a 0..1 value onto discrete levels
# ============================================================

@pytest.mark.parametrize(
    "raw,steps,expected",
    [
        (0.0, 4, 0.0),
        (1.0, 4, 1.0),
        (0.1, 4, 0.0),
        (0.4, 4, 0.5),
        (0.6, 4, 0.5),
        (0.9, 4, 1.0),
    ],
)
def test_stepped_quantizes_to_discrete_levels(raw, steps, expected):
    glyph = make_glyph()
    assert glyph._stepped(raw, steps) == expected


def test_stepped_clamps_out_of_range_input():
    glyph = make_glyph()
    assert glyph._stepped(-5, 4) == 0.0
    assert glyph._stepped(5, 4) == 1.0


def test_stepped_single_step_rounds_to_nearest_endpoint():
    glyph = make_glyph()
    assert glyph._stepped(0.4, 1) == 0.0
    assert glyph._stepped(0.6, 1) == 1.0


# ============================================================
# _step_toward: fixed-increment movement toward a target
# ============================================================

def test_step_toward_moves_by_fixed_increment():
    glyph = make_glyph()
    assert glyph._step_toward(0.0, 1.0, 0.1) == pytest.approx(0.1)
    assert glyph._step_toward(1.0, 0.0, 0.1) == pytest.approx(0.9)


def test_step_toward_snaps_exactly_when_within_one_step():
    glyph = make_glyph()
    assert glyph._step_toward(0.95, 1.0, 0.1) == 1.0
    assert glyph._step_toward(0.05, 0.0, 0.1) == 0.0


def test_step_toward_returns_target_when_already_equal():
    glyph = make_glyph()
    assert glyph._step_toward(0.5, 0.5, 0.1) == 0.5


# ============================================================
# _neutral / BOUNDS
# ============================================================

def test_neutral_state_has_all_numeric_keys():
    glyph = make_glyph()
    neutral = glyph._neutral()
    assert set(neutral.keys()) == set(HeartEyesGlyph.NUMERIC_KEYS)


def test_neutral_scales_are_full_size_and_offsets_are_zero():
    glyph = make_glyph()
    neutral = glyph._neutral()
    assert neutral["left_scale"] == 1.0
    assert neutral["right_scale"] == 1.0
    assert neutral["mouth_scale"] == 1.0
    for key in (
        "left_x", "right_x", "left_y", "right_y",
        "gaze_x", "gaze_y", "mouth_y",
    ):
        assert neutral[key] == 0.0


def test_bounds_cover_every_numeric_key_with_valid_ranges():
    for key in HeartEyesGlyph.NUMERIC_KEYS:
        assert key in BOUNDS
        lo, hi = BOUNDS[key]
        assert lo < hi


# ============================================================
# _expression: named target poses
# ============================================================

def test_expression_returns_only_known_numeric_keys():
    glyph = make_glyph()
    for name in set(HeartEyesGlyph.EXPRESSIONS):
        state = glyph._expression(name)
        assert set(state.keys()) == set(HeartEyesGlyph.NUMERIC_KEYS)


def test_expression_unknown_name_returns_neutral():
    glyph = make_glyph()
    assert glyph._expression("not-a-real-expression") == glyph._neutral()


def test_blink_closes_both_eyes():
    glyph = make_glyph()
    state = glyph._expression("blink")
    assert state["left_scale"] < 0.1
    assert state["right_scale"] < 0.1


def test_wink_left_closes_only_the_left_eye():
    glyph = make_glyph()
    state = glyph._expression("wink_left")
    assert state["left_scale"] < 0.1
    assert state["right_scale"] > 0.5


def test_wink_right_closes_only_the_right_eye():
    glyph = make_glyph()
    state = glyph._expression("wink_right")
    assert state["right_scale"] < 0.1
    assert state["left_scale"] > 0.5


# ============================================================
# EXPRESSIONS / EXPRESSION_WEIGHTS / MOUTH_FOR_EXPRESSION wiring
# ============================================================

def test_expression_weights_align_with_expressions():
    assert len(HeartEyesGlyph.EXPRESSIONS) == len(HeartEyesGlyph.EXPRESSION_WEIGHTS)
    assert all(w > 0 for w in HeartEyesGlyph.EXPRESSION_WEIGHTS)


def test_choose_expression_always_returns_a_known_expression():
    glyph = make_glyph()
    for _ in range(50):
        assert glyph._choose_expression() in HeartEyesGlyph.EXPRESSIONS


def test_mouth_for_expression_maps_to_real_expressions_and_mouths():
    for expression, mouth in HeartEyesGlyph.MOUTH_FOR_EXPRESSION.items():
        assert expression in HeartEyesGlyph.EXPRESSIONS
        assert mouth in MOUTHS


# ============================================================
# _scaled_pose: anticipation/overshoot/rebound pushes, clamped
# ============================================================

def test_scaled_pose_zero_factor_returns_neutral():
    glyph = make_glyph()
    target = glyph._expression("happy")
    assert glyph._scaled_pose(target, 0.0) == glyph._neutral()


def test_scaled_pose_one_factor_returns_target():
    glyph = make_glyph()
    target = glyph._expression("happy")
    assert glyph._scaled_pose(target, 1.0) == target


def test_scaled_pose_clamps_extreme_factors_to_bounds():
    glyph = make_glyph()
    target = glyph._expression("surprised")
    pose = glyph._scaled_pose(target, 100.0)
    for key, value in pose.items():
        lo, hi = BOUNDS[key]
        assert lo <= value <= hi


# ============================================================
# _build_keyframe_poses: full anticipation -> ... -> neutral arc
# ============================================================

def test_build_keyframe_poses_has_one_pose_per_keyframe():
    glyph = make_glyph()
    target = glyph._expression("happy")
    poses = glyph._build_keyframe_poses(target)
    assert len(poses) == len(KEYFRAME_KINDS)


def test_build_keyframe_poses_starts_and_ends_neutral():
    glyph = make_glyph()
    target = glyph._expression("happy")
    poses = glyph._build_keyframe_poses(target)
    assert poses[0] == glyph._neutral()
    assert poses[-1] == glyph._neutral()


def test_build_keyframe_poses_hits_target_on_target_frames():
    glyph = make_glyph()
    target = glyph._expression("happy")
    poses = glyph._build_keyframe_poses(target)
    target_indices = [i for i, k in enumerate(KEYFRAME_KINDS) if k == "target"]
    assert target_indices, "no 'target' keyframes defined"
    for i in target_indices:
        assert poses[i] == target


# ============================================================
# _interpolate_state: blends two poses into self.state at t
# ============================================================

def test_interpolate_state_at_t0_matches_first_pose():
    glyph = make_glyph()
    a = glyph._neutral()
    b = glyph._expression("happy")
    glyph._interpolate_state(a, b, 0.0)
    assert glyph.state == a


def test_interpolate_state_at_t1_matches_second_pose():
    glyph = make_glyph()
    a = glyph._neutral()
    b = glyph._expression("happy")
    glyph._interpolate_state(a, b, 1.0)
    assert glyph.state == b


def test_interpolate_state_at_midpoint_averages_values():
    glyph = make_glyph()
    a = {key: 0.0 for key in HeartEyesGlyph.NUMERIC_KEYS}
    b = {key: 2.0 for key in HeartEyesGlyph.NUMERIC_KEYS}
    glyph._interpolate_state(a, b, 0.5)
    for key in HeartEyesGlyph.NUMERIC_KEYS:
        assert glyph.state[key] == pytest.approx(1.0)
"""Tests for glyphs.heart_eyes.heart_points().

Pure geometry/math — no Tk window needed, so this runs headless in CI.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from glyphs.heart_eyes import heart_points  # noqa: E402


def test_returns_expected_number_of_coordinates():
    pts = heart_points(0, 0, 100, squash=1.0, n=40)
    # n points, each contributing an (x, y) pair -> 2*n flat values
    assert len(pts) == 80


def test_points_are_centered_around_cx_cy():
    cx, cy = 500, 300
    pts = heart_points(cx, cy, 100, squash=1.0, n=60)
    xs = pts[0::2]
    ys = pts[1::2]

    assert min(xs) < cx < max(xs)
    assert min(ys) < cy or max(ys) > cy  # has vertical extent


def test_squash_reduces_vertical_extent():
    cx, cy = 0, 0
    open_pts = heart_points(cx, cy, 100, squash=1.0, n=60)
    closed_pts = heart_points(cx, cy, 100, squash=0.05, n=60)

    open_height = max(open_pts[1::2]) - min(open_pts[1::2])
    closed_height = max(closed_pts[1::2]) - min(closed_pts[1::2])

    assert closed_height < open_height
    assert closed_height < open_height * 0.2


def test_larger_size_produces_larger_shape():
    small = heart_points(0, 0, 50, squash=1.0, n=60)
    large = heart_points(0, 0, 200, squash=1.0, n=60)

    small_width = max(small[0::2]) - min(small[0::2])
    large_width = max(large[0::2]) - min(large[0::2])

    assert large_width > small_width

"""Coordinate helpers for ACNH `.nhl` acre scratch files."""

ACRE_WIDTH = 32
ACRE_HEIGHT = 32
TILE_SIZE = 8


def get_addr_from_x_y(x, y):
    """Return the byte offset for a 0-based acre tile coordinate."""
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("x and y must be integers")
    if not 0 <= x < ACRE_WIDTH or not 0 <= y < ACRE_HEIGHT:
        raise ValueError("x and y must be in the range 0..31")
    return (y * ACRE_WIDTH + x) * TILE_SIZE


def get_size_obj_doubled(item):
    """Return item width/height in acre slots.

    ACNH item sizes are represented in whole-tile units in the source metadata,
    while a dropped/placed object occupies a 2x2 slot minimum in the acre bytes.
    """
    size = item.get("size")
    if not size:
        return 2, 2

    x_text, y_text = size.split("x", 1)
    return int(2 * float(x_text)), int(2 * float(y_text))

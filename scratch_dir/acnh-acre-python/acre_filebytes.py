"""Byte helpers for old ACNH acre placement experiments."""

from pathlib import Path

from acre_mapping import ACRE_HEIGHT, ACRE_WIDTH, TILE_SIZE, get_addr_from_x_y, get_size_obj_doubled

BLANK_TILE = (0xFE, 0xFF)
CONTINUATION_TILE = 0xFFFD
DIY_CONST = 0x16A2
ITEM_VARIATION_NONE = 0x0000
DROPPED_FLAG = 0x20


def new_acre():
    """Create a blank 32x32 acre byte array."""
    filebytes = bytearray(ACRE_WIDTH * ACRE_HEIGHT * TILE_SIZE)
    for index in range(ACRE_WIDTH * ACRE_HEIGHT):
        addr = index * TILE_SIZE
        filebytes[addr] = BLANK_TILE[0]
        filebytes[addr + 1] = BLANK_TILE[1]
    return filebytes


def write_filebytes(filename, filebytes):
    """Write generated acre bytes to the ignored local output directory."""
    output_dir = Path(__file__).resolve().parent / "acre_output"
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / filename
    with file_path.open("wb") as f:
        f.write(filebytes)
    return file_path


def add_list_of_items_to_filebytes(filebytes, items, x_start=0, y_start=0):
    """Pack a sequence of item dictionaries into an acre, row by row."""
    max_y = y_start
    x_current = x_start
    y_current = y_start

    for item in items:
        item_tiles = item_as_list_of_lists(item, "dropped")
        item_width = len(item_tiles[0])
        item_height = len(item_tiles)

        if x_current + item_width > ACRE_WIDTH:
            x_current = 0
            y_current = max_y + 1
        if y_current + item_height > ACRE_HEIGHT:
            return filebytes, x_current, y_current

        filebytes, x_last, y_last = add_item_to_filebytes(filebytes, item_tiles, x_current, y_current)
        max_y = max(max_y, y_last)
        x_current = x_last + 1

    return filebytes, x_current, y_current


def add_item_to_filebytes(filebytes, item_tiles, x, y):
    """Place a pre-expanded item tile matrix at a 0-based coordinate."""
    width = len(item_tiles[0])
    height = len(item_tiles)
    if x + width > ACRE_WIDTH:
        raise ValueError("item will not fit near east edge")
    if y + height > ACRE_HEIGHT:
        raise ValueError("item will not fit near south edge")

    for yy, row in enumerate(item_tiles):
        for xx, tile in enumerate(row):
            addr = get_addr_from_x_y(x + xx, y + yy)
            filebytes[addr : addr + TILE_SIZE] = tile

    return filebytes, x + width - 1, y + height - 1


def item_as_list_of_lists(item, placement_state):
    """Expand an item dictionary into a 2D matrix of 8-byte acre tiles."""
    start_tile = bytearray(TILE_SIZE)
    continuation_tile = bytearray(TILE_SIZE)
    continuation_tile[0:2] = CONTINUATION_TILE.to_bytes(2, byteorder="little")

    should_drop = "dropped" in placement_state.lower() or "diy_name" in item
    x_width, y_height = get_size_obj_doubled(item)

    if "diy_name" in item:
        item_hex = DIY_CONST
        start_tile[0:2] = DIY_CONST.to_bytes(2, byteorder="little")
        start_tile[4:6] = item["internal_id"].to_bytes(2, byteorder="little")
    else:
        item_hex = item["internal_id"]
        start_tile[0:2] = item_hex.to_bytes(2, byteorder="little")
        start_tile[2] = DROPPED_FLAG if should_drop else 0
        start_tile[4:6] = ITEM_VARIATION_NONE.to_bytes(2, byteorder="little")

    tile_rows = []
    for yy in range(y_height):
        row = []
        for xx in range(x_width):
            continuation_tile[4:6] = item_hex.to_bytes(2, byteorder="little")
            continuation_tile[6] = xx
            continuation_tile[7] = yy
            row.append(continuation_tile.copy())
        tile_rows.append(row)

    tile_rows[0][0] = start_tile
    return tile_rows

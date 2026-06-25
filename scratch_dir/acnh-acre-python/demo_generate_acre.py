"""Generate a sample `.nhl` acre from sanitized scratch data."""

from acre_filebytes import add_list_of_items_to_filebytes, new_acre, write_filebytes
from sample_items import RUINED_ITEMS


def main():
    acre = new_acre()
    acre, _, _ = add_list_of_items_to_filebytes(acre, RUINED_ITEMS)
    output = write_filebytes("sample_ruined_items.nhl", acre)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

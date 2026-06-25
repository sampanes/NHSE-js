# ACNH Acre Python Scratch

This directory preserves a small, sanitized Python prototype for generating
Animal Crossing: New Horizons `.nhl` acre bytes. It is historical scratch work
for understanding field-item byte layout and dropped-item behavior; it is not
wired into the NHSE application.

## What Was Kept

- Acre coordinate-to-byte-address mapping.
- Blank acre generation.
- Dropped item and DIY recipe byte construction.
- A small synthetic sample catalog for local experiments.
- Notes about observed tile patterns and pickup behavior.

## What Was Excluded

- Real save exports and related personal island data.
- Generated `.nhl` and `.nhi` output files.
- Spreadsheet dumps and recovered workbook files.
- Bulk generated item dictionaries with unclear provenance.
- Machine-specific paths and local usernames.

## Useful Observations

- A single acre appears to be `0x2000` bytes.
- The acre grid is modeled as 32x32 slots.
- Each slot is represented by 8 bytes.
- Blank tiles begin with `FE FF`.
- Continuation tiles begin with `FD FF`.
- Dropped or pickup-able items use flag `0x20`.
- Placed/decorating-state objects may not be pickup-able by visitors.
- DIY recipes use item constant `0x16A2`; the recipe internal ID is stored in
  bytes 4-5 of the first tile.

Example dropped 1x1 item:

```text
C2 36 20 00 00 00 00 00
FD FF 00 00 C2 36 01 00
FD FF 00 00 C2 36 00 01
FD FF 00 00 C2 36 01 01
```

## Run The Demo

```powershell
python demo_generate_acre.py
```

The demo writes a generated acre to `acre_output/sample_ruined_items.nhl`.
That output is ignored by git.

## Relationship To NHSE

The main C# codebase already has mature placement paths through `BulkSpawn`,
`FieldItemDropper`, `LayerItem`, and `ItemParser`. Treat this scratch directory
as reference material for old byte-level experiments, not as the implementation
path for future themed pickup-island work.

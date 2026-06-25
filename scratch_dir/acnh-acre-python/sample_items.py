"""Small synthetic item catalog for the ACNH acre scratch demo.

The old local prototype used large generated item dictionaries. Those were
excluded from this repository because the main NHSE codebase already has item
data and the generated dictionary provenance was not reviewed.
"""

RUINED_ITEMS = [
    {
        "name": "ruined arch",
        "size": "3x1",
        "internal_id": 0x3892,
    },
    {
        "name": "ruined broken pillar",
        "size": "1x1",
        "internal_id": 0x3894,
    },
    {
        "name": "ruined decorated pillar",
        "size": "1x1",
        "internal_id": 0x3895,
    },
]

SAMPLE_DIY = {
    "name": "sample DIY recipe",
    "diy_name": "sample DIY recipe",
    "internal_id": 0x1234,
}

"""Standard daily time slots for booking (30-minute intervals)."""


def all_time_slots():
    """Return list of HH:MM strings from 09:00 to 16:30 inclusive (30-minute steps)."""
    slots = []
    for hour in range(9, 17):
        for minute in (0, 30):
            slots.append(f"{hour:02d}:{minute:02d}")
    return slots


def slot_label(slot):
    """Format slot for display (e.g. 09:30 -> 9:30 AM)."""
    h, m = map(int, slot.split(":"))
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {ampm}"

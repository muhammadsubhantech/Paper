# Task 13 - Booking Conflict Scheduler

from datetime import datetime


class BookingScheduler:
    def __init__(self):
        self.bookings = []
        self.booking_ids = set()
        self.conflicts = []

    def add_booking(self, room, start, end, booking_id):
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise TypeError("Start and end must be datetime objects")

        if booking_id in self.booking_ids:
            reason = "Duplicate booking ID"
            self.conflicts.append((booking_id, reason))
            return False

        # Remember the ID even if this booking is rejected.
        self.booking_ids.add(booking_id)

        if end <= start:
            reason = "End time must be after start time"
            self.conflicts.append((booking_id, reason))
            return False

        for booking in self.bookings:
            if booking["room"] == room:
                # Adjacent bookings are allowed.
                if start < booking["end"] and end > booking["start"]:
                    reason = "Booking time overlaps an existing booking"
                    self.conflicts.append((booking_id, reason))
                    return False

        new_booking = {
            "room": room,
            "start": start,
            "end": end,
            "booking_id": booking_id
        }

        self.bookings.append(new_booking)
        self.bookings.sort(key=lambda item: (item["room"], item["start"]))
        return True


if __name__ == "__main__":
    scheduler = BookingScheduler()

    date = "%Y-%m-%d %H:%M"
    first_start = datetime.strptime("2026-11-07 09:00", date)
    first_end = datetime.strptime("2026-11-07 10:00", date)
    second_start = datetime.strptime("2026-11-07 10:00", date)
    second_end = datetime.strptime("2026-11-07 11:00", date)
    third_start = datetime.strptime("2026-11-07 09:30", date)
    third_end = datetime.strptime("2026-11-07 10:30", date)

    print(scheduler.add_booking("A", first_start, first_end, "B1"))
    print(scheduler.add_booking("A", second_start, second_end, "B2"))
    print(scheduler.add_booking("A", third_start, third_end, "B3"))
    print("Conflicts:", scheduler.conflicts)

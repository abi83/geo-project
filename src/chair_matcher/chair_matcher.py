from src.constants import CHAIR_TYPES


class ChairMatcher:
    """
    Find all matches between room polygons and chair coordinates
    Can print short report in desired format
    """
    rooms = []
    chairs = []

    def __init__(self, rooms, chairs):
        self.rooms = rooms
        self.chairs = chairs

    @staticmethod
    def _initialise_empty_chairs():
        return {chair_type: 0 for chair_type in CHAIR_TYPES}

    @staticmethod
    def _print_report(object):
        for key, value in object.items():
            print(f'{key}:')
            print(', '.join([
                f'{chair_type}: {chair_quantity}' for chair_type, chair_quantity in value.items()
            ]))

    def _initialise_empty_rooms(self):
        room_names = [room['name'] for room in self.rooms]
        return {room_name: self._initialise_empty_chairs() for room_name in room_names}

    def room_matcher(self):
        output = self._initialise_empty_rooms()
        for chair in self.chairs:
            for room in self.rooms:
                if room['polygon'].contains(chair['point']):
                    output[room['name']][chair['type']] += 1
        return output

    def total_matcher(self):
        total = self._initialise_empty_chairs()
        for room_chairs in self.room_matcher().values():
            for chair_type, chair_quantity  in room_chairs.items():
                total[chair_type] += chair_quantity
        return {"total": total}

    def print_report(self):
        self._print_report(self.total_matcher())
        self._print_report(dict(sorted(self.room_matcher().items())))

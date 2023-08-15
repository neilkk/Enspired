from dataclasses import dataclass, field
from re import finditer, search
from typing import Dict, List


@dataclass
class RoomSegment:
    row_number: int
    column_start: int
    column_end: int

    def __repr__(self):
        return f'{self.row_number}:{self.column_start}-{self.column_end}'


@dataclass
class RoomSpace:
    name: str = 'empty'
    chair_count: Dict[str, int] = field(default_factory=dict)
    segments: List[RoomSegment] = field(default_factory=list)
    complete: bool = False


def read_floor_layout(name):
    with open(name, 'r') as file:
        lines = file.readlines()
    return lines


def find_segments(found, number):
    room_segments = []
    for room_segment in found:
        room_segments.append(RoomSegment(number, room_segment.start(), room_segment.end()))
    return room_segments


def process_floor_layout(layout):
    chair_types = 'CPSW'
    rooms = []
    spaces = []

    for number, row in enumerate(layout):
        found = list(finditer(r'[^/\\|+-]+', row))
        if found:
            room_segments = find_segments(found, number)
            for space in spaces:
                for room_segment in room_segments:
                    if max(space.segments[-1].column_start, room_segment.column_start) < min(space.segments[-1].column_end, room_segment.column_end):  # add room_segment to space
                        space.segments.append(room_segment)
                        room_segments.remove(room_segment)
                        break
                else:
                    text = ''.join([layout[segment.row_number][segment.column_start:segment.column_end]
                                    for segment in space.segments])
                    name = search(r'\([^()]+\)', text)
                    if name:
                        space.name = name[0][1:-1]
                        space.chair_count = {chair: text.count(chair) for chair in chair_types}
                        rooms.append(space)
                    space.complete = True
            spaces = [space for space in spaces if not space.complete]
            for room_segment in room_segments:
                room_space = RoomSpace()
                room_space.segments.append(room_segment)
                spaces.append(room_space)

    return rooms


if __name__ == "__main__":
    filename = "rooms.txt"
    layout = read_floor_layout(filename)
    rooms = process_floor_layout(layout)
    rooms.sort(key=lambda room: room.name)
    for room in rooms:
        print(room.name + ':')
        print(*[(key + ': ' + str(value)) for key, value in room.chair_count.items()], sep=', ')


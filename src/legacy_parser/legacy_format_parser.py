from shapely.geometry import LineString, Point
from shapely.ops import polygonize
from src.constants import CHAIR_TYPES

CORNERS = "+"
WALLS = "-|/\\"


class LegacyParser:
    """
    Parses the data in legacy text format and outputs rooms as geopandas Polygons annotated with room name
    and chairs as geopandas Point annotated with chair type
    """
    raw_txt_data = []
    edges = set()

    def __init__(self, data):
        self.raw_txt_data = data

    @staticmethod
    def _around_points():
        """Generates relative coordinates for nearest points"""
        for x in range(-1, 2):
            for y in range(-1, 2):
                yield x, y

    def _get_max_wall_length(self):
        """Evaluates max possible wall length"""
        return max(
            [len(self.raw_txt_data)]
            + [len(row) for row in self.raw_txt_data]
        )

    def _get_wall_directions(self, start_point):
        """Yields all vector directions with walls from point"""
        for direction in self._around_points():
            row_idx = start_point[0] + direction[0]
            column_idx = start_point[1] + direction[1]
            try:
                if self.raw_txt_data[row_idx][column_idx] in WALLS:
                    yield direction
            except IndexError:
                continue

    def _get_edges_from_node(self, start_point):
        """Yields all full vectors from point as tuple of two coordinate tuples"""
        try:
            wall_directions = self._get_wall_directions(start_point)
        except TypeError:
            wall_directions = []
        for direction in wall_directions:
            for step in range(1, self._get_max_wall_length()):
                row_idx = start_point[0] + direction[0] * step
                column_idx = start_point[1] + direction[1] * step
                try:
                    if row_idx >= 0 and column_idx >= 0 and self.raw_txt_data[row_idx][column_idx] in CORNERS:
                        yield start_point, (row_idx, column_idx)
                        break
                except IndexError:
                    break

    def _get_start_node(self):
        """Returns first node in raw_txt_data as tuple of coordinates"""
        for row_idx, row in enumerate(self.raw_txt_data):
            for col_idx, symbol in enumerate(row):
                if symbol in CORNERS:
                    return row_idx, col_idx
        raise ValueError('No nodes in raw data')

    def _get_raw_edges(self, start_point=None):
        """Recursively find and returns all edges as tuple of two coordinate tuples"""
        if start_point is None:
            start_point = self._get_start_node()
        try:
            start_edges = self._get_edges_from_node(start_point)
            for edge in start_edges:
                if edge not in self.edges and (edge[1], edge[0]) not in self.edges:
                    self.edges.add(edge)
                    self._get_raw_edges(edge[1])
            return self.edges
        except TypeError:
            return []

    def _get_raw_room_names(self):
        """Returns all room names, annotated with position vector"""
        for row_idx, row in enumerate(self.raw_txt_data):
            for col_idx, start in enumerate(row):
                if start == "(":
                    room_name = start
                    while room_name[-1] != ")":
                        try:
                            room_name += self.raw_txt_data[row_idx][col_idx + len(room_name)]
                        except IndexError:
                            break
                    if room_name.endswith(")"):
                        yield {
                            "name": room_name[1:-1],
                            "vector": ((row_idx, col_idx), (row_idx, col_idx + len(room_name)))
                        }

    def parse_rooms(self):
        """Returns all rooms in raw_txt_data annotated with room names"""
        edges = self._get_raw_edges()
        vectors = [LineString(edge) for edge in edges]
        polygons = list(polygonize(vectors))
        raw_room_names = list(self._get_raw_room_names())
        for polygon in polygons:
            room_name = ""
            for room in raw_room_names:
                if polygon.contains(Point(room['vector'][0])) and polygon.contains(Point(room['vector'][1])):
                    room_name = room['name']
            yield {
                "name": room_name,
                "polygon": polygon,
            }

    def parse_chairs(self):
        """Returns all chairs in raw_txt_data annotated with chair types"""
        for row_idx, row in enumerate(self.raw_txt_data):
            for col_idx, symbol in enumerate(row):
                if symbol in CHAIR_TYPES:
                    yield {
                        'type': symbol,
                        'point': Point((row_idx, col_idx))
                    }

#Check if classes are hashable
class Position:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    def __eq__(self, value: object) -> bool:
        return self.y == value.y and self.x == value.x
    
p = (Position(1, 2), Position(2, 4), Position(4, 6))
p1 = Position(1, 2)
print(p1 in p)
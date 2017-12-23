from enum import Enum


class Mode(Enum):
    LINE = 1
    ARROW = 2
    RECTANGLE = 3
    CIRCLE = 4


class RectangularObj:
    def __init__(self, init, final, color, thickness):
        self.init = init
        self.final = final
        self.color = color
        self.thickness = thickness


class CircleObj:
    def __init__(self, init, dist, color, thickness):
        self.init = init
        self.dist = dist
        self.color = color
        self.thickness = thickness


class TextObj:
    def __init__(self, rect, text, font_size, color, thickness):
        self.rect = rect
        self.text = text
        self.font_size = font_size
        self.color = color
        self.thickness = thickness


class Subset:

    def __init__(self, mode, obj, img):
        self.mode = mode
        self.obj = obj
        self.img = img




class Image:

    def __init__(self, img, filename, subsets):
        self.img = img
        self.filename = filename
        self.subsets = subsets

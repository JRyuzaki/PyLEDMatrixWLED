import socket
from typing import List, Tuple


class LEDMatrix:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, image):
        message = image_to_packet(image.pixels)
        self.sock.sendto(message, (self.ip, self.port))


def packet(num: int, r: int, g: int, b: int):
    return bytes([num]) + bytes([r]) + bytes([g]) + bytes([b])


def image_to_packet(image: List[List[Tuple[int, int, int]]]):
    """TODO: Docstring for image_to_packet.

    :image: TODO
    :returns: TODO

    """
    packet_string = b"\x01\x01"
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            packet_string += packet(y * len(row) + x, pixel[0], pixel[1], pixel[2])
    return packet_string


def png_to_image(png_image, image):
    png_image = png_image.resize((image.width, image.height))

    for y in range(png_image.height):
        for x in range(png_image.width):
            pixel = png_image.getpixel((x, y))
            image.set_pixel(y, image.width - x - 1, (pixel[0], pixel[1], pixel[2]))


class Image:
    def __init__(self, width, height, color=(0, 0, 0)) -> None:
        self.width = width
        self.height = height
        self.pixels = [[color for j in range(0, width)] for i in range(0, height)]

    def set_pixel(self, x, y, color):
        """TODO: Docstring for set_pixel.

        :x: TODO
        :y: TODO
        :color: TODO
        :returns: TODO
        """
        self.pixels[y][x] = color

    def clear(self, color=(0, 0, 0), opacity=1.0):
        self.pixels = [
            [
                tuple(
                    [
                        int(color[z] * opacity + self.pixels[i][j][z] * (1 - opacity))
                        for z in range(0, 3)
                    ]
                )
                for j in range(0, self.width)
            ]
            for i in range(0, self.height)
        ]

import torch
from ray import Rays
from image import Image
from func import unit
import matplotlib.pyplot as plt
from math import tan, pi
from param import device


class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, image_width, image_height, render_depth):
        h = tan(vfov *  pi/ 360)
        viewport_height = 2.0 * h
        viewport_width = image_height/image_width * viewport_height

        w = unit(lookfrom - lookat)
        u = unit(torch.cross(vup, w))
        v = torch.cross(w, u)

        self.origin = lookfrom
        self.horizontal = viewport_width * u
        self.vertical = viewport_height * v
        self.lower_left_corner = self.origin - self.horizontal / 2 - self.vertical / 2 - w

        self.image_width = image_width
        self.image_height = image_height
        self.out_shape = (self.image_height, self.image_width, 3)

        self.render_depth = render_depth


    def render(self, world, antialiasing=1):
        colors = torch.zeros((self.image_width * self.image_height, 3), device=device)
        for _ in range(antialiasing):
            x = torch.tile(torch.linspace(0, (self.out_shape[1] - 1) / self.out_shape[1], self.out_shape[1], device=device),
                           (self.out_shape[0],)).unsqueeze(1)
            y = torch.repeat_interleave(torch.linspace(0, (self.out_shape[0] - 1) / self.out_shape[0], self.out_shape[0], device=device),
                                        self.out_shape[1]).unsqueeze(1)
            if antialiasing != 1:
                x += torch.rand(x.shape, device=device) / self.out_shape[1]
                y += torch.rand(y.shape, device=device) / self.out_shape[0]
            ray = Rays(self.origin, self.lower_left_corner + x * self.horizontal + y * self.vertical - self.origin)
            colors += ray.trace(world, self.render_depth)

        scale = 1 / antialiasing
        colors = torch.sqrt(scale * colors)
        return Image.from_flat(colors, self.image_width, self.image_height)



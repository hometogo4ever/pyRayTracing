import torch
from param import device
class World:
    def __init__(self, light):
        self.objects = []
        self.light = torch.tensor(light, device=device)
    def add(self, obj):
        self.objects.append(obj)
    def hit(self, r_in, t_max):
        intersections = [obj.intersect(r_in, t_max) for obj in self.objects]
        stack = torch.stack(intersections, dim=0)
        nv, ni = torch.min(stack, dim=0)
        return intersections, nv

import torch
from param import device
from func import dirunit
class Material:
    def __init__(self, ambient,kd, cols = 0,kersnel=0, n=1):
        self.ambient = ambient
        self.kersnel = kersnel
        self.cols = cols
        self.n = n
        self.kd = torch.tensor(kd, device=device)
    def diffuse(self, normal, point, shadow, col):
        N = normal
        D = shadow.unit_direction()
        d = shadow.squared_length()
        cos = torch.sum(N * D.direct, dim=-1)
        c = cos.unsqueeze(1)
        c2 = torch.max(c, torch.zeros_like(c, device=device))
        ktemp = self.kd * col
        kd = (ktemp * 10).unsqueeze(0)
        diffuse_color = kd * c2 / d
        return diffuse_color
        

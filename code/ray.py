import numpy as np
from param import TMAX, device
import torch
from func import rcolor, dot, dirunit

class Rays:
    def __init__(self, origin, direct, col=[1,1,1], currentn = 1):
        self.origin = torch.tensor(origin, device=device)
        self.direct = direct
        self.col = torch.tensor(col, device=device)
        self.currentn = currentn
    def t2p(self, t):
        return self.origin + self.direct * t
    def squared_length(self):
        return torch.einsum('...i,...i', self.direct, self.direct).unsqueeze(1)

    def length(self):
        return torch.sqrt(self.squared_length())
    def unit_direction(self):
        unit_directions = self.direct / self.length()
        return Rays(self.origin, unit_directions)
    def trace(self, world, depth):
    # 월드에서 레이와 교차하는 객체를 찾습니다.
        intersections, near = world.hit(self, TMAX)
        # 색상을 저장할 텐서를 초기화합니다.
        color = torch.zeros_like(self.direct, device=device)
        
        # 월드의 각 객체에 대해
        for obj, distance in zip(world.objects, intersections):
            # 현재 객체와 가장 가까운 교차점을 찾습니다.
            hit = (near != TMAX) & (distance == near)
            if hit.any():
                # 앰비언트 색상 계산
                col1 = obj.getambient()
                # 그림자 레이를 생성
                shadowray = ShadowRays(self.t2p(near), world.light)
                # 그림자 레이와 월드의 교차점 계산
                idx2, shadownear = world.hit(shadowray, TMAX)
                sp = ShadowRays(self.t2p(near), shadowray.t2p(shadownear))
                hit2 = (torch.abs(sp.length() - shadowray.length()) < 0.1) | (sp.length() > shadowray.length())
                # 객체의 색상 계산
                col2 = obj.getColor(self, near, shadowray, self.col)
                col3 = col2 + col1
                
                # 법선 벡터와 반사 방향 계산
                if self.currentn != 1:
                    norm = obj.getnormal(self.t2p(near)) * -1
                else:
                    norm = obj.getnormal(self.t2p(near))
                dirreclect = self.direct - 2 * dot(self.direct, norm) * norm
                l = self.unit_direction().direct
                cosine = -1 * dot(l, norm)
                
                # 굴절률 계산
                if self.currentn == 1:
                    newn = 1/obj.material.n
                    nextn = obj.material.n
                else:
                    newn = 1 / self.currentn
                    nextn = 1
                
                # 굴절 방향 계산
                d = 1 - newn * newn * (1 - cosine * cosine)
                refractC = (newn * cosine - torch.sqrt(1 - newn * newn * (1 - cosine * cosine)))
                refractdir = refractC * norm + newn * l
                
                # 깊이 제한을 초과하지 않고 불투명도가 0 이상일 때
                if depth > 1 and obj.material.cols > 0:
                    reflectRay = Rays(self.t2p(near) + dirreclect * 0.1, dirreclect)
                    refractRay = Rays(self.t2p(near) + refractdir * 0.1, refractdir, currentn=nextn)
                    if obj.material.kersnel == 1:
                        refcol = reflectRay.trace(world, depth - 1)
                        col3p = col3 * (1 - obj.material.cols) + obj.material.cols * refcol
                        col1p = col1 * (1 - obj.material.cols) + obj.material.cols * refcol
                    elif obj.material.kersnel == 0:
                        reffcol = refractRay.trace(world, depth - 1)
                        col3p = col3 * (1 - obj.material.cols) + obj.material.cols * reffcol
                        col1p = col1 * (1 - obj.material.cols) + obj.material.cols * reffcol
                    else:
                        refcol = reflectRay.trace(world, depth - 1)
                        reffcol = refractRay.trace(world, depth - 1)
                        col3p = col3 * (1 - obj.material.cols) + obj.material.cols * (refcol * obj.material.kersnel + reffcol * (1 - obj.material.kersnel))
                        col1p = col1 * (1 - obj.material.cols) + obj.material.cols * (refcol * obj.material.kersnel + reffcol * (1 - obj.material.kersnel))
                else:
                    col3p = rcolor(col3)
                    col1p = rcolor(col1)
                
                # 최종 색상 계산
                color = (col3p * hit2 + col1p * (~hit2)) * hit + color * (~hit)
        
        return color


class ShadowRays(Rays):
    def __init__(self, origin, light):
        self.direct = torch.tensor(light, device=device)-origin
        self.origin = torch.tensor(origin, device=device) + 0.1 * self.direct




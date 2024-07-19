import torch
from param import device
from abc import *
from func import dirunit, unit

class Shape(metaclass=ABCMeta):
    @abstractmethod
    def intersect(self, ray, t_max):
        pass
    @abstractmethod
    def getColor(self, r, t, shadow, col):
        pass
    @abstractmethod
    def getambient(self):
        pass
    @abstractmethod
    def getnormal(self, p):
        pass


class Polygon(Shape):
    def __init__(self, points, material, normal=None):
        self.p = torch.tensor(points, device=device).view(3,3)
        A, B, C = self.p
        if normal == None:
            self.normal = torch.cross(C-A, B-A)
        else:
            self.normal = torch.tensor(normal, device=device)
        self.material = material
    # BaryCentric Coordinate
    def intersect(self, ray, t_max):
        A, B, C = self.p
        #print("a: ", A, "b:", B, "c:",C)
        O = ray.origin
        D = ray.direct

        AB = B - A
        AC = C - A
        
        # Compute normal vector of the triangle
        N = self.normal
        
        # Compute denominator for plane-ray intersection
        denom = torch.sum(N * D, dim=-1)
        # Check if the ray is parallel to the triangle plane
        
        # Compute intersection point with the triangle plane
        AO = A - O
        t = torch.sum(N * AO, dim=-1) / denom
        # Compute intersection point P
        P = O + t.unsqueeze(-1) * D
        # Compute areas
        Area_ABC = 0.5 * torch.norm(torch.cross(AB, AC), dim=-1)
        Area_PBC = 0.5 * torch.norm(torch.cross(B - P, C - P), dim=-1)  # (num_rays,)
        Area_PCA = 0.5 * torch.norm(torch.cross(C - P, A - P), dim=-1)  # (num_rays,)
        Area_PAB = 0.5 * torch.norm(torch.cross(A - P, B - P), dim=-1)  # (num_rays,)
        
        
        # Compute barycentric coordinates
        u = Area_PBC / Area_ABC
        v = Area_PCA / Area_ABC
        w = Area_PAB / Area_ABC
        
        # Check if P is inside the triangle
        inside_mask = (u > 0) & (v > 0) & (w > 0) & ((u + v + w) <= 1) & (t>0)
        return torch.where(inside_mask.unsqueeze(-1), t.unsqueeze(-1), t_max)
    def getColor(self, r, t, shadowray, col):
        color = torch.zeros_like(r.direct)
        P = r.t2p(t)
        N = unit(self.normal)
        dif = self.material.diffuse(N, P, shadowray, col)
        color += dif
        return color
    def getambient(self):
        return self.material.ambient * self.material.kd
    def getnormal(self, p):
        return unit(self.normal)

class Sphere(Shape):
    def __init__(self, pos, r, material):
        self.pos = torch.tensor(pos, device=device)
        self.r = r
        self.material = material
    # Use Geometry
    def intersect(self, ray, t_max):
        OC = ray.origin - self.pos
        A = ray.squared_length()
        HalfB = torch.einsum('...i,...i', OC, ray.direct).unsqueeze(-1)
        C = torch.einsum('...i,...i', OC, OC).unsqueeze(-1) - self.r * self.r
        D = (HalfB * HalfB) - (A * C)

        # 판별식을 제곱근으로 계산
        DR = torch.sqrt(torch.maximum(torch.zeros_like(D), D))
        x0 = (-HalfB - DR) / A
        x1 = (-HalfB + DR) / A

        # 작은 t를 선택하지만, 0.1보다 큰 값으로 제한
        x = torch.where((x0 > 0.1) & (x0 < x1), x0, x1)
        pred = (D > 0) & (x > 0)
        
        # 레이가 내부로 향하는 경우를 처리
        inside_sphere = torch.einsum('...i,...i', ray.direct, OC).unsqueeze(-1) > 0
        x = torch.where(inside_sphere, x1, x)
        
        root = torch.where(pred, x, t_max)
        return root
    def getColor(self, r, t, shadowray, col):
        color = torch.zeros_like(r.direct, device=device)
        P = r.t2p(t)
        N = dirunit(P - self.pos)
        dif = self.material.diffuse(N, P, shadowray, col)
        color += dif
        
        return color
    def getambient(self):
        return self.material.ambient * self.material.kd
    def getnormal(self, p):
        return dirunit(p-self.pos)





class Group:
    def __init__(self, polygonlist):
        self.polygons = polygonlist
        tmin = torch.tensor([0,0,0], device=device)
        tmax = torch.tensor([0,0,0], device=device)
        for i in polygonlist:
            for j in range(3):
                for k in range(3):
                    if tmin[k] > polygonlist.p[j][k]:
                        tmin[k] = polygonlist.p[j][k]
                    if tmax[k] < polygonlist.p[j][k]:
                        tmax[k] = polygonlist.p[j][k]
        self.tmin = tmin
        self.tmax = tmax

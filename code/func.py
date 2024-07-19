import torch
def unit(vec):
    norm = torch.norm(vec)
    return vec/norm

def dirunit(vec):
    norm = torch.sqrt(torch.einsum('...i,...i', vec, vec).unsqueeze(1))
    return vec/norm

def rcolor(col):
    minz = torch.max(col, torch.zeros_like(col))
    maxz = torch.min(col, torch.ones_like(col))
    return maxz

def dot(v1, v2):
    return torch.einsum('...i,...i', v1, v2).unsqueeze(1)
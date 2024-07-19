from object import Polygon, Sphere
from world import World
from render import Camera
from material import Material
from param import device
import torch

lookfrom = torch.tensor((0., 1., 0.), device=device)
lookat = torch.tensor((0., 5., 0.), device=device)
vup = torch.tensor((0., 0., 1.), device=device)
width = 800
height = 600
antialize = 20
depth = 4
fov = 90

if __name__ == '__main__':
    f = open("object/world.txt", "r")
    plist = []
    flist = []
    clist = []
    mode = False
    while True:
        line = f.readline()
        if line == 'EOF':
            break
        linelist = line.split(' ')
        if linelist[0] == 'p':
            plist+= [float(linelist[1]), float(linelist[2]), float(linelist[3])]
        if (linelist[0] == 'o'):
            mode = True
            continue
        if mode:
            if linelist[0] == 'f':
                flist += [int(linelist[1]),int(linelist[2]),int(linelist[3])]
            if linelist[0] == 'c':
                clist += [int(linelist[1])/256,int(linelist[2])/256,int(linelist[3])/256]
            if linelist[0] == 'o':
                mode = False
                continue
    f.close()
    world = World([0,5,3])
    for n in range(int(len(flist)/3)):
        p1 = flist[3*n]
        p2 = flist[3*n+1]
        p3 = flist[3*n+2]
        col = clist[3*n:3*n+3]
        points = plist[3*p1:3*p1+3] + plist[3*p2:3*p2+3] + plist[3*p3:3*p3+3]
        if n == 5 or n == 4:
            material =  Material(0.01, [1, 1, 1], cols=0.9, kersnel=1)
        else:
            material =  Material(0.01, col)
        polygon = Polygon(points, material)
        world.add(polygon)
    
    objfile = open("object/rotated_cube.txt", "r")
    while True:
        line = objfile.readline()
        if line == '':
            break
        linelist = line.split(' ')
        if linelist[0] == 'o' and linelist[-1].strip() == 'start':
            plist = []
            flist = []
            nlist = []
            clist = []
            while True:
                line = objfile.readline()
                linelist = line.split(' ')
                if linelist[0] == 'o' and linelist[-1].strip() == 'end':
                    break
                if linelist[0] == 'v':
                    plist+= [float(linelist[1]), float(linelist[2]), float(linelist[3])]
                if linelist[0] == 'f':
                    flist += [int(linelist[1]),int(linelist[2]),int(linelist[3])]
                if linelist[0] == 'vn':
                    nlist += [float(linelist[1]), float(linelist[2]), float(linelist[3])]
                if linelist[0] == 'c':
                    clist += [int(linelist[1])/256,int(linelist[2])/256,int(linelist[3])/256]
            for n in range(int(len(flist)/3)):
                p1 = flist[3*n]
                p2 = flist[3*n+1]
                p3 = flist[3*n+2]
                norm = nlist[3*n:3*n+3]
                col = clist
                points = plist[3*p1:3*p1+3] + plist[3*p2:3*p2+3] + plist[3*p3:3*p3+3]
                material =  Material(0.05, col)
                polygon = Polygon(points, material, norm)
                world.add(polygon)
            print('ADD COMPLETE')
    objfile.close()
    
    spm = Material(0.05, [135/256, 206/256, 235/256], cols=0.9, kersnel=0, n=1.2)
    sp1 = Sphere([2, 7, -2.5], 1.5, spm)

    spm2 = Material(0.05, [1, 1, 1], cols = 0.5, kersnel=1, n=1.2)
    sp2 = Sphere([0, 7, -4], 0.5, spm2)
    world.add(sp1)
    world.add(sp2)
    cam = Camera(lookfrom, lookat, vup, fov, width, height, depth)
    with torch.no_grad():
        image = cam.render(world, antialiasing=antialize)

    image.show(flip = True)
    image.save('result/result_1.png', flip=True)

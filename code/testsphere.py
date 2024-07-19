import math

# 구의 중심 좌표와 반지름
center = (0, 7, -3)
radius = 2

# 샘플링된 점들을 생성합니다 (20개로 샘플링)
sample_points = []
for phi in range(1, 180, 179 // 10):
    for theta in range(1, 360, 359 // 10):
        x = radius * math.sin(math.radians(phi)) * math.cos(math.radians(theta))
        y = radius * math.sin(math.radians(phi)) * math.sin(math.radians(theta))
        z = radius * math.cos(math.radians(phi))
        sample_points.append((x + center[0], y + center[1], z + center[2]))

# 노말 벡터 계산
normals = [(point[0] - center[0], point[1] - center[1], point[2] - center[2]) for point in sample_points]
normals_normalized = [(nx / radius, ny / radius, nz / radius) for nx, ny, nz in normals]

# 파일 생성
with open("sphere.txt", "w") as file:
    file.write(f"o 1 start\n")
    
    # 꼭짓점 정보 작성
    for v in sample_points:
        file.write(f"v {v[0]} {v[1]} {v[2]}\n")
    
    # 노말 벡터 정보 작성
    for vn in normals_normalized:
        file.write(f"vn {vn[0]} {vn[1]} {vn[2]}\n")
    
    # 삼각형 면 정보 작성
    for i in range(0, len(sample_points) - 20, 10):
        file.write(f"f {i} {i+1} {i+11}\n")
        file.write(f"f {i+1} {i+11} {i+10}\n")
        file.write(f"f {i+1} {i+2} {i+12}\n")
        file.write(f"f {i+1} {i+11} {i+12}\n")
        file.write(f"f {i+2} {i+12} {i+13}\n")
        file.write(f"f {i+2} {i+13} {i+3}\n")
        file.write(f"f {i+3} {i+13} {i+14}\n")
        file.write(f"f {i+3} {i+14} {i+4}\n")
        file.write(f"f {i+4} {i+14} {i+15}\n")
        file.write(f"f {i+4} {i+15} {i+5}\n")
        file.write(f"f {i+5} {i+15} {i+16}\n")
        file.write(f"f {i+5} {i+16} {i+6}\n")
        file.write(f"f {i+6} {i+16} {i+17}\n")
        file.write(f"f {i+6} {i+17} {i+7}\n")
        file.write(f"f {i+7} {i+17} {i+18}\n")
        file.write(f"f {i+7} {i+18} {i+8}\n")
        file.write(f"f {i+8} {i+18} {i+19}\n")
        file.write(f"f {i+8} {i+19} {i+9}\n")
        file.write(f"f {i+9} {i+19} {i}\n")
    
    file.write(f"c 255 192 203\n")  # 핑크색
    
    file.write(f"o 1 end\n")
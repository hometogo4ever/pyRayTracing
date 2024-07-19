import math
import torch

# 중심 좌표와 각 변의 길이의 절반
center = (-2, 8, -3)
half_length = 0.7

# 원점을 중심으로 이동하기 위한 이동 벡터
translation = torch.tensor(center, dtype=torch.float32)

# 각 축 기준 회전 각도 (라디안)
theta_x = math.radians(30)
theta_y = math.radians(30)
theta_z = math.radians(30)

# 각 축 기준 회전 행렬 정의
R_x = torch.tensor([
    [1, 0, 0, 0],
    [0, math.cos(theta_x), -math.sin(theta_x), 0],
    [0, math.sin(theta_x), math.cos(theta_x), 0],
    [0, 0, 0, 1]
], dtype=torch.float32)

R_y = torch.tensor([
    [math.cos(theta_y), 0, math.sin(theta_y), 0],
    [0, 1, 0, 0],
    [-math.sin(theta_y), 0, math.cos(theta_y), 0],
    [0, 0, 0, 1]
], dtype=torch.float32)

R_z = torch.tensor([
    [math.cos(theta_z), -math.sin(theta_z), 0, 0],
    [math.sin(theta_z), math.cos(theta_z), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
], dtype=torch.float32)

# 원점을 중심으로 이동하는 행렬 정의
T = torch.eye(4, dtype=torch.float32)
T[:3, 3] = translation

# 아핀 변환 행렬 계산 (순서: 이동 -> 회전)
affine_matrix = torch.matmul(T, torch.matmul(R_z, torch.matmul(R_y, R_x)))

# 꼭짓점 좌표 계산
vertices = [
    torch.tensor([-half_length, -half_length, -half_length, 1], dtype=torch.float32),
    torch.tensor([half_length, -half_length, -half_length, 1], dtype=torch.float32),
    torch.tensor([half_length, half_length, -half_length, 1], dtype=torch.float32),
    torch.tensor([-half_length, half_length, -half_length, 1], dtype=torch.float32),
    torch.tensor([-half_length, -half_length, half_length, 1], dtype=torch.float32),
    torch.tensor([half_length, -half_length, half_length, 1], dtype=torch.float32),
    torch.tensor([half_length, half_length, half_length, 1], dtype=torch.float32),
    torch.tensor([-half_length, half_length, half_length, 1], dtype=torch.float32)
]

# 아핀 변환 적용
rotated_vertices = []
for v in vertices:
    v_tensor = torch.tensor(v, dtype=torch.float32)
    rotated_v = torch.matmul(affine_matrix, v_tensor).tolist()
    rotated_vertices.append(rotated_v[:3])
# 각 면의 노멀 벡터 계산 (세 개의 꼭짓점을 가지고 외적을 계산)
def compute_normal(v0, v1, v2):
    v0 = torch.tensor(v0)
    v1 = torch.tensor(v1)
    v2 = torch.tensor(v2)
    edge1 = v1 - v0
    edge2 = v2 - v0
    normal = torch.cross(edge2, edge1)
    normal = normal / torch.norm(normal)  # 노멀 벡터를 단위 벡터로 만듦
    return normal.tolist()

# 각 면의 꼭짓점 인덱스
faces = [
    (0, 1, 2), (0, 2, 3),  # front
    (1, 5, 6), (1, 6, 2),  # right
    (5, 4, 7), (5, 7, 6),  # back
    (4, 0, 3), (4, 3, 7),  # left
    (3, 2, 6), (3, 6, 7),  # top
    (4, 5, 1), (4, 1, 0)   # bottom
]

# 회전된 정육면체의 각 면의 노멀 벡터 계산
rotated_normals = []
for face in faces:
    v0 = rotated_vertices[face[0]]
    v1 = rotated_vertices[face[1]]
    v2 = rotated_vertices[face[2]]
    normal = compute_normal(v0, v1, v2)
    rotated_normals.append(normal)

# 결과를 파일로 저장
file_path = "rotated_cube.txt"
with open(file_path, "w") as file:
    file.write(f"o 1 start\n")
    # 회전된 꼭짓점 정보 작성
    for v in rotated_vertices:
        file.write(f"v {v[0]} {v[1]} {v[2]}\n")
    
    # 회전된 노멀 벡터 정보 작성
    for n in rotated_normals:
        file.write(f"vn {n[0]} {n[1]} {n[2]}\n")
    
    # 면 정보 작성 (노멀 벡터 포함)
    for i, face in enumerate(faces):
        file.write(f"f {face[0]} {face[1]} {face[2]}\n")
    file.write(f"c 255 192 203\n")  # 핑크색
    # 파일 쓰기 종료
    file.write(f"o 1 end\n")

print(f"정육면체가 {file_path}에 성공적으로 저장되었습니다.")
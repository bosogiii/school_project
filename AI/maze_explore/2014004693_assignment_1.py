#2014004693_assignment_1
#18-2 AI class
from Queue import Queue, PriorityQueue

#file open with the location
path = "/Users/boseok/Desktop/3-2_class/인공지능/과제/assignment1_maze/"
maze_name = "fifth_floor.txt"
source_location = path + maze_name
with open(source_location, 'r') as f:
	data = f.readlines()

#maze number, maze size serching
line = data.pop(0)
lline = line.split()
floor = int(lline[0])
M = int(lline[1])
N = int(lline[2])

#starting point, end poing, key location serching
maze = []

for idx, line in enumerate(data):
	lline = line.split()
	lline = [int(i) for i in lline]
	if(6 in lline):
		idx_x, idx_y = (idx, lline.index(6))
	maze.append(lline)

S = (maze[0].index(3), 0)
E = (maze[M-1].index(4), M-1)
key = (idx_x, idx_y)

#각 맵에 맞게 함수를 호출
if floor == 1:
	out_maze, length, time = first_floor(maze, M, S, E, key)

elif floor == 2:
	out_maze, length, time = second_floor(maze, M, S, E, key)

elif floor == 3:
	out_maze, length, time = third_floor(maze, M, S, E, key)

elif floor == 4:
	out_maze, length, time = fourth_floor(maze, M, S, E, key)

else:
	out_maze, length, time = fifth_floor(maze, M, S, E, key)

#리턴값으로 output 파일 생성
maze_name = "fifth_floor_output.txt"
source_location = path + maze_name
with open(source_location, 'w') as f:
	for line in out_maze:
		for i in line:
			f.write(f'{i} ')
		f.write("\n")
	f.write("---\n")
	f.write(f"length={length}\n")
	f.write(f"time={time}\n")

def heuristic(a, b):
	x1, x2 = a
	y1, y2 = b
	return abs(x1 -x2) + abs(y1 - y2)

def Astar(maze, M, S, E, key):
	here = S

	return out_maze, length, time

def Greedy(maze, M, S, E, key):
	return out_maze, length, time

def bfs(maze, M, S):

def ids(maze, M, S):
	return out_maze, length, time

def first_floor(maze, M, S, E, key):
	return out_maze, length, time

def second_floor(maze, M, S, E, key):
	return out_maze, length, time

def third_floor(maze, M, S, E, key):
	return out_maze, length, time

def fourth_floor(maze, M, S, E, key):
	return out_maze, length, time

def fifth_floor(maze, M, S, E, key):
	return out_maze, length, time


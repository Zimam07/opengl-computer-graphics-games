from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

snow = []
rain = []
maze_size = 15
cell_size = 40
player_size = 20
zombie_size = 18
bullet_size = 5
wall_height = 60
camera_height = 200
bullet_speed = 18
zombie_speed = 0.2
player_speed = 0.15
camera_angle = 0.05
player_life = 5
cheat_mode = False
door = None
box = 3
bomb = 2
collectibles = []
boxs_collected = 0

class GameState:
    playing = 0
    won = 1
    lost = 2

game_state = GameState.playing
player_pos = [1.5, 1.5]
player_angle = 0.0
camera_pos = [0, 0, 120]
camera_angle = 45.0
camera_follow = True
camera_height = 60
camera_dis = 80
weather_mode = None
mode = 'day'

maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,0,1,0,1,1,0,1,1],
    [1,0,0,1,0,0,0,0,0,0,0,1,0,0,1],
    [1,1,0,1,1,1,0,1,1,1,0,1,0,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,0,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,1,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

def bfs(start, goal):
    sx, sy = int(start[0]), int(start[1])
    gx, gy = int(goal[0]), int(goal[1])
    if (sx, sy) == (gx, gy):
        return None
    queue = [(sx, sy)]
    visited = set()
    visited.add((sx, sy))
    parent = {}
    found = False
    while queue:
        x, y = queue.pop(0)
        if (x, y) == (gx, gy):
            found = True
            break
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < maze_size and 0 <= ny < maze_size and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))
    if not found:
        return None
    x, y = gx, gy
    path = []
    while (x, y) != (sx, sy):
        path.append((x, y))
        x, y = parent[(x, y)]
    path.reverse()
    return path[0] if path else None

class Zombie:
    def __init__(self, x, y):
        self.x = float(x) + 0.5
        self.y = float(y) + 0.5
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        if cheat_mode:
            angle = random.uniform(0, 2*math.pi)
            step_x = math.cos(angle) * zombie_speed * dt
            step_y = math.sin(angle) * zombie_speed * dt
            if valid_position(self.x + step_x, self.y + step_y):
                self.x += step_x
                self.y += step_y
        else:
            next_cell = bfs((self.x, self.y), (player_pos[0], player_pos[1]))
            if next_cell:
                tx, ty = next_cell
                dx = tx + 0.5 - self.x
                dy = ty + 0.5 - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0.01:
                    step = min(zombie_speed * dt, dist)
                    self.x += dx / dist * step
                    self.y += dy / dist * step
            else:
                dx = player_pos[0] - self.x
                dy = player_pos[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0.01:
                    step = min(zombie_speed * dt, dist)
                    self.x += dx / dist * step
                    self.y += dy / dist * step
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 0.6:
            global player_life, game_state
            player_life -= 1
            if player_life <= 0:
                game_state = GameState.lost
            else:
                empty_cells = [(x, y) for y in range(1, maze_size-1) for x in range(1, maze_size-1)
                               if maze[y][x] == 0 and (abs(x - player_pos[0]) > 2 or abs(y - player_pos[1]) > 2)]
                if empty_cells:
                    rx, ry = random.choice(empty_cells)
                    self.x = rx + 0.5
                    self.y = ry + 0.5

class Bullet:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.alive = True
        self.life_time = 2.0

    def update(self, dt):
        global alive_zombies_count
        if not self.alive:
            return
        self.life_time -= dt
        if self.life_time <= 0:
            self.alive = False
            return
        speed = bullet_speed * dt
        self.x += math.cos(math.radians(self.angle)) * speed
        self.y += math.sin(math.radians(self.angle)) * speed
        if not valid_position(self.x, self.y):
            self.alive = False
            return
        for z in zombies:
            if z.alive and (self.x - z.x)**2 + (self.y - z.y)**2 < 0.4:
                z.alive = False
                alive_zombies_count -= 1
                empty_cells = [(x, y) for y in range(1, maze_size-1) for x in range(1, maze_size-1)
                               if maze[y][x] == 0 and (abs(x - player_pos[0]) > 2 or abs(y - player_pos[1]) > 2)]
                if empty_cells:
                    rx, ry = random.choice(empty_cells)
                    z.x = rx + 0.5
                    z.y = ry + 0.5
                    z.alive = True
                    alive_zombies_count += 1
                self.alive = False
                break

zombies = []
bullets = []
last_time = 0

def initialize():
    global zombies, bullets, game_state, player_pos, player_angle, last_time
    global camera_height, player_life, alive_zombies_count, boxs_collected
    zombies.clear()
    bullets.clear()
    game_state = GameState.playing
    alive_zombies_count = 5
    boxs_collected = 0
    empty_cells = [(x, y) for y in range(1, maze_size-1)
                   for x in range(1, maze_size-1) if maze[y][x] == 0]
    if empty_cells:
        px, py = random.choice(empty_cells)
        player_pos[:] = [px + 0.5, py + 0.5]
    else:
        player_pos[:] = [1.5, 1.5]
    player_angle = 0
    camera_height = 200
    player_life = 5
    last_time = 0
    empty_cells = [(x, y) for y in range(1, maze_size-1)
                   for x in range(1, maze_size-1)
                   if maze[y][x] == 0 and (x, y) != (int(player_pos[0]), int(player_pos[1]))]
    random.shuffle(empty_cells)
    for _ in range(5):
        if empty_cells:
            x, y = empty_cells.pop(0)
            zombies.append(Zombie(x, y))
    place_collectibles()
    door()

def find_wall():
    arr = []
    for y in range(1, maze_size-1):
        for x in range(1, maze_size-1):
            if maze[y][x] == 0:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < maze_size and 0 <= ny < maze_size and maze[ny][nx] == 1:
                        arr.append((x, y))
                        break
    return arr

def place_collectibles():
    global collectibles
    wall_adjacent_positions = find_wall()
    available_positions = [(x, y) for x, y in wall_adjacent_positions
                           if abs(x - player_pos[0]) > 1.5 or abs(y - player_pos[1]) > 1.5]
    if len(available_positions) < box + bomb:
        available_positions = [(x, y) for y in range(1, maze_size-1) for x in range(1, maze_size-1)
                               if maze[y][x] == 0 and (abs(x - player_pos[0]) > 1.5 or abs(y - player_pos[1]) > 1.5)]
    random.shuffle(available_positions)
    collectibles = []
    for i in range(box):
        if available_positions:
            x, y = available_positions.pop(0)
            collectibles.append({'type': 'box', 'x': x + 0.5, 'y': y + 0.5, 'collected': False})
    for i in range(bomb):
        if available_positions:
            x, y = available_positions.pop(0)
            collectibles.append({'type': 'bomb', 'x': x + 0.5, 'y': y + 0.5, 'collected': False})

def check_collectible_collisions():
    global boxs_collected, game_state
    for item in collectibles:
        if not item['collected']:
            dx = player_pos[0] - item['x']
            dy = player_pos[1] - item['y']
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 0.4:
                if item['type'] == 'bomb' and cheat_mode:
                    continue
                item['collected'] = True
                if item['type'] == 'box':
                    boxs_collected += 1
                elif item['type'] == 'bomb':
                    game_state = GameState.lost

def draw_collectibles():
    quad = gluNewQuadric()
    for item in collectibles:
        if not item['collected']:
            if cheat_mode and item['type'] == 'bomb':
                continue
            px = item['x'] * cell_size
            py = item['y'] * cell_size
            pz = 10
            glPushMatrix()
            glTranslatef(px, py, pz)
            if item['type'] == 'box':
                glColor3f(0.812, 0.710, 0.231)
                glutSolidCube(18)
            elif item['type'] == 'bomb':
                glColor3f(0.1, 0.1, 0.1)
                gluSphere(quad, 7, 10, 10)
            glPopMatrix()
def valid_position(x, y, radius=0.20):
    for dx in [-radius, radius]:
        for dy in [-radius, radius]:
            mx, my = int(x + dx), int(y + dy)
            if not (0 <= mx < maze_size and 0 <= my < maze_size and maze[my][mx] == 0):
                return False
    return True

def draw_weather():
    global snow, rain
    if weather_mode == 'snow':
        if len(snow) < 100:
            for _ in range(100 - len(snow)):
                snow.append([random.uniform(0, maze_size*cell_size),
                                       random.uniform(0, maze_size*cell_size),
                                       random.uniform(80, 200)])
        glColor3f(1,1,1)
        glPointSize(5)
        glBegin(GL_POINTS)
        for p in snow:
            glVertex3f(p[0], p[1], p[2])
        glEnd()
        for p in snow:
            p[2] -= 1
            if p[2] < 0:
                p[0] = random.uniform(0, maze_size*cell_size)
                p[1] = random.uniform(0, maze_size*cell_size)
                p[2] = random.uniform(120, 500)
    elif weather_mode == 'rain':
        if len(rain) < 300:
            for _ in range(300 - len(rain)):
                rain.append([random.uniform(0, maze_size*cell_size),
                                       random.uniform(0, maze_size*cell_size),
                                       random.uniform(200, 900)])
        glColor3f(0.8,0.8,1)
        glLineWidth(4)
        glBegin(GL_LINES)
        for p in rain:
            glVertex3f(p[0], p[1], p[2])
            glVertex3f(p[0], p[1], p[2]-14)
        glEnd()
        glLineWidth(1)
        for p in rain:
            p[2] -= 4
            if p[2] < 0:
                p[0] = random.uniform(0, maze_size*cell_size)
                p[1] = random.uniform(0, maze_size*cell_size)
                p[2] = random.uniform(120, 200)



def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(font, ord(c))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_floor():
    for y in range(maze_size):
        for x in range(maze_size):
            if maze[y][x] == 0:
                glBegin(GL_QUADS)
                glColor3f(0.8, 0.4 + 0.3*((x+y)%2), 0.7)
                px, py = x*cell_size, y*cell_size
                glVertex3f(px, py, 0)
                glVertex3f(px+cell_size, py, 0)
                glVertex3f(px+cell_size, py+cell_size, 0)
                glVertex3f(px, py+cell_size, 0)
                glEnd()

def wall():
    section_map = [[-1 for _ in range(maze_size)] for _ in range(maze_size)]
    section_id = 0
    for y in range(maze_size):
        for x in range(maze_size):
            if maze[y][x] == 1 and section_map[y][x] == -1:
                queue = [(x, y)]
                section_map[y][x] = section_id
                while queue:
                    cx, cy = queue.pop(0)
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < maze_size and 0 <= ny < maze_size:
                            if maze[ny][nx] == 1 and section_map[ny][nx] == -1:
                                section_map[ny][nx] = section_id
                                queue.append((nx, ny))
                section_id += 1
    return section_map, section_id

wall_section_map, wall_section_count = wall()
wall_palette = [
    (0.09, 0.23, 0.1),
    (0.85, 0.1, 0.5),
    (0.98, 0.82, 0.09),
    (0.13, 0.7, 0.4),
    (0.8, 0.0, 0.2),
    (0.5, 0.3, 0.7),
    (0.2, 0.2, 0.2),
    (0.1, 0.5, 0.8),
    (0.9, 0.4, 0.1),
    (0.4, 0.9, 0.2),
    (0.7, 0.7, 0.7),
    (0.9, 0.1, 0.1),
    (0.1, 0.9, 0.7),
    (0.7, 0.5, 0.2),
    (0.6, 0.2, 0.6),
]

def draw_maze():
    wall_thickness = cell_size
    brick_height = 20
    brick_length = 20
    for y in range(maze_size):
        for x in range(maze_size):
            if maze[y][x] == 1:
                px = x * cell_size + cell_size / 2
                py = y * cell_size + cell_size / 2
                section_id = wall_section_map[y][x]
                is_door = door and (x, y) == door
                wall_color = wall_palette[section_id % len(wall_palette)]
                glPushMatrix()
                glTranslatef(px, py, wall_height / 2)
                glScalef(cell_size, wall_thickness, wall_height)
                glColor3f(*wall_color)
                glutSolidCube(1)
                glPopMatrix()
                if is_door:
                    glPushMatrix()
                    glTranslatef(px, py, wall_height/4)
                    glScalef(cell_size, wall_thickness + 8, wall_height )
                    glColor3f(1,1,1)
                    glutSolidCube(1.25)
                    glPopMatrix()
                for face in range(4):
                    glPushMatrix()
                    glTranslatef(px, py, 0)
                    if face == 0:
                        glTranslatef(0, wall_thickness / 2, 0)
                    elif face == 1:
                        glTranslatef(0, -wall_thickness / 2, 0)
                    elif face == 2:
                        glRotatef(90, 0, 0, 1)
                        glTranslatef(0, wall_thickness / 2, 0)
                    else:
                        glRotatef(90, 0, 0, 1)
                        glTranslatef(0, -wall_thickness / 2, 0)
                    glColor3f(0.1, 0.05, 0.05)
                    glLineWidth(2)
                    glBegin(GL_LINES)
                    for h in range(0, int(wall_height)+1, brick_height):
                        glVertex3f(-cell_size / 2, 0, h)
                        glVertex3f(cell_size / 2, 0, h)
                    row = 0
                    for h in range(0, int(wall_height), brick_height):
                        offset = (brick_length // 2) if (row % 2 == 1) else 0
                        for l in range(offset, int(cell_size), brick_length):
                            glVertex3f(-cell_size / 2 + l, 0, h)
                            glVertex3f(-cell_size / 2 + l, 0, h + brick_height)
                        row += 1
                    glEnd()
                    glLineWidth(1)
                    glPopMatrix()


def draw_player():
    px, py = player_pos[0] * cell_size, player_pos[1] * cell_size

    glPushMatrix()
    glTranslatef(px, py, 0)
    glRotatef(player_angle, 0, 0, 1)

    # Body
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glColor3f(0.2, 0.5, 0.2)
    glScalef(0.8, 0.6, 1.2)
    glutSolidCube(12)
    glPopMatrix()

    # Head
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0.9, 0.7, 0.6)
    gluSphere(gluNewQuadric(), 6, 10, 10)
    glPopMatrix()

    # Helmet
    glPushMatrix()
    glTranslatef(0, 0, 28)
    glColor3f(0.15, 0.4, 0.15)
    glScalef(1.1, 1.1, 0.7)
    gluSphere(gluNewQuadric(), 6, 8, 8)
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glTranslatef(5, 5, 15)
    glRotatef(-20, 0, 1, 0)
    glColor3f(0.2, 0.5, 0.2)
    gluCylinder(gluNewQuadric(), 2.5, 2, 10, 8, 8)
    glPopMatrix()

    # Hands
    glPushMatrix()
    glTranslatef(8, -8, 12)
    glColor3f(0.9, 0.7, 0.6)
    gluSphere(gluNewQuadric(), 2, 6, 6)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(8, 8, 12)
    glColor3f(0.9, 0.7, 0.6)
    gluSphere(gluNewQuadric(), 2, 6, 6)
    glPopMatrix()

    # Legs
    glPushMatrix()
    glTranslatef(-4, 0, 2)
    glColor3f(0.2, 0.5, 0.2)
    gluCylinder(gluNewQuadric(), 3, 2.5, 12, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(4, 0, 2)
    glColor3f(0.2, 0.5, 0.2)
    gluCylinder(gluNewQuadric(), 3, 2.5, 12, 8, 8)
    glPopMatrix()

    # Boots
    glPushMatrix()
    glTranslatef(-4, 1, 1)
    glColor3f(0.1, 0.1, 0.1)
    glScalef(1.2, 1.5, 0.8)
    glutSolidCube(4)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(4, 1, 1)
    glColor3f(0.1, 0.1, 0.1)
    glScalef(1.2, 1.5, 0.8)
    glutSolidCube(4)
    glPopMatrix()

    # Gun 
    glPushMatrix()
    glTranslatef(9, 0, 13)
    glScalef(0.6, 0.6, 0.6)

    # Gun barrel
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.6, 0.6, 10, 8, 8)
    glPopMatrix()

    # Gun body
    glPushMatrix()
    glTranslatef(-4, 0, 0)
    glColor3f(0.15, 0.15, 0.15)
    glScalef(1.5, 0.8, 0.6)
    glutSolidCube(3)
    glPopMatrix()

    # Gun handle
    glPushMatrix()
    glTranslatef(-2.5, 0, -2)
    glColor3f(0.1, 0.1, 0.1)
    glScalef(0.6, 1.0, 1.2)
    glutSolidCube(2)
    glPopMatrix()

    # Muzzle flash
    glPushMatrix()
    glTranslatef(10, 0, 0)
    glColor3f(0.05, 0.05, 0.05)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 1.5, 6, 6)
    glPopMatrix()

    glPopMatrix()  

    # Vest
    glPushMatrix()
    glTranslatef(0, -2, 15)
    glColor3f(0.15, 0.3, 0.15)
    glScalef(0.9, 0.4, 1.3)
    glutSolidCube(10)
    glPopMatrix()

    # Belt
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glColor3f(0.1, 0.08, 0.05)
    glScalef(1.1, 0.8, 0.3)
    glutSolidCube(8)
    glPopMatrix()

    glPopMatrix()  

def draw_zombies():
    for z in zombies:
        if z.alive:
            px, py = z.x * cell_size, z.y * cell_size
            glPushMatrix()
            glTranslatef(px, py, 0)
            glRotatef(math.degrees(math.atan2(player_pos[1] - z.y, player_pos[0] - z.x)), 0, 0, 1)
            
            # Zombie Body (cube)
            glPushMatrix()
            glTranslatef(0, 0, 15)
            glColor3f(1.0, 0, 0)
            glScalef(0.8, 0.6, 1.2)
            glutSolidCube(10)
            glPopMatrix()
            
            # Zombie Head (sphere)
            glPushMatrix()
            glTranslatef(0, 0, 25)
            glColor3f(0.7, 0.3, 0.3)
            gluSphere(gluNewQuadric(), 5, 10, 10)
            glPopMatrix()
            
            # Zombie Arms
            glPushMatrix()
            glTranslatef(5, 5, 15)
            glColor3f(0.274, 0.263, 0.231)
            gluCylinder(gluNewQuadric(), 2, 1.5, 10, 8, 8)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(5, -5, 15)
            glColor3f(0.274, 0.263, 0.231)
            gluCylinder(gluNewQuadric(), 2, 1.5, 10, 8, 8)
            glPopMatrix()

            # Zombie Legs
            glPushMatrix()
            glTranslatef(-3, 0, 2)
            glColor3f(0.1, 0.1, 0.1)
            gluCylinder(gluNewQuadric(), 2.5, 2, 10, 8, 8)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(3, 0, 2)
            glColor3f(0.1, 0.1, 0.1)
            gluCylinder(gluNewQuadric(), 2.5, 2, 10, 8, 8)
            glPopMatrix()
            
            glPopMatrix()


def door():
    global door
    arr = []
    for y in range(maze_size):
        for x in range(maze_size):
            if maze[y][x] == 1:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < maze_size and 0 <= ny < maze_size and maze[ny][nx] == 0:
                        if x == 0 or x == maze_size-1 or y == 0 or y == maze_size-1:
                            arr.append((x, y))
                        break
    if arr:
        door = random.choice(arr)
    else:
        door = (1, 1)

def draw_bullets():
    quad = gluNewQuadric()
    for b in bullets:
        if b.alive:
            px, py = b.x * cell_size, b.y * cell_size
            glPushMatrix()
            glTranslatef(px, py, 15)
            glColor3f(1,1,0)
            gluSphere(quad, bullet_size, 8, 8)
            glPopMatrix()

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1000 / 800, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    px = player_pos[0] * cell_size
    py = player_pos[1] * cell_size
    if camera_follow:
        cam_x = px - math.cos(math.radians(player_angle)) * camera_dis
        cam_y = py - math.sin(math.radians(player_angle)) * camera_dis
        cam_z = camera_height
        gluLookAt(cam_x, cam_y, cam_z, px, py, 0, 0, 0, 1)
    else:
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2], px, py, 0, 0, 0, 1)


def update_game():
    global last_time, game_state
    dt = 0.05
    last_time += dt
    if game_state != GameState.playing:
        return
    for z in zombies:
        z.update(dt)
    for b in bullets:
        b.update(dt)
    bullets[:] = [b for b in bullets if b.alive]
    check_collectible_collisions()
    if door and boxs_collected >= 3:
        px, py = int(player_pos[0]), int(player_pos[1])
        dx = abs(px - door[0])
        dy = abs(py - door[1])
        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            game_state = GameState.won

def idle():
    update_game()
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global player_angle, weather_mode, mode, cheat_mode, game_state
    ROTATION_SPEED = 5.0
    if key in [b'c', b'C']:
        cheat_mode = not cheat_mode
    if key in [b'r', b'R'] and game_state in [GameState.lost, GameState.won]:
        initialize()
    if game_state == GameState.playing:
        gun_tip_offset = 0.36
        if key in [b'w', b'W']:
            nx = player_pos[0] + math.cos(math.radians(player_angle)) * player_speed
            ny = player_pos[1] + math.sin(math.radians(player_angle)) * player_speed
            gun_nx = nx + math.cos(math.radians(player_angle)) * gun_tip_offset
            gun_ny = ny + math.sin(math.radians(player_angle)) * gun_tip_offset
            if valid_position(nx, ny) and valid_position(gun_nx, gun_ny, 0.05):
                player_pos[0], player_pos[1] = nx, ny
        elif key in [b's', b'S']:
            nx = player_pos[0] - math.cos(math.radians(player_angle)) * player_speed
            ny = player_pos[1] - math.sin(math.radians(player_angle)) * player_speed
            gun_nx = nx + math.cos(math.radians(player_angle)) * gun_tip_offset
            gun_ny = ny + math.sin(math.radians(player_angle)) * gun_tip_offset
            if valid_position(nx, ny) and valid_position(gun_nx, gun_ny, 0.05):
                player_pos[0], player_pos[1] = nx, ny
        elif key in [b'a', b'A']:
            new_angle = player_angle + ROTATION_SPEED
            gun_x_pred = player_pos[0] + math.cos(math.radians(new_angle)) * gun_tip_offset
            gun_y_pred = player_pos[1] + math.sin(math.radians(new_angle)) * gun_tip_offset
            if valid_position(gun_x_pred, gun_y_pred, 0.05):
                player_angle = new_angle % 360
        elif key in [b'd', b'D']:
            new_angle = player_angle - ROTATION_SPEED
            gun_x_pred = player_pos[0] + math.cos(math.radians(new_angle)) * gun_tip_offset
            gun_y_pred = player_pos[1] + math.sin(math.radians(new_angle)) * gun_tip_offset
            if valid_position(gun_x_pred, gun_y_pred, 0.05):
                player_angle = new_angle % 360
    if key in [b'g', b'G']:
        weather_mode = 'snow' if weather_mode != 'snow' else None
    elif key in [b'f', b'F']:
        weather_mode = 'rain' if weather_mode != 'rain' else None


def specialKeyListener(key, x, y):
    global camera_follow, camera_pos, camera_height, camera_dis
    if key == GLUT_KEY_UP:
        camera_height = min(camera_height + 20, 800) if camera_follow else camera_pos[2] + 10
    elif key == GLUT_KEY_DOWN:
        camera_height = max(camera_height - 10, 20) if camera_follow else camera_pos[2] - 10

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and game_state == GameState.playing:
        bullets.append(Bullet(player_pos[0], player_pos[1], player_angle))

def showScreen():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()
    draw_floor()
    draw_maze()
    draw_collectibles()
    draw_player()
    draw_zombies()
    draw_bullets()
    draw_weather()
    if door:
        door_cx = door[0] + 0.5
        door_cy = door[1] + 0.5
        dx = player_pos[0] - door_cx
        dy = player_pos[1] - door_cy
        dist = math.sqrt(dx*dx + dy*dy)
        draw_text(10, 740, f"Distance to door: {dist:.2f}", GLUT_BITMAP_HELVETICA_18)
    if game_state == GameState.won:
        draw_text(300, 420, "You Win! You reached the Final door!", GLUT_BITMAP_HELVETICA_18)
    elif game_state == GameState.lost:
        draw_text(350, 400, "Game is over! Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
    draw_text(10, 770, f"Life Remaining: {player_life}   Boxs collected: {boxs_collected}/3")
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 900)
    glutCreateWindow(b"Zombie Maze Shooter")
    glEnable(GL_DEPTH_TEST)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    initialize()
    glutDisplayFunc(showScreen)
    glutMainLoop()

if __name__=="__main__":
    main()

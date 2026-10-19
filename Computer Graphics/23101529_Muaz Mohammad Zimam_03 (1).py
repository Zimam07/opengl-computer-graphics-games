from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


############################################################# TILES DRAWING PART #################################################
window_width, window_height = 1000, 800
tiles_boundary = 800
def draw_tiles():
    tile_size = 50
    for x in range(-tiles_boundary, tiles_boundary, tile_size):
        for y in range(-tiles_boundary, tiles_boundary, tile_size):
            if (x // tile_size + y // tile_size) % 2 == 0:
                glColor3f(0.6, 0.6, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x+tile_size, y, 0)
            glVertex3f(x+tile_size, y+tile_size, 0)
            glVertex3f(x, y+tile_size, 0)
            glEnd()

############################################################ BOUNDARY DRAWING PART #######################################################3
def boundary():
    w_height = 100
    w_width = 20
#BLUE WALL DRAWING
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)
    glTranslatef(-tiles_boundary-w_width/2, 0, w_height/2)
    glScalef(w_width, tiles_boundary * 2, w_height)
    glutSolidCube(1)
    glPopMatrix()

#GREEN WALL DRAWING
    glPushMatrix()
    glColor3f(0.0, 1.0, 0.0)
    glTranslatef(tiles_boundary + w_width/2, 0, w_height / 2)
    glScalef(w_width, tiles_boundary * 2, w_height)
    glutSolidCube(1)
    glPopMatrix()

#CYAN WALL DRAWING
    glPushMatrix()
    glColor3f(0.0, 1.0, 1.0)
    glTranslatef(0, tiles_boundary + w_width/2, w_height / 2)
    glScalef(tiles_boundary * 2, w_width, w_height)
    glutSolidCube(1)
    glPopMatrix()

#WHITE WALL DRAWING
    glPushMatrix()
    glColor3f(1.0, 1.0, 1.0)
    glTranslatef(0, -tiles_boundary - w_width/2, w_height / 2)
    glScalef(tiles_boundary * 2, w_width, w_height)
    glutSolidCube(1)
    glPopMatrix()

###################################################### PLAYER DRAWING PART ##########################################################

player_pos = [0, 0]                  
player_standing = 90  
def draw_player():
    glPushMatrix()                                        
    glTranslatef(player_pos[0], player_pos[1], 0) 
    glRotatef(player_standing, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 0, 40)

#HEAD DRAWING PART
    glColor3f(0.15, 0.15, 0.15)
    glTranslatef(0, 250, 0)
    gluSphere(gluNewQuadric(), 40, 20, 20)               ##(gluNewQuadric, Radius, Slices, Stacks)

#BODY DRAWING PART
    glTranslatef(0, -100, 0)
    glPushMatrix()
    glScalef(1.2, 1.4, 0.6)
    glColor3f(0.1, 0.5, 0.8)
    glutSolidCube(80)
    glPopMatrix()

#LEG DRAWING PART
    glPushMatrix()
    glTranslatef(-20, -120, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.7)
    gluCylinder(gluNewQuadric(), 20, 10, 120, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(20, -120, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.7)
    gluCylinder(gluNewQuadric(), 20, 10, 120, 20, 20)                  #(gluNewQuadric, base, top, height, slices, stacks)
    glPopMatrix()

#ARM DRAWING

#RIGHT ARM DRAWING
    glPushMatrix()
    glTranslatef(-60, 15, 3) 
    glRotatef(-90, 0, 0, 1)
    glColor3f(0.2, 0.8, 0.2)
    gluCylinder(gluNewQuadric(), 16, 8, 70, 20, 20)
    glPopMatrix()

#LEFT ARM DRAWING
    glPushMatrix()
    glTranslatef(60, 15, 3)
    glRotatef(90, 0, 0, 1)
    glColor3f(0.2, 0.8, 0.2)
    gluCylinder(gluNewQuadric(), 16, 8, 70, 20, 20)
    glPopMatrix()

#GUN DRAWING
    glPushMatrix()
    glTranslatef(0, 15, 3)
    glColor3f(0.9, 0.1, 0.1)
    gluCylinder(gluNewQuadric(), 24, 12, 80, 20, 20)
    glPopMatrix()

    glPopMatrix()

####################################################### INSIDE BOUNDARY WORK #################################################
def inside_boundary(x, y, margin=0.0):
    limit = max(0.0, tiles_boundary - margin)
    x = max(-limit, min(limit, x))
    y = max(-limit, min(limit, y))
    return x, y
###################################################### ENEMY CLASS ############################################
class Enemy:
    def __init__(self):
        self.reset()

    def reset(self):
        angle = random.uniform(0, 2 * math.pi)
        radius = 500
        self.base_size = 60
        self.top_size  = 40
        self.growing   = True
        px = radius * math.cos(angle)
        py = radius * math.sin(angle)
        self.pos_x, self.pos_y = inside_boundary(px, py, self.base_size + 2.0)
        self.pos_z = 50

    def approach_player(self):
        dx = player_pos[0] - self.pos_x
        dy = player_pos[1] - self.pos_y
        distance = math.hypot(dx, dy)
        if distance > 1:
            step = 0.5
            self.pos_x += dx / distance * step
            self.pos_y += dy / distance * step
        self.pos_x, self.pos_y = inside_boundary(self.pos_x, self.pos_y, self.base_size + 2.0)
        if self.growing:
            self.base_size += 0.5
            self.top_size  += 0.3
            if self.base_size >= 70:
                self.growing = False
        else:
            self.base_size -= 0.5
            self.top_size  -= 0.3
            if self.base_size <= 50:
                self.growing = True
        self.base_size = max(50, min(self.base_size, 70))
        self.top_size  = max(30, min(self.top_size, 50))
        self.pos_x, self.pos_y = inside_boundary(self.pos_x, self.pos_y, self.base_size + 2.0)

    def draw(self):
#BIG SPHERE ON BOTTOM
        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        glColor3f(0.9, 0.1, 0.1)
        glutSolidSphere(self.base_size, 20, 20)
        glPopMatrix()

#LITTLE SPHERE ON TOP
        glPushMatrix()
        top_center_z = self.pos_z + self.base_size + self.top_size
        glTranslatef(self.pos_x, self.pos_y, top_center_z)
        glColor3f(0.1, 0.1, 0.1)
        glutSolidSphere(self.top_size, 20, 20)
        glPopMatrix()

############################################################ BULLET GENERATING PART  ##########################################33
class Bullet:
    def __init__(self, pos_x, pos_y, direction_deg):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = 120
        self.direction = direction_deg

    def move(self):
        self.pos_x += 10 * math.cos(math.radians(self.direction - 90))
        self.pos_y += 10 * math.sin(math.radians(self.direction - 90))

def bullet_draw(bullet):
    glPushMatrix()
    glTranslatef(bullet.pos_x, bullet.pos_y, bullet.pos_z)
    glColor3f(1, 0, 0)
    glutSolidCube(8)
    glPopMatrix()


####################################################### DEAD ENEMY PART ############################################
dead_pose = False
dead_pos = [0.0, 0.0]
dead_angle = 0.0

bullets = []
enemies = []

dead_enemies = []
PLAYER_RADIUS = 70.0

def draw_dead_enemies():
    for m in dead_enemies:
        glPushMatrix()
        glTranslatef(m["x"], m["y"], m["z"])
        glRotatef(m["tilt_deg"], 1, 0, 0)
        glColor3f(0.7, 0.08, 0.08)
        glutSolidSphere(m["base"], 20, 20)
        glTranslatef(0, 0, m["base"] + m["top"])
        glColor3f(0.2, 0.2, 0.2)
        glutSolidSphere(m["top"], 20, 20)
        glPopMatrix()

def dead_player_position():
    global dead_pose, dead_pos, dead_angle
    BIG_FALL_MARGIN = 300.0
    dead_pos[0], dead_pos[1] = inside_boundary(player_pos[0], player_pos[1], BIG_FALL_MARGIN)
    dead_angle = player_standing
    dead_pose = True

lives = 5 
missed = 0
score = 0
game_over = False

cheat_mode = False
vision_mode = False
cheat_count = 0

##################################################### CHEAT MODE PART #########################################################
def cheat_mode_func():
    global cheat_count, player_standing
    cheat_count += 1
    player_standing = (player_standing + 3) % 360
    if cheat_count % 100 == 0 and enemies:
        nearest = min(enemies, key=lambda e: (e.pos_x - player_pos[0])**2 + (e.pos_y - player_pos[1])**2)
        dx = nearest.pos_x - player_pos[0]
        dy = nearest.pos_y - player_pos[1]
        aim_deg = 90 + math.degrees(math.atan2(dy, dx))
        player_standing = aim_deg
        spawn_x = player_pos[0] + 10 * math.cos(math.radians(player_standing - 90))
        spawn_y = player_pos[1] + 10 * math.sin(math.radians(player_standing - 90))
        bullets.append(Bullet(spawn_x, spawn_y, player_standing))



##################################################### DISPLAY TEXT PART ######################################################

def display_text(x, y, message):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for char in message:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
####################################################### CAMERA PART ################################################################
cam_current   = False
orbit_radius    = 700
orbit_theta_deg = 35
cam_height   = 420
cam_angle      = 105 
def use_follow_camera_now():
    return cam_current or (cheat_mode and vision_mode)
def setup_camera():
    aspect_ratio = float(window_width) / float(window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if use_follow_camera_now():
        gluPerspective(90.0, aspect_ratio, 1.0, 3000.0)                    #(fovY, Aspect, Znear, Zfar)
    else:
        gluPerspective(cam_angle, aspect_ratio, 1.0, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if use_follow_camera_now():
        fwd_x = math.cos(math.radians(player_standing - 90))
        fwd_y = math.sin(math.radians(player_standing - 90))
        offset_x = player_pos[0] + 100 * fwd_x
        offset_y = player_pos[1] + 100 * fwd_y
        offset_z = 100
        gluLookAt(offset_x, offset_y, offset_z,
                  player_pos[0] + 200 * fwd_x,
                  player_pos[1] + 200 * fwd_y,
                  offset_z,
                  0.0, 0.0, 1.0)
    else:
        th = math.radians(orbit_theta_deg)
        eye_x = orbit_radius * math.cos(th)
        eye_y = orbit_radius * math.sin(th)
        eye_z = cam_height
        gluLookAt(eye_x, eye_y, eye_z,
                  0.0, 0.0, 0.0,
                  0.0, 0.0, 1.0)
##################################################### RENDER GAME PART ########################################################
def render_game():
    global bullets, enemies, lives, missed, score, game_over, cheat_mode, dead_pose

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)
    setup_camera()

    if game_over:
        cheat_mode = False 
        draw_tiles()
        boundary()

        if not dead_pose:
            dead_player_position()
        glPushMatrix()
        glTranslatef(dead_pos[0], dead_pos[1], 0)
        glRotatef(dead_angle, 0, 0, 1)
        glRotatef(90, 1, 0, 0)
        glRotatef(45, 0, 1, 0)
        draw_player()
        glPopMatrix()
        draw_dead_enemies()

        display_text(40, window_height - 100, f" Score: {score} Life: {lives} Missed: {missed}")
        display_text(40, 700, "GAME OVER! Press 'R' to Restart")
        glutSwapBuffers()
        return
    draw_tiles()
    boundary()
    draw_player()
    new_bullets = []
    for bullet in bullets:
        bullet.move()

        if abs(bullet.pos_x) > tiles_boundary or abs(bullet.pos_y) > tiles_boundary:
            missed += 1
            continue

        hit = False
        for enemy in enemies:
            dx = enemy.pos_x - bullet.pos_x
            dy = enemy.pos_y - bullet.pos_y
            dist = math.hypot(dx, dy)
            if dist < enemy.base_size:
                score += 1
                dead_enemies.append({
                    "x": enemy.pos_x, "y": enemy.pos_y, "z": enemy.pos_z,
                    "base": enemy.base_size, "top": enemy.top_size,
                    "ttl": 45,
                    "tilt_deg": random.uniform(65, 100)
                })
                enemy.reset()
                hit = True
                break
        if not hit:
            new_bullets.append(bullet)
        bullet_draw(bullet)

    bullets = new_bullets
    for enemy in enemies:
        enemy.approach_player()
        enemy.draw()
    draw_dead_enemies()

    for enemy in enemies:
        dx = enemy.pos_x - player_pos[0]
        dy = enemy.pos_y - player_pos[1]
        if math.hypot(dx, dy) < enemy.base_size + 30:
            lives -= 1
            enemy.reset()

    if (lives <= 0 or missed >= 10) and not game_over:
        dead_player_position()
        game_over = True

    display_text(40, window_height - 90, f"Life: {lives}  Score: {score}  Missed: {missed}")
    glutSwapBuffers()

######################################################### KEYBOARD PART ##################################################################
def camera_key(key, x, y):
    global orbit_theta_deg, cam_height
    if key == GLUT_KEY_LEFT:
        orbit_theta_deg += 5
    elif key == GLUT_KEY_RIGHT:
        orbit_theta_deg -= 5
    elif key == GLUT_KEY_UP:
        cam_height += 20
    elif key == GLUT_KEY_DOWN:
        cam_height -= 20
    cam_height = max(120, min(cam_height, 2000))

def keyboard(key, x, y):
    global player_pos, player_standing
    global cheat_mode, vision_mode
    global lives, score, missed, bullets, game_over, dead_pose, cam_current
    if key in (b'f', b'F'):
        cam_current = not cam_current
        glutPostRedisplay()
        return
    if game_over and key in (b'r', b'R'):
        lives = 5
        missed = 0
        score = 0
        bullets.clear()
        dead_enemies.clear()
        for enemy in enemies:
            enemy.reset()
        game_over = False
        dead_pose = False
        return
    if game_over:
        return
    
    if key in (b'w', b'W'):
        nx = player_pos[0] + 20 * math.cos(math.radians(player_standing - 90))
        ny = player_pos[1] + 20 * math.sin(math.radians(player_standing - 90))
        player_pos[0], player_pos[1] = inside_boundary(nx, ny, PLAYER_RADIUS)
    elif key in (b's', b'S'):
        nx = player_pos[0] - 20 * math.cos(math.radians(player_standing - 90))
        ny = player_pos[1] - 20 * math.sin(math.radians(player_standing - 90))
        player_pos[0], player_pos[1] = inside_boundary(nx, ny, PLAYER_RADIUS)
    elif key in (b'a', b'A'):
        player_standing += 10
    elif key in (b'd', b'D'):
        player_standing -= 10
    elif key in (b'c', b'C'):
        cheat_mode = not cheat_mode
    elif key in (b'v', b'V'):
        vision_mode = not vision_mode

########################################################### MOUSE PART #########################################################

def mouse(button, state, x, y):
    global cam_current
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        spawn_x = player_pos[0] + 10 * math.cos(math.radians(player_standing - 90))
        spawn_y = player_pos[1] + 10 * math.sin(math.radians(player_standing - 90))
        bullets.append(Bullet(spawn_x, spawn_y, player_standing))
        glutPostRedisplay()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        cam_current = not cam_current
        glutPostRedisplay()

################################################# UPDATE PART ####################################################
def update_func():
    if dead_enemies:
        survivors = []
        for m in dead_enemies:
            m["ttl"] -= 1
            if m["ttl"] > 0:
                survivors.append(m)
        dead_enemies[:] = survivors
    if cheat_mode:
        cheat_mode_func()
    glutPostRedisplay()

################################################# INITIALIZATION PART ###########################################
def initialize():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Bullet Frenzy")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.08, 1.0)

    glutDisplayFunc(render_game)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(camera_key)
    glutMouseFunc(mouse)
    glutIdleFunc(update_func)

    enemies.clear()
    for _ in range(5):
        enemies.append(Enemy())
    glutMainLoop()

if __name__ == '__main__':
    initialize() 
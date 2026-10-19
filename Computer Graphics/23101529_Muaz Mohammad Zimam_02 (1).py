from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import sys

# Window size
width, height = 800, 600
ball_size = 18
ball_speed = 1

# Catcher variables
catcher_x = width // 2
catcher_y = 60
catcher_w = 120
catcher_h = 10

# Initial game state
score = 0
active_ball = None
pause = False
game_over = False
button_size = 28

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(round(x)), int(round(y)))
    glEnd()

def color_generator():
    return (
        random.uniform(0, 1.0),
        random.uniform(0, 1.0),
        random.uniform(0, 1.0)
    )

def new_ball():
    return {
        "x": random.randint(ball_size, width-ball_size),
        "y": height-ball_size,
        "color": color_generator()
    }

# Finding zone using midpoint line drawing algorithm
def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    new_dx = abs(dx)
    new_dy = abs(dy)
    if new_dx >= new_dy:
        if dx >= 0 and dy >= 0: return 0
        elif dx < 0 and dy >= 0: return 3
        elif dx < 0 and dy < 0: return 4
        else: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        elif dx < 0 and dy >= 0: return 2
        elif dx < 0 and dy < 0: return 5
        else: return 6
        
# Converting any zone to zone 0
def convert_zone0(x, y, zone):
    if zone == 0: 
        return (x, y)
    elif zone == 1: 
        return (y, x)
    elif zone == 2:    
        return (y, -x)
    elif zone == 3:   
        return (-x, y)
    elif zone == 4:     
        return (-x, -y)
    elif zone == 5:    
        return (-y, -x)
    elif zone == 6:    
        return (-y, x)
    elif zone == 7:  
        return (x, -y)


# Converting back to their original zone
def convert_original(x, y, zone):
    if zone == 0:
        return (x, y)
    elif zone == 1:
        return (y, x)
    elif zone == 2: 
        return (-y, x)
    elif zone == 3:
        return (-x, y)
    elif zone == 4: 
        return (-x, -y)
    elif zone == 5:
        return (-y, -x)
    elif zone == 6:
        return (y, -x)
    elif zone == 7:
        return (x, -y)


# Using midpoint line drawing algorithm
def midpoint(x1, y1, x2, y2):
    x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
    zone = find_zone(x1, y1, x2, y2)
    new_x1, new_y1 = convert_zone0(x1, y1, zone)
    new_x2, new_y2 = convert_zone0(x2, y2, zone)
    new_x1, new_y1, new_x2, new_y2 = int(new_x1), int(new_y1), int(new_x2), int(new_y2)
    dx = new_x2 - new_x1
    dy = new_y2 - new_y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = new_x1, new_y1
    for _ in range(int(dx) + 1):
        px, py = convert_zone0(x, y, zone)
        draw_pixel(px, py)
        if d > 0:
            y += 1
            d += incNE
        else:
            d += incE
        x += 1

# Ball drawing
def render_ball(cx, cy, r):
    midpoint(cx, cy + r, cx + r, cy)
    midpoint(cx + r, cy, cx, cy - r)
    midpoint(cx, cy - r, cx - r, cy)
    midpoint(cx - r, cy, cx, cy + r)

# Collision check (AABB)
def overlap(a, b):
    return (
        a["x"] < b["x"] + b["width"] and
        a["x"] + a["width"] > b["x"] and
        a["y"] < b["y"] + b["height"] and
        a["y"] + a["height"] > b["y"]
    )

# Catcher drawing
def catcher(x, y, w, h):
    glColor3f(1.0, 0.0, 0.0) if game_over else glColor3f(1.0, 1.0, 1.0)
    margin = 15
    b_y = y
    tl_x = x
    tr_x = x + w
    bl_x = x + margin
    br_x = x + w - margin
    t_y = y + h
    midpoint(tl_x, t_y, tr_x, t_y)
    midpoint(tr_x, t_y, br_x, b_y)
    midpoint(br_x, b_y, bl_x, b_y)
    midpoint(bl_x, b_y, tl_x, t_y)

# Button drawing
def buttons():
    # First Button (Restart)
    glColor3f(0.0, 1.0, 1.0)
    x_start = 20
    y_center = (height - 20) - (button_size // 2)
    midpoint(x_start, y_center, x_start + button_size, y_center)
    midpoint(x_start, y_center, x_start + 10, y_center + 10)
    midpoint(x_start, y_center, x_start + 10, y_center - 10)

    # Second Button (Pause)
    glColor3f(1.0, 0.6, 0.0)
    centre_x = width // 2
    top_y = height - 20
    bottom_y = (height - 20) - button_size
    if pause:
        midpoint(centre_x - 5, bottom_y, centre_x - 5, top_y)
        midpoint(centre_x - 5, top_y, centre_x + 10, (top_y + bottom_y) // 2)
        midpoint(centre_x + 10, (top_y + bottom_y) // 2, centre_x - 5, bottom_y)
    else:
        midpoint(centre_x - 8, bottom_y, centre_x - 8, top_y)
        midpoint(centre_x + 8, bottom_y, centre_x + 8, top_y)
    
    # Third Button (Exit)
    glColor3f(1.0, 0.0, 0.0)
    midpoint((width - 20) - button_size, height - 20, width - 20, (height - 20) - button_size)
    midpoint((width - 20) - button_size, (height - 20) - button_size, width - 20, height - 20)

# Rendering the frame
def render_frame():
    glClear(GL_COLOR_BUFFER_BIT)
    catcher(catcher_x, catcher_y, catcher_w, catcher_h)
    buttons()
    if active_ball:
        glColor3f(*active_ball["color"])
        render_ball(active_ball["x"], active_ball["y"], ball_size)
    glutSwapBuffers()

# Main game loop
def loop(value):
    global active_ball, score, pause, ball_speed, game_over
    if pause:
        glutPostRedisplay()
        glutTimerFunc(16, loop, 0)
        return

    if active_ball:
        active_ball["y"] -= ball_speed
        ball_box = {
            "x": active_ball["x"] - ball_size,
            "y": active_ball["y"] - ball_size,
            "width": 2 * ball_size,
            "height": 2 * ball_size
        }
        catcher_box = {
            "x": catcher_x,
            "y": catcher_y,
            "width": catcher_w,
            "height": catcher_h
        }
        if overlap(ball_box, catcher_box):
            score += 1
            ball_speed += 0.2
            print(f"Score: {score}")
            active_ball = new_ball()
        elif active_ball["y"] < 0:
            print(f"Game Over! Final Score: {score}")
            active_ball = None
            pause = True
            game_over = True

    glutPostRedisplay()
    glutTimerFunc(16, loop, 0)

# Initialize canvas
def init_canvas():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

# Mouse input handling
def mouse(button, state, x, y):
    global pause, score, ball_speed, active_ball, game_over
    if state != GLUT_DOWN:
        return
    y = height - y

    # First Button (Restart)
    if 20 <= x <= (20 + button_size) and (height - 20) - button_size <= y <= (height - 20):
        score = 0
        ball_speed = 2
        active_ball = new_ball()
        pause = False
        game_over = False
        print("Restarting:")

    # Second Button (Pause)
    if (width // 2) - 15 <= x <= (width // 2) + 15 and (height - 20) - button_size <= y <= (height - 20):
        pause = not pause

    # Third Button (Exit)
    if (width - 20) - button_size <= x <= (width - 20) and (height - 20) - button_size <= y <= (height - 20):
        print(f"Goodbye! Final Score: {score}")
        try:
            glutLeaveMainLoop()
        except:
            sys.exit()

# Keyboard input handling
def keyboard(key, x, y):
    global catcher_x
    if pause: return
    if key == GLUT_KEY_LEFT and catcher_x > 0:
        catcher_x -= 12
    elif key == GLUT_KEY_RIGHT and (catcher_x + catcher_w) < width:
        catcher_x += 12

# Start the game
def start():
    global active_ball
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Catcher Game")
    init_canvas()
    active_ball = new_ball()
    glutDisplayFunc(render_frame)
    glutMouseFunc(mouse)
    glutSpecialFunc(keyboard)
    glutTimerFunc(16, loop, 0)
    glutMainLoop()

if __name__ == "__main__":
    start()

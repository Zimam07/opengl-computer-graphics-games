# Task 1: Building a House in Rainfall

# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random

# width,height=500,500
# raindrops=[(random.randint(0,width),random.randint(0,height)) for _ in range(500)]
# rain_direction=0
# background_color = [0.6,0.8,1.0]

# def rain_part():
#     glColor3f(0.5,0.5,1.0)
#     glPointSize(4)
#     glBegin(GL_POINTS)
#     for i in range(len(raindrops)):
#         x,y=raindrops[i]
#         glVertex2f(x,y)
#         raindrops[i]=(x+rain_direction,y-7)
#         if raindrops[i][1]<0:raindrops[i]=(random.randint(0,width),height)
#     glEnd()

# def house_part():
#     glColor3f(0.6,0.3,0.0)
#     glBegin(GL_QUADS)
#     glVertex2f(150,100)
#     glVertex2f(350,100)
#     glVertex2f(350,250)
#     glVertex2f(150,250)
#     glEnd()

#     glColor3f(1.0,0.0,0.0)
#     glBegin(GL_TRIANGLES)
#     glVertex2f(120,250)
#     glVertex2f(380,250)
#     glVertex2f(250,350)
#     glEnd()

#     glColor3f(0,0,0)
#     glBegin(GL_QUADS)
#     glVertex2f(230,100)
#     glVertex2f(270,100)
#     glVertex2f(270,180)
#     glVertex2f(230,180)
#     glEnd()

# def iterate():
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(0,width,0,height,-1,1)
#     glMatrixMode(GL_MODELVIEW)

# def showScreen():
#     glClearColor(*background_color, 1.0)
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
#     iterate()
#     house_part()
#     rain_part()
#     glutSwapBuffers()

# def arrow_keys(key,x,y):
#     global rain_direction
#     if key==GLUT_KEY_LEFT:
#         rain_direction-=1
#     elif key==GLUT_KEY_RIGHT:
#         rain_direction+=1

# def background_change_buttons(key,x,y):
#     global background_color
#     key=key.decode("utf-8")
#     if key=='n':
#         background_color=[0.0,0.0,0.2]
#     elif key=='d':
#         background_color=[0.6,0.8,1.0]

# def update(value):
#     glutPostRedisplay()
#     glutTimerFunc(50,update,0)

# glutInit()
# glutInitDisplayMode(GLUT_RGBA)
# glutInitWindowSize(width,height)
# glutCreateWindow(b"House in Rainfall")
# glutDisplayFunc(showScreen)
# glutSpecialFunc(arrow_keys)
# glutKeyboardFunc(background_change_buttons)
# glutTimerFunc(50,update,0)
# glutMainLoop()





# Task 2: Building the Amazing Box

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

points=[]
last_blink_time=0
window_width=600
window_height=600
initial_speed=1.5
freeze=False
blink_active=False
blink_state=False

def init():
    glClearColor(0.0,0.0,0.0,1.0)
    gluOrtho2D(0,window_width,0,window_height)

def box_part():
    glColor3f(1,1,1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    glVertex2f(window_width,0)
    glVertex2f(window_width,window_height)
    glVertex2f(0,window_height)
    glEnd()

def point_part(x,y):
    glPointSize(8)
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    box_part()
    for point in points:
        if blink_active and blink_state:
            glColor3f(0,0,0)
        else:
            glColor3fv(point['color'])
        point_part(point['x'],point['y'])
    glutSwapBuffers()

def update(value):
    global last_blink_time,blink_state
    if not freeze:
        current_time=glutGet(GLUT_ELAPSED_TIME) / \
            1000.0
        for point in points:
            point['x']+=point['dx_dir']*point['speed']
            point['y']+=point['dy_dir']*point['speed']
            if point['x']<=0 or point['x']>=window_width:
                point['dx_dir']*=-1
                point['x']=max(0,min(point['x'],window_width))
            if point['y']<=0 or point['y']>=window_height:
                point['dy_dir']*=-1
                point['y']=max(0,min(point['y'],window_height))
        if blink_active:
            if current_time-last_blink_time>=0.5:
                blink_state=not blink_state
                last_blink_time=current_time
        glutPostRedisplay()
    glutTimerFunc(16,update,0)

def mouse_part(button,state,x,y):
    if freeze:
        return
    y=window_height-y
    if button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
        new_point={
            'x':x,
            'y':y,
            'dx_dir':random.choice([-1,1]),
            'dy_dir':random.choice([-1,1]),
            'speed':initial_speed,
            'color':(random.random(),random.random(),random.random())
        }
        points.append(new_point)
    elif button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
        global blink_active
        blink_active=not blink_active
def space_bar(key,x,y):
    global freeze
    if key==b' ':
        freeze=not freeze

def keyboard_part(key,x,y):
    if freeze:
        return
    if key==GLUT_KEY_UP:
        for point in points:
            point['speed']*=1.1
    elif key==GLUT_KEY_DOWN:
        for point in points:
            point['speed']*=0.9

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Amazing Box")
    init()
    glutDisplayFunc(display)
    glutTimerFunc(0,update,0)
    glutMouseFunc(mouse_part)
    glutSpecialFunc(keyboard_part)
    glutKeyboardFunc(space_bar)
    glutMainLoop()

if __name__ == "__main__":
    main()
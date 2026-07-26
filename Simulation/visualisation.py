import pygame as pg
import math

import os
import sys
import json



base_dir = os.path.dirname(os.path.abspath(__file__))

logs_dir = os.path.join(base_dir, 'logs')

filename = os.path.join(logs_dir, 'simulation.json')



try:

    with open(filename, 'r') as f:

        logs = json.load(f)

    print(f'\nlogs loaded from : {filename}')

except FileNotFoundError:
    
    raise Exception(f'No logs found at {filename}')


parametre = logs[0]

g = parametre['g']
m = parametre['m']
M = parametre['M']
l = parametre['l']
max_x = parametre['max_x']

print(f'\nParametre : gravité = {g}, masse pendule = {m}, masse chariot = {M}, longeur pendule = {l}')




os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 25'
pg.init()

info = pg.display.Info()
largeur, hauteur = info.current_w, info.current_h - 25

screen = pg.display.set_mode((largeur, hauteur), pg.RESIZABLE)
pg.display.set_caption("basic")

clock = pg.time.Clock()
font = pg.font.SysFont('Trebuchet MS', 25)
fps = 0.0




def handle_event():
    
    global largeur, hauteur, screen, speed, reset

    for e in pg.event.get():
        
        if e.type == pg.QUIT:
            
            pg.quit()
            sys.exit()

        if e.type == pg.KEYDOWN:
            
            if e.key == pg.K_UP:
                
                speed *= 2
                speed = min(speed, 32)


            if e.key == pg.K_DOWN:
                
                speed /= 2
                speed = max(speed, 0.125)


            if e.key == pg.K_r:
                
                reset = True


def draw_texte(x, y, texte, shadow = True):
    
    if shadow:
        
        shadow_surface = font.render(texte, True, (40, 40, 40))
        
        screen.blit(shadow_surface, (x + 2, y + 2))

    texte_surface = font.render(texte, True, (240, 230, 230))
    
    screen.blit(texte_surface, (x, y))


def texte_fps(dt):
    
    global fps
    
    if dt > 0:
        
        instant_fps = 1 / dt
        fps = 0.9 * fps + 0.1 * instant_fps
        
    else:
        
        fps = fps
        
    draw_texte(10, 10, f'FPS : {int(fps)}')


def draw_pendule(data):
    
    x = data['x']
    x *= 250

    mid_x = largeur // 2
    mid_y = hauteur // 2

    pos = (
        int(mid_x + x),
        int(mid_y)
    )

    lenght = l * 100

    angle = data['theta'] - math.pi/ 2

    pos_ = (
        int(pos[0] + lenght * math.cos(angle)),
        int(pos[1] + lenght * math.sin(angle))
    )


    # zone de déplacement (rail)
    pg.draw.line(
        screen,
        (150, 150, 150),
        (mid_x - max_x * 250, mid_y),
        (mid_x + max_x * 250, mid_y),
        1
    )

    # la tige du pendule
    pg.draw.line(
        screen,
        (255, 255, 255),
        pos,
        pos_,
        3
    )

    # la boule du chario
    pg.draw.circle(
        screen,
        (40, 40, 255),
        pos,
        20
    )

    # la boule au bout de la tige
    pg.draw.circle(
        screen,
        (255, 40, 40),
        pos_,
        15
    )



dt_total = 0

speed = 1

while True:

    dt = clock.tick(1440) / 1000

    dt_total += dt * speed

    reset = False

    handle_event()

    if reset:

        speed = 1
        dt_total = 0

    tick = int(dt_total / 0.016)

    tick %= (len(logs) - 1)

    data = logs[tick + 1]

    screen.fill((0, 0, 0))

    texte_fps(dt = dt)

    text = f"x = {data['x']:<25}"
    draw_texte(1250, 90, text, True)

    text = f"theta (rad) = {data['theta'] / math.pi:<20}"
    draw_texte(1175, 50, text, True)
    
    text = f"force : {data['force']:.2f}"
    draw_texte(1200, 130, text, True)

    text = f'tick : {tick}'
    draw_texte(1450, 10, text, True)

    text = f'temps : {tick * 0.016:.2f}s'
    draw_texte(1225, 10, text, True)

    text = f'speed : {speed}x'
    draw_texte(1050, 10, text, True)

    draw_pendule(data)

    pg.display.update()
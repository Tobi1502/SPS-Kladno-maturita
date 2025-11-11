
'''Flappy Dino
Autor: Toby
'''

import pygame
import random
import sys

# --------------------------- Konfigurace ---------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Cesty k obrázkům (vlož sem cesty k obrázkům, pokud chceš používat vlastní)
BIRD_IMG_PATH = "C:\\Users\\tobik\\Desktop\\Projekt M\\Bird.png"
BACKGROUND_IMG_PATH = "C:\\Users\\tobik\\Desktop\\Projekt M\\Džungle.png"
PILLAR_IMG_PATH = "C:\\Users\\tobik\\Desktop\\Projekt M\\Pilíř2.png"

# Barvy a styl
BG_COLOR = (15, 30, 15)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (70, 20, 20)
BUTTON_HOVER = (120, 20, 20)
BIRD_COLOR = (240, 200, 60)

# Pták
BIRD_SIZE = 108
GRAVITY = 0.45
FLAP_STRENGTH = -9.5

# Překážky
PILLAR_WIDTH = 110
PILLAR_MIN_HEIGHT = 60
PILLAR_MAX_HEIGHT = 260
SPAWN_INTERVAL = 1100
BASE_SPEED = 3.4
SPEED_INCREMENT_PER_SCORE = 0.18
MAX_HEIGHT_DIFF = 120
MIN_GAP_RATIO = 0.25
NEXT_GAP_EXTRA = 90

# Nová proměnná pro horizontální vzdálenost mezi pilíři (3x větší)
MIN_HORIZONTAL_GAP = 3 * 200  # původně ~200 px

# --------------------------- Datové struktury ----------------------------
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
    def rect(self):
        return pygame.Rect(int(self.x - BIRD_SIZE/2), int(self.y - BIRD_SIZE/2), BIRD_SIZE, BIRD_SIZE)

class Pillar:
    def __init__(self, x, height, is_top):
        self.x = x
        self.height = height
        self.width = PILLAR_WIDTH
        self.is_top = is_top
    def rect(self, screen_height):
        if self.is_top:
            return pygame.Rect(int(self.x), 0, self.width, self.height)
        else:
            return pygame.Rect(int(self.x), screen_height - self.height, self.width, self.height)

# --------------------------- Pomocné funkce ------------------------------
def draw_background(surface, width, height, bg_image):
    if bg_image:
        surface.blit(pygame.transform.scale(bg_image, (width, height)), (0,0))
    else:
        for i in range(height):
            color = (15, 15 + int(i*20/height), 15)
            pygame.draw.line(surface, color, (0,i), (width,i))
        for i in range(6):
            cx = i*(width//6)+30
            cy = height - 60
            pygame.draw.rect(surface, (30,20,10), (cx, cy-100, 20, 100))
            pygame.draw.ellipse(surface, (10,50,10), (cx-30, cy-120, 80, 80))

def draw_bird(surface, bird, bird_image):
    r = bird.rect()
    if bird_image:
        surface.blit(pygame.transform.scale(bird_image, (BIRD_SIZE,BIRD_SIZE)), (r.x,r.y))
    else:
        pygame.draw.ellipse(surface, BIRD_COLOR, r)

def draw_pillar(surface, pillar, pillar_image, screen_height):
    r = pillar.rect(screen_height)
    if pillar_image:
        surface.blit(pygame.transform.scale(pillar_image, (r.width, r.height)), (r.x, r.y))
    else:
        if pillar.is_top:
            for i in range(r.height):
                shade = 80 + int(i*(50/r.height))
                pygame.draw.line(surface, (shade, shade, shade), (r.x, r.y+i), (r.x+r.width, r.y+i))
        else:
            for i in range(r.height):
                shade = 130 - int(i*(50/r.height))
                pygame.draw.line(surface, (shade, shade, shade), (r.x, r.y+i), (r.x+r.width, r.y+i))

def draw_hud(surface, score, distance, width, font):
    score_s = font.render(f"Skóre: {score}", True, TEXT_COLOR)
    dist_s = font.render(f"Vzdálenost: {int(distance)} m", True, TEXT_COLOR)
    surface.blit(score_s, (11,11))
    surface.blit(dist_s, (width - dist_s.get_width() -11, 11))
    surface.blit(score_s, (10,10))
    surface.blit(dist_s, (width - dist_s.get_width() -10, 10))

def draw_button(surface, rect, text, font, hover=False):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=12)
    text_s = font.render(text, True, TEXT_COLOR)
    surface.blit(text_s, text_s.get_rect(center=rect.center))

# --------------------------- Hlavní hra ----------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Flappy Dino")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Verdana', 28, bold=True)
    large_font = pygame.font.SysFont('Verdana', 46, bold=True)

    bird_img = pygame.image.load(BIRD_IMG_PATH) if BIRD_IMG_PATH else None
    bg_img = pygame.image.load(BACKGROUND_IMG_PATH) if BACKGROUND_IMG_PATH else None
    pillar_img = pygame.image.load(PILLAR_IMG_PATH) if PILLAR_IMG_PATH else None

    in_menu = True
    fullscreen = False
    running = True

    bird = None
    pillars = []
    score = 0
    distance = 0
    speed = BASE_SPEED
    last_spawn = 0
    game_over = False
    last_top_height = None

    def start_new_game(width, height):
        bird = Bird(width*0.28, height/2)
        pillars = []
        score = 0
        distance = 0.0
        speed = BASE_SPEED
        last_spawn = pygame.time.get_ticks()
        return bird, pillars, score, distance, speed, last_spawn

    while running:
        dt = clock.tick(FPS)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if in_menu:
                        running = False
                    else:
                        in_menu = True
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                elif event.key == pygame.K_SPACE:
                    if in_menu:
                        in_menu = False
                        SCREEN_W, SCREEN_H = screen.get_size()
                        bird, pillars, score, distance, speed, last_spawn = start_new_game(SCREEN_W, SCREEN_H)
                        game_over = False
                    elif bird and not game_over:
                        bird.vy = FLAP_STRENGTH
                elif event.key == pygame.K_r and game_over:
                    SCREEN_W, SCREEN_H = screen.get_size()
                    bird, pillars, score, distance, speed, last_spawn = start_new_game(SCREEN_W, SCREEN_H)
                    game_over = False
                    last_top_height = None

        w, h = screen.get_size()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        MIN_GAP_CURRENT = max(int(h*MIN_GAP_RATIO), BIRD_SIZE*2 + 20)

        if in_menu:
            draw_background(screen, w, h, bg_img)
            title = large_font.render("Flappy Dino", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(w//2, h//4)))
            button_rect = pygame.Rect(w//2-130, h//2-35, 260, 70)
            hover = button_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, button_rect, "Hrát", font, hover)
            hint = font.render("Stiskni F pro fullscreen. Mezerník nebo klik start.", True, TEXT_COLOR)
            screen.blit(hint, hint.get_rect(center=(w//2, h//2 + 60)))
            if pygame.mouse.get_pressed()[0] and hover:
                in_menu = False
                SCREEN_W, SCREEN_H = screen.get_size()
                bird, pillars, score, distance, speed, last_spawn = start_new_game(SCREEN_W, SCREEN_H)
                game_over = False
            pygame.display.flip()
            continue

        if bird and not game_over:
            w, h = screen.get_size()
            # --- Spawn pilířů ---
            if not pillars:
                # první pilíře spawnou blíže pro vyšší obtížnost
                gap_x = w * 0.6
            else:
                # následující páry pilířů s horizontálním gapem
                gap_x = pillars[-1].x + MIN_HORIZONTAL_GAP

            if not pillars or (pillars[-1].x + PILLAR_WIDTH < w):
                if last_top_height is None:
                    last_top_height = random.randint(PILLAR_MIN_HEIGHT, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT)
                max_diff = min(MAX_HEIGHT_DIFF, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT - PILLAR_MIN_HEIGHT)
                delta = random.randint(-max_diff, max_diff)
                top_height = max(PILLAR_MIN_HEIGHT, min(last_top_height + delta, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT))
                bottom_height = h - top_height - MIN_GAP_CURRENT
                pillars.append(Pillar(gap_x, top_height, True))
                pillars.append(Pillar(gap_x, bottom_height, False))
                last_top_height = top_height + NEXT_GAP_EXTRA

            for p in pillars:
                p.x -= speed
            pillars = [p for p in pillars if p.x + p.width > -50]

            # --- Pták ---
            bird.vy += GRAVITY
            bird.y += bird.vy
            if bird.y - BIRD_SIZE/2 <=0 or bird.y + BIRD_SIZE/2 >= h:
                game_over = True

            bird_rect = bird.rect()
            passed_any = False
            for i in range(0, len(pillars), 2):
                top_p, bottom_p = pillars[i], pillars[i+1]
                if bird_rect.colliderect(top_p.rect(h)) or bird_rect.colliderect(bottom_p.rect(h)):
                    game_over = True
                    break
                center_x = top_p.x + top_p.width/2
                if center_x < bird.x and center_x + speed >= bird.x:
                    score +=1
                    passed_any = True
            if passed_any:
                speed += SPEED_INCREMENT_PER_SCORE
            distance += speed*dt*12

            # --- Kreslení ---
            draw_background(screen, w, h, bg_img)
            for p in pillars:
                draw_pillar(screen, p, pillar_img, h)
            draw_bird(screen, bird, bird_img)
            draw_hud(screen, score, distance, w, font)
            pygame.display.flip()
            continue

        # --- Game over ---
        if game_over:
            draw_background(screen, w, h, bg_img)
            for p in pillars:
                draw_pillar(screen, p, pillar_img, h)
            if bird:
                draw_bird(screen, bird, bird_img)
            draw_hud(screen, score, distance, w, font)
            over_text = large_font.render("Game Over", True, (220,40,40))
            screen.blit(over_text, over_text.get_rect(center=(w//2, h//2-40)))
            sub = font.render("Stiskni R pro restart, ESC pro menu", True, TEXT_COLOR)
            screen.blit(sub, sub.get_rect(center=(w//2, h//2+10)))
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=='__main__':
    main()

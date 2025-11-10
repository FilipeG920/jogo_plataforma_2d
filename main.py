import pgzrun
import math

WIDTH = 800
HEIGHT = 480
TITLE = "Alien Adventure Platformer"

# ---------- Estados ----------
game_state = "menu"
music_enabled = True
sound_enabled = True

# ---------- Botões ----------
buttons = {
    "start": Rect((WIDTH // 2 - 100, 200), (200, 50)),
    "sound": Rect((WIDTH // 2 - 100, 270), (200, 50)),
    "quit":  Rect((WIDTH // 2 - 100, 340), (200, 50)),
}

# ---------- Física ----------
GRAVITY = 0.5
MOVE_SPEED = 3
JUMP_SPEED = -11

# ---------- Classes ----------
class Platform:
    def __init__(self, x, y, w, h):
        self.rect = Rect((x, y), (w, h))

    def draw(self):
        screen.blit("platform", self.rect.topleft)


class Hero:
    def __init__(self, x, y):
        # sprites direita/esquerda
        self.image_idle_r = "alien_idle"
        self.image_idle_l = "alien_idle_left"
        self.image_jump_r = "alien_jump"
        self.image_jump_l = "alien_jump_left"
        self.walk_r = [f"alien_walk{i}" for i in range(1, 12)]
        self.walk_l = [f"alien_walk_left{i}" for i in range(1, 12)]

        self.actor = Actor(self.image_idle_r, (x, y))
        self.vel_y = 0.0
        self.on_ground = False
        self.anim_timer = 0
        self.anim_index = 0
        self.facing = 1
        self.moving = False

    def update(self, platforms):
        # ---- MOVIMENTO HORIZONTAL ----
        old_x = self.actor.x
        self.moving = False
        if keyboard.left:
            self.actor.x -= MOVE_SPEED
            self.facing = -1
            self.moving = True
        if keyboard.right:
            self.actor.x += MOVE_SPEED
            self.facing = 1
            self.moving = True

        # colisão lateral (ignora "apenas encostado no topo")
        for p in platforms:
            if self.actor.colliderect(p.rect):
                vertical_overlap = (self.actor.bottom > p.rect.top + 1) and (self.actor.top < p.rect.bottom - 1)
                if vertical_overlap:
                    if self.actor.x > old_x:      # movia para a direita
                        self.actor.right = p.rect.left
                    elif self.actor.x < old_x:    # movia para a esquerda
                        self.actor.left = p.rect.right

        # ---- MOVIMENTO VERTICAL ----
        old_bottom = self.actor.bottom
        old_top = self.actor.top

        self.vel_y += GRAVITY
        self.actor.y += self.vel_y

        self.on_ground = False
        for p in platforms:
            if self.actor.colliderect(p.rect):
                # pouso
                if self.vel_y > 0 and old_bottom <= p.rect.top:
                    self.actor.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # bateu cabeça no "teto"
                elif self.vel_y < 0 and old_top >= p.rect.bottom:
                    self.actor.top = p.rect.bottom
                    self.vel_y = 0

        self.animate()

        # limites e segurança
        self.actor.x = max(0, min(WIDTH, self.actor.x))
        if self.actor.top > HEIGHT + 200:
            self.respawn()

    def respawn(self):
        self.actor.pos = (100, HEIGHT - 120)
        self.vel_y = 0
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_SPEED
            if sound_enabled:
                sounds.jump.play()

    def animate(self):
        self.anim_timer += 1
        in_air = not self.on_ground

        if in_air:
            self.actor.image = self.image_jump_r if self.facing == 1 else self.image_jump_l
            return

        if self.moving:
            if self.anim_timer % 4 == 0:
                self.anim_index = (self.anim_index + 1) % 11
            self.actor.image = self.walk_r[self.anim_index] if self.facing == 1 else self.walk_l[self.anim_index]
        else:
            self.actor.image = self.image_idle_r if self.facing == 1 else self.image_idle_l

    def draw(self):
        self.actor.draw()


# ---------- Setup ----------
# Apenas uma plataforma (chão)
platforms = [
    Platform(0, HEIGHT - 32, WIDTH, 32)
]

hero = Hero(100, HEIGHT - 120)

# ---------- UI / Estados ----------
def draw_menu():
    screen.blit("background", (0, 0))
    screen.draw.text("Alien Adventure", center=(WIDTH // 2, 100),
                     fontsize=64, color="white")
    for name, rect in buttons.items():
        screen.draw.filled_rect(rect, (30, 30, 60))
        screen.draw.rect(rect, (255, 255, 255))
        screen.draw.text(name.capitalize(), center=rect.center,
                         fontsize=32, color="yellow")
    screen.draw.text("Setas para mover • Espaço para pular",
                     center=(WIDTH // 2, 430), fontsize=28, color="white")


def draw_game():
    screen.blit("background", (0, 0))
    for p in platforms:
        p.draw()
    hero.draw()


def on_mouse_down(pos):
    global game_state, music_enabled, sound_enabled
    if game_state == "menu":
        if buttons["start"].collidepoint(pos):
            game_state = "play"
            if music_enabled:
                music.play("music")
        elif buttons["sound"].collidepoint(pos):
            music_enabled = not music_enabled
            sound_enabled = not sound_enabled
            if music_enabled:
                music.play("music")
            else:
                music.stop()
        elif buttons["quit"].collidepoint(pos):
            exit()


def on_key_down(key):
    global game_state
    if game_state == "play":
        if key == keys.SPACE:
            hero.jump()
        elif key == keys.ESCAPE:
            game_state = "menu"
            music.stop()


def update():
    if game_state == "play":
        hero.update(platforms)


def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "play":
        draw_game()


pgzrun.go()
git reset --soft HEAD~1
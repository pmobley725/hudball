import pygame, sys, random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodgeball - Scaled Sprites")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Global settings
PLAYER_SPEED = 20
AI_SPEED = 20
PLAYER_SIZE = 50
AI_SIZE = 50

# Background selection globals
BACKGROUND_FILES = ["background.png", "background2.png", "background3.png"]
CURRENT_BACKGROUND_INDEX = 0
background = pygame.image.load(BACKGROUND_FILES[CURRENT_BACKGROUND_INDEX]).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def update_background():
    global background, CURRENT_BACKGROUND_INDEX, BACKGROUND_FILES
    background = pygame.image.load(BACKGROUND_FILES[CURRENT_BACKGROUND_INDEX]).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_controls = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'throw': pygame.K_q
}

# --- Classes ---
class AnimatedPlayer(pygame.sprite.Sprite):
    def __init__(self, image_prefix, frame_count, pos, controls, animation_speed=0.1, speed=20, size=50):
        super().__init__()
        self.frames = []
        for i in range(frame_count):
            filename = f"{image_prefix}_{i}.png"
            image = pygame.image.load(filename).convert_alpha()
            image = pygame.transform.scale(image, (size, size))
            self.frames.append(image)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.controls = controls
        self.speed = speed
        self.ball_count = 100
        self.last_dir = pygame.math.Vector2(1, 0)
        self.animation_speed = animation_speed
        self.time_accumulator = 0

    def update(self, keys, dt):
        move = pygame.math.Vector2(0, 0)
        if keys[self.controls['up']]:
            move.y = -self.speed
        if keys[self.controls['down']]:
            move.y = self.speed
        if keys[self.controls['left']]:
            move.x = -self.speed
        if keys[self.controls['right']]:
            move.x = self.speed

        if move.length() > 0:
            move = move.normalize() * self.speed
            self.last_dir = move
            self.rect.x += int(move.x)
            self.rect.y += int(move.y)
            self.rect.clamp_ip(screen.get_rect())

        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.time_accumulator = 0

    def throw_ball(self):
        if self.ball_count > 0:
            self.ball_count -= 1
            if self.last_dir.length() == 0:
                self.last_dir = pygame.math.Vector2(1, 0)
            direction = self.last_dir.normalize()
            return Ball("fireball.png", self.rect.center, direction, self)
        return None

class AIPlayer(pygame.sprite.Sprite):
    def __init__(self, image_file, pos, speed=20, size=50):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.ball_count = 10
        self.last_throw = pygame.time.get_ticks()
        self.throw_interval = 2000

    def update(self, target):
        direction = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize() * self.speed
            direction.x += random.uniform(-1, 1)
            direction.y += random.uniform(-1, 1)
        self.rect.x += int(direction.x)
        self.rect.y += int(direction.y)
        self.rect.clamp_ip(screen.get_rect())

    def try_throw(self, target):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_throw > self.throw_interval and self.ball_count > 0:
            self.last_throw = current_time
            direction = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() == 0:
                direction = pygame.math.Vector2(1, 0)
            direction = direction.normalize()
            self.ball_count -= 1
            return Ball("fireball.png", self.rect.center, direction, self)
        return None

class Ball(pygame.sprite.Sprite):
    def __init__(self, image_file, pos, direction, owner):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        # Double fireball size (from 10x10 to 20x20)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=pos)
        self.velocity = direction * 7
        self.owner = owner

    def update(self):
        self.rect.x += int(self.velocity.x)
        self.rect.y += int(self.velocity.y)
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Game State Initialization ---
def init_game():
    player = AnimatedPlayer("skeleton-run", 21, (100, HEIGHT//2), player_controls,
                            animation_speed=0.1, speed=PLAYER_SPEED, size=PLAYER_SIZE)
    ai = AIPlayer("ai.png", (WIDTH-100, HEIGHT//2), speed=AI_SPEED, size=AI_SIZE)
    players = pygame.sprite.Group(player, ai)
    balls = pygame.sprite.Group()
    game_over = False
    winner = None
    start_time = pygame.time.get_ticks()
    end_time = None
    return player, ai, players, balls, game_over, winner, start_time, end_time

# --- Button Rectangles ---
# Home screen buttons
begin_button_rect = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
settings_button_rect = pygame.Rect(WIDTH//2 - 100, 320, 200, 50)
# Settings buttons for speeds and sizes
player_speed_minus_rect = pygame.Rect(400, 150, 50, 40)
player_speed_plus_rect  = pygame.Rect(500, 150, 50, 40)
ai_speed_minus_rect     = pygame.Rect(400, 210, 50, 40)
ai_speed_plus_rect      = pygame.Rect(500, 210, 50, 40)
player_size_minus_rect  = pygame.Rect(400, 270, 50, 40)
player_size_plus_rect   = pygame.Rect(500, 270, 50, 40)
ai_size_minus_rect      = pygame.Rect(400, 330, 50, 40)
ai_size_plus_rect       = pygame.Rect(500, 330, 50, 40)
# New background selection buttons
background_minus_rect   = pygame.Rect(400, 390, 50, 40)
background_plus_rect    = pygame.Rect(500, 390, 50, 40)
# Back button for settings
back_button_rect        = pygame.Rect(WIDTH//2 - 50, 500, 100, 50)

# --- Main Loop ---
def main():
    global PLAYER_SPEED, AI_SPEED, PLAYER_SIZE, AI_SIZE, CURRENT_BACKGROUND_INDEX, background
    state = "home"
    player, ai, players, balls, game_over, winner, start_time, end_time = init_game()

    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- Home Screen Events ---
            if state == "home":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if begin_button_rect.collidepoint(mouse_pos):
                        player, ai, players, balls, game_over, winner, start_time, end_time = init_game()
                        state = "game"
                    elif settings_button_rect.collidepoint(mouse_pos):
                        state = "settings"

            # --- Settings Screen Events ---
            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if player_speed_minus_rect.collidepoint(mouse_pos) and PLAYER_SPEED > 1:
                        PLAYER_SPEED -= 1
                    if player_speed_plus_rect.collidepoint(mouse_pos):
                        PLAYER_SPEED += 1
                    if ai_speed_minus_rect.collidepoint(mouse_pos) and AI_SPEED > 1:
                        AI_SPEED -= 1
                    if ai_speed_plus_rect.collidepoint(mouse_pos):
                        AI_SPEED += 1
                    if player_size_minus_rect.collidepoint(mouse_pos) and PLAYER_SIZE > 10:
                        PLAYER_SIZE -= 1
                    if player_size_plus_rect.collidepoint(mouse_pos):
                        PLAYER_SIZE += 1
                    if ai_size_minus_rect.collidepoint(mouse_pos) and AI_SIZE > 10:
                        AI_SIZE -= 1
                    if ai_size_plus_rect.collidepoint(mouse_pos):
                        AI_SIZE += 1
                    # Background selection events
                    if background_minus_rect.collidepoint(mouse_pos):
                        CURRENT_BACKGROUND_INDEX = (CURRENT_BACKGROUND_INDEX - 1) % len(BACKGROUND_FILES)
                        update_background()
                    if background_plus_rect.collidepoint(mouse_pos):
                        CURRENT_BACKGROUND_INDEX = (CURRENT_BACKGROUND_INDEX + 1) % len(BACKGROUND_FILES)
                        update_background()
                    if back_button_rect.collidepoint(mouse_pos):
                        state = "home"

            # --- Game Screen Events ---
            elif state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == player_controls['throw'] and not game_over:
                        ball = player.throw_ball()
                        if ball:
                            balls.add(ball)
                if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 50, 100, 50)
                    if restart_button_rect.collidepoint(mouse_pos):
                        player, ai, players, balls, game_over, winner, start_time, end_time = init_game()

        # --- Drawing ---
        if state == "home":
            screen.blit(background, (0, 0))
            title_text = font.render("Dodgeball Game", True, (255,255,255))
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
            pygame.draw.rect(screen, (200,200,200), begin_button_rect)
            begin_text = font.render("Begin", True, (0,0,0))
            screen.blit(begin_text, (begin_button_rect.x + (begin_button_rect.width - begin_text.get_width())//2,
                                       begin_button_rect.y + (begin_button_rect.height - begin_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), settings_button_rect)
            settings_text = font.render("Settings", True, (0,0,0))
            screen.blit(settings_text, (settings_button_rect.x + (settings_button_rect.width - settings_text.get_width())//2,
                                          settings_button_rect.y + (settings_button_rect.height - settings_text.get_height())//2))

        elif state == "settings":
            screen.blit(background, (0, 0))
            settings_title = font.render("Settings", True, (255,255,255))
            screen.blit(settings_title, (WIDTH//2 - settings_title.get_width()//2, 50))

            # Player Speed
            ps_text = font.render(f"Player Speed: {PLAYER_SPEED}", True, (255,255,255))
            screen.blit(ps_text, (100, 150))
            pygame.draw.rect(screen, (200,200,200), player_speed_minus_rect)
            minus_text = font.render("-", True, (0,0,0))
            screen.blit(minus_text, (player_speed_minus_rect.x + (player_speed_minus_rect.width - minus_text.get_width())//2,
                                       player_speed_minus_rect.y + (player_speed_minus_rect.height - minus_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), player_speed_plus_rect)
            plus_text = font.render("+", True, (0,0,0))
            screen.blit(plus_text, (player_speed_plus_rect.x + (player_speed_plus_rect.width - plus_text.get_width())//2,
                                      player_speed_plus_rect.y + (player_speed_plus_rect.height - plus_text.get_height())//2))
            # AI Speed
            ai_text_disp = font.render(f"AI Speed: {AI_SPEED}", True, (255,255,255))
            screen.blit(ai_text_disp, (100, 210))
            pygame.draw.rect(screen, (200,200,200), ai_speed_minus_rect)
            screen.blit(minus_text, (ai_speed_minus_rect.x + (ai_speed_minus_rect.width - minus_text.get_width())//2,
                                       ai_speed_minus_rect.y + (ai_speed_minus_rect.height - minus_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), ai_speed_plus_rect)
            screen.blit(plus_text, (ai_speed_plus_rect.x + (ai_speed_plus_rect.width - plus_text.get_width())//2,
                                      ai_speed_plus_rect.y + (ai_speed_plus_rect.height - plus_text.get_height())//2))
            # Player Size
            psize_text = font.render(f"Player Size: {PLAYER_SIZE}", True, (255,255,255))
            screen.blit(psize_text, (100, 270))
            pygame.draw.rect(screen, (200,200,200), player_size_minus_rect)
            screen.blit(minus_text, (player_size_minus_rect.x + (player_size_minus_rect.width - minus_text.get_width())//2,
                                       player_size_minus_rect.y + (player_size_minus_rect.height - minus_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), player_size_plus_rect)
            screen.blit(plus_text, (player_size_plus_rect.x + (player_size_plus_rect.width - plus_text.get_width())//2,
                                      player_size_plus_rect.y + (player_size_plus_rect.height - plus_text.get_height())//2))
            # AI Size
            a_size_text = font.render(f"AI Size: {AI_SIZE}", True, (255,255,255))
            screen.blit(a_size_text, (100, 330))
            pygame.draw.rect(screen, (200,200,200), ai_size_minus_rect)
            screen.blit(minus_text, (ai_size_minus_rect.x + (ai_size_minus_rect.width - minus_text.get_width())//2,
                                       ai_size_minus_rect.y + (ai_size_minus_rect.height - minus_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), ai_size_plus_rect)
            screen.blit(plus_text, (ai_size_plus_rect.x + (ai_size_plus_rect.width - plus_text.get_width())//2,
                                      ai_size_plus_rect.y + (ai_size_plus_rect.height - plus_text.get_height())//2))
            # Background Selection
            bg_text = font.render(f"Background: {BACKGROUND_FILES[CURRENT_BACKGROUND_INDEX]}", True, (255,255,255))
            screen.blit(bg_text, (100, 390))
            pygame.draw.rect(screen, (200,200,200), background_minus_rect)
            screen.blit(minus_text, (background_minus_rect.x + (background_minus_rect.width - minus_text.get_width())//2,
                                      background_minus_rect.y + (background_minus_rect.height - minus_text.get_height())//2))
            pygame.draw.rect(screen, (200,200,200), background_plus_rect)
            screen.blit(plus_text, (background_plus_rect.x + (background_plus_rect.width - plus_text.get_width())//2,
                                      background_plus_rect.y + (background_plus_rect.height - plus_text.get_height())//2))
            # Back button
            pygame.draw.rect(screen, (200,200,200), back_button_rect)
            back_text = font.render("Back", True, (0,0,0))
            screen.blit(back_text, (back_button_rect.x + (back_button_rect.width - back_text.get_width())//2,
                                      back_button_rect.y + (back_button_rect.height - back_text.get_height())//2))

        elif state == "game":
            if not game_over:
                keys = pygame.key.get_pressed()
                player.update(keys, dt)
                ai.update(player)
                ai_ball = ai.try_throw(player)
                if ai_ball:
                    balls.add(ai_ball)
                balls.update()
                for ball in balls:
                    if ball.owner == player and ball.rect.colliderect(ai.rect):
                        game_over = True
                        winner = "Human Player"
                        end_time = pygame.time.get_ticks()
                    if ball.owner == ai and ball.rect.colliderect(player.rect):
                        game_over = True
                        winner = "AI Opponent"
                        end_time = pygame.time.get_ticks()
                if player.ball_count == 0 and ai.ball_count == 0 and len(balls) == 0:
                    game_over = True
                    winner = "No one"
                    end_time = pygame.time.get_ticks()
            screen.blit(background, (0, 0))
            players.draw(screen)
            balls.draw(screen)
            human_text = font.render(f"Your Balls: {player.ball_count}", True, (255,255,255))
            ai_text_disp = font.render(f"AI Balls: {ai.ball_count}", True, (255,255,255))
            screen.blit(human_text, (10, 10))
            screen.blit(ai_text_disp, (WIDTH - ai_text_disp.get_width() - 10, 10))
            elapsed = (pygame.time.get_ticks() - start_time) / 1000 if not game_over else (end_time - start_time) / 1000
            time_text = font.render(f"Time: {elapsed:.2f}s", True, (255,255,255))
            screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 10))
            if game_over:
                result_text = font.render(f"{winner} wins!", True, (255,255,255))
                screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2,
                                           HEIGHT//2 - result_text.get_height()//2))
                restart_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 50, 100, 50)
                pygame.draw.rect(screen, (200,200,200), restart_button_rect)
                restart_text = font.render("Restart", True, (0,0,0))
                screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width())//2,
                                           restart_button_rect.y + (restart_button_rect.height - restart_text.get_height())//2))
        pygame.display.flip()

if __name__ == "__main__":
    main()

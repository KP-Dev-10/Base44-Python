import pygame
import random
import asyncio

pygame.init()

WIDTH = 336
HEIGHT = 512

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 52)
small_font = pygame.font.Font(None, 24)

gravity = 0.20
bird_movement = 0
bird_x = 70
bird_y = 256
bird_radius = 16

pipe_width = 55
pipe_gap = 145
pipe_speed = 3

pipes = []

score = 0
high_score = 0

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU

spawn_timer = 0
bird_animation_timer = 0
bird_frame = 0

ground_height = 52


def create_pipe():
    gap_y = random.randint(130, 350)

    top_height = gap_y - pipe_gap // 2
    bottom_y = gap_y + pipe_gap // 2

    pipes.append({
        "x": WIDTH,
        "top": top_height,
        "bottom": bottom_y,
        "passed": False
    })


def start_game():
    global bird_y
    global bird_movement
    global score
    global pipes
    global spawn_timer
    global bird_animation_timer
    global bird_frame
    global game_state

    bird_y = HEIGHT // 2
    bird_movement = 0
    score = 0

    pipes.clear()

    spawn_timer = 0
    bird_animation_timer = 0
    bird_frame = 0

    game_state = PLAYING


def go_to_menu():
    global game_state
    global bird_y
    global bird_movement
    global pipes
    global spawn_timer

    bird_y = HEIGHT // 2
    bird_movement = 0

    pipes.clear()
    spawn_timer = 0

    game_state = MENU


def draw_background():
    screen.fill((135, 206, 235))

    pygame.draw.circle(
        screen,
        (255, 240, 150),
        (280, 70),
        35
    )

    pygame.draw.polygon(
        screen,
        (100, 190, 100),
        [
            (0, 390),
            (70, 310),
            (145, 390)
        ]
    )

    pygame.draw.polygon(
        screen,
        (80, 175, 90),
        [
            (100, 390),
            (200, 300),
            (300, 390)
        ]
    )


def draw_ground():
    pygame.draw.rect(
        screen,
        (222, 190, 90),
        (
            0,
            HEIGHT - ground_height,
            WIDTH,
            ground_height
        )
    )

    pygame.draw.rect(
        screen,
        (80, 190, 70),
        (
            0,
            HEIGHT - ground_height,
            WIDTH,
            8
        )
    )

    for x in range(-20, WIDTH + 20, 25):
        pygame.draw.line(
            screen,
            (190, 155, 65),
            (x, HEIGHT - 25),
            (x + 15, HEIGHT),
            3
        )


def draw_bird():
    wing_y = int(bird_y)

    if bird_frame == 0:
        wing_offset = 5
    elif bird_frame == 1:
        wing_offset = 0
    else:
        wing_offset = -5

    pygame.draw.circle(
        screen,
        (255, 220, 40),
        (bird_x, wing_y),
        bird_radius
    )

    pygame.draw.ellipse(
        screen,
        (240, 190, 30),
        (
            bird_x - 14,
            wing_y + wing_offset - 2,
            20,
            12
        )
    )

    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (bird_x + 7, wing_y - 6),
        6
    )

    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (bird_x + 9, wing_y - 6),
        3
    )

    pygame.draw.polygon(
        screen,
        (255, 120, 30),
        [
            (bird_x + 13, wing_y),
            (bird_x + 28, wing_y + 5),
            (bird_x + 13, wing_y + 9)
        ]
    )


def draw_pipe(pipe):
    x = int(pipe["x"])

    top_height = int(pipe["top"])
    bottom_y = int(pipe["bottom"])

    pygame.draw.rect(
        screen,
        (40, 180, 70),
        (
            x,
            0,
            pipe_width,
            top_height
        )
    )

    pygame.draw.rect(
        screen,
        (30, 145, 55),
        (
            x - 5,
            top_height - 20,
            pipe_width + 10,
            20
        )
    )

    pygame.draw.rect(
        screen,
        (40, 180, 70),
        (
            x,
            bottom_y,
            pipe_width,
            HEIGHT - ground_height - bottom_y
        )
    )

    pygame.draw.rect(
        screen,
        (30, 145, 55),
        (
            x - 5,
            bottom_y,
            pipe_width + 10,
            20
        )
    )


def check_collision(pipe):
    bird_left = bird_x - bird_radius
    bird_right = bird_x + bird_radius
    bird_top = bird_y - bird_radius
    bird_bottom = bird_y + bird_radius

    pipe_left = pipe["x"]
    pipe_right = pipe["x"] + pipe_width

    horizontal_collision = (
        bird_right > pipe_left
        and bird_left < pipe_right
    )

    if not horizontal_collision:
        return False

    if bird_top < pipe["top"]:
        return True

    if bird_bottom > pipe["bottom"]:
        return True

    return False


def draw_score():
    text = font.render(
        str(score),
        True,
        (255, 255, 255)
    )

    shadow = font.render(
        str(score),
        True,
        (0, 0, 0)
    )

    text_rect = text.get_rect(
        center=(WIDTH // 2, 45)
    )

    shadow_rect = shadow.get_rect(
        center=(WIDTH // 2 + 2, 47)
    )

    screen.blit(
        shadow,
        shadow_rect
    )

    screen.blit(
        text,
        text_rect
    )


def draw_menu():
    # Dark transparent overlay
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 60))

    screen.blit(
        overlay,
        (0, 0)
    )

    # Title
    title = large_font.render(
        "FLAPPY BIRD",
        True,
        (255, 255, 255)
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 150)
    )

    screen.blit(
        title,
        title_rect
    )

    # Bird
    draw_bird()

    # Start button
    button_width = 180
    button_height = 60

    button_x = (WIDTH - button_width) // 2
    button_y = 270

    pygame.draw.rect(
        screen,
        (70, 190, 80),
        (
            button_x,
            button_y,
            button_width,
            button_height
        ),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (40, 130, 50),
        (
            button_x,
            button_y,
            button_width,
            button_height
        ),
        3,
        border_radius=12
    )

    start_text = font.render(
        "START",
        True,
        (255, 255, 255)
    )

    start_rect = start_text.get_rect(
        center=(
            WIDTH // 2,
            button_y + button_height // 2
        )
    )

    screen.blit(
        start_text,
        start_rect
    )

    # Instructions
    instruction = small_font.render(
        "Click or press SPACE to start",
        True,
        (255, 255, 255)
    )

    instruction_rect = instruction.get_rect(
        center=(WIDTH // 2, 370)
    )

    screen.blit(
        instruction,
        instruction_rect
    )

    # High score
    best_text = font.render(
        "Best: " + str(high_score),
        True,
        (255, 255, 255)
    )

    best_rect = best_text.get_rect(
        center=(WIDTH // 2, 420)
    )

    screen.blit(
        best_text,
        best_rect
    )


def draw_game_over():
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 100)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = large_font.render(
        "GAME OVER",
        True,
        (255, 255, 255)
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 190)
    )

    screen.blit(
        title,
        title_rect
    )

    score_text = font.render(
        "Score: " + str(score),
        True,
        (255, 255, 255)
    )

    score_rect = score_text.get_rect(
        center=(WIDTH // 2, 250)
    )

    screen.blit(
        score_text,
        score_rect
    )

    high_text = font.render(
        "Best: " + str(high_score),
        True,
        (255, 255, 255)
    )

    high_rect = high_text.get_rect(
        center=(WIDTH // 2, 290)
    )

    screen.blit(
        high_text,
        high_rect
    )

    restart_text = small_font.render(
        "Click or press SPACE for menu",
        True,
        (255, 255, 255)
    )

    restart_rect = restart_text.get_rect(
        center=(WIDTH // 2, 350)
    )

    screen.blit(
        restart_text,
        restart_rect
    )


async def game_loop():
    global bird_y
    global bird_movement
    global spawn_timer
    global bird_animation_timer
    global bird_frame
    global score
    global high_score
    global game_state

    running = True

    while running:

        # -------------------------
        # EVENTS
        # -------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    if game_state == MENU:
                        start_game()

                    elif game_state == PLAYING:
                        bird_movement = -5.5

                    elif game_state == GAME_OVER:
                        go_to_menu()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if game_state == MENU:
                    start_game()

                elif game_state == PLAYING:
                    bird_movement = -5.5

                elif game_state == GAME_OVER:
                    go_to_menu()

        # -------------------------
        # GAME UPDATE
        # -------------------------

        if game_state == PLAYING:

            bird_movement += gravity
            bird_y += bird_movement

            spawn_timer += 1

            if spawn_timer >= 90:
                create_pipe()
                spawn_timer = 0

            # Bird animation
            bird_animation_timer += 1

            if bird_animation_timer >= 8:
                bird_animation_timer = 0
                bird_frame += 1

                if bird_frame >= 3:
                    bird_frame = 0

            # Move pipes
            for pipe in pipes:

                pipe["x"] -= pipe_speed

                # Score when bird passes pipe
                if (
                    not pipe["passed"]
                    and pipe["x"] + pipe_width < bird_x
                ):
                    pipe["passed"] = True
                    score += 1

            # Remove old pipes
            pipes[:] = [
                pipe
                for pipe in pipes
                if pipe["x"] > -pipe_width - 20
            ]

            # Ceiling collision
            if bird_y - bird_radius < 0:
                game_state = GAME_OVER

            # Ground collision
            if bird_y + bird_radius >= HEIGHT - ground_height:
                game_state = GAME_OVER

            # Pipe collision
            for pipe in pipes:

                if check_collision(pipe):
                    game_state = GAME_OVER
                    break

            # Update high score
            if game_state == GAME_OVER:

                if score > high_score:
                    high_score = score

        # -------------------------
        # DRAW
        # -------------------------

        draw_background()

        if game_state == PLAYING:

            for pipe in pipes:
                draw_pipe(pipe)

            draw_ground()
            draw_bird()
            draw_score()

        elif game_state == MENU:

            draw_ground()
            draw_menu()

        elif game_state == GAME_OVER:

            for pipe in pipes:
                draw_pipe(pipe)

            draw_ground()
            draw_bird()
            draw_game_over()

        pygame.display.flip()

        clock.tick(60)

        await asyncio.sleep(0)

    pygame.quit()


asyncio.ensure_future(game_loop())
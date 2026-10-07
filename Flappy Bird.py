import pygame
import random
import math
import asyncio

pygame.init()

WIDTH = 336
HEIGHT = 512

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird • Modern Edition")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 22)
large_font = pygame.font.Font(None, 54)
huge_font = pygame.font.Font(None, 72)

SKY_TOP = (75, 170, 235)
SKY_BOTTOM = (185, 235, 255)

WHITE = (255, 255, 255)
BLACK = (20, 25, 35)

YELLOW = (255, 214, 55)
YELLOW_LIGHT = (255, 235, 100)

GREEN = (67, 205, 100)
GREEN_DARK = (35, 145, 70)
GREEN_LIGHT = (105, 230, 125)

GROUND = (224, 190, 105)
GROUND_DARK = (188, 150, 70)

RED = (245, 75, 80)
BLUE = (70, 150, 255)

FPS_REFERENCE = 60.0
REFERENCE_DT = 1.0 / FPS_REFERENCE
MAX_DT = 0.05

gravity = 0.20
bird_movement = 0

bird_x = 78
bird_y = 256
bird_radius = 16

pipe_width = 58
pipe_gap = 145
pipe_speed = 3

PIPE_VERTICAL_SPEED = 0.15
PIPE_VERTICAL_RANGE = 40

pipes = []

score = 0
high_score = 0

MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU

spawn_timer = 0

bird_animation_timer = 0
bird_frame = 0

background_time = 0

shake_timer = 0
shake_strength = 0

fps_display = 60
fps_timer = 0

particles = []

ground_height = 54


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def draw_text_center(text, font_obj, color, x, y):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def rounded_rect(
    surface,
    color,
    rect,
    radius=12,
    border=0,
    border_color=None
):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    if border > 0 and border_color:
        pygame.draw.rect(
            surface,
            border_color,
            rect,
            border,
            border_radius=radius
        )


def create_particles(x, y, color, amount=8):
    for _ in range(amount):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-1.5, 1.5),
            "vy": random.uniform(-1.5, 1.5),
            "life": random.randint(20, 40),
            "size": random.randint(2, 5),
            "color": color
        })


def update_particles(frame_scale):
    for particle in particles[:]:
        particle["x"] += particle["vx"] * frame_scale
        particle["y"] += particle["vy"] * frame_scale
        particle["vy"] += 0.03 * frame_scale
        particle["life"] -= frame_scale

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        alpha = clamp(
            int(particle["life"] * 6),
            0,
            255
        )

        particle_surface = pygame.Surface(
            (
                particle["size"] * 2,
                particle["size"] * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (*particle["color"], alpha),
            (
                particle["size"],
                particle["size"]
            ),
            particle["size"]
        )

        screen.blit(
            particle_surface,
            (
                int(
                    particle["x"]
                    - particle["size"]
                ),
                int(
                    particle["y"]
                    - particle["size"]
                )
            )
        )


def draw_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(
            SKY_TOP[0] * (1 - ratio)
            + SKY_BOTTOM[0] * ratio
        )

        g = int(
            SKY_TOP[1] * (1 - ratio)
            + SKY_BOTTOM[1] * ratio
        )

        b = int(
            SKY_TOP[2] * (1 - ratio)
            + SKY_BOTTOM[2] * ratio
        )

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )

    sun_surface = pygame.Surface(
        (150, 150),
        pygame.SRCALPHA
    )

    for radius in range(60, 5, -5):
        alpha = int(
            2 + (60 - radius) * 0.8
        )

        pygame.draw.circle(
            sun_surface,
            (
                255,
                245,
                160,
                alpha
            ),
            (75, 75),
            radius
        )

    screen.blit(
        sun_surface,
        (225, 15)
    )

    pygame.draw.circle(
        screen,
        (255, 238, 130),
        (300, 70),
        32
    )

    draw_cloud(55, 100, 0.9)
    draw_cloud(230, 145, 0.7)
    draw_cloud(145, 55, 0.55)

    pygame.draw.polygon(
        screen,
        (113, 195, 135),
        [
            (0, 390),
            (55, 320),
            (110, 380),
            (170, 295),
            (245, 380),
            (290, 325),
            (336, 380),
            (336, 430),
            (0, 430)
        ]
    )

    pygame.draw.polygon(
        screen,
        (80, 175, 105),
        [
            (0, 410),
            (75, 350),
            (135, 405),
            (205, 345),
            (270, 400),
            (336, 350),
            (336, 430),
            (0, 430)
        ]
    )


def draw_cloud(x, y, scale):
    color = (255, 255, 255)

    pygame.draw.circle(
        screen,
        color,
        (int(x), int(y)),
        int(18 * scale)
    )

    pygame.draw.circle(
        screen,
        color,
        (
            int(x + 20 * scale),
            int(y - 7 * scale)
        ),
        int(25 * scale)
    )

    pygame.draw.circle(
        screen,
        color,
        (
            int(x + 45 * scale),
            int(y)
        ),
        int(18 * scale)
    )

    pygame.draw.rect(
        screen,
        color,
        (
            int(x),
            int(y),
            int(45 * scale),
            int(18 * scale)
        )
    )


def draw_ground():
    ground_y = HEIGHT - ground_height

    pygame.draw.rect(
        screen,
        (93, 205, 91),
        (
            0,
            ground_y,
            WIDTH,
            9
        )
    )

    pygame.draw.rect(
        screen,
        (63, 175, 75),
        (
            0,
            ground_y + 7,
            WIDTH,
            5
        )
    )

    pygame.draw.rect(
        screen,
        GROUND,
        (
            0,
            ground_y + 12,
            WIDTH,
            ground_height - 12
        )
    )

    for x in range(-20, WIDTH + 20, 28):
        pygame.draw.line(
            screen,
            GROUND_DARK,
            (
                x,
                ground_y + 20
            ),
            (
                x + 12,
                ground_y + 31
            ),
            3
        )

        pygame.draw.line(
            screen,
            GROUND_DARK,
            (
                x + 13,
                ground_y + 40
            ),
            (
                x + 25,
                ground_y + 50
            ),
            2
        )


def draw_bird():
    wing_offset = {
        0: 5,
        1: 0,
        2: -5
    }[bird_frame]

    x = int(bird_x)
    y = int(bird_y)

    glow = pygame.Surface(
        (60, 60),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow,
        (
            255,
            225,
            60,
            45
        ),
        (30, 30),
        23
    )

    screen.blit(
        glow,
        (
            x - 30,
            y - 30
        )
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (x, y),
        bird_radius
    )

    pygame.draw.circle(
        screen,
        YELLOW_LIGHT,
        (
            x - 5,
            y - 6
        ),
        7
    )

    pygame.draw.ellipse(
        screen,
        (
            239,
            184,
            35
        ),
        (
            x - 15,
            y + wing_offset - 3,
            21,
            13
        )
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            x + 7,
            y - 7
        ),
        7
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            x + 9,
            y - 7
        ),
        3
    )

    pygame.draw.polygon(
        screen,
        (
            225,
            95,
            20
        ),
        [
            (x + 13, y + 1),
            (x + 29, y + 6),
            (x + 13, y + 11)
        ]
    )

    pygame.draw.polygon(
        screen,
        (
            255,
            135,
            35
        ),
        [
            (x + 13, y),
            (x + 28, y + 4),
            (x + 13, y + 7)
        ]
    )


def create_pipe():
    gap_y = random.randint(
        145,
        330
    )

    pipes.append({
        "x": WIDTH + 10,
        "gap_y": gap_y,
        "base_y": gap_y,
        "phase": random.uniform(
            0,
            math.pi * 2
        ),
        "passed": False
    })


def update_pipe_vertical_movement(pipe):
    pipe["gap_y"] = (
        pipe["base_y"]
        +
        math.sin(
            background_time
            * PIPE_VERTICAL_SPEED
            * 0.035
            +
            pipe["phase"]
        )
        * PIPE_VERTICAL_RANGE
    )

    pipe["gap_y"] = clamp(
        pipe["gap_y"],
        125,
        340
    )


def draw_pipe(pipe):
    x = int(
        pipe["x"]
    )

    gap_y = int(
        pipe["gap_y"]
    )

    top_height = int(
        gap_y
        - pipe_gap // 2
    )

    bottom_y = int(
        gap_y
        + pipe_gap // 2
    )

    pygame.draw.rect(
        screen,
        GREEN_DARK,
        (
            x,
            0,
            pipe_width,
            top_height
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            x + 5,
            0,
            pipe_width - 12,
            top_height
        )
    )

    pygame.draw.rect(
        screen,
        GREEN_DARK,
        (
            x - 6,
            top_height - 22,
            pipe_width + 12,
            22
        ),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        GREEN_LIGHT,
        (
            x - 2,
            top_height - 19,
            pipe_width - 8,
            7
        ),
        border_radius=3
    )

    bottom_height = (
        HEIGHT
        - ground_height
        - bottom_y
    )

    pygame.draw.rect(
        screen,
        GREEN_DARK,
        (
            x,
            bottom_y,
            pipe_width,
            bottom_height
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            x + 5,
            bottom_y,
            pipe_width - 12,
            bottom_height
        )
    )

    pygame.draw.rect(
        screen,
        GREEN_DARK,
        (
            x - 6,
            bottom_y,
            pipe_width + 12,
            22
        ),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        GREEN_LIGHT,
        (
            x - 2,
            bottom_y + 3,
            pipe_width - 8,
            7
        ),
        border_radius=3
    )


def check_collision(pipe):
    bird_left = (
        bird_x
        - bird_radius
        + 3
    )

    bird_right = (
        bird_x
        + bird_radius
        - 3
    )

    bird_top = (
        bird_y
        - bird_radius
        + 3
    )

    bird_bottom = (
        bird_y
        + bird_radius
        - 3
    )

    pipe_left = pipe["x"]

    pipe_right = (
        pipe["x"]
        + pipe_width
    )

    horizontal_collision = (
        bird_right > pipe_left
        and
        bird_left < pipe_right
    )

    if not horizontal_collision:
        return False

    gap_y = pipe["gap_y"]

    top_height = (
        gap_y
        - pipe_gap // 2
    )

    bottom_y = (
        gap_y
        + pipe_gap // 2
    )

    if bird_top < top_height:
        return True

    if bird_bottom > bottom_y:
        return True

    return False


def start_game():
    global bird_y
    global bird_movement
    global score
    global pipes
    global spawn_timer
    global bird_animation_timer
    global bird_frame
    global game_state
    global particles
    global background_time

    bird_y = HEIGHT // 2
    bird_movement = 0
    score = 0

    pipes.clear()
    particles.clear()

    spawn_timer = 0
    bird_animation_timer = 0
    bird_frame = 0
    background_time = 0

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


def game_over():
    global game_state
    global high_score
    global shake_timer
    global shake_strength

    game_state = GAME_OVER

    if score > high_score:
        high_score = score

    create_particles(
        bird_x,
        bird_y,
        YELLOW,
        25
    )

    shake_timer = 12
    shake_strength = 5


def draw_score():
    panel = pygame.Surface(
        (
            100,
            58
        ),
        pygame.SRCALPHA
    )

    rounded_rect(
        panel,
        (
            20,
            30,
            45,
            100
        ),
        (
            0,
            0,
            100,
            58
        ),
        18
    )

    screen.blit(
        panel,
        (
            WIDTH // 2 - 50,
            15
        )
    )

    score_text = huge_font.render(
        str(score),
        True,
        WHITE
    )

    score_rect = score_text.get_rect(
        center=(
            WIDTH // 2,
            44
        )
    )

    screen.blit(
        score_text,
        score_rect
    )


def draw_fps():
    fps_text = small_font.render(
        f"FPS: {fps_display}",
        True,
        WHITE
    )

    shadow = small_font.render(
        f"FPS: {fps_display}",
        True,
        (
            20,
            30,
            40
        )
    )

    screen.blit(
        shadow,
        (
            9,
            10
        )
    )

    screen.blit(
        fps_text,
        (
            8,
            9
        )
    )


def draw_menu():
    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            10,
            25,
            45,
            95
        )
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    card = pygame.Surface(
        (
            290,
            390
        ),
        pygame.SRCALPHA
    )

    rounded_rect(
        card,
        (
            20,
            35,
            60,
            185
        ),
        (
            0,
            0,
            290,
            390
        ),
        28,
        2,
        (
            255,
            255,
            255,
            35
        )
    )

    screen.blit(
        card,
        (
            23,
            70
        )
    )

    draw_text_center(
        "FLAPPY",
        large_font,
        BLACK,
        WIDTH // 2 + 2,
        122
    )

    draw_text_center(
        "FLAPPY",
        large_font,
        WHITE,
        WIDTH // 2,
        120
    )

    draw_text_center(
        "BIRD",
        large_font,
        YELLOW,
        WIDTH // 2,
        165
    )

    draw_bird()

    button_rect = pygame.Rect(
        68,
        260,
        200,
        62
    )

    rounded_rect(
        screen,
        (
            45,
            190,
            95
        ),
        button_rect,
        18
    )

    pygame.draw.rect(
        screen,
        (
            35,
            130,
            70
        ),
        button_rect,
        3,
        border_radius=18
    )

    draw_text_center(
        "PLAY",
        font,
        WHITE,
        WIDTH // 2,
        291
    )

    draw_text_center(
        "CLICK  •  SPACE  •  TAP",
        small_font,
        (
            220,
            235,
            245
        ),
        WIDTH // 2,
        355
    )

    draw_text_center(
        f"BEST  {high_score}",
        font,
        YELLOW_LIGHT,
        WIDTH // 2,
        410
    )

    draw_text_center(
        "Uncapped rendering",
        small_font,
        (
            190,
            210,
            225
        ),
        WIDTH // 2,
        445
    )


def draw_game_over():
    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            10,
            15,
            25,
            150
        )
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    card = pygame.Surface(
        (
            280,
            300
        ),
        pygame.SRCALPHA
    )

    rounded_rect(
        card,
        (
            20,
            30,
            50,
            225
        ),
        (
            0,
            0,
            280,
            300
        ),
        28,
        2,
        (
            255,
            255,
            255,
            40
        )
    )

    screen.blit(
        card,
        (
            28,
            100
        )
    )

    draw_text_center(
        "GAME OVER",
        large_font,
        WHITE,
        WIDTH // 2,
        145
    )

    pygame.draw.rect(
        screen,
        (
            255,
            255,
            255,
            18
        ),
        (
            65,
            185,
            206,
            58
        ),
        border_radius=14
    )

    draw_text_center(
        f"SCORE   {score}",
        font,
        WHITE,
        WIDTH // 2,
        214
    )

    draw_text_center(
        f"BEST   {high_score}",
        font,
        YELLOW,
        WIDTH // 2,
        255
    )

    button_rect = pygame.Rect(
        68,
        300,
        200,
        58
    )

    rounded_rect(
        screen,
        (
            55,
            175,
            245
        ),
        button_rect,
        17
    )

    draw_text_center(
        "MENU",
        font,
        WHITE,
        WIDTH // 2,
        329
    )

    draw_text_center(
        "CLICK or SPACE",
        small_font,
        (
            205,
            220,
            235
        ),
        WIDTH // 2,
        390
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
    global background_time
    global fps_display
    global fps_timer

    running = True

    clock.get_time()

    while running:

        dt = clock.get_time() / 1000.0
        dt = min(dt, MAX_DT)
        frame_scale = dt / REFERENCE_DT

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if game_state == PLAYING:
                        go_to_menu()

                    elif game_state == GAME_OVER:
                        go_to_menu()

                elif event.key == pygame.K_SPACE:

                    if game_state == MENU:
                        start_game()

                    elif game_state == PLAYING:

                        bird_movement = -5.5

                        create_particles(
                            bird_x - 10,
                            bird_y + 10,
                            (
                                255,
                                220,
                                70
                            ),
                            4
                        )

                    elif game_state == GAME_OVER:
                        go_to_menu()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if game_state == MENU:
                    start_game()

                elif game_state == PLAYING:

                    bird_movement = -5.5

                    create_particles(
                        bird_x - 10,
                        bird_y + 10,
                        (
                            255,
                            220,
                            70
                        ),
                        4
                    )

                elif game_state == GAME_OVER:
                    go_to_menu()

        background_time += frame_scale

        fps_timer += dt

        if fps_timer >= 0.5:

            fps_display = round(
                clock.get_fps()
            )

            fps_timer = 0

        if game_state == PLAYING:

            bird_movement += (
                gravity * frame_scale
            )

            bird_y += (
                bird_movement * frame_scale
            )

            spawn_timer += frame_scale

            spawn_delay = max(
                72,
                90 - score * 2
            )

            if spawn_timer >= spawn_delay:

                create_pipe()

                spawn_timer -= spawn_delay

            bird_animation_timer += frame_scale

            while bird_animation_timer >= 7:

                bird_animation_timer -= 7

                bird_frame += 1

                if bird_frame >= 3:
                    bird_frame = 0

            for pipe in pipes:

                pipe_speed_current = (
                    pipe_speed
                    + min(
                        score * 0.04,
                        1.3
                    )
                )

                pipe["x"] -= (
                    pipe_speed_current
                    * frame_scale
                )

                update_pipe_vertical_movement(
                    pipe
                )

                if (
                    not pipe["passed"]
                    and
                    pipe["x"] + pipe_width < bird_x
                ):

                    pipe["passed"] = True

                    score += 1

                    create_particles(
                        bird_x,
                        bird_y,
                        YELLOW,
                        10
                    )

            pipes[:] = [
                pipe
                for pipe in pipes
                if pipe["x"] > -pipe_width - 20
            ]

            if (
                bird_y - bird_radius < 0
            ):

                game_over()

            if (
                bird_y + bird_radius
                >= HEIGHT - ground_height
            ):

                game_over()

            if game_state == PLAYING:

                for pipe in pipes:

                    if check_collision(pipe):

                        game_over()

                        break

        update_particles(
            frame_scale
        )

        screen.fill(
            SKY_TOP
        )

        draw_background()

        if game_state == PLAYING:

            for pipe in pipes:
                draw_pipe(pipe)

            draw_ground()
            draw_particles()
            draw_bird()
            draw_score()

        elif game_state == MENU:

            draw_ground()
            draw_menu()

        elif game_state == GAME_OVER:

            for pipe in pipes:
                draw_pipe(pipe)

            draw_ground()
            draw_particles()
            draw_bird()
            draw_game_over()

        draw_fps()

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.ensure_future(
    game_loop()
)

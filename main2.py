import pygame, sys, time


class StaticObstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill("yellow")
        self.rect = self.image.get_rect(topleft=pos)


class MovingVerticalObstacle(StaticObstacle):
    def __init__(self, pos, size, groups):
        super().__init__(pos, size, groups)
        self.image.fill("green")
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((0, 1))
        self.speed = 450

    def update(self, dt):
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.pos.y = self.rect.y
            self.direction.y *= -1
        if self.rect.bottom < 120:
            self.rect.bottom = 120
            self.pos.y = self.rect.y
            self.direction.y *= -1

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)


class MovingHorizontalObstacle(StaticObstacle):
    def __init__(self, pos, size, groups):
        super().__init__(pos, size, groups)
        self.image.fill("purple")
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((1, 0))
        self.speed = 400

    def update(self, dt):
        if self.rect.right > 1000:
            self.rect.right = 1000
            self.pos.x = self.rect.x
            self.direction.x *= -1
        if self.rect.left < 600:
            self.rect.left = 600
            self.pos.x = self.rect.x
            self.direction.x *= -1

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        # image
        self.image = pygame.Surface((30, 60))
        self.image.fill("blue")

        # position
        self.rect = self.image.get_rect(topleft=(640, 360))

        # movement
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2()
        self.speed = 200

    def input(self):
        keys = pygame.key.get_pressed()

        # movement input
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self, dt):
        self.input()

        if self.direction.magnitude() != 0:
            # avoid diagonal speed faster than axis speed
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)


class Ball(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface((40, 40))
        self.image.fill("red")
        self.rect = self.image.get_rect(center=(640, 360))

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(1, 1)
        self.speed = 400


# general setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# group setup
all_sprites = pygame.sprite.Group()
collision_sprites = pygame.sprite.Group()

# sprite setup
StaticObstacle((100, 300), (100, 50), [all_sprites, collision_sprites])
StaticObstacle((800, 600), (100, 200), [all_sprites, collision_sprites])
StaticObstacle((900, 200), (200, 10), [all_sprites, collision_sprites])
MovingVerticalObstacle((200, 300), (200, 60), [all_sprites, collision_sprites])
MovingHorizontalObstacle((850, 350), (100, 100), [all_sprites, collision_sprites])
Player(all_sprites)
Ball(all_sprites)

# loop
last_time = time.time()
while True:

    # delta time
    dt = time.time() - last_time
    last_time = time.time()

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # drawing and updating the screen
    screen.fill("black")
    all_sprites.update(dt)
    all_sprites.draw(screen)

    # display output
    pygame.display.update()
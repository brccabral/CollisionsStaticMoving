from typing import List, Tuple
import pygame, sys, time

# to detect collision we need to know where the collision came from (top, bottom, left, right)
# just checking the direction of one object is not enough because they can be in the same direction
# but one object moving faster than the other, the collision might think it happened on the
# other side.
# to avoid this confusion, we check the position of current frame but also previous frame
# this way we know exactly where the collision came from, but requires more code

# the final code there is still a bug where the player gets squeezed by a moving obstacle
# and a static one. In this case, the player passes through the static one and keeps
# being pushed by the moving one
# also, if the ball is being pushed for some time, it thinks it is changing direction
# many times and the final result is kind of random final direction


class StaticObstacle(pygame.sprite.Sprite):
    def __init__(
        self, pos: Tuple[int], size: Tuple[int], groups: List[pygame.sprite.Group]
    ):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill("yellow")
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()


class MovingVerticalObstacle(StaticObstacle):
    def __init__(
        self, pos: Tuple[int], size: Tuple[int], groups: List[pygame.sprite.Group]
    ):
        super().__init__(pos, size, groups)
        self.image.fill("green")
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((0, 1))
        self.speed = 450

    def update(self, dt: float):
        self.old_rect = self.rect.copy()  # previous frame
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.pos.y = self.rect.y
            self.direction.y *= -1
        if self.rect.bottom < 120:
            self.rect.bottom = 120
            self.pos.y = self.rect.y
            self.direction.y *= -1

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)  # current frame


class MovingHorizontalObstacle(StaticObstacle):
    def __init__(
        self, pos: Tuple[int], size: Tuple[int], groups: List[pygame.sprite.Group]
    ):
        super().__init__(pos, size, groups)
        self.image.fill("purple")
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((1, 0))
        self.speed = 400

    def update(self, dt: float):
        self.old_rect = self.rect.copy()  # previous frame
        if self.rect.right > 1000:
            self.rect.right = 1000
            self.pos.x = self.rect.x
            self.direction.x *= -1
        if self.rect.left < 600:
            self.rect.left = 600
            self.pos.x = self.rect.x
            self.direction.x *= -1

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)  # current frame


class Player(pygame.sprite.Sprite):
    def __init__(
        self, groups: List[pygame.sprite.Group], obstacles: pygame.sprite.Group
    ):
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
        self.old_rect = self.rect.copy()  # previous frame

        self.obstacles = obstacles

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

    def collision(self, direction: str):
        collision_sprites: List[StaticObstacle] = pygame.sprite.spritecollide(
            self, self.obstacles, False
        )
        if collision_sprites:
            if direction == "horizontal":
                for sprite in collision_sprites:
                    # collision on the right
                    if (
                        self.rect.right >= sprite.rect.left
                        and self.old_rect.right <= sprite.old_rect.left
                    ):
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x

                    # collision on the left
                    if (
                        self.rect.left <= sprite.rect.right
                        and self.old_rect.left >= sprite.old_rect.right
                    ):
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x

            if direction == "vertical":
                for sprite in collision_sprites:
                    # collision on the bottom
                    if (
                        self.rect.bottom >= sprite.rect.top
                        and self.old_rect.bottom <= sprite.old_rect.top
                    ):
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y

                    # collision on the top
                    if (
                        self.rect.top <= sprite.rect.bottom
                        and self.old_rect.top >= sprite.old_rect.bottom
                    ):
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y

    def update(self, dt: float):
        self.old_rect = self.rect.copy()  # previous frame
        self.input()

        if self.direction.magnitude() != 0:
            # avoid diagonal speed faster than axis speed
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision("horizontal")
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.collision("vertical")


class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        groups: List[pygame.sprite.Group],
        obstacles: pygame.sprite.Group,
        player: Player,
    ):
        super().__init__(groups)
        self.image = pygame.Surface((40, 40))
        self.image.fill("red")
        self.rect = self.image.get_rect(center=(640, 360))

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(1, 1)
        self.speed = 400
        self.old_rect = self.rect.copy()  # previous frame

        self.obstacles = obstacles
        self.player = player

    def collision(self, direction: str):
        collision_sprites: List[StaticObstacle] = pygame.sprite.spritecollide(
            self, self.obstacles, False
        )

        # make player part of the collision sprites if there is a collision
        if self.rect.colliderect(self.player.rect):
            collision_sprites.append(self.player)

        if collision_sprites:
            if direction == "horizontal":
                for sprite in collision_sprites:
                    # collision on the right
                    if (
                        self.rect.right >= sprite.rect.left
                        and self.old_rect.right <= sprite.old_rect.left
                    ):
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x
                        self.direction.x *= -1

                    # collision on the left
                    if (
                        self.rect.left <= sprite.rect.right
                        and self.old_rect.left >= sprite.old_rect.right
                    ):
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x
                        self.direction.x *= -1

            elif direction == "vertical":
                for sprite in collision_sprites:
                    # collision on the bottom
                    if (
                        self.rect.bottom >= sprite.rect.top
                        and self.old_rect.bottom <= sprite.old_rect.top
                    ):
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y
                        self.direction.y *= -1

                    # collision on the top
                    if (
                        self.rect.top <= sprite.rect.bottom
                        and self.old_rect.top >= sprite.old_rect.bottom
                    ):
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y
                        self.direction.y *= -1

    def window_collision(self, direction: str):
        if direction == "horizontal":
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.direction.x *= -1
            if self.rect.right > 1280:
                self.rect.right = 1280
                self.pos.x = self.rect.x
                self.direction.x *= -1

        elif direction == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
            if self.rect.bottom > 720:
                self.rect.bottom = 720
                self.pos.y = self.rect.y
                self.direction.y *= -1

    def update(self, dt: float):
        self.old_rect = self.rect.copy()  # previous frame

        if self.direction.magnitude() != 0:
            # avoid diagonal speed faster than axis speed
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision("horizontal")
        self.window_collision("horizontal")
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.collision("vertical")
        self.window_collision("vertical")


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
player = Player(all_sprites, collision_sprites)
Ball(all_sprites, collision_sprites, player)

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

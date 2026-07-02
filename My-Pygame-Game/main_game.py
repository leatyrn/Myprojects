import pygame
import random

pygame.init()


def create_bullet():   # фунція жля створення кулі
    bullet_x = player_x + 14
    bullet_y = player_y
    new_bullet = [bullet_x, bullet_y]
    bullets.append(new_bullet)


def create_all_enemy_skins(name):  # фунція для створення скінів ворогів
    enemy = pygame.image.load(f'My game/{name}').convert()
    enemy.set_colorkey((255, 255, 255))
    enemy = pygame.transform.rotate(enemy, 180)
    enemy = pygame.transform.scale(enemy, (30, 30))
    return enemy


screen = pygame.display.set_mode((400, 510))  # робимо екран

pygame.display.set_caption('Космічний захисник')

# СПИСКИ ДЛЯ ІНФОРМАЦІЇ ДЛЯ ГРИ

explosions = []
enemies = []
bullets = []
enemy_skins = []
enemy_list_names = ['ship2.png',
                    'ship3.png',
                    'ship4.png',
                    'ship5.png']  # ship1.png це ми, тому тут немає

boom = pygame.image.load('My game/boom.png').convert_alpha()  # створення кулі

boom = pygame.transform.scale(boom, (40, 40))


for ship_file_name in enemy_list_names:  # цикл для заповнення списку: enemy_skins скінами
    new_skin = create_all_enemy_skins(ship_file_name)
    enemy_skins.append(new_skin)

for i in range(4):  # робимо "ворога", містить координати, швидкість і сам скін
    new_enemy = {'x': random.randint(30, 370),
                 'y': random.randint(-150, -40),
                 'speed': random.randint(1, 2),
                 'skin': random.choice(enemy_skins)}
    enemies.append(new_enemy)


clock = pygame.time.Clock()

# ЗМІННІ

go_left = False
go_right = False

player_x = 185
player_y = 400

player_img = pygame.image.load('My game/ship1.png')
player_img = pygame.transform.scale(player_img, (30, 30))

last_shot_time = 0

shot_delay = 450

running = True

# ГОЛОВНИЙ ЦИКЛ WHILE

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:  # перевірка на вихід
            running = False

        if event.type == pygame.KEYDOWN:  # перевірка на НАЖАТТЯ клавіші
            if event.key == pygame.K_a:
                go_left = True
            if event.key == pygame.K_d:
                go_right = True

        if event.type == pygame.KEYUP:   # перевірка на ВІДПУСКАННЯ клавіші
            if event.key == pygame.K_a:
                go_left = False
            if event.key == pygame.K_d:
                go_right = False

    # ПЕРЕВІРКИ НА РУХ ГРАВЦЯ "True"
    if go_left:
        player_x -= 3
    if go_right:
        player_x += 3

    # ПЕРЕВІРКИ НА ТЕ ЧИ ГРАВЕЦЬ ПОКИНУВ ЗОНУ КАРТИ
    if player_x > 420:
        player_x = -20
    if player_x < -20:
        player_x = 420

    for bullet in bullets:  # цикл, який дає змогу "рухатися" кулі
        bullet[1] -= 5
        if bullet[1] < -10:
            # коли куля вийшла за карту (догори): видалюємо її
            bullets.remove(bullet)

    for enemy in enemies:  # цикл, який бере ворога з списку ворогів, і дає змогу рухатися відповідно до своєї швидкості
        enemy['y'] += enemy['speed']
        if enemy['y'] > 515:  # коли він вийшов за кордон карти: телепортуєм угору, але щоб поки гравець не бачив
            enemy['x'] = random.randint(30, 370)
            enemy['y'] = random.randint(-150, -40)

    current_time = pygame.time.get_ticks()

    if current_time - last_shot_time > shot_delay:  # таймер
        create_bullet()
        last_shot_time = current_time

    for bullet in bullets:
        bullet_destroyed = False
        for enemy in enemies:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 3, 10)
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], 30, 30)

            if bullet_rect.colliderect(enemy_rect):
                explosions.append({
                    'x': enemy['x'],
                    'y': enemy['y'],
                    'time': pygame.time.get_ticks()
                })
                bullets.remove(bullet)
                enemy['y'] = random.randint(-150, -40)
                enemy['x'] = random.randint(0, 370)
                bullet_destroyed = True
                break
        if bullet_destroyed:
            break

    screen.fill((0, 0, 0))
    screen.blit(player_img, (player_x, player_y))

    for bullet in bullets:
        pygame.draw.rect(screen, (255, 0, 0), (bullet[0], bullet[1], 3, 10))

    for enemy in enemies:
        screen.blit(enemy['skin'], (enemy['x'], enemy['y']))

    for explosion in explosions[:]:
        screen.blit(boom, (explosion['x'], explosion['y']))

        if current_time - explosion['time'] > 250:
            explosions.remove(explosion)

    pygame.display.flip()  # "малюємо" те що намалювали
    clock.tick(60)  # встановлюємо кордон ФПС

# Importaciones
import pygame
import random
import os
import sys

# Configuración
WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIVES = 3  # Número inicial de vidas
INVULNERABILITY_TIME = 2000  # 2 segundos de invulnerabilidad después  de ser golpeado (en milisegundos)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(ROOT_DIR, 'assest')

# Función para cargar imágenes con manejo de errores
def load_image(name, default_color=(255, 0, 255), size=(50, 50)):
    try:
        image = pygame.image.load(os.path.join(IMAGE_DIR, name))
        if image.get_alpha():  # Si tiene transparencia
            image = image.convert_alpha()
        else:
            image = image.convert()
        print(f"Imagen cargada correctamente: {name}")
        return image
    except Exception as e:
        print(f"ERROR al cargar {name}: {str(e)}")
        print(f"Buscando en: {os.path.join(IMAGE_DIR, name)}")
        # Crear imagen de relleno
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, default_color, (0, 0, size[0], size[1]))
        return surface

# Inicialización
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GALAGA')
clock = pygame.time.Clock()

# Clases
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('nave.png', (0, 0, 255), (64, 64))
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.invulnerable = False
        self.invulnerability_end = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
        # Manejar invulnerabilidad
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time > self.invulnerability_end:
            self.invulnerable = False
            self.image.set_alpha(255)  # Hacer completamente visible

    def make_invulnerable(self, duration):
        self.invulnerable = True
        self.invulnerability_end = pygame.time.get_ticks() + duration

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('enemigo.png', (255, 0, 0), (40, 40))
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 5)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('laser.png', (0, 255, 0), (10, 30))
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Cargar fondo
try:
    background = pygame.image.load(os.path.join(IMAGE_DIR, 'fondo.jpg')).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    print("ERROR: No se pudo cargar el fondo. Usando fondo negro.")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)

# Grupos de sprites
all_sprites = pygame.sprite.Group()
meteor_list = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Crear jugador
player = Player()
all_sprites.add(player)

# Crear meteoritos iniciales
for i in range(8):
    meteor = Meteor()
    all_sprites.add(meteor)
    meteor_list.add(meteor)

# Sistema de puntuación
score = 0
font = pygame.font.SysFont('Arial', 25)

# Bucle principal
running = True
last_hit_time = 0

while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not player.invulnerable:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Actualización
    all_sprites.update()

    # Colisiones balas-meteoritos
    hits = pygame.sprite.groupcollide(meteor_list, bullets, True, True)
    for hit in hits:
        score += 10
        meteor = Meteor()
        all_sprites.add(meteor)
        meteor_list.add(meteor)

    # Colisiones jugador-meteoritos (solo si no es invulnerable)
    if not player.invulnerable:
        hits = pygame.sprite.spritecollide(player, meteor_list, True)
        if hits:
            LIVES -= 1
            player.make_invulnerable(INVULNERABILITY_TIME)
            # Parpadeo inicial
            player.image.set_alpha(100)
            
            for hit in hits:
                meteor = Meteor()
                all_sprites.add(meteor)
                meteor_list.add(meteor)
                
            if LIVES <= 0:
                running = False
    
    # Efecto de parpadeo durante invulnerabilidad
    if player.invulnerable and (current_time // 100) % 2 == 0:
        player.image.set_alpha(100)
    else:
        player.image.set_alpha(255)

    # Dibujado
    screen.blit(background, [0, 0])
    all_sprites.draw(screen)
    
    # Mostrar puntuación y vidas
    score_text = font.render(f'Puntuación: {score}', True, WHITE)
    lives_text = font.render(f'Vidas: {LIVES}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))

    pygame.display.flip()

# Pantalla de Game Over
if LIVES <= 0:
    screen.fill(BLACK)
    game_over_font = pygame.font.SysFont('Arial', 72)
    score_font = pygame.font.SysFont('Arial', 36)
    
    game_over_text = game_over_font.render('GAME OVER', True, WHITE)
    score_text = score_font.render(f'Puntuación final: {score}', True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    pygame.time.wait(3000)  # Esperar 3 segundos antes de cerrar

pygame.quit()
sys.exit() 
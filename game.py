import pygame
import random
import json

# CONSTANTES
DIRECTION_GAUCHE_DROITE = 0
DIRECTION_DROITE_GAUCHE = 1

STATE_PLAYING = 0
STATE_PAUSED = 1
STATE_FINISHED = 2
STATE_EXIT = 3

class Entity:
    def __init__(self, size, position, image):
        self.size = size
        self.position = position
        self.image = image

    def draw(self, fenetre):
        fenetre.blit(self.image, self.position)

    def move(self, x, y):
        self.position = self.position[0] + x, self.position[1] + y

    def collides(self, point ):
        return pygame.Rect(self.position, self.size).collidepoint(point)

class Alien(Entity):

    def __init__(self, size, position, image, kill_sound):
        Entity.__init__(self, size, position, image)
        self.kill_sound = kill_sound

    def clone(self, position):
        return Alien(self.size, position, self.image, self.kill_sound)

    def kill(self):
        global score
        score += 1
        self.kill_sound.play()

class Spaceship(Entity):

    def __init__(self, size, position, image, shot_sound):
        Entity.__init__(self, size, position, image)
        self.shot_sound = shot_sound

    def shoot(self):
        global projectiles_amount
        projectiles_amount -= 1
        self.shot_sound.play()
        projectiles.append( (int(self.position[0])  + int(self.size[0]/2),self.position[1]) )

class Level():

    def __init__(self, name, alien_template, aliens_columns = 5, aliens_rows = 2):
        self.name = name
        self.alien_template = alien_template
        self.aliens_columns = aliens_columns
        self.aliens_rows = aliens_rows

def generate_stars(amount = 50):
    stars = []
    for i in range (amount):
        stars.append( (random.randint(0, SCREEN_SIZE[0]), random.randint(0, SCREEN_SIZE[1])) )
    return stars

def generate_aliens(alien, columns = 5, rows = 2):
    aliens = [ ]
    for x in range (rows):
        for y in range (columns):
            position = (x * (alien.size[0] + 10) , 10 + (10 + alien.size[1]) * y )
            aliens.append( alien.clone(position) )
    return aliens

def print_text(content, color):
    font = pygame.font.SysFont("arial", 45)
    text = font.render(content, True, color)
    x = int((SCREEN_SIZE[0]-font.size(content)[0])/2)
    y = int((SCREEN_SIZE[1]-font.size(content)[1])/2)
    fenetre.blit(text, (x,y))

def win_level():
    global state
    print_text("You won the level", pygame.Color(211, 200, 51))
    state = STATE_PAUSED
    pygame.display.flip()

def lose_game():
    global state
    print_text("You lost", pygame.Color(255, 25, 25))
    state = STATE_FINISHED
    pygame.display.flip()

def win_game():
    global state
    print_text("You won the game", pygame.Color(211, 200, 51))
    state = STATE_FINISHED
    pygame.display.flip()

def load_settings(settings):
    global SCREEN_SIZE, FONT, fenetre, spaceship
    pygame.display.set_caption( settings["title"] )
    SCREEN_SIZE = ( settings["screen_width"], settings["screen_lenght"] )
    fenetre = pygame.display.set_mode( SCREEN_SIZE )
    spaceship_size = ( settings["spaceship_width"], settings["spaceship_lenght"] )
    spaceship_sound = pygame.mixer.Sound(settings["spaceship_shot_sound"])

    spaceship = Spaceship(spaceship_size, (SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 75), pygame.transform.scale(pygame.image.load("vaisseau.png"), spaceship_size), spaceship_sound)

    FONT = pygame.font.SysFont(settings["font_name"], settings["font_size"])

def get_alien(alien_name):
    alien_config = config["aliens"][alien_name]
    alien_size = ( alien_config["width"], alien_config["lenght"] )
    alien_image = alien_config["image"]
    kill_sound = pygame.mixer.Sound( alien_config["kill_sound"] )
    return Alien( alien_size,  None, pygame.transform.scale(pygame.image.load(alien_image), alien_size), kill_sound)

current_level = 0
def get_level():
    global current_level
    levels_config = config["levels"]
    level = levels_config[current_level]
    current_level += 1
    return Level(level["name"], get_alien(level["aliens"]), level["aliens_columns"], level["aliens_rows"])

def load_level():
    global aliens
    level = get_level()
    aliens = generate_aliens(level.alien_template, level.aliens_columns, level.aliens_rows)

pygame.init() # initialisation du module "pygame"
with open("./config.json") as json_file:
    config = json.load(json_file)
load_settings(config["settings"])
stars = generate_stars()
load_level()

direction_alien = DIRECTION_GAUCHE_DROITE
projectiles = [ ]
state = STATE_PLAYING
score = 0
projectiles_amount = 100


def move_aliens():
    global direction_alien
    move_to_bottom = False
    shift_right = False
    shift_left = False
    for alien in aliens:
        if direction_alien == DIRECTION_GAUCHE_DROITE:
            if alien.position[0] + alien.size[0] > SCREEN_SIZE[0]:
                direction_alien = DIRECTION_DROITE_GAUCHE
                move_to_bottom = True
            else:
                shift_right = True
        else:
            if alien.position[0] < 0:
                direction_alien = DIRECTION_GAUCHE_DROITE
                move_to_bottom = True
            else:
                shift_left = True

    for alien in aliens:
        if move_to_bottom:
            alien.move(0, alien.size[1])
            if alien.position[1] >= SCREEN_SIZE[1]:
                lose_game()
        elif shift_right:
            alien.move(5, 0)
        elif shift_left:
            alien.move(-5, 0)

def update_projectiles():
    global projectiles, projectiles_amount
    new_projectiles = []
    for index in range (len(stars)):
        x, y = stars[index]
        stars[index] = x, (y+1)%SCREEN_SIZE[1]

    for projectile in projectiles:
        new_aliens_position = []
        collided = False
        for alien in aliens:
            if alien.collides(projectile):
                alien.kill()
                aliens.remove(alien)
                collided = True
                projectiles_amount -= 1

        # On fait avancer le projectile (si il existe)
        if not collided and projectile[1] < SCREEN_SIZE[1] and projectile != (-1, -1):
            projectile = (projectile[0], projectile[1] - 5)
            new_projectiles.append(projectile)
        
    projectiles = new_projectiles

# Fonction en charge de dessiner tous les éléments sur notre fenêtre graphique.
# Cette fonction sera appelée depuis notre boucle infinie
#count = 0
def dessiner():
    global fenetre, spaceship, projectile
    # On remplit complètement notre fenêtre avec la couleur noire: (0,0,0)
    # Ceci permet de 'nettoyer' notre fenêtre avant de la dessiner
    fenetre.fill( (0,0,0) )
    spaceship.draw(fenetre) # On dessine l'image du vaisseau à sa position
    for alien in aliens:
        alien.draw(fenetre)

    score_text = FONT.render("score: " + str(score), True, pygame.Color(255, 0, 255))
    fenetre.blit(score_text, (10, 10))

    projectile_text_content = "projectiles: " + str(projectiles_amount)
    projectile_text = FONT.render(projectile_text_content, True, pygame.Color(0, 255, 255))
    fenetre.blit(projectile_text, (SCREEN_SIZE[0]-10-FONT.size(projectile_text_content)[0], 10))
    for star in stars:
        pygame.draw.circle(fenetre, (255,255,0), star, 2) 
    for projectile in projectiles:
        if projectile != (-1, -1):
            pygame.draw.circle(fenetre, (255,255,255), projectile, 5) # On dessine le projectile (un simple petit cercle)

    pygame.display.flip() # Rafraichissement complet de la fenêtre avec les dernières opérations de dessin


# Fonction en charge de gérer les évènements clavier (ou souris)
# Cette fonction sera appelée depuis notre boucle infinie
def gerer_clavier_souris():
    global state, spaceship, projectiles, projectiles_amount
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            state = STATE_EXIT

        elif event.type == pygame.KEYDOWN:

            if state == STATE_FINISHED:
                print("todo: load new level")
            
            if event.key == pygame.K_SPACE and projectiles_amount > 0:
                spaceship.shoot()

    touches_pressees = pygame.key.get_pressed()

    if touches_pressees[pygame.K_RIGHT] == True and spaceship.position[0] + spaceship.size[0] < SCREEN_SIZE[0]:
        spaceship.move( 10, 0 )

    elif touches_pressees[pygame.K_LEFT] == True and spaceship.position[0] > 0 :
        spaceship.move( -10, 0 )

clock = pygame.time.Clock()
while state != STATE_EXIT:

    clock.tick(60)

    if len(aliens) == 0:
        win_level()

    gerer_clavier_souris()
    if state != STATE_PAUSED: 
        dessiner()
        move_aliens()
        update_projectiles()

pygame.quit()
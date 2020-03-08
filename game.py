import pygame
import random
import json

# CONSTANTES
DIRECTION_GAUCHE_DROITE = 0
DIRECTION_DROITE_GAUCHE = 1

STATE_PLAYING = 0
STATE_PAUSED = 1
STATE_PAUSED_LOST = 2
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

    def __init__(self, size, position, speed, projectiles_gain, image, kill_sound):
        Entity.__init__(self, size, position, image)
        self.speed = speed
        self.projectiles_gain = projectiles_gain
        self.kill_sound = kill_sound

    def clone(self, position):
        return Alien(self.size, position, self.speed, self.projectiles_gain, self.image, self.kill_sound)

    def kill(self):
        global score, projectiles_amount
        score += 1
        projectiles_amount += self.projectiles_gain
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

def generate_stars(amount = 50):
    stars = []
    for i in range (amount):
        stars.append( (random.randint(0, SCREEN_SIZE[0]), random.randint(0, SCREEN_SIZE[1])) )
    return stars

def generate_aliens(alien, columns = 5, rows = 2):
    aliens = [ ]
    for x in range (columns):
        for y in range (rows):
            position = (x * (alien.size[0] + 10) , 10 + (10 + alien.size[1]) * y )
            aliens.append( alien.clone(position) )
    return aliens

def show_title_and_text(color, title, text = None):
    font = pygame.font.SysFont("arial", 45)
    title_size = font.size(title)
    text_size = simulate_show_text(text)
    
    x_title, y_title = int((SCREEN_SIZE[0]-font.size(title)[0])/2), int(((SCREEN_SIZE)[1] - title_size[1] - text_size[1])/2)

    title_surface = font.render(title, True, color)
    fenetre.blit(title_surface, (x_title, y_title))
    

    if text: # les string se comportent comme des booléens
        show_text(text, ( int((SCREEN_SIZE[0]-text_size[0])/2), y_title + title_size[1] ), color)


def simulate_show_text(content):
    font = pygame.font.SysFont("arial", 25)
    words = [word.split() for word in content.splitlines()]
    space_size = font.size(' ')[0]
    max_width, max_height = fenetre.get_size()
    x, y = (0, 0)
    max_x = x
    for line in words:
        for word in line:
            word_width, word_height = font.size(word)
            if x + word_width >= max_width:
                if x > max_x:
                    max_x = x
                x = 0
                y += word_height
            x += word_width + space_size
        if x > max_x:
            max_x = x
        x = 0
        y += word_height
    return (max_x, y)

def show_text(content, position, color):
    font = pygame.font.SysFont("arial", 25)
    text = font.render(content, True, color)

    words = [word.split() for word in content.splitlines()]  # Tableau 2d pour pouvoir revenir à la ligne manuellement
    space_size = font.size(' ')[0]
    max_width, max_height = SCREEN_SIZE
    x, y = position
    for line in words: # on sépare le texte en lignes (manuelles)
        for word in line: # on sépare les lignes en mots
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width: # on va à la ligne d'après si on a pas la place
                x = position[0]
                y += word_height
            fenetre.blit(word_surface, (x, y))
            x += word_width + space_size
        x = position[0]  # on revient à la fin d'une ligne manuelle
        y += word_height

def win_level():
    global state
    if current_level < levels_amount:
        show_title_and_text(pygame.Color(211, 200, 51), "Vous avez réussi le niveau {} !".format(current_level), "Il reste encore un ou plusieurs niveaux, appuyez sur entrer pour continuer !")
        state = STATE_PAUSED
        pygame.display.flip()
    else:
        win_game()

def lose_game():
    global state
    show_title_and_text(pygame.Color(255, 25, 25), "Vous avez perdu !", "Il ne vous manquait peut-être qu'un niveau ou bien des dizaines avant de gagner mais comme vous avez perdu vous devrez recommencer depuis le début pour le savoir ! Appuyez sur entrer pour quitter !")
    state = STATE_PAUSED_LOST
    pygame.display.flip()

def win_game():
    global state
    show_title_and_text(pygame.Color(211, 200, 51), "Vous avez gagné !", "Le jeu est malheureusement terminé : vous avez fini tous les niveaux. Mais ne vous inquiétez pas, j'ai tout prévu : vous pouvez rajouter des niveaux dans config.json")
    state = STATE_PAUSED
    pygame.display.flip()

def load_settings(settings):
    global SCREEN_SIZE, FONT, fenetre, spaceship
    pygame.display.set_caption( settings["title"] )
    SCREEN_SIZE = ( settings["screen_width"], settings["screen_height"] )
    fenetre = pygame.display.set_mode( SCREEN_SIZE )
    spaceship_size = ( settings["spaceship_width"], settings["spaceship_height"] )
    spaceship_sound = pygame.mixer.Sound(settings["spaceship_shot_sound"])

    spaceship = Spaceship(spaceship_size, (SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 75), pygame.transform.scale(pygame.image.load("vaisseau.png"), spaceship_size), spaceship_sound)

    FONT = pygame.font.SysFont(settings["font_name"], settings["font_size"])

def get_alien(alien_name):
    alien_config = config["aliens"][alien_name]
    alien_size = ( alien_config["width"], alien_config["height"] )
    alien_speed = alien_config["speed"] # in pixels per image
    alien_projectiles_gain = alien_config["projectiles_gain"]
    alien_image = alien_config["image"]
    kill_sound = pygame.mixer.Sound( alien_config["kill_sound"] )
    return Alien( alien_size,  None, alien_speed, alien_projectiles_gain, pygame.transform.scale(pygame.image.load(alien_image), alien_size), kill_sound)

current_level = 0
def load_next_level():
    global state, aliens, current_level, levels_amount
    level_configs = config["levels"]
    levels_amount = len(level_configs)
    level_config = level_configs[current_level]

    aliens = generate_aliens(get_alien(level_config["aliens"]), level_config["aliens_columns"], level_config["aliens_rows"])

    current_level += 1
    state = STATE_PLAYING

pygame.init() # initialisation du module "pygame"
with open("./config.json") as json_file:
    config = json.load(json_file)
load_settings(config["settings"])
stars = generate_stars()
load_next_level()

direction_alien = DIRECTION_GAUCHE_DROITE
projectiles = [ ]
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
            if alien.position[1] + alien.size[1] >= SCREEN_SIZE[1]:
                lose_game()
        elif shift_right:
            alien.move(alien.speed, 0)
        elif shift_left:
            alien.move(-alien.speed, 0)

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
    global state
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            state = STATE_EXIT

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                if state == STATE_PAUSED:
                    if current_level < levels_amount: # si tous les niveaux n'ont pas été joués
                        load_next_level()
                    else:
                        state = STATE_EXIT
                elif state == STATE_PAUSED_LOST:
                    state = STATE_EXIT

            else:       
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
    if state != STATE_PAUSED and state != STATE_PAUSED_LOST: 
        dessiner()
        move_aliens()
        update_projectiles()

pygame.quit()
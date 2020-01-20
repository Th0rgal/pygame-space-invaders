import pygame
import random

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
        projectiles.append( (int(self.position[0])  + int(SPACESHIP_SIZE[0]/2),self.position[1]) )

def generate_stars(amount = 50):
    stars = []
    for i in range (amount):
        stars.append( (random.randint(0, SCREEN_SIZE[0]), random.randint(0, SCREEN_SIZE[1])) )
    return stars

def generate_aliens(alien, rows = 2, columns = 5):
    aliens = [ ]
    for x in range (columns):
        for y in range (rows):
            position = (x * (ALIEN_SIZE[0] + 10) , 10 + (10 + ALIEN_SIZE[1]) * y )
            aliens.append( alien.clone(position) )
    return aliens

def print_text(content, color):
    global FONT
    text = FONT.render(content, True, color)
    x = int((SCREEN_SIZE[0]-FONT.size(content)[0])/2)
    y = int((SCREEN_SIZE[1]-FONT.size(content)[1])/2)
    fenetre.blit(text, (x,y))

def end_game():
    global finished
    pygame.display.flip() 
    finished = True

def win_game():
    print_text("You won", pygame.Color(211, 200, 51))
    end_game()

def lose_game():
    print_text("You lost", pygame.Color(255, 25, 25))
    end_game()


pygame.init() # initialisation du module "pygame"

# CONSTANTES
SCREEN_SIZE = (600, 600)
ALIEN_SIZE = (33, 27)
SPACESHIP_SIZE = (64, 64)
FONT = pygame.font.SysFont("arial", 24)
DIRECTION_GAUCHE_DROITE = 0
DIRECTION_DROITE_GAUCHE = 1
PEW_SOUND = pygame.mixer.Sound("./pew.wav")
KILL_SOUND = pygame.mixer.Sound("./kill.wav")

# VARIABLES INITIALES
fenetre = pygame.display.set_mode( SCREEN_SIZE )
pygame.display.set_caption("Space Invader, Marchand Thomas 707")
stars = generate_stars()
alien_template = Alien( ALIEN_SIZE,  None, pygame.transform.scale(pygame.image.load("alien.png"), ALIEN_SIZE), KILL_SOUND)
aliens = generate_aliens(alien_template, 1, 3)
spaceship = Spaceship(SPACESHIP_SIZE, (SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 75), pygame.transform.scale(pygame.image.load("vaisseau.png"), SPACESHIP_SIZE), PEW_SOUND)
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
            if alien.position[0] + ALIEN_SIZE[0] > SCREEN_SIZE[0]:
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
            alien.move(0, ALIEN_SIZE[1])
            if alien.position[0] <= 0:
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

#    if count == 0:
#        if random.randrange(60 * 30) == 1: # 1 fois toutes les 30 secondes
#            projectile_text_content = "je s'appelle Groot, amorelézariéjoi"
#            projectile_text = FONT.render(projectile_text_content, True, pygame.Color(255, 255, 255))
#            x = random.randrange(SCREEN_SIZE[0]-FONT.size(projectile_text_content)[0])
#            y = random.randrange(SCREEN_SIZE[1]-FONT.size(projectile_text_content)[1])
#            fenetre.blit(projectile_text, (x,y))


    pygame.display.flip() # Rafraichissement complet de la fenêtre avec les dernières opérations de dessin


# Fonction en charge de gérer les évènements clavier (ou souris)
# Cette fonction sera appelée depuis notre boucle infinie
def gerer_clavier_souris():
    global continuer, spaceship, projectiles, projectiles_amount
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            continuer = False

        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_SPACE and projectiles_amount > 0:
                spaceship.shoot()

    touches_pressees = pygame.key.get_pressed()

    if touches_pressees[pygame.K_RIGHT] == True and spaceship.position[0] + spaceship.size[0] < SCREEN_SIZE[0]:
        spaceship.move( 10, 0 )

    elif touches_pressees[pygame.K_LEFT] == True and spaceship.position[0] > 0 :
        spaceship.move( -10, 0 )

clock = pygame.time.Clock()
continuer = True
finished = False
while continuer:

    clock.tick(60)

    if len(aliens) == 0:
        win_game()

    gerer_clavier_souris()
    if not finished: 
        dessiner()
        move_aliens()
        update_projectiles()

pygame.quit()
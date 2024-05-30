import pygame, time, random, sys
pygame.init() ## initialized all the pygame modules


## all uppercase to indicate that these are constants
WIDTH, HEIGHT = 405, 720

## set up the size and caption of the window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying to the Moon")

### background image fit to display scale
BG = pygame.transform.scale(pygame.image.load("./img/galaxy.png"), (WIDTH, HEIGHT))
FONT = pygame.font.SysFont("comicsans", 30)

## set up the initialization of the player
PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_VEL = 60, 90, 5
player_image = pygame.transform.scale(pygame.image.load("./img/spaceship.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha()
PLAYER_X, PLAYER_Y = WIDTH//2, HEIGHT - PLAYER_HEIGHT
PLAYER_HEALTH = 3 ## number of times allowed to be hit by the stars

## set up the star sizes, image, range of random location to appear
STAR_WIDTH, STAR_HEIGHT, STAR_VEL = 15, 50, 3 
star_image = pygame.transform.scale(pygame.image.load("./img/star.png"), (STAR_WIDTH, STAR_HEIGHT)).convert_alpha()
star_xrange = list(range(STAR_WIDTH+5, WIDTH-STAR_WIDTH-5, 20)) ## set up a list of x locations for stars to appear

record = [] ## create a list for records

## class buttons (reference: https://www.geeksforgeeks.org/hover-button-in-pygame/)
class Button(pygame.sprite.Sprite):   
    def __init__(self, color, color_hover, rect, text="", outline=None):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        tmp_rect = pygame.Rect(0, 0, *rect.size)
        self.org = self._create_image(color, outline, text, tmp_rect)
        self.hov = self._create_image(color_hover, outline, text, tmp_rect)
        self.image = self.org
        self.rect = rect
    def _create_image(self, color, outline, text, rect): ## create the actual surface
        img = pygame.Surface(rect.size)
        if outline is not None:
            img.fill(outline)
            img.fill(color, rect.inflate(-4, -3)) ## decrease fill color area for outline
        else:
            img.fill(color)
        if text != "":
            text_surf = FONT.render(text, 1, pygame.Color('black'))
            text_rect = text_surf.get_rect(center=rect.center) ## place text at the center of the button
            img.blit(text_surf, text_rect)
        return img
    def clicked(self):
        pos = pygame.mouse.get_pos()
        hit = self.rect.collidepoint(pos)
        self.image = self.hov if hit else self.org ## update the img to hov if the mouse hits the button
        if hit and pygame.mouse.get_pressed()[0]: return True
        else: return False
        
## class player rocket
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_image
        self.rect = self.image.get_rect() ##have a rectangle for the image so that it can be moved, and set its location
        self.rect.center = [x, y]
        self.health = PLAYER_HEALTH
        self.total_health = PLAYER_HEALTH
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        key = pygame.key.get_pressed()# check for key states to move while the keys are pressed
        if (key[pygame.K_LEFT] or key[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= PLAYER_VEL
        if (key[pygame.K_RIGHT] or key[pygame.K_d]) and (self.rect.x+PLAYER_VEL <= WIDTH-PLAYER_WIDTH):
            self.rect.x += PLAYER_VEL
        if (key[pygame.K_UP] or key[pygame.K_w]) and (self.rect.y > HEIGHT*2/3):
            self.rect.y -= PLAYER_VEL
        if (key[pygame.K_DOWN] or key[pygame.K_s]) and (self.rect.y+PLAYER_VEL <= HEIGHT-PLAYER_HEIGHT-20):
            self.rect.y += PLAYER_VEL
        pygame.draw.rect(WIN, pygame.Color('red'), (self.rect.x, self.rect.bottom+10, self.rect.width, 8))
        if self.health > 0:
            pygame.draw.rect(WIN, pygame.Color('green'), (self.rect.x, self.rect.bottom+10, int(self.rect.width*(self.health/self.total_health)), 8))

## class stars
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = star_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.rect.y += STAR_VEL
        if self.rect.y > HEIGHT:
            self.kill()

## initialize the stars
stars = pygame.sprite.Group()
def create_stars(n):
    star_x = random.sample(star_xrange, n)
    for i in range(n):
        star_left = star_x[i]
        star = Star(star_left, -STAR_HEIGHT)
        stars.add(star)

## create planets in the background
class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./img/planet_" + str(random.randint(1, 8)) + ".png")
        self.scale = random.randint(10, 50)
        self.width = self.image.get_width()*self.scale*0.01
        self.height = self.image.get_height()*self.scale*0.01
        self.image = pygame.transform.scale(self.image, (self.width, self.height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if self.scale > 30:
            self.vel = random.randint(1, 3) ## objects pass faster when they are smaller
        else:
            self.vel = random.randint(3, 6)
    def update(self):
        self.rect.y += self.vel
        if self.rect.y > HEIGHT:
            self.kill()
planets = pygame.sprite.Group()

## draw background & text for time
def draw_bg(elapsed_time, scroll): ## draw 2 backgrounds so that it won't glitch
    WIN.blit(BG, (0, 0+scroll))
    WIN.blit(BG, (0, -700+scroll))
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white") ## 1 for anti-aliasing
    WIN.blit(time_text, (10, 10)) ##padding 10 from top and left

def main():    ## menu page 
    ## create buton objects beforehand
    main_buttons = pygame.sprite.Group()
    start = Button(pygame.Color('cadetblue2'), pygame.Color('white'), pygame.Rect(125, 300, 150, 100), 'START', pygame.Color('black'))
    bquit = Button(pygame.Color('cadetblue2'), pygame.Color('white'), pygame.Rect(125, 500, 150, 100), 'QUIT', pygame.Color('black'))
    main_buttons.add(start)
    main_buttons.add(bquit)
    while True:
        events = pygame.event.get()
        for event in events:    ### check all the different events that are occurring in the game
            if event.type == pygame.QUIT or bquit.clicked():
                pygame.quit()
                sys.exit()
            if start.clicked(): 
                game()
                
        
        main_buttons.update(events)
        WIN.blit(BG, (0, 0))
        menu_title = FONT.render("Flying to the Moon", 1, (255, 255, 255))
        WIN.blit(menu_title, (WIDTH//2 - menu_title.get_width()//2, 100))
        ##main_buttons.update()
        main_buttons.draw(WIN)

        pygame.display.update()
        
def lose():    ## page after getting hit 
    lose_buttons = pygame.sprite.Group()
    retry = Button(pygame.Color('cadetblue2'), pygame.Color('white'), pygame.Rect(125, 300, 150, 100), 'RESTART', pygame.Color('black'),)
    lquit = Button(pygame.Color('cadetblue2'), pygame.Color('white'), pygame.Rect(125, 500, 150, 100), 'QUIT', pygame.Color('black'),)
    lose_buttons.add(retry)
    lose_buttons.add(lquit)
    score = record.pop()
    for star in stars: ## reset stars when lose
        star.kill()
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or lquit.clicked():
                pygame.quit()
                sys.exit()    
            if retry.clicked(): 
                game()
        
        lose_buttons.update(events)
        WIN.blit(BG, (0, 0))
        lost_text = FONT.render("You are hit by the stars!", 1, (255, 255, 255))
        WIN.blit(lost_text, (WIDTH//2 - lost_text.get_width()//2, 100))
        record_text = FONT.render("Score: "+str(score)+" s", 1, (255, 255, 255))
        WIN.blit(record_text, (WIDTH//2 - record_text.get_width()//2, lost_text.get_height()+150))
        lose_buttons.draw(WIN)

        pygame.display.update()

def game():    ## main game loop
    clock = pygame.time.Clock()    ###set up a clock object for the looping timestamp, player moving at constant speed
    start_time = time.time()    ##current time when the game starts
    elapsed_time = 0
    star_add_increment = 200    ##stars added at 2000 millisecond
    star_count = 3    ##to tell when to add the next star
    cooldown = 0      ## time for stars and player to pass after collision
    loop_count, loop10_count, planet_count = 0, 0, 0    ## number of loops
    scroll = 0
    player = Player(PLAYER_X, PLAYER_Y)
    players = pygame.sprite.Group()
    players.add(player)
    create_stars(3)
 
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        clock.tick(60)    ## FPS
        loop_count += 1   ## number of loops
        loop10_count += 1
        planet_count += 1
        elapsed_time = time.time() - start_time    ##iterate the seconds since the game starts
        scroll+=5           # moving background
        if scroll>=720:     # reset background if reaches the end
            scroll=0
        
        if planet_count > 200:
            planet_x = random.randint(-30, WIDTH-20)
            planet = Planet(planet_x, -HEIGHT*1.5)
            planets.add(planet)
            planet_count = 0
        
        if loop_count > star_add_increment: ## draw stars every 2 second
            if (loop10_count > 10*loop_count) and (star_count <= 8): ## increase stars every certain time
                star_count += 1
                loop10_count = 0
            create_stars(star_count)
            star_add_increment = max(100, star_add_increment - 10) ## gradually increases the speed of stars appearing
            loop_count = 0
        
        for star in stars.sprites():
            if pygame.sprite.collide_mask(star, player): ## perfect pixel collision
                if cooldown > 0:
                    cooldown -= 1
                elif star_add_increment < 150: ## speed of cooldown decreases when stars appear faster
                    player.health -= 1
                    cooldown = 25 ## < duration between 2 waves of stars
                else:
                    player.health -= 1
                    cooldown = 40
                if player.health <= 0:  ## if star and player collide more than 3 times, go to lose page
                    record.append(round(elapsed_time))
                    lose()
        
        draw_bg(elapsed_time, scroll)
        planets.update()
        planets.draw(WIN)

        players.update()
        stars.update()
        players.draw(WIN)
        stars.draw(WIN)

        pygame.display.update()


###make sure that the game starts only when this file itself is directly called, not when it is imported somewhere else
if __name__ == "__main__":
  main()

import pygame
import os
import random
pygame.font.init()

# Janela
WIDTH, HEIGHT = 480, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WW2 Shooter")

# Imagens
MENU_IMG      = pygame.image.load(os.path.join("assets", "background", "menu.png"))
BG1_IMG       = pygame.image.load(os.path.join("assets", "background", "cloudsky.png"))
BG2_IMG       = pygame.image.load(os.path.join("assets", "background", "fullmoon.png"))

ENEMY01_IMG   = pygame.image.load(os.path.join("assets", "enemies", "Aircraft_01.png"))  
ENEMY02_IMG   = pygame.image.load(os.path.join("assets", "enemies", "Aircraft_02.png"))  
ENEMY03_IMG   = pygame.image.load(os.path.join("assets", "enemies", "Aircraft_03.png")) 
ENEMYBOSS_IMG = pygame.image.load(os.path.join("assets", "enemies", "Aircraft_Boss.png"))

PLAYER_IMG      = pygame.image.load(os.path.join("assets", "playerp38", "P38_lvl_3_d0.png"))
PLAYERDMG01_IMG = pygame.image.load(os.path.join("assets", "playerp38", "P38_lvl_3_d1.png"))
PLAYERDMG02_IMG = pygame.image.load(os.path.join("assets", "playerp38", "P38_lvl_3_d2.png"))
PLAYERDMG03_IMG = pygame.image.load(os.path.join("assets", "playerp38", "P38_lvl_3_d3.png"))
PLAYERDMG04_IMG = pygame.image.load(os.path.join("assets", "playerp38", "P38_lvl_3_d4.png"))

BULLETBLUE_IMG   = pygame.image.load(os.path.join("assets", "bullets", "bullet_blue.png"))
BULLETPURPLE_IMG = pygame.image.load(os.path.join("assets", "bullets", "bullet_purple.png"))
BULLETORANGE_IMG = pygame.image.load(os.path.join("assets", "bullets", "bullet_orange.png"))
ROCKET_IMG       = pygame.image.load(os.path.join("assets", "bullets", "rocket.png"))

# Cor e fonte
fontecustom = pygame.font.SysFont("Imagine_Font", 30)
BRANCO  = (255, 255, 255)

# Configuracoes dos inimigos
ATRIBUTOS = {                   #mais baixo, mais rapido
    #          vida  vel_y  vel_x  cadencia  dano_proj
    "me262":  (100,    3,     6,     90,       20),   
    "p40":    (100,    1,     3,     90,       20),   
    "j5n1":   (100,    1,     3,     45,       20),   
    "bomber": (800,    1,     2,     90,       50),    
}

#funcao de colisao
def colisao(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

# Projetil
class Projetil:
    def __init__(self, x, y, img, velocidade):
        self.x = x
        self.y = y
        self.img = img
        self.velocidade = velocidade
        self.mask = pygame.mask.from_surface(self.img)

    def mover(self):
        self.y += self.velocidade

    def fora_da_tela(self):
        return self.y < -self.img.get_height() or self.y > HEIGHT

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

# Player
class Player:
    CADENCIA_TIRO = 20  # menor valor, mais rapido

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vida = 100
        self.projeteis = []
        self.recarga = 0  
        self.mask = pygame.mask.from_surface(PLAYER_IMG)

      
    def get_img(self):
        # Imagens de dano 
        if self.vida > 80:   return PLAYER_IMG
        elif self.vida > 60: return PLAYERDMG01_IMG
        elif self.vida > 40: return PLAYERDMG02_IMG
        elif self.vida > 20: return PLAYERDMG03_IMG
        else:                return PLAYERDMG04_IMG

    def draw(self, window):
        window.blit(self.get_img(), (self.x, self.y))
        # Desenha os projeteis
        for p in self.projeteis:
            p.draw(window)
        
    def atirar(self):
        if self.recarga == 0: # pode atirar quando o numero da cadencia chega a zero
            largura_img = BULLETORANGE_IMG.get_width()
            centro_x = self.x + self.get_img().get_width() // 2 - largura_img // 2
            self.projeteis.append(Projetil(centro_x, self.y, BULLETORANGE_IMG, -7))
            self.recarga = self.CADENCIA_TIRO # reseta o contador

    def balistica(self, inimigos):
        self.recarga = max(0, self.recarga - 1) # decrementa o numero da cadencia a cada frame
        for p in self.projeteis[:]:
            p.mover()
            if p.fora_da_tela():
                self.projeteis.remove(p)
                continue
            for inimigo in inimigos[:]:
                if inimigo.totalmente_visivel():
                    if colisao(p, inimigo):
                        inimigo.vida -= 25
                        if p in self.projeteis:
                            self.projeteis.remove(p)
                        if inimigo.vida <= 0:
                            inimigos.remove(inimigo)

    
# Inimigo
class Inimigo:
    TiposImagens = {
        "me262":  (ENEMY01_IMG,   BULLETBLUE_IMG),
        "p40":    (ENEMY02_IMG,   BULLETPURPLE_IMG),
        "j5n1":   (ENEMY03_IMG,   BULLETPURPLE_IMG),
        "bomber": (ENEMYBOSS_IMG, ROCKET_IMG),
    }

    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.inimigo_img, self.projetil_img = self.TiposImagens[tipo]
        self.mask = pygame.mask.from_surface(self.inimigo_img)
        self.projeteis = []

        # Carrega os atributos
        vida, self.vel_y, self.vel_x, self.cadencia, self.dano_proj = ATRIBUTOS[tipo]
        self.vida = vida

        # Movimento lateral aleatório
        self.direcao_x = random.choice([-1, 1]) * self.vel_x

        # Contador de recarga do tiro
        self.recarga = 0

        # Contador de mudança de direcao
        self.timer_direcao = random.randint(30, 90)

    def totalmente_visivel(self):
        return (self.y >= 0)

    def mover(self):
        largura_img = self.inimigo_img.get_width()
        altura_img  = self.inimigo_img.get_height()
        metade_tela = HEIGHT // 2 

        # Desce se estiver acima da metade
        if self.y + altura_img < metade_tela:
            self.y += self.vel_y

        # move lateralmente
        if self.y >= 0:
            self.timer_direcao -= 1
            if self.timer_direcao <= 0:
                # Muda direção aleatoriamente
                self.direcao_x = random.choice([-1, 1]) * self.vel_x
                self.timer_direcao = random.randint(30, 90)

            novo_x = self.x + self.direcao_x
            # Nao sair pelas bordas
            if 0 <= novo_x <= WIDTH - largura_img:
                self.x = novo_x
            else:
                self.direcao_x *= -1 
    
    def atirar(self):
        if self.recarga == 0 and self.totalmente_visivel():
            centro_x = self.x + self.inimigo_img.get_width() // 2 - self.projetil_img.get_width() // 2
            self.projeteis.append(Projetil(centro_x, self.y + self.inimigo_img.get_height(), self.projetil_img, 4))
            self.recarga = self.cadencia

    def balistica(self, player):
        self.recarga = max(0, self.recarga - 1) 
        for p in self.projeteis[:]:
            p.mover()
            if p.fora_da_tela():
                self.projeteis.remove(p)
                continue
            if colisao(p, player):
                player.vida -= self.dano_proj
                self.projeteis.remove(p)

    def draw(self, window):
        window.blit(self.inimigo_img, (self.x, self.y))
        for p in self.projeteis:
            p.draw(window)
 
def gerar_onda(numero_onda):
    inimigos = []
    tipos_cacas = ["me262", "p40", "j5n1"]

    # Limitar a largura do spawn
    largura_normal = ENEMY03_IMG.get_width()
    largura_boss   = ENEMYBOSS_IMG.get_width()

    if numero_onda % 3 == 0:
        for i in range(2):
            x = random.randint(0, WIDTH - largura_boss) 
            y = random.randint(-200, -80)
            inimigos.append(Inimigo(x, y, "bomber"))
    else:
        for i in range(5):
            x = random.randint(0, WIDTH - largura_normal) 
            y = random.randint(-500, -60) - i * 80
            tipo = random.choice(tipos_cacas)
            inimigos.append(Inimigo(x, y, tipo))

    return inimigos

def main():
    run = True
    clock = pygame.time.Clock()
    FPS = 60

    # Estado inicial
    numero_onda = 0
    player = Player(182, 500)
    inimigos = []
    state = "menu"

    # LOOP
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if state == "menu" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = "game"

        # Gerar onda
        if state == "game" and len(inimigos) == 0:
            numero_onda += 1
            inimigos = gerar_onda(numero_onda)
        
        if state == "game":
            # Movimento do player
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x > 0:           player.x -= 4
            if keys[pygame.K_d] and player.x < 364:         player.x += 4
            if keys[pygame.K_w] and player.y > 360:         player.y -= 2
            if keys[pygame.K_s] and player.y < 512:         player.y += 2

            # Tiro do player
            if keys[pygame.K_SPACE]:
                player.atirar()

            # Verifica colisao
            player.balistica(inimigos)

            # Atualiza movimentacao e balistica
            for inimigo in inimigos:
                inimigo.mover()
                inimigo.atirar()
                inimigo.balistica(player)

            # Voltar pro menu e resetar
            if player.vida <= 0 or keys[pygame.K_ESCAPE]:
                state = "menu"
                numero_onda = 0
                player = Player(182, 500)
                inimigos = []
        
        # MENU OU INGAME
        if state == "menu":
            WIN.blit(MENU_IMG, (0, 0))

        else:
            tem_boss = any(i.tipo == "bomber" for i in inimigos)
            if tem_boss:
                WIN.blit(BG2_IMG, (0, 0))
            else:
                WIN.blit(BG1_IMG, (0, 0))

            # Desenhar vida e numero da onda
            vida_text  = fontecustom.render(f"Vida: {player.vida}", 1, BRANCO)
            onda_text  = fontecustom.render(f"Onda: {numero_onda}", 1, BRANCO)
            WIN.blit(vida_text,  (10, 10))
            WIN.blit(onda_text,  (10, 40))

            player.draw(WIN)
            for inimigo in inimigos:
                inimigo.draw(WIN)

        pygame.display.update()
main()
import pygame
import os
import time
import random

pygame.font.init()

# Dimensões da Tela
LARGURA, ALTURA = 750, 750  
JANELA = pygame.display.set_mode((LARGURA, ALTURA)) 
pygame.display.set_caption("Space Shooter | 22125 | 22136 ") 

# Carregar imagens
PROFESSOR_UM = pygame.image.load(os.path.join("imagens", "jodir.png"))
PROFESSOR_DOIS = pygame.image.load(os.path.join("imagens", "chico.png"))
PROFESSOR_TRES = pygame.image.load(os.path.join("imagens", "sergio.png"))

# Jogador
ALUNO = pygame.image.load(os.path.join("imagens", "aluno.png"))

# Lasers
DP = pygame.image.load(os.path.join("imagens", "dp.png"))
PROVA = pygame.image.load(os.path.join("imagens", "provaa.png"))

# Plano de fundo
PLANO_DE_FUNDO = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "sala_De_aula.png")), (LARGURA, ALTURA))

# Definição da classe para Laser
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def desenhar(self, janela): 
        janela.blit(self.img, (self.x, self.y))

    def move(self, vel): 
        self.y += vel

    def fora_da_tela(self, altura): # Retorna caso o laser saia da tela
        return not(self.y <= altura and self.y >= 0)

    def colisao(self, obj): # Verifica Colisao
        return colidir(self, obj)

# Definição da classe para Nave (classe base para Jogador e Inimigo)
class Nave:
    COOLDOWN = 30

    def __init__(self, x, y, vida=100):
        self.x = x
        self.y = y
        self.vida = vida
        self.imagem_nave = None
        self.imagem_laser = None
        self.lasers = []
        self.contador_restante_resfriamento = 0

    def desenhar(self, janela):
        janela.blit(self.imagem_nave, (self.x, self.y))
        for laser in self.lasers:
            laser.desenhar(janela)

    def mover_lasers(self, vel, obj): # Metodo base para movimento de lasers
        self.resfriamento()
        for laser in self.lasers:
            laser.move(vel)
            if laser.fora_da_tela(ALTURA):
                self.lasers.remove(laser)
            elif laser.colisao(obj):
                obj.vida -= 10
                self.lasers.remove(laser)

    def resfriamento(self): # Controla tempo entre dois tiros consecutivos
        if self.contador_restante_resfriamento >= self.COOLDOWN:
            self.contador_restante_resfriamento = 0
        elif self.contador_restante_resfriamento > 0:
            self.contador_restante_resfriamento += 1

    def atirar(self): # Método para atirar lasers
        if self.contador_restante_resfriamento == 0:
            laser = Laser(self.x, self.y, self.imagem_laser)
            self.lasers.append(laser)
            self.contador_restante_resfriamento = 1

    #Obtem dimensoes dos objetos
    def obter_largura(self):
        return self.imagem_nave.get_width()

    def obter_altura(self):
        return self.imagem_nave.get_height()

# Definição da classe para Jogador, herdando de Nave
class Jogador(Nave):
    def __init__(self, x, y, vida=100):
        super().__init__(x, y, vida)
        self.imagem_nave = ALUNO
        self.imagem_laser = PROVA
        self.mask = pygame.mask.from_surface(self.imagem_nave)
        self.vida_maxima = vida

    def mover_lasers(self, vel, objs): # Implementacao do metodo mover_lasers para a classe jogador
        self.resfriamento()
        for laser in self.lasers:
            laser.move(vel)
            if laser.fora_da_tela(ALTURA):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.colisao(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def desenhar(self, janela): # Desenhar jogador
        super().desenhar(janela)
        self.barra_de_vida(janela)

    def barra_de_vida(self, janela):
        pygame.draw.rect(janela, (255,0,0), (self.x, self.y + self.imagem_nave.get_height() + 10, self.imagem_nave.get_width(), 10))
        pygame.draw.rect(janela, (0,255,0), (self.x, self.y + self.imagem_nave.get_height() + 10, self.imagem_nave.get_width() * (self.vida/self.vida_maxima), 10))

# Definição da classe para Inimigo, herdando de Nave
class Inimigo(Nave):
    # Armazena os diferentes tipos de inimigos
    MAPA_DE_COR = { 
                "vermelho": (PROFESSOR_UM, DP),
                "verde": (PROFESSOR_DOIS, DP),
                "azul": (PROFESSOR_TRES, DP)
                } 

    def __init__(self, x, y, cor, vida=100):
        super().__init__(x, y, vida)
        self.imagem_nave, self.imagem_laser = self.MAPA_DE_COR[cor]
        self.mask = pygame.mask.from_surface(self.imagem_nave)

    def move(self, vel):
        self.y += vel

    def atirar(self): # Implementacao do metodo atirar
        if self.contador_restante_resfriamento == 0:
            laser = Laser(self.x-20, self.y, self.imagem_laser)
            self.lasers.append(laser)
            self.contador_restante_resfriamento = 1

# Função para verificar colisão entre dois objetos
def colidir(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Loop principal do jogo
def principal():
    #Definicao de variaveis de controle
    executando = True
    FPS = 60
    nivel = 0
    vidas = 5
    fonte_principal = pygame.font.SysFont("arial", 30)
    fonte_perdida = pygame.font.SysFont("arial", 60)

    inimigos = []
    comprimento_onda = 5
    velocidade_inimigo = 1

    velocidade_jogador = 5
    velocidade_laser = 5

    jogador = Jogador(300, 630)

    relogio = pygame.time.Clock()

    perdido = False
    contador_perdido = 0

    # Função para redesenhar a janela
    def redesenhar_janela():
        JANELA.blit(PLANO_DE_FUNDO, (0,0))
        # desenhar vidas e nivel
        rotulo_vidas = fonte_principal.render(f"Vidas: {vidas}", 1, (255,255,255))
        rotulo_nivel = fonte_principal.render(f"Nível: {nivel}", 1, (255,255,255))

        JANELA.blit(rotulo_vidas, (10, 10))
        JANELA.blit(rotulo_nivel, (LARGURA - rotulo_nivel.get_width() - 10, 10))
        #desenhar inimigos
        for inimigo in inimigos:
            inimigo.desenhar(JANELA)

        jogador.desenhar(JANELA)
        #Se perdeu, desenhar tela de Reprovado
        if perdido:
            rotulo_perdido = fonte_perdida.render("Reprovou!!", 1, (255,255,255))
            JANELA.blit(rotulo_perdido, (LARGURA/2 - rotulo_perdido.get_width()/2, 350))

        pygame.display.update()

    #Loop principal
    while executando:
        relogio.tick(FPS) #Taxa de mudança do jogo
        redesenhar_janela()

        if vidas <= 0 or jogador.vida <= 0: #Verificar se perdeu
            perdido = True
            contador_perdido += 1

        if perdido: #Tratador de perdedor
            if contador_perdido > FPS * 3:
                executando = False
            else:
                continue

        #Anexa inimigos ao vetor de inimigos, aumenta horda a cada nivel
        if len(inimigos) == 0: 
            nivel += 1
            comprimento_onda += 5 #Aumenta horda de inimigos
            for i in range(comprimento_onda):
                inimigo = Inimigo(random.randrange(50, LARGURA-100), random.randrange(-1500, -100), random.choice(["vermelho", "azul", "verde"]))
                inimigos.append(inimigo)

        for evento in pygame.event.get(): #Tratador de evento para saida do jogo
            if evento.type == pygame.QUIT:
                quit()

        #Tratador de evento para movimento do personagem
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] and jogador.x - velocidade_jogador > 0: # esquerda
            jogador.x -= velocidade_jogador
        if teclas[pygame.K_d] and jogador.x + velocidade_jogador + jogador.obter_largura() < LARGURA: # direita
            jogador.x += velocidade_jogador
        if teclas[pygame.K_w] and jogador.y - velocidade_jogador > 0: # cima
            jogador.y -= velocidade_jogador
        if teclas[pygame.K_s] and jogador.y + velocidade_jogador + jogador.obter_altura() + 15 < ALTURA: # baixo
            jogador.y += velocidade_jogador
        if teclas[pygame.K_SPACE]:
            jogador.atirar()

        #Atualizar posicao dos inimigos e suas DPs
        for inimigo in inimigos[:]:
            inimigo.move(velocidade_inimigo)
            inimigo.mover_lasers(velocidade_laser, jogador)

            if random.randrange(0, 2*60) == 1: #Verifica quando atirar
                inimigo.atirar()

            if colidir(inimigo, jogador): #Verifica se o jogador colidiu com um inimigo
                jogador.vida -= 10
                inimigos.remove(inimigo)
            elif inimigo.y + inimigo.obter_altura() > ALTURA: #Verifica se o inimigo alcançou a base da tela
                vidas -= 1
                inimigos.remove(inimigo)

        jogador.mover_lasers(-velocidade_laser, inimigos) #Altera a posiçao das provas e verifica colisao com inimigos

# Função para exibir o menu principal
def menu_principal():
    fonte_titulo = pygame.font.SysFont("arial", 60)
    executando = True
    while executando:
        JANELA.blit(PLANO_DE_FUNDO, (0,0))
        rotulo_titulo = fonte_titulo.render("Pressione o mouse para iniciar!", 1, (255,255,255))
        JANELA.blit(rotulo_titulo, (LARGURA/2 - rotulo_titulo.get_width()/2, 350))
        pygame.display.update()
        for evento in pygame.event.get(): #Verica caso o jogador inicie o jogo, ou saia dele
            if evento.type == pygame.QUIT:
                executando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                principal()
    pygame.quit()

# Chama a função do menu principal para iniciar o jogo
menu_principal()

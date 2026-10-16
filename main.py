import pygame
import random
import time
import os

# Inicializa o Pygame
pygame.init()

#inicio tempo
tempo_inicio = time.time()

#musica
time.sleep(1) #tempo para sincronizar a musica e o jogo

pygame.mixer.init() #inicia o mixer

pasta = os.path.dirname(os.path.abspath(__file__))
musica = os.path.join(pasta, "musica.mp3")

pygame.mixer.music.load(musica) #carrega a música
pygame.mixer.music.set_volume(0.5) #volume de 0 a 1 
pygame.mixer.music.play(-1) #toca em loop

# Configurações da tela e grade
TAMANHO_BLOCO = 30
COLUNAS = 10
LINHAS = 20

LADO_TELA = LINHAS * TAMANHO_BLOCO  # janela quadrada (usa a altura como referência)
BORDA_X = (LADO_TELA - COLUNAS * TAMANHO_BLOCO) // 2  # faixa preta de cada lado

tela = pygame.display.set_mode((LADO_TELA, LADO_TELA))
pygame.display.set_caption("Tetris")

relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 30)
fonte_borda = pygame.font.SysFont(None, 22)  # fonte menor para caber na faixa preta

# Cores das peças (RGB)
AZUL_CLARO   = (0, 255, 255)   # I
AMARELO      = (255, 255, 0)   # O
ROXO         = (128, 0, 255)   # T
LARANJA      = (255, 165, 0)   # L
AZUL_ESCURO  = (0, 0, 255)    # J
VERDE        = (0, 255, 0)     # S
VERMELHO     = (255, 0, 0)     # Z

# Formatos das peças (1 para bloco preenchido, 0 para vazio)
MODELOS_PECAS = [
    {"formato": [[1,1,1,1]], "cor": AZUL_CLARO},
    {"formato": [[1,1],[1,1]], "cor": AMARELO},
    {"formato": [[0,1,0],[1,1,1]], "cor": ROXO},
    {"formato": [[1,0,0],[1,1,1]], "cor": LARANJA},
    {"formato": [[0,0,1],[1,1,1]], "cor": AZUL_ESCURO},
    {"formato": [[0,1,1],[1,1,0]], "cor": VERDE},
    {"formato": [[1,1,0],[0,1,1]], "cor": VERMELHO}
]

# Matriz de controle do tabuleiro
tabuleiro = [[0] * COLUNAS for _ in range(LINHAS)]

def criar_nova_peca():
    """Gera uma peça aleatória no topo central."""
    peca = random.choice(MODELOS_PECAS)
    return {
        "formato": peca["formato"], 
        "cor": peca["cor"], 
        "x": 3,
        "y": 0
    }

def verificar_colisao(peca):
    """Detecta colisões com as bordas do tabuleiro ou blocos fixados."""
    for y, linha in enumerate(peca["formato"]):
        for x, bloco in enumerate(linha):
            if bloco:
                px, py = peca["x"] + x, peca["y"] + y
                if px < 0 or px >= COLUNAS or py >= LINHAS or (py >= 0 and tabuleiro[py][px]):
                    return True
    return False

def fixar_peca(peca):
    """Transfere a peça atual de forma definitiva para a matriz do tabuleiro."""
    for y, linha in enumerate(peca["formato"]):
        for x, bloco in enumerate(linha):
            if bloco:
                tabuleiro[peca["y"] + y][peca["x"] + x] = peca["cor"]

def eliminar_linhas():
    """Remove linhas cheias e adiciona novas linhas vazias no topo."""
    global tabuleiro, linhas_eliminadas
    linhas_vivas = [linha for linha in tabuleiro if 0 in linha]
    sumidas = LINHAS - len(linhas_vivas)
    tabuleiro = [[0] * COLUNAS for _ in range(sumidas)] + linhas_vivas
    linhas_eliminadas += sumidas

def tentar_mover(peca, dx, dy):
    """Aplica o movimento de translação e desfaz em caso de colisão."""
    peca["x"] += dx
    peca["y"] += dy
    if verificar_colisao(peca):
        peca["x"] -= dx
        peca["y"] -= dy
        return False
    return True

def fixar_e_proxima_peca():
    """Faz a transição da peça atual para o tabuleiro e gera a próxima."""
    global peca_atual, pecas_colocadas, atraso_queda, fim_de_jogo
    fixar_peca(peca_atual)
    pecas_colocadas += 1
    eliminar_linhas()
    peca_atual = criar_nova_peca()
    
    # Aumenta a dificuldade diminuindo 1ms de atraso a cada peça (mínimo de 100ms)
    atraso_queda = max(100, atraso_queda - 1)
    
    if verificar_colisao(peca_atual):
        fim_de_jogo = True

def reiniciar():
    """Reseta o estado do jogo para começar uma nova partida."""
    global tabuleiro, peca_atual, pecas_colocadas, tempo_queda, tempo_movimento, fim_de_jogo, atraso_queda, tempo_inicio, linhas_eliminadas
    tabuleiro = [[0] * COLUNAS for _ in range(LINHAS)]
    peca_atual = criar_nova_peca()
    pecas_colocadas = 0
    tempo_queda = tempo_movimento = 0
    fim_de_jogo = False
    atraso_queda = 500
    tempo_inicio = time.time()
    linhas_eliminadas = 0

def formatar_tempo(segundos):
    """Formata segundos totais como MM:SS."""
    minutos = int(segundos) // 60
    segs = int(segundos) % 60
    return f"{minutos:02d}:{segs:02d}"

# Estado inicial do jogo
peca_atual = criar_nova_peca()
pecas_colocadas = 0
linhas_eliminadas = 0    # Contador de linhas completadas
tempo_queda = 0          # Temporizador de gravidade
tempo_movimento = 0      # Temporizador das setas
fim_de_jogo = False
atraso_queda = 500       # Velocidade de queda inicial (em ms)
jogo_rodando = True

# Loop principal
while jogo_rodando:
    dt = relogio.tick(60)  # Limita a execução a 60 FPS
    tempo_queda += dt
    tempo_movimento += dt

    # Captura de eventos de clique único
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jogo_rodando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar()
                
            # Rotação da peça ativa
            elif evento.key == pygame.K_UP and not fim_de_jogo:
                antigo = peca_atual["formato"]
                peca_atual["formato"] = [list(c) for c in zip(*antigo[::-1])]
                if verificar_colisao(peca_atual):
                    peca_atual["formato"] = antigo

    # Entradas contínuas (segurar teclas de direção)
    teclas = pygame.key.get_pressed()
    if not fim_de_jogo and tempo_movimento >= 70:
        tempo_movimento = 0
        if teclas[pygame.K_LEFT]: tentar_mover(peca_atual, -1, 0)
        if teclas[pygame.K_RIGHT]: tentar_mover(peca_atual, 1, 0)
        if teclas[pygame.K_DOWN]: tentar_mover(peca_atual, 0, 1)

    # Gravidade natural (Queda automática por tempo)
    if not fim_de_jogo and tempo_queda >= atraso_queda:
        tempo_queda = 0
        if not tentar_mover(peca_atual, 0, 1):
            fixar_e_proxima_peca()

    # Renderização visual
    tela.fill((0, 0, 0))  # bordas pretas nas laterais
    pygame.draw.rect(tela, (25, 25, 25), (BORDA_X, 0, COLUNAS * TAMANHO_BLOCO, LADO_TELA))  # área de jogo

    # Desenha o tabuleiro com recuo de 1px para criar o quadriculado
    for y in range(LINHAS):
        for x in range(COLUNAS):
            if tabuleiro[y][x]:
                px = BORDA_X + x * TAMANHO_BLOCO + 1
                py = y * TAMANHO_BLOCO + 1
                pygame.draw.rect(tela, tabuleiro[y][x], (px, py, TAMANHO_BLOCO - 2, TAMANHO_BLOCO - 2))

    # Desenha a peça ativa com recuo de 1px para criar o quadriculado
    for y, linha in enumerate(peca_atual["formato"]):
        for x, bloco in enumerate(linha):
            if bloco:
                px = BORDA_X + (peca_atual["x"] + x) * TAMANHO_BLOCO + 1
                py = (peca_atual["y"] + y) * TAMANHO_BLOCO + 1
                pygame.draw.rect(tela, peca_atual["cor"], (px, py, TAMANHO_BLOCO - 2, TAMANHO_BLOCO - 2))

    # Exibição de texto (Interface) - posicionada na borda preta esquerda
    tela.blit(fonte_borda.render("Peças:", True, (255, 255, 255)), (10, 15))
    tela.blit(fonte_borda.render(f"{pecas_colocadas}", True, (255, 255, 255)), (10, 35))

    # Contador de linhas eliminadas
    tela.blit(fonte_borda.render("Linhas:", True, (255, 255, 255)), (10, 75))
    tela.blit(fonte_borda.render(f"{linhas_eliminadas}", True, (255, 255, 255)), (10, 95))

    # Cronômetro de tempo de jogo (usa o time.time() do início)
    tempo_decorrido = time.time() - tempo_inicio
    tela.blit(fonte_borda.render("Tempo:", True, (255, 255, 255)), (10, 135))
    tela.blit(fonte_borda.render(formatar_tempo(tempo_decorrido), True, (255, 255, 255)), (10, 155))

    if fim_de_jogo:
        tela.blit(fonte_borda.render("Game Over", True, (255, 255, 255)), (10, 200))
        tela.blit(fonte_borda.render("R p/ reiniciar", True, (255, 255, 255)), (10, 220))
    

    pygame.display.flip()

pygame.quit()

import pygame
import sys
import random

# Configuración básica
WIDTH, HEIGHT = 400, 460  # Agregamos espacio para la barra inferior
ROWS, COLS = 10, 10
MINES_COUNT = 15
CELL_SIZE = WIDTH // COLS

# Colores
GRAY = (189, 189, 189)
DARK_GRAY = (99, 99, 99)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buscaminas")

font = pygame.font.SysFont(None, 24)
font_big = pygame.font.SysFont(None, 32)

# Celdas
class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.is_mine = False
        self.adjacent_mines = 0
        self.revealed = False
        self.flagged = False

    def draw(self, reveal_all=False):
        # Mostrar todas las minas si reveal_all está activado (al perder)
        if reveal_all and self.is_mine:
            pygame.draw.rect(screen, GRAY, self.rect)
            pygame.draw.circle(screen, BLACK, self.rect.center, CELL_SIZE//4)
            pygame.draw.rect(screen, BLACK, self.rect, 1)
            return

        if self.revealed:
            pygame.draw.rect(screen, GRAY, self.rect)
            if self.is_mine:
                pygame.draw.circle(screen, BLACK, self.rect.center, CELL_SIZE//4)
            elif self.adjacent_mines > 0:
                # Mostrar número con colores distintos por número
                colors = [BLUE, GREEN, RED, (0,0,128), (128,0,0), (0,128,128), (0,0,0), (128,128,128)]
                color = colors[self.adjacent_mines-1] if self.adjacent_mines <= len(colors) else BLACK
                text = font.render(str(self.adjacent_mines), True, color)
                text_rect = text.get_rect(center=self.rect.center)
                screen.blit(text, text_rect)
        else:
            pygame.draw.rect(screen, DARK_GRAY, self.rect)
            if self.flagged:
                # Dibuja bandera con triángulo rojo
                pygame.draw.polygon(screen, RED, [
                    (self.rect.left + CELL_SIZE//4, self.rect.top + CELL_SIZE//4),
                    (self.rect.left + CELL_SIZE//4, self.rect.bottom - CELL_SIZE//4),
                    (self.rect.right - CELL_SIZE//4, self.rect.centery)
                ])
                pygame.draw.line(screen, BLACK, (self.rect.left + CELL_SIZE//4, self.rect.top + CELL_SIZE//4), (self.rect.left + CELL_SIZE//4, self.rect.bottom - CELL_SIZE//4), 2)
        pygame.draw.rect(screen, BLACK, self.rect, 1)

# Inicializar tablero
def create_board():
    board = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
    # Colocar minas
    mines_placed = 0
    while mines_placed < MINES_COUNT:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        cell = board[r][c]
        if not cell.is_mine:
            cell.is_mine = True
            mines_placed += 1

    # Calcular minas adyacentes
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c].is_mine:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc].is_mine:
                        count += 1
            board[r][c].adjacent_mines = count
    return board

# Revelar celdas recursivamente
def reveal_cell(board, row, col):
    cell = board[row][col]
    if cell.revealed or cell.flagged:
        return
    cell.revealed = True
    if cell.adjacent_mines == 0 and not cell.is_mine:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if not board[nr][nc].revealed:
                        reveal_cell(board, nr, nc)

# Comprobar si se ganó
def check_win(board):
    for row in board:
        for cell in row:
            if not cell.is_mine and not cell.revealed:
                return False
    return True

# Botón reiniciar
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, LIGHT_BLUE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surf = font_big.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    board = create_board()
    game_over = False
    win = False
    flags_left = MINES_COUNT

    restart_button = Button(WIDTH//2 - 50, HEIGHT - 40, 100, 30, "Reiniciar")

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.is_clicked(mouse_pos):
                    # Reiniciar juego
                    board = create_board()
                    game_over = False
                    win = False
                    flags_left = MINES_COUNT
                elif not game_over and mouse_pos[1] < ROWS * CELL_SIZE:
                    row, col = mouse_pos[1] // CELL_SIZE, mouse_pos[0] // CELL_SIZE
                    cell = board[row][col]
                    if event.button == 1:  # Click izquierdo
                        if not cell.flagged:
                            cell.revealed = True
                            if cell.is_mine:
                                game_over = True
                            elif cell.adjacent_mines == 0:
                                reveal_cell(board, row, col)
                            if check_win(board):
                                game_over = True
                                win = True
                    elif event.button == 3:  # Click derecho
                        if not cell.revealed:
                            if not cell.flagged and flags_left > 0:
                                cell.flagged = True
                                flags_left -= 1
                            elif cell.flagged:
                                cell.flagged = False
                                flags_left += 1

        # Dibujar celdas
        for row in board:
            for cell in row:
                # Si perdiste, muestra todas las minas
                cell.draw(reveal_all=game_over and not win)

        # Dibujar barra inferior con info y botón reiniciar
        # Fondo barra
        pygame.draw.rect(screen, GRAY, (0, HEIGHT - 60, WIDTH, 60))

        # Texto de banderas restantes
        flags_text = font_big.render(f"Banderas restantes: {flags_left}", True, BLACK)
        screen.blit(flags_text, (10, HEIGHT - 50))

        # Mensaje final
        if game_over:
            msg = "¡Ganaste!" if win else "¡Perdiste!"
            msg_color = GREEN if win else RED
            msg_text = font_big.render(msg, True, msg_color)
            screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, HEIGHT - 90))

        restart_button.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()

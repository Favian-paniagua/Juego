import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Constantes del juego
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 150, 0)

# Direcciones
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        
    def move(self):
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Verificar colisión con paredes
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
            
        # Verificar colisión consigo misma
        if new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
        
    def change_direction(self, direction):
        # Evitar que la serpiente se mueva en dirección opuesta
        if (self.direction[0] * -1, self.direction[1] * -1) != direction:
            self.direction = direction
            
    def eat_food(self):
        self.grow = True
        
    def draw(self, surface):
        for i, position in enumerate(self.positions):
            rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE, 
                             CELL_SIZE, CELL_SIZE)
            # Cabeza de la serpiente en color diferente
            if i == 0:
                pygame.draw.rect(surface, DARK_GREEN, rect)
                pygame.draw.rect(surface, WHITE, rect, 2)
            else:
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.color = RED
        
    def generate_position(self):
        return (random.randint(0, GRID_WIDTH - 1), 
                random.randint(0, GRID_HEIGHT - 1))
                
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE,
                          CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()
        
    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                elif self.paused:
                    if event.key == pygame.K_p:
                        self.paused = False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_p:
                        self.paused = True
                        
        return True
        
    def update(self):
        if not self.game_over and not self.paused:
            if not self.snake.move():
                self.game_over = True
                return
                
            # Verificar si la serpiente comió la comida
            if self.snake.positions[0] == self.food.position:
                self.snake.eat_food()
                self.score += 10
                
                # Generar nueva comida en posición libre
                while self.food.position in self.snake.positions:
                    self.food.position = self.food.generate_position()
                    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Dibujar grid
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))
            
        # Dibujar serpiente y comida
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Dibujar puntuación
        score_text = self.font.render(f"Puntuación: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Dibujar mensajes
        if self.paused:
            pause_text = self.font.render("PAUSADO - Presiona P para continuar", True, YELLOW)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
            
        elif self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_final_text = self.font.render(f"Puntuación Final: {self.score}", True, WHITE)
            restart_text = self.font.render("Presiona ESPACIO para reiniciar o ESC para salir", True, WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            score_rect = score_final_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_final_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
            
        # Mostrar controles
        if not self.game_over:
            controls_text = pygame.font.Font(None, 24).render("Controles: WASD o Flechas | P: Pausa", True, WHITE)
            self.screen.blit(controls_text, (10, WINDOW_HEIGHT - 25))
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # 10 FPS para hacer el juego más manejable
            
        pygame.quit()
        sys.exit()

# Función principal
def main():
    """
    Función principal del juego Snake.
    
    Instrucciones:
    - Usa las teclas WASD o las flechas para mover la serpiente
    - Come la comida roja para crecer y ganar puntos
    - Evita chocar con las paredes o contigo mismo
    - Presiona P para pausar el juego
    - Cuando pierdas, presiona ESPACIO para reiniciar o ESC para salir
    """
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error al ejecutar el juego: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
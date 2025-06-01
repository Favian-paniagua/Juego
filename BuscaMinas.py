import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Constantes
ANCHO = 600
ALTO = 700
FILAS = 16
COLUMNAS = 16
MINAS = 40
TAMAÑO_CELDA = 30
MARGEN = 50

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
GRIS_CLARO = (192, 192, 192)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)

# Estados de celda
OCULTA = 0
REVELADA = 1
MARCADA = 2

class Celda:
    def __init__(self):
        self.tiene_mina = False
        self.estado = OCULTA
        self.minas_adyacentes = 0

class Buscaminas:
    def __init__(self):
        self.tablero = [[Celda() for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.juego_terminado = False
        self.juego_ganado = False
        self.primer_click = True
        self.minas_restantes = MINAS
        self.tiempo_inicio = 0
        
        # Configurar pantalla
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Buscaminas")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 20)
        self.fuente_grande = pygame.font.Font(None, 36)
        
    def colocar_minas(self, fila_segura, col_segura):
        """Coloca minas evitando la posición del primer click"""
        minas_colocadas = 0
        while minas_colocadas < MINAS:
            fila = random.randint(0, FILAS - 1)
            col = random.randint(0, COLUMNAS - 1)
            
            # No colocar mina en la posición segura o si ya hay mina
            if (fila == fila_segura and col == col_segura) or self.tablero[fila][col].tiene_mina:
                continue
                
            self.tablero[fila][col].tiene_mina = True
            minas_colocadas += 1
            
        self.calcular_numeros()
    
    def calcular_numeros(self):
        """Calcula el número de minas adyacentes para cada celda"""
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if not self.tablero[fila][col].tiene_mina:
                    count = 0
                    for df in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if df == 0 and dc == 0:
                                continue
                            nf, nc = fila + df, col + dc
                            if 0 <= nf < FILAS and 0 <= nc < COLUMNAS:
                                if self.tablero[nf][nc].tiene_mina:
                                    count += 1
                    self.tablero[fila][col].minas_adyacentes = count
    
    def revelar_celda(self, fila, col):
        """Revela una celda y aplica lógica del juego"""
        if (fila < 0 or fila >= FILAS or col < 0 or col >= COLUMNAS or 
            self.tablero[fila][col].estado != OCULTA or self.juego_terminado):
            return
        
        # Primer click: colocar minas
        if self.primer_click:
            self.colocar_minas(fila, col)
            self.primer_click = False
            self.tiempo_inicio = pygame.time.get_ticks()
        
        celda = self.tablero[fila][col]
        celda.estado = REVELADA
        
        # Si hay mina, terminar juego
        if celda.tiene_mina:
            self.juego_terminado = True
            self.revelar_todas_minas()
            return
        
        # Si no hay minas adyacentes, revelar celdas vecinas
        if celda.minas_adyacentes == 0:
            for df in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if df == 0 and dc == 0:
                        continue
                    self.revelar_celda(fila + df, col + dc)
        
        # Verificar si ganó
        self.verificar_victoria()
    
    def marcar_celda(self, fila, col):
        """Marca/desmarca una celda con bandera"""
        if (fila < 0 or fila >= FILAS or col < 0 or col >= COLUMNAS or 
            self.tablero[fila][col].estado == REVELADA or self.juego_terminado):
            return
        
        celda = self.tablero[fila][col]
        if celda.estado == OCULTA:
            celda.estado = MARCADA
            self.minas_restantes -= 1
        elif celda.estado == MARCADA:
            celda.estado = OCULTA
            self.minas_restantes += 1
    
    def revelar_todas_minas(self):
        """Revela todas las minas al terminar el juego"""
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if self.tablero[fila][col].tiene_mina:
                    self.tablero[fila][col].estado = REVELADA
    
    def verificar_victoria(self):
        """Verifica si el jugador ganó"""
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                celda = self.tablero[fila][col]
                if not celda.tiene_mina and celda.estado != REVELADA:
                    return
        self.juego_ganado = True
        self.juego_terminado = True
    
    def obtener_coordenadas_celda(self, pos):
        """Convierte coordenadas de mouse a coordenadas de celda"""
        x, y = pos
        col = (x - MARGEN) // TAMAÑO_CELDA
        fila = (y - MARGEN - 50) // TAMAÑO_CELDA
        return fila, col
    
    def dibujar(self):
        """Dibuja el juego completo"""
        self.pantalla.fill(GRIS_CLARO)
        
        # Dibujar información superior
        tiempo = 0 if self.primer_click else (pygame.time.get_ticks() - self.tiempo_inicio) // 1000
        texto_tiempo = self.fuente_grande.render(f"Tiempo: {tiempo}", True, NEGRO)
        texto_minas = self.fuente_grande.render(f"Minas: {self.minas_restantes}", True, NEGRO)
        
        self.pantalla.blit(texto_tiempo, (MARGEN, 10))
        self.pantalla.blit(texto_minas, (ANCHO - 150, 10))
        
        # Dibujar tablero
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                x = MARGEN + col * TAMAÑO_CELDA
                y = MARGEN + 50 + fila * TAMAÑO_CELDA
                celda = self.tablero[fila][col]
                
                # Dibujar fondo de celda
                if celda.estado == REVELADA:
                    if celda.tiene_mina:
                        color = ROJO
                    else:
                        color = BLANCO
                else:
                    color = GRIS
                
                pygame.draw.rect(self.pantalla, color, (x, y, TAMAÑO_CELDA, TAMAÑO_CELDA))
                pygame.draw.rect(self.pantalla, NEGRO, (x, y, TAMAÑO_CELDA, TAMAÑO_CELDA), 1)
                
                # Dibujar contenido de celda
                if celda.estado == REVELADA:
                    if celda.tiene_mina:
                        # Dibujar mina
                        centro = (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2)
                        pygame.draw.circle(self.pantalla, NEGRO, centro, 8)
                    elif celda.minas_adyacentes > 0:
                        # Dibujar número
                        colores_numeros = [NEGRO, AZUL, VERDE, ROJO, (128, 0, 128), 
                                         (128, 0, 0), (0, 128, 128), NEGRO, GRIS]
                        color_numero = colores_numeros[celda.minas_adyacentes]
                        texto = self.fuente.render(str(celda.minas_adyacentes), True, color_numero)
                        texto_rect = texto.get_rect(center=(x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2))
                        self.pantalla.blit(texto, texto_rect)
                elif celda.estado == MARCADA:
                    # Dibujar bandera
                    pygame.draw.polygon(self.pantalla, ROJO, 
                                      [(x + 5, y + 5), (x + 20, y + 10), (x + 5, y + 15)])
                    pygame.draw.line(self.pantalla, NEGRO, 
                                   (x + 5, y + 5), (x + 5, y + 25), 2)
        
        # Mensaje de fin de juego
        if self.juego_terminado:
            mensaje = "¡GANASTE!" if self.juego_ganado else "¡PERDISTE!"
            color = VERDE if self.juego_ganado else ROJO
            texto = self.fuente_grande.render(mensaje, True, color)
            texto_rect = texto.get_rect(center=(ANCHO // 2, ALTO - 50))
            self.pantalla.blit(texto, texto_rect)
            
            instruccion = self.fuente.render("Presiona R para reiniciar", True, NEGRO)
            inst_rect = instruccion.get_rect(center=(ANCHO // 2, ALTO - 20))
            self.pantalla.blit(instruccion, inst_rect)
        
        pygame.display.flip()
    
    def reiniciar(self):
        """Reinicia el juego"""
        self.__init__()
    
    def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        self.reiniciar()
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if not self.juego_terminado:
                        fila, col = self.obtener_coordenadas_celda(evento.pos)
                        if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                            if evento.button == 1:  # Click izquierdo
                                self.revelar_celda(fila, col)
                            elif evento.button == 3:  # Click derecho
                                self.marcar_celda(fila, col)
            
            self.dibujar()
            self.reloj.tick(60)
        
        pygame.quit()
        sys.exit()

# Ejecutar el juego
if __name__ == "__main__":
    juego = Buscaminas()
    juego.ejecutar()

import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math
from typing import List, Tuple

# Initialize Pygame and OpenGL
pygame.init()
glutInit()
display = (1024, 768)
pygame.display.set_mode(display, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("CYBER TYPER 3000")

# Initialize OpenGL settings
glViewport(0, 0, display[0], display[1])
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, display[0], display[1], 0, -1, 1)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Enhanced Color Palette
COLORS = {
    'background': (0.05, 0.05, 0.15),  # Deep blue background
    'grid': (0.1, 0.1, 0.2),          # Slightly lighter blue for grid
    'neon_blue': (0.0, 0.8, 1.0),     # Bright cyan
    'neon_pink': (1.0, 0.2, 0.8),     # Hot pink
    'neon_purple': (0.8, 0.2, 1.0),   # Bright purple
    'neon_green': (0.2, 1.0, 0.5),    # Bright green
    'neon_yellow': (1.0, 0.8, 0.0),   # Bright yellow
    'success': (0.0, 1.0, 0.5),       # Bright success green
    'danger': (1.0, 0.2, 0.2),        # Bright red
    'white': (1.0, 1.0, 1.0),         # Pure white
    'gold': (1.0, 0.84, 0.0),         # Gold for special effects
    'text_primary': (1.0, 1.0, 1.0),  # Adding the missing color
}

class BackgroundEffect:
    def __init__(self):
        self.grid_size = 50
        self.time = 0
        self.grid_points: List[Tuple[float, float]] = []
        self.generate_grid()
        
    def generate_grid(self):
        for x in range(0, display[0] + self.grid_size, self.grid_size):
            for y in range(0, display[1] + self.grid_size, self.grid_size):
                self.grid_points.append((x, y))

    def draw(self):
        self.time += 0.01
        
        # Draw moving grid
        glLineWidth(1.0)
        glColor4f(*COLORS['grid'], 0.3)
        
        # Vertical lines
        for x in range(0, display[0] + self.grid_size, self.grid_size):
            offset = math.sin(self.time + x * 0.01) * 5
            glBegin(GL_LINES)
            glVertex2f(x, 0)
            glVertex2f(x + offset, display[1])
            glEnd()

        # Horizontal lines
        for y in range(0, display[1] + self.grid_size, self.grid_size):
            offset = math.cos(self.time + y * 0.01) * 5
            glBegin(GL_LINES)
            glVertex2f(0, y)
            glVertex2f(display[0], y + offset)
            glEnd()

        # Draw grid points with glow effect
        for x, y in self.grid_points:
            glow = (math.sin(self.time + x * 0.05 + y * 0.05) + 1) * 0.5
            self.draw_glow_point(x, y, glow)

    def draw_glow_point(self, x, y, intensity):
        sizes = [4, 3, 2, 1]
        alphas = [0.1, 0.2, 0.3, 0.5]
        
        for size, alpha in zip(sizes, alphas):
            glColor4f(*COLORS['neon_blue'], alpha * intensity)
            glBegin(GL_QUADS)
            glVertex2f(x - size, y - size)
            glVertex2f(x + size, y - size)
            glVertex2f(x + size, y + size)
            glVertex2f(x - size, y + size)
            glEnd()

class Particle:
    def __init__(self, x, y, color, velocity=(-2, -2)):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.size = random.uniform(2, 6)
        self.rotation = random.uniform(0, 360)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= self.decay
        self.rotation += 5
        return self.life > 0

    def draw(self):
        if self.life <= 0:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        
        glColor4f(*self.color, self.life)
        size = self.size * self.life
        
        glBegin(GL_QUADS)
        glVertex2f(-size, -size)
        glVertex2f(size, -size)
        glVertex2f(size, size)
        glVertex2f(-size, size)
        glEnd()
        
        glPopMatrix()

class Letter:
    def __init__(self, char, x):
        self.char = char
        self.x = x
        self.y = 0
        self.base_speed = 1.5
        self.speed = self.base_speed
        self.active = True
        self.scale = 1.0
        self.color = self.get_random_neon_color()
        self.particles = []
        self.pulse = 0
        self.glow_intensity = 1.0
        
    def get_random_neon_color(self):
        neon_colors = [COLORS['neon_blue'], COLORS['neon_pink'], 
                      COLORS['neon_purple'], COLORS['neon_green']]
        return random.choice(neon_colors)

    def update(self, delta_time):
        self.y += self.speed * delta_time * 60
        self.pulse = (math.sin(time.time() * 5) * 0.1) + 1
        self.glow_intensity = (math.sin(time.time() * 3) * 0.3) + 0.7
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]

    def draw(self):
        if not self.active:
            return

        # Draw glow effect
        self.draw_glow()
        
        # Draw the letter
        glColor4f(*self.color, 1.0)
        scale = self.pulse * self.scale
        x = self.x + math.sin(time.time() * 2) * 2
        y = self.y
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(scale, scale, 1.0)
        glRasterPos2f(0, 0)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(self.char))
        glPopMatrix()

        # Draw particles
        for particle in self.particles:
            particle.draw()

    def draw_glow(self):
        glow_sizes = [20, 15, 10, 5]
        glow_alphas = [0.1, 0.2, 0.3, 0.4]
        
        for size, alpha in zip(glow_sizes, glow_alphas):
            glColor4f(*self.color, alpha * self.glow_intensity)
            glBegin(GL_QUADS)
            glVertex2f(self.x - size, self.y - size)
            glVertex2f(self.x + size, self.y - size)
            glVertex2f(self.x + size, self.y + size)
            glVertex2f(self.x - size, self.y + size)
            glEnd()

    def add_hit_effect(self):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(self.x, self.y, self.color, velocity))

class Game:
    def __init__(self):
        self.background = BackgroundEffect()
        self.letters = []
        self.score = 0
        self.lives = 5
        self.wpm = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.start_time = time.time()
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = 2000
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.experience = 0
        self.particles = []
        self.screen_shake = 0
        self.difficulty_multiplier = 1.0
        self.last_update = time.time()
        self.power_up_active = False
        self.power_up_timer = 0
        self.score_multiplier = 1

    def spawn_letter(self):
        char = chr(random.randint(97, 122))
        x = random.randint(100, display[0] - 100)
        self.letters.append(Letter(char, x))

    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Update background
        self.background.time += delta_time

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= delta_time * 10

        # Update power-up
        if self.power_up_active:
            self.power_up_timer -= delta_time
            if self.power_up_timer <= 0:
                self.power_up_active = False
                self.score_multiplier = 1

        # Spawn new letters
        current_ticks = pygame.time.get_ticks()
        if current_ticks - self.spawn_timer > self.spawn_interval:
            self.spawn_letter()
            self.spawn_timer = current_ticks
            self.spawn_interval = max(500, 2000 - (self.level * 100))

        # Update letters and particles
        for letter in self.letters:
            letter.update(delta_time)
            if letter.active and letter.y > display[1]:
                letter.active = False
                self.lives -= 1
                self.combo = 0
                self.add_screen_shake(0.5)

        # Remove inactive letters
        self.letters = [l for l in self.letters if l.active]

        # Update WPM
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.wpm = int((self.correct_chars / 5) / (elapsed_time / 60))

        # Level up system
        level_threshold = self.level * 100
        if self.experience >= level_threshold:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.difficulty_multiplier += 0.1
        self.add_screen_shake(1.0)
        # Add level up particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(display[0]/2, display[1]/2, COLORS['warning'], velocity))

    def add_screen_shake(self, intensity):
        self.screen_shake = intensity

    def handle_input(self, char):
        for letter in self.letters:
            if letter.active and letter.char == char:
                letter.active = False
                self.score += 10 * (1 + self.combo / 10) * self.score_multiplier
                self.correct_chars += 1
                self.total_chars += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.experience += 10
                letter.add_hit_effect()
                return
        # Wrong key pressed
        self.total_chars += 1
        self.combo = 0
        self.add_screen_shake(0.3)

    def draw(self):
        glClearColor(*COLORS['background'], 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw background effect
        self.background.draw()

        # Apply screen shake
        if self.screen_shake > 0:
            shake_offset_x = random.uniform(-5, 5) * self.screen_shake
            shake_offset_y = random.uniform(-5, 5) * self.screen_shake
            glTranslatef(shake_offset_x, shake_offset_y, 0)

        # Draw letters
        for letter in self.letters:
            letter.draw()

        # Draw HUD with enhanced visuals
        self.draw_enhanced_hud()

    def draw_enhanced_hud(self):
        # Draw score with glow effect
        score_color = COLORS['neon_green'] if self.power_up_active else COLORS['neon_blue']
        self.draw_glowing_text(f"Score: {int(self.score)}", 20, 30, score_color, 1.2)
        
        # Draw lives with animated hearts
        for i in range(self.lives):
            self.draw_animated_heart(20 + i * 30, 70)

        # Draw level and experience bar with glow
        self.draw_glowing_text(f"Level {self.level}", 20, 100, COLORS['neon_yellow'], 1.0)
        self.draw_glowing_exp_bar(20, 120, 200, 10)

        # Draw combo with dynamic scaling and color
        if self.combo > 0:
            combo_color = self.get_combo_color()
            scale = 1 + min(self.combo/50, 0.5)
            self.draw_glowing_text(f"Combo x{self.combo}", 
                                 display[0] - 150, 30, 
                                 combo_color, scale)

        # Draw WPM and accuracy with subtle animation
        stats_y = 150
        self.draw_glowing_text(f"WPM: {self.wpm}", 20, stats_y, 
                              COLORS['neon_purple'], 1.0)
        
        accuracy = (self.correct_chars / self.total_chars * 100) if self.total_chars > 0 else 0
        self.draw_glowing_text(f"Accuracy: {accuracy:.1f}%", 
                              20, stats_y + 30, 
                              COLORS['neon_pink'], 1.0)

        # Draw power-up indicator if active
        if self.power_up_active:
            self.draw_power_up_indicator()

    def draw_glowing_text(self, text, x, y, color, scale=1.0):
        # Draw glow
        glow_intensities = [0.2, 0.15, 0.1, 0.05]
        glow_scales = [1.1, 1.05, 1.02, 1.0]
        
        for intensity, glow_scale in zip(glow_intensities, glow_scales):
            glColor4f(*color, intensity)
            self.draw_text(text, x, y, scale * glow_scale)
        
        # Draw main text
        glColor4f(*color, 1.0)
        self.draw_text(text, x, y, scale)

    def draw_animated_heart(self, x, y):
        pulse = (math.sin(time.time() * 4) * 0.2) + 1
        
        # Draw heart glow
        glow_colors = [(1.0, 0.2, 0.2, 0.1), (1.0, 0.3, 0.3, 0.2)]
        for color, size_mult in zip(glow_colors, [1.5, 1.2]):
            glColor4f(*color)
            self.draw_heart_shape(x, y, 12 * size_mult * pulse)
        
        # Draw main heart
        glColor4f(*COLORS['danger'], 1.0)
        self.draw_heart_shape(x, y, 10 * pulse)

    def draw_heart_shape(self, x, y, size):
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)
        
        for i in range(31):
            angle = i * math.pi * 2 / 30
            if angle < math.pi:
                px = x + math.sin(angle) * size
                py = y - math.cos(angle) * size
            else:
                px = x + math.sin(angle) * size
                py = y - math.cos(angle) * size
            glVertex2f(px, py)
        
        glEnd()

    def draw_glowing_exp_bar(self, x, y, width, height):
        # Draw background with glow
        glColor4f(*COLORS['grid'], 0.3)
        self.draw_rectangle_with_glow(x, y, width, height)

        # Draw progress with glow
        progress = min(self.experience / (self.level * 100), 1.0)
        color = COLORS['neon_yellow']
        glColor4f(*color, 0.8)
        self.draw_rectangle_with_glow(x, y, width * progress, height)

    def draw_rectangle_with_glow(self, x, y, width, height):
        glow_sizes = [3, 2, 1]
        for glow_size in glow_sizes:
            glBegin(GL_QUADS)
            glVertex2f(x - glow_size, y - glow_size)
            glVertex2f(x + width + glow_size, y - glow_size)
            glVertex2f(x + width + glow_size, y + height + glow_size)
            glVertex2f(x - glow_size, y + height + glow_size)
            glEnd()

    def draw_power_up_indicator(self):
        x = display[0] - 200
        y = 100
        pulse = (math.sin(time.time() * 8) * 0.3) + 1
        
        glColor4f(*COLORS['neon_green'], 0.8 * pulse)
        self.draw_text(f"POWER UP! x{self.score_multiplier}", x, y, 1.2)
        
        # Draw timer bar
        width = 150 * (self.power_up_timer / 10)  # 10 seconds total duration
        height = 5
        self.draw_rectangle_with_glow(x, y + 20, width, height)

    def draw_text(self, text, x, y, scale=1.0):
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(scale, scale, 1.0)
        glRasterPos2f(0, 0)
        for char in str(text):
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glPopMatrix()

    def get_combo_color(self):
        if self.combo >= 50:
            return COLORS['neon_green']
        elif self.combo >= 30:
            return COLORS['neon_yellow']
        elif self.combo >= 10:
            return COLORS['neon_blue']
        return COLORS['white']

    def draw_game_over(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw particles
        for particle in self.particles:
            particle.draw()

        # Game Over title
        glColor4f(*COLORS['danger'], 1.0)
        self.draw_text("GAME OVER", display[0]/2 - 100, display[1]/2 - 50, scale=2.0)

        # Stats
        glColor4f(*COLORS['text_primary'], 1.0)
        stats = [
            f"Final Score: {int(self.score)}",
            f"Max Level: {self.level}",
            f"Max Combo: {self.max_combo}",
            f"Final WPM: {self.wpm}",
            f"Accuracy: {(self.correct_chars / self.total_chars * 100) if self.total_chars > 0 else 0:.1f}%"
        ]

        for i, stat in enumerate(stats):
            self.draw_text(stat, display[0]/2 - 100, display[1]/2 + 30 * i, scale=1.2)

        # Press any key to restart
        if int(time.time() * 2) % 2:  # Blinking effect
            glColor4f(*COLORS['warning'], 1.0)
            self.draw_text("Press any key to restart", 
                         display[0]/2 - 100, 
                         display[1] - 100)

def main():
    game = Game()
    clock = pygame.time.Clock()

    while True:
        if game.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    game = Game()
            
            game.draw_game_over()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha():
                        game.handle_input(event.unicode.lower())

            game.update()
            game.draw()

            if game.lives <= 0:
                game.game_over = True

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 
import pygame
import sys
import random
import math

pygame.init()

# Screen and Grid Configuration lol
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BOARD_COLS = 10
BOARD_ROWS = 10
BOX_SIZE = 50
BOARD_SPACING = 100
TOTAL_BOARD_WIDTH = 2 * (BOARD_COLS * BOX_SIZE) + BOARD_SPACING

# Centering offset
CENTER_OFFSET_X = (SCREEN_WIDTH - TOTAL_BOARD_WIDTH) // 2

# Vibrant Color Palette
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'OCEAN_BLUE': (0, 128, 255),
    'SHIP_GRAY': (128, 128, 128),
    'HIT_RED': (255, 69, 0),
    'MISS_ORANGE': (255, 165, 0),
    'BACKGROUND_NAVY': (25, 25, 112),
    'GRID_LINE': (255, 255, 0),
    'AI_HIDDEN': (0, 191, 255)
}

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Battleship AI Challenge")
font = pygame.font.SysFont(None, 36)

# Load Images
SHIP_IMAGES = {
    'carrier': pygame.image.load("ship1.png"),
    'battleship': pygame.image.load("ship2.png"),
    'cruiser': pygame.image.load("ship3.png"),
    'submarine': pygame.image.load("ship4.png"),
    'destroyer': pygame.image.load("ship5.png")
}

# Scale images to fit the grid
for key in SHIP_IMAGES:
    SHIP_IMAGES[key] = pygame.transform.scale(SHIP_IMAGES[key], (BOX_SIZE, BOX_SIZE))

class SmartAI:
    def __init__(self, board_size):
        self.board_size = board_size
        self.last_hit = None
        self.hunt_mode = True
        self.direction = None
        self.ship_segments = []
        self.remaining_ships = [5, 4, 3, 3, 2]

    def choose_target(self, player_board):
        if not self.hunt_mode and self.last_hit:
            return self._target_mode(player_board)
        return self._hunt_mode(player_board)

    def _hunt_mode(self, player_board):
        # Checkerboard hunting strategy
        candidates = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if ((x + y) % 2 == 0) and player_board[x][y] in ['', *list(SHIP_IMAGES.keys())]:
                    candidates.append((x, y))
        
        return random.choice(candidates) if candidates else self._random_target(player_board)

    def _target_mode(self, player_board):
        # Prioritize cells around the last hit
        x, y = self.last_hit
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        if self.direction:
            # Continue in the known direction if possible
            dx, dy = self.direction
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
                player_board[nx][ny] in ['', *list(SHIP_IMAGES.keys())]):
                return (nx, ny)

        # Check around the last hit
        valid_targets = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
                player_board[nx][ny] in ['', *list(SHIP_IMAGES.keys())]):
                valid_targets.append((nx, ny))
        
        return random.choice(valid_targets) if valid_targets else self._hunt_mode(player_board)

    def _random_target(self, player_board):
        # Fallback method to find an untargeted cell
        untargeted = [(x, y) for x in range(self.board_size) 
                      for y in range(self.board_size) 
                      if player_board[x][y] in ['', *list(SHIP_IMAGES.keys())]]
        return random.choice(untargeted)

    def update_targeting(self, x, y, is_hit):
        if is_hit:
            self.hunt_mode = False
            self.last_hit = (x, y)
            self.ship_segments.append((x, y))
            
            # Try to determine ship direction
            if len(self.ship_segments) > 1:
                first = self.ship_segments[0]
                second = self.ship_segments[1]
                self.direction = (second[0] - first[0], second[1] - first[1])
        else:
            # If miss, potentially adjust hunting strategy
            if not self.hunt_mode and len(self.ship_segments) > 1:
                # Reset if multiple misses occur
                if random.random() < 0.3:
                    self.hunt_mode = True
                    self.direction = None
                    self.ship_segments = []

class BattleshipBoard:
    def __init__(self, is_player=True):
        self.board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.ships_placed = []  # Store ship placement details
        self.ships = [
            {'name': 'carrier', 'length': 5},
            {'name': 'battleship', 'length': 4},
            {'name': 'cruiser', 'length': 3},
            {'name': 'submarine', 'length': 3},
            {'name': 'destroyer', 'length': 2}
        ]
        self.is_player = is_player
        self.place_ships()

    def place_ships(self):
        for ship in self.ships:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice(['H', 'V'])
                x = random.randint(0, BOARD_ROWS - 1)
                y = random.randint(0, BOARD_COLS - 1)

                if self.can_place_ship(ship, (x, y), direction):
                    self.place_ship(ship, (x, y), direction)
                    placed = True
                
                attempts += 1

            if not placed:
                raise ValueError(f"Could not place ship {ship['name']}")

    def can_place_ship(self, ship, start, direction):
        x, y = start
        ship_length = ship['length']

        if direction == 'H':
            if y + ship_length > BOARD_COLS:
                return False
            return all(self.board[x][y + i] == '' for i in range(ship_length))
        else:  # Vertical
            if x + ship_length > BOARD_ROWS:
                return False
            return all(self.board[x + i][y] == '' for i in range(ship_length))

    def place_ship(self, ship, start, direction):
        x, y = start
        for i in range(ship['length']):
            if direction == 'H':
                self.board[x][y + i] = ship['name']
            else:  # Vertical
                self.board[x + i][y] = ship['name']
        
        # Store ship placement details for drawing
        self.ships_placed.append({
            'name': ship['name'], 
            'start': start, 
            'direction': direction, 
            'length': ship['length']
        })

    def draw(self, x_offset):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                cell_x = x_offset + col * BOX_SIZE
                cell_y = (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2 + row * BOX_SIZE

                cell_value = self.board[row][col]
                if self.is_player:
                    if cell_value in SHIP_IMAGES:
                        # Skip drawing individual cell ships, we'll draw full ships later
                        pass
                    elif cell_value == 'H':
                        pygame.draw.rect(screen, COLORS['HIT_RED'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                    elif cell_value == 'M':
                        pygame.draw.rect(screen, COLORS['MISS_ORANGE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                    else:
                        pygame.draw.rect(screen, COLORS['OCEAN_BLUE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                else:
                    if cell_value == 'H':
                        pygame.draw.rect(screen, COLORS['HIT_RED'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                    elif cell_value == 'M':
                        pygame.draw.rect(screen, COLORS['MISS_ORANGE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))
                    else:
                        pygame.draw.rect(screen, COLORS['AI_HIDDEN'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE))

                pygame.draw.rect(screen, COLORS['GRID_LINE'], (cell_x, cell_y, BOX_SIZE, BOX_SIZE), 2)

        # Draw ships as full images
        if self.is_player:
            for ship in self.ships_placed:
                name = ship['name']
                x, y = ship['start']
                direction = ship['direction']
                length = ship['length']

                # Prepare the ship image
                ship_image = SHIP_IMAGES[name].copy()
                
                # Resize the image to span the entire ship length
                if direction == 'H':
                    ship_image = pygame.transform.scale(ship_image, (length * BOX_SIZE, BOX_SIZE))
                else:  # Vertical
                    ship_image = pygame.transform.rotate(ship_image, 90)
                    ship_image = pygame.transform.scale(ship_image, (BOX_SIZE, length * BOX_SIZE))

                # Calculate the drawing position
                ship_x = x_offset + y * BOX_SIZE
                ship_y = (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2 + x * BOX_SIZE

                # Draw the ship image
                screen.blit(ship_image, (ship_x, ship_y))
class BattleshipGame:
    def __init__(self):
        self.player_board = BattleshipBoard(is_player=True)
        self.ai_board = BattleshipBoard(is_player=False)
        self.smart_ai = SmartAI(BOARD_ROWS)
        self.player_turn = True
        self.game_over = False
        self.turn_count = 0

    def handle_click(self, mouse_pos):
        x, y = mouse_pos
        ai_board_x_offset = CENTER_OFFSET_X + BOARD_COLS * BOX_SIZE + BOARD_SPACING

        # Check if click is on AI's board
        if ai_board_x_offset <= x < ai_board_x_offset + BOARD_COLS * BOX_SIZE:
            col = (x - ai_board_x_offset) // BOX_SIZE
            row = (y - (SCREEN_HEIGHT - (BOARD_ROWS * BOX_SIZE)) // 2) // BOX_SIZE

            if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
                if self.ai_board.board[row][col] in SHIP_IMAGES:
                    self.ai_board.board[row][col] = 'H'
                    print(f"Player hit at {row}, {col}")
                elif self.ai_board.board[row][col] == '':
                    self.ai_board.board[row][col] = 'M'
                    print(f"Player missed at {row}, {col}")

                self.player_turn = False

    def ai_turn(self):
        # Intelligent target selection
        row, col = self.smart_ai.choose_target(self.player_board.board)

        if self.player_board.board[row][col] in SHIP_IMAGES:
            self.player_board.board[row][col] = 'H'
            print(f"AI hit at {row}, {col}")
            self.smart_ai.update_targeting(row, col, True)
        else:
            self.player_board.board[row][col] = 'M'
            print(f"AI missed at {row}, {col}")
            self.smart_ai.update_targeting(row, col, False)

        self.player_turn = True
        self.turn_count += 1

    def check_game_over(self):
        # Check if all ships are sunk
        def are_ships_sunk(board):
            return all(all(cell not in SHIP_IMAGES for cell in row) for row in board.board)

        if are_ships_sunk(self.ai_board):
            print(f"Player Wins in {self.turn_count} turns!")
            self.game_over = True
        elif are_ships_sunk(self.player_board):
            print(f"AI Wins in {self.turn_count} turns!")
            self.game_over = True

    def run(self):
        clock = pygame.time.Clock()

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn:
                    self.handle_click(pygame.mouse.get_pos())
                    self.check_game_over()

            if not self.player_turn:
                self.ai_turn()
                self.check_game_over()

            screen.fill(COLORS['BACKGROUND_NAVY'])
            
            # Draw boards
            self.player_board.draw(CENTER_OFFSET_X)
            self.ai_board.draw(CENTER_OFFSET_X + BOARD_COLS * BOX_SIZE + BOARD_SPACING)

            pygame.display.flip()
            clock.tick(5)  # Slow down AI turns for visibility

        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

def main():
    game = BattleshipGame()
    game.run()

if __name__ == "__main__":
    main()

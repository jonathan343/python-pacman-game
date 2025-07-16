"""
Demo script to test GameStateManager functionality with basic game loop.
"""

import pygame
import sys
from pacman_game.game_state_manager import GameStateManager
from pacman_game.models import GameState
from pacman_game.config import GameConfig


def main():
    """Main demo function to test GameStateManager."""
    # Initialize Pygame
    pygame.init()
    
    # Create game configuration
    config = GameConfig()
    
    # Create screen
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Pacman Game State Demo")
    
    # Create clock for frame rate control
    clock = pygame.time.Clock()
    
    # Create game state manager
    state_manager = GameStateManager(screen, config)
    
    # Game state variables
    running = True
    demo_score = 0
    demo_level = 1
    
    # Set up callbacks
    def start_game():
        print("Starting new game...")
        nonlocal demo_score, demo_level
        demo_score = 0
        demo_level = 1
    
    def restart_game():
        print("Restarting game...")
        nonlocal demo_score, demo_level
        demo_score = 0
        demo_level = 1
    
    def quit_game():
        print("Quitting game...")
        nonlocal running
        running = False
    
    state_manager.set_callbacks(
        on_start_game=start_game,
        on_restart_game=restart_game,
        on_quit_game=quit_game
    )
    
    print("Game State Manager Demo")
    print("Controls:")
    print("- Menu: UP/DOWN arrows to navigate, ENTER to select")
    print("- Playing: ESC or P to pause, G to trigger game over")
    print("- Paused: ESC or P to resume, M for main menu")
    print("- Game Over: UP/DOWN arrows to navigate, ENTER to select")
    print("- Close window or select Quit to exit")
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Let state manager handle input
                state_manager.handle_input(event)
                
                # Demo-specific input handling
                if state_manager.is_playing() and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:  # Trigger game over for demo
                        print("Demo: Triggering game over...")
                        demo_score = 1500  # Demo final score
                        demo_level = 3     # Demo final level
                        state_manager.set_game_over_data(demo_score, demo_level)
                        state_manager.set_state(GameState.GAME_OVER)
                    elif event.key == pygame.K_s:  # Simulate score increase
                        demo_score += 100
                        print(f"Demo: Score increased to {demo_score}")
        
        # Update game logic (only when playing)
        if state_manager.should_update_game():
            # Demo game logic would go here
            pass
        
        # Render
        if state_manager.should_render_game():
            # Clear screen for game rendering
            screen.fill(config.BLACK)
            
            # Demo game rendering
            if state_manager.is_playing():
                # Render demo game state
                font = pygame.font.Font(None, 36)
                
                # Show current state info
                state_text = font.render("PLAYING STATE", True, config.YELLOW)
                screen.blit(state_text, (50, 50))
                
                score_text = font.render(f"Score: {demo_score}", True, config.WHITE)
                screen.blit(score_text, (50, 100))
                
                level_text = font.render(f"Level: {demo_level}", True, config.WHITE)
                screen.blit(level_text, (50, 150))
                
                # Instructions
                instructions = [
                    "Press G to trigger Game Over",
                    "Press S to increase score",
                    "Press ESC or P to pause"
                ]
                
                small_font = pygame.font.Font(None, 24)
                for i, instruction in enumerate(instructions):
                    instruction_text = small_font.render(instruction, True, config.WHITE)
                    screen.blit(instruction_text, (50, 250 + i * 30))
        
        # Always render state manager screens (menu, game over, pause)
        state_manager.render()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(config.FPS)
    
    # Cleanup
    pygame.quit()
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()
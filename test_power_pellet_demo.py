#!/usr/bin/env python3
"""
Demonstration of power pellet mechanics and ghost interactions.
"""

from pacman_game.models import Position, Maze, Ghost, ScoreManager, PowerPelletManager, GhostMode, GhostPersonality


def main():
    """Demonstrate power pellet mechanics."""
    print("=== Power Pellet Mechanics Demo ===\n")
    
    # Initialize components
    maze = Maze(tile_size=20)
    score_manager = ScoreManager()
    power_manager = PowerPelletManager()
    
    # Create some ghosts
    ghosts = [
        Ghost(Position(100, 100), maze, GhostPersonality.BLINKY),
        Ghost(Position(120, 100), maze, GhostPersonality.PINKY),
        Ghost(Position(140, 100), maze, GhostPersonality.INKY),
        Ghost(Position(160, 100), maze, GhostPersonality.SUE)
    ]
    
    print("Initial state:")
    print(f"Score: {score_manager.get_score()}")
    print(f"Ghost modes: {[ghost.mode.value for ghost in ghosts]}")
    print()
    
    # Simulate collecting a power pellet
    print("1. Collecting power pellet...")
    pellet_points = score_manager.collect_power_pellet()
    power_manager.activate_power_mode(ghosts)
    
    print(f"Power pellet points: {pellet_points}")
    print(f"Score: {score_manager.get_score()}")
    print(f"Ghost modes: {[ghost.mode.value for ghost in ghosts]}")
    print(f"Power mode active: {power_manager.is_power_mode_active()}")
    print(f"Remaining time: {power_manager.get_remaining_seconds():.1f} seconds")
    print()
    
    # Simulate eating ghosts with point progression
    print("2. Eating ghosts in sequence...")
    for i, ghost in enumerate(ghosts):
        points = power_manager.eat_ghost(ghost, score_manager)
        print(f"Ghost {i+1}: {points} points (Total: {score_manager.get_score()})")
        print(f"Ghost mode: {ghost.mode.value}")
    print()
    
    # Simulate time passing
    print("3. Simulating time passage...")
    for seconds in range(1, 11):
        # Update 60 times (1 second at 60 FPS)
        for _ in range(60):
            still_active = power_manager.update()
        
        if seconds % 2 == 0:  # Print every 2 seconds
            print(f"After {seconds} seconds - Power mode active: {still_active}")
            if still_active:
                print(f"Remaining time: {power_manager.get_remaining_seconds():.1f} seconds")
    
    print()
    print("4. Final state:")
    print(f"Final score: {score_manager.get_score()}")
    print(f"Ghost modes: {[ghost.mode.value for ghost in ghosts]}")
    print(f"Power mode active: {power_manager.is_power_mode_active()}")
    print()
    
    # Demonstrate collision detection
    print("5. Collision detection demo...")
    player_pos = Position(100, 100)  # Same as first ghost
    
    # Reset ghosts to normal mode
    for ghost in ghosts:
        ghost.set_mode(GhostMode.NORMAL)
    
    print("Player collides with normal ghost:")
    player_died, points = power_manager.check_ghost_collision(
        player_pos, ghosts, score_manager
    )
    print(f"Player died: {player_died}, Points earned: {points}")
    
    # Activate power mode and try again
    power_manager.activate_power_mode(ghosts)
    print("\nPlayer collides with frightened ghost:")
    player_died, points = power_manager.check_ghost_collision(
        player_pos, ghosts, score_manager
    )
    print(f"Player died: {player_died}, Points earned: {points}")
    print(f"Final score: {score_manager.get_score()}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
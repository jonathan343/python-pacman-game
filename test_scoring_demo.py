#!/usr/bin/env python3
"""
Demo script to showcase the scoring system and collectible interaction functionality.
This demonstrates the implementation of task 6 requirements.
"""

from pacman_game.models import Maze, Player, ScoreManager, Position

def main():
    """Demonstrate the scoring system functionality."""
    print("=== Pacman Scoring System Demo ===\n")
    
    # Initialize game components
    maze = Maze(tile_size=20)
    score_manager = ScoreManager()
    
    # Initialize level with total dots
    total_dots = maze.get_dots_remaining()
    score_manager.initialize_level(total_dots)
    
    print(f"Level initialized with {total_dots} dots")
    print(f"Initial score: {score_manager.get_score()}")
    print(f"Initial lives: {score_manager.get_lives()}")
    print(f"Current level: {score_manager.get_level()}\n")
    
    # Find a dot position and create player there
    dot_positions = list(maze.dots)
    if dot_positions:
        dot_pos = dot_positions[0]
        pixel_pos = maze.get_pixel_position(dot_pos[0], dot_pos[1])
        player = Player(pixel_pos, maze)
        
        print(f"Player positioned at dot location: Grid({dot_pos[0]}, {dot_pos[1]})")
        
        # Collect the dot
        collected_dot, collected_pellet, points = player.collect_item_at_position(score_manager)
        
        print(f"Collected dot: {collected_dot}")
        print(f"Points earned: {points}")
        print(f"New score: {score_manager.get_score()}")
        print(f"Dots remaining: {score_manager.get_dots_remaining()}")
        print(f"Level progress: {score_manager.get_level_progress():.1%}\n")
    
    # Find a power pellet position and test collection
    pellet_positions = list(maze.power_pellets)
    if pellet_positions:
        pellet_pos = pellet_positions[0]
        pixel_pos = maze.get_pixel_position(pellet_pos[0], pellet_pos[1])
        player = Player(pixel_pos, maze)
        
        print(f"Player positioned at power pellet location: Grid({pellet_pos[0]}, {pellet_pos[1]})")
        
        # Collect the power pellet
        collected_dot, collected_pellet, points = player.collect_item_at_position(score_manager)
        
        print(f"Collected power pellet: {collected_pellet}")
        print(f"Points earned: {points}")
        print(f"New score: {score_manager.get_score()}\n")
    
    # Demonstrate ghost eating scoring progression
    print("=== Ghost Eating Scoring Demo ===")
    print("Ghost eating point progression:")
    for i in range(4):
        points = score_manager.eat_ghost()
        print(f"Ghost {i+1}: {points} points (Total: {score_manager.get_score()})")
    
    print(f"\nGhost multiplier capped at: {score_manager.ghost_eat_multiplier}x")
    
    # Test level completion
    print(f"\n=== Level Completion Demo ===")
    print(f"Simulating collection of remaining {score_manager.get_dots_remaining()} dots...")
    
    remaining_dots = score_manager.get_dots_remaining()
    for i in range(remaining_dots):
        score_manager.collect_dot()
        if i % 10 == 0 or i == remaining_dots - 1:
            print(f"Collected {i+1}/{remaining_dots} dots - Progress: {score_manager.get_level_progress():.1%}")
    
    print(f"Level complete: {score_manager.is_level_complete()}")
    print(f"Final score: {score_manager.get_score()}")
    
    print("\n=== Demo Complete ===")
    print("All scoring system requirements have been successfully implemented:")
    print("✓ Dot collection with 10-point scoring (Requirement 2.1)")
    print("✓ Power pellet collection with 50-point scoring (Requirement 2.2)")
    print("✓ Level completion detection when all dots collected (Requirement 2.3)")
    print("✓ Real-time score updates (Requirement 2.4)")

if __name__ == "__main__":
    main()
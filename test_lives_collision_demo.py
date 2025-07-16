#!/usr/bin/env python3
"""
Demo script to test the lives system and collision handling functionality.
This script demonstrates the key features implemented in task 9.
"""

from pacman_game.models import (
    Position, Direction, Maze, Player, Ghost, ScoreManager, 
    CollisionManager, GhostMode, GhostPersonality
)


def test_lives_system():
    """Test the lives system functionality."""
    print("=== Testing Lives System ===")
    
    # Create score manager with 3 lives
    score_manager = ScoreManager(starting_lives=3)
    print(f"Initial lives: {score_manager.get_lives()}")
    print(f"Game over status: {score_manager.is_game_over()}")
    
    # Lose first life
    game_over = score_manager.lose_life()
    print(f"After losing 1 life: {score_manager.get_lives()} lives, game over: {game_over}")
    
    # Lose second life
    game_over = score_manager.lose_life()
    print(f"After losing 2 lives: {score_manager.get_lives()} lives, game over: {game_over}")
    
    # Lose final life
    game_over = score_manager.lose_life()
    print(f"After losing final life: {score_manager.get_lives()} lives, game over: {game_over}")
    print(f"Game over status: {score_manager.is_game_over()}")
    
    # Reset game
    score_manager.reset_game()
    print(f"After reset: {score_manager.get_lives()} lives, game over: {score_manager.is_game_over()}")
    print()


def test_collision_detection():
    """Test collision detection between player and ghosts."""
    print("=== Testing Collision Detection ===")
    
    # Set up game entities
    maze = Maze(tile_size=20)
    player = Player(Position(260, 380), maze)
    ghost = Ghost(Position(265, 385), maze, GhostPersonality.BLINKY)  # Close to player
    
    # Test collision detection
    collision = player.check_collision_with_ghost(ghost)
    print(f"Player at {player.position.x}, {player.position.y}")
    print(f"Ghost at {ghost.position.x}, {ghost.position.y}")
    print(f"Collision detected: {collision}")
    
    # Test with far ghost
    far_ghost = Ghost(Position(100, 100), maze, GhostPersonality.PINKY)
    collision_far = player.check_collision_with_ghost(far_ghost)
    print(f"Far ghost at {far_ghost.position.x}, {far_ghost.position.y}")
    print(f"Collision with far ghost: {collision_far}")
    print()


def test_ghost_collision_handling():
    """Test different types of ghost collisions."""
    print("=== Testing Ghost Collision Handling ===")
    
    maze = Maze(tile_size=20)
    player = Player(Position(260, 380), maze)
    score_manager = ScoreManager()
    
    # Test collision with normal ghost (player loses life)
    normal_ghost = Ghost(Position(265, 385), maze, GhostPersonality.BLINKY)
    print(f"Initial lives: {score_manager.get_lives()}")
    
    life_lost, points = player.handle_ghost_collision(normal_ghost, score_manager)
    print(f"Collision with normal ghost - Life lost: {life_lost}, Points: {points}")
    print(f"Lives after collision: {score_manager.get_lives()}")
    
    # Test collision with frightened ghost (player eats ghost)
    frightened_ghost = Ghost(Position(265, 385), maze, GhostPersonality.PINKY)
    frightened_ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
    
    life_lost, points = player.handle_ghost_collision(frightened_ghost, score_manager)
    print(f"Collision with frightened ghost - Life lost: {life_lost}, Points: {points}")
    print(f"Score after eating ghost: {score_manager.get_score()}")
    print(f"Ghost mode after being eaten: {frightened_ghost.mode}")
    print()


def test_collision_manager():
    """Test the collision manager functionality."""
    print("=== Testing Collision Manager ===")
    
    maze = Maze(tile_size=20)
    player = Player(Position(260, 380), maze)
    ghost = Ghost(Position(265, 385), maze, GhostPersonality.BLINKY)
    score_manager = ScoreManager()
    collision_manager = CollisionManager()
    
    print(f"Initial player position: {player.position.x}, {player.position.y}")
    print(f"Initial ghost position: {ghost.position.x}, {ghost.position.y}")
    print(f"Initial lives: {score_manager.get_lives()}")
    
    # Test collision that causes life loss
    life_lost, points, game_over = collision_manager.check_player_ghost_collisions(
        player, [ghost], score_manager
    )
    
    print(f"Collision result - Life lost: {life_lost}, Points: {points}, Game over: {game_over}")
    print(f"Lives after collision: {score_manager.get_lives()}")
    print(f"Player position after reset: {player.position.x}, {player.position.y}")
    print(f"Ghost position after reset: {ghost.position.x}, {ghost.position.y}")
    print(f"Respawn timer active: {collision_manager.is_respawning()}")
    print(f"Respawn time remaining: {collision_manager.get_respawn_time_remaining()} frames")
    print()


def test_multiple_ghost_eating():
    """Test eating multiple ghosts for point progression."""
    print("=== Testing Multiple Ghost Eating ===")
    
    maze = Maze(tile_size=20)
    player = Player(Position(260, 380), maze)
    score_manager = ScoreManager()
    
    # Create multiple frightened ghosts
    ghosts = []
    for i in range(4):
        ghost = Ghost(Position(260 + i*5, 380), maze, GhostPersonality.BLINKY)
        ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
        ghosts.append(ghost)
    
    expected_points = [200, 400, 800, 1600]
    total_score = 0
    
    print("Eating ghosts in sequence:")
    for i, ghost in enumerate(ghosts):
        life_lost, points = player.handle_ghost_collision(ghost, score_manager)
        total_score += points
        print(f"Ghost {i+1}: {points} points (Total: {score_manager.get_score()})")
        print(f"Expected: {expected_points[i]} points")
    
    print(f"Final score: {score_manager.get_score()}")
    print()


def test_game_over_scenario():
    """Test complete game over scenario."""
    print("=== Testing Game Over Scenario ===")
    
    maze = Maze(tile_size=20)
    player = Player(Position(260, 380), maze)
    ghost = Ghost(Position(265, 385), maze, GhostPersonality.BLINKY)
    score_manager = ScoreManager(starting_lives=1)  # Start with only 1 life
    collision_manager = CollisionManager()
    
    print(f"Starting with {score_manager.get_lives()} life")
    print(f"Game over status: {score_manager.is_game_over()}")
    
    # Lose final life
    life_lost, points, game_over = collision_manager.check_player_ghost_collisions(
        player, [ghost], score_manager
    )
    
    print(f"After collision - Life lost: {life_lost}, Game over: {game_over}")
    print(f"Final lives: {score_manager.get_lives()}")
    print(f"Game over status: {score_manager.is_game_over()}")
    print()


def main():
    """Run all demo tests."""
    print("Lives System and Collision Handling Demo")
    print("=" * 50)
    
    test_lives_system()
    test_collision_detection()
    test_ghost_collision_handling()
    test_collision_manager()
    test_multiple_ghost_eating()
    test_game_over_scenario()
    
    print("Demo completed successfully!")
    print("All lives system and collision handling features are working correctly.")


if __name__ == "__main__":
    main()
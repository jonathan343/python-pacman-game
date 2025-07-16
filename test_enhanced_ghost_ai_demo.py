#!/usr/bin/env python3
"""
Demo script to showcase enhanced ghost AI behaviors.
"""

from pacman_game.models import (
    Ghost, GhostPersonality, GhostMode, Position, Direction, Maze, Player
)


def demo_ghost_personalities():
    """Demonstrate different ghost AI personalities."""
    print("=== Enhanced Ghost AI Demo ===\n")
    
    # Create maze and player
    maze = Maze(tile_size=20)
    player_position = Position(100, 100)
    
    # Create ghosts with different personalities
    ghosts = {
        "Blinky": Ghost(Position(200, 200), maze, GhostPersonality.BLINKY, speed=2),
        "Pinky": Ghost(Position(220, 200), maze, GhostPersonality.PINKY, speed=2),
        "Inky": Ghost(Position(240, 200), maze, GhostPersonality.INKY, speed=2),
        "Sue": Ghost(Position(260, 200), maze, GhostPersonality.SUE, speed=2)
    }
    
    print("1. Ghost Personalities and Colors:")
    for name, ghost in ghosts.items():
        print(f"   {name}: {ghost.color} - {ghost.personality.value}")
    
    print("\n2. Chase Mode Behaviors:")
    other_ghosts = list(ghosts.values())
    
    for name, ghost in ghosts.items():
        ghost.set_mode(GhostMode.NORMAL)
        ghost._calculate_chase_target(player_position, other_ghosts)
        print(f"   {name} targets: ({ghost.target_position.x:.1f}, {ghost.target_position.y:.1f})")
    
    print("\n3. Scatter Mode Behaviors:")
    for name, ghost in ghosts.items():
        ghost.set_mode(GhostMode.SCATTER)
        ghost._calculate_scatter_target()
        corner = ghost.scatter_targets[ghost.personality]
        print(f"   {name} scatter corner: ({corner.x}, {corner.y})")
    
    print("\n4. Ghost House Mechanics:")
    for name, ghost in ghosts.items():
        exit_delay = ghost._get_house_exit_delay()
        dot_threshold = ghost._get_dot_threshold_for_exit()
        print(f"   {name}: Exit delay={exit_delay} frames, Dot threshold={dot_threshold}")
    
    print("\n5. Frightened Mode Behavior:")
    blinky = ghosts["Blinky"]
    blinky.position = Position(120, 120)
    blinky.set_mode(GhostMode.FRIGHTENED, duration=600)
    blinky._calculate_flee_target(player_position)
    
    distance_before = player_position.distance_to(Position(120, 120))
    distance_after = player_position.distance_to(blinky.target_position)
    print(f"   Blinky flees from player:")
    print(f"   Distance before: {distance_before:.1f}")
    print(f"   Distance to flee target: {distance_after:.1f}")
    print(f"   Successfully fleeing: {distance_after > distance_before}")


def demo_mode_transitions():
    """Demonstrate ghost mode transitions."""
    print("\n=== Mode Transition Demo ===\n")
    
    maze = Maze(tile_size=20)
    ghost = Ghost(Position(200, 200), maze, GhostPersonality.BLINKY, speed=2)
    
    print("1. Normal to Frightened transition:")
    ghost.direction = Direction.UP
    print(f"   Before: Mode={ghost.mode}, Direction={ghost.direction}")
    
    ghost.set_mode(GhostMode.FRIGHTENED, duration=600)
    print(f"   After: Mode={ghost.mode}, Direction={ghost.direction}")
    print(f"   Direction reversed: {ghost.direction == Direction.DOWN}")
    
    print("\n2. Eaten mode transition:")
    ghost.set_mode(GhostMode.EATEN, duration=180)
    print(f"   Mode: {ghost.mode}")
    print(f"   Target set to house: {ghost.target_position.x == ghost.ghost_house_position.x}")
    
    print("\n3. Timer-based mode expiration:")
    ghost.frightened_timer = 1
    ghost.set_mode(GhostMode.FRIGHTENED, duration=1)
    print(f"   Before update: Mode={ghost.mode}, Timer={ghost.frightened_timer}")
    
    ghost._update_mode_timers()
    print(f"   After update: Mode={ghost.mode}, Timer={ghost.frightened_timer}")


def demo_ai_targeting():
    """Demonstrate advanced AI targeting behaviors."""
    print("\n=== AI Targeting Demo ===\n")
    
    maze = Maze(tile_size=20)
    player_pos = Position(100, 100)
    
    # Create Blinky and Inky to test complex targeting
    blinky = Ghost(Position(200, 150), maze, GhostPersonality.BLINKY, speed=2)
    inky = Ghost(Position(250, 200), maze, GhostPersonality.INKY, speed=2)
    
    print("1. Inky's complex targeting (with Blinky):")
    print(f"   Player position: ({player_pos.x}, {player_pos.y})")
    print(f"   Blinky position: ({blinky.position.x}, {blinky.position.y})")
    
    inky._calculate_chase_target(player_pos, [blinky])
    print(f"   Inky targets: ({inky.target_position.x:.1f}, {inky.target_position.y:.1f})")
    
    print("\n2. Inky's fallback behavior (without Blinky):")
    inky._calculate_chase_target(player_pos, [])  # No Blinky
    print(f"   Inky targets (fallback): ({inky.target_position.x}, {inky.target_position.y})")
    
    print("\n3. Sue's distance-based behavior:")
    sue = Ghost(Position(300, 300), maze, GhostPersonality.SUE, speed=2)
    
    # Test when far from player
    sue._calculate_chase_target(player_pos, [])
    print(f"   Sue (far) targets: ({sue.target_position.x}, {sue.target_position.y})")
    
    # Test when close to player
    sue.position = Position(110, 110)
    sue._calculate_chase_target(player_pos, [])
    scatter_corner = sue.scatter_targets[GhostPersonality.SUE]
    is_scattering = (sue.target_position.x == scatter_corner.x and 
                    sue.target_position.y == scatter_corner.y)
    print(f"   Sue (close) scattering: {is_scattering}")


def demo_house_mechanics():
    """Demonstrate ghost house mechanics."""
    print("\n=== Ghost House Mechanics Demo ===\n")
    
    maze = Maze(tile_size=20)
    house_pos = Position(260, 180)
    
    # Create ghost in house
    inky = Ghost(Position(260, 200), maze, GhostPersonality.INKY, speed=2, 
                ghost_house_position=house_pos)
    
    print("1. House exit based on dots eaten:")
    inky.set_mode(GhostMode.IN_HOUSE)
    print(f"   Inky in house: {inky.mode == GhostMode.IN_HOUSE}")
    
    # Simulate enough dots eaten
    inky._update_house_mechanics(dots_eaten=35)  # Above threshold of 30
    print(f"   After 35 dots eaten: {inky.mode}")
    
    print("\n2. House exit based on timer:")
    sue = Ghost(Position(260, 200), maze, GhostPersonality.SUE, speed=2,
               ghost_house_position=house_pos)
    sue.set_mode(GhostMode.IN_HOUSE)
    sue.house_exit_timer = 0  # Timer expired
    
    sue._update_house_mechanics(dots_eaten=0)  # Below dot threshold
    print(f"   Sue with expired timer: {sue.mode}")
    
    print("\n3. House patrol behavior:")
    inky.set_mode(GhostMode.IN_HOUSE)
    inky.position = Position(house_pos.x, house_pos.y - 20)  # Top of house
    inky._calculate_house_patrol_target()
    
    expected_y = house_pos.y + 20  # Should target bottom
    print(f"   Inky patrol target: ({inky.target_position.x}, {inky.target_position.y})")
    print(f"   Targeting bottom of house: {inky.target_position.y == expected_y}")


if __name__ == "__main__":
    demo_ghost_personalities()
    demo_mode_transitions()
    demo_ai_targeting()
    demo_house_mechanics()
    
    print("\n=== Demo Complete ===")
    print("Enhanced ghost AI features implemented:")
    print("✓ Different AI patterns for each ghost (chase, ambush, patrol)")
    print("✓ Scatter mode behavior for ghosts")
    print("✓ Ghost respawn system after being eaten")
    print("✓ Ghost house mechanics and exit timing")
    print("✓ Comprehensive unit tests for all behaviors")
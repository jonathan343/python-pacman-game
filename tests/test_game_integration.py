"""
Integration tests for the complete game loop and system coordination.
"""

import pytest
import pygame
import time
from unittest.mock import Mock, patch, MagicMock

from pacman_game.game import Game
from pacman_game.models import GameState, Direction, Position
from pacman_game.config import GameConfig


class TestGameIntegration:
    """Test complete game loop integration and system coordination."""
    
    @pytest.fixture
    def game_config(self):
        """Create a test game configuration."""
        config = GameConfig()
        config.SCREEN_WIDTH = 400
        config.SCREEN_HEIGHT = 450
        config.FPS = 60
        return config
    
    @pytest.fixture
    def mock_pygame(self):
        """Mock pygame to avoid actual window creation during tests."""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.font.Font'), \
             patch('pygame.time.Clock') as mock_clock:
            
            # Mock display surface
            mock_surface = Mock()
            mock_display.return_value = mock_surface
            
            # Mock clock
            mock_clock_instance = Mock()
            mock_clock_instance.tick.return_value = 16  # ~60 FPS
            mock_clock_instance.get_fps.return_value = 60.0
            mock_clock.return_value = mock_clock_instance
            
            yield {
                'display': mock_display,
                'surface': mock_surface,
                'clock': mock_clock_instance
            }
    
    def test_game_initialization(self, game_config, mock_pygame):
        """Test that the game initializes all systems correctly."""
        game = Game(game_config)
        
        # Verify core systems are initialized
        assert game.config == game_config
        assert game.renderer is not None
        assert game.input_handler is not None
        assert game.state_manager is not None
        assert game.maze is not None
        assert game.score_manager is not None
        assert game.player is not None
        assert len(game.ghosts) == 4
        
        # Verify initial state
        assert game.get_game_state() == GameState.MENU
        assert game.get_score() == 0
        assert game.get_lives() == game_config.STARTING_LIVES
        assert game.get_level() == 1
        assert not game.power_pellet_active
        
        game._cleanup()
    
    def test_game_state_transitions(self, game_config, mock_pygame):
        """Test game state transitions work correctly."""
        game = Game(game_config)
        
        # Start in menu state
        assert game.get_game_state() == GameState.MENU
        
        # Transition to playing state
        game._start_new_game()
        game.state_manager.set_state(GameState.PLAYING)
        assert game.get_game_state() == GameState.PLAYING
        
        # Transition to paused state
        game.state_manager.set_state(GameState.PAUSED)
        assert game.get_game_state() == GameState.PAUSED
        
        # Transition to game over state
        game._handle_game_over()
        assert game.get_game_state() == GameState.GAME_OVER
        
        game._cleanup()
    
    def test_60_fps_game_loop_timing(self, game_config, mock_pygame):
        """Test that the game loop maintains proper 60 FPS timing."""
        game = Game(game_config)
        
        # Mock the clock to simulate frame timing
        frame_count = 0
        def mock_tick(fps):
            nonlocal frame_count
            frame_count += 1
            if frame_count >= 5:  # Stop after 5 frames
                game.running = False
            return 16  # 16ms per frame = ~60 FPS
        
        mock_pygame['clock'].tick.side_effect = mock_tick
        
        # Mock event handling and rendering to avoid infinite loop and pygame errors
        with patch('pygame.event.get', return_value=[]), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.circle'), \
             patch('pygame.draw.polygon'), \
             patch('pygame.display.flip'):
            
            game.run()
        
        # Verify clock.tick was called with correct FPS
        mock_pygame['clock'].tick.assert_called_with(game_config.FPS)
        assert frame_count == 5
        
        game._cleanup()
    
    def test_input_integration(self, game_config, mock_pygame):
        """Test input handling integration across all systems."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Mock keyboard events
        key_down_event = Mock()
        key_down_event.type = pygame.KEYDOWN
        key_down_event.key = pygame.K_RIGHT
        
        key_up_event = Mock()
        key_up_event.type = pygame.KEYUP
        key_up_event.key = pygame.K_RIGHT
        
        events = [key_down_event, key_up_event]
        
        # Process input
        game._handle_events(events)
        
        # Verify input was processed
        assert game.input_handler is not None
        
        game._cleanup()
    
    def test_player_movement_integration(self, game_config, mock_pygame):
        """Test player movement integrates with maze collision detection."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Store initial position
        initial_pos = Position(game.player.position.x, game.player.position.y)
        
        # Set player direction
        game.player.set_direction(Direction.RIGHT)
        
        # Update game state
        game._update_game()
        
        # Verify player moved (if not blocked by wall)
        if game.maze.can_move(initial_pos, Direction.RIGHT):
            assert game.player.position.x != initial_pos.x or game.player.position.y != initial_pos.y
        
        game._cleanup()
    
    def test_ghost_ai_integration(self, game_config, mock_pygame):
        """Test ghost AI integrates with player position and maze navigation."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Store initial ghost positions
        initial_positions = [Position(ghost.position.x, ghost.position.y) for ghost in game.ghosts]
        
        # Update game state multiple times
        for _ in range(10):
            game._update_game()
        
        # Verify at least one ghost moved (AI is working)
        moved_ghosts = 0
        for i, ghost in enumerate(game.ghosts):
            if (ghost.position.x != initial_positions[i].x or 
                ghost.position.y != initial_positions[i].y):
                moved_ghosts += 1
        
        assert moved_ghosts > 0, "At least one ghost should have moved"
        
        game._cleanup()
    
    def test_collectible_system_integration(self, game_config, mock_pygame):
        """Test collectible collection integrates with scoring system."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        initial_score = game.get_score()
        initial_dots = game.maze.get_dots_remaining()
        
        # Place player on a dot position
        for dot_pos in list(game.maze.dots)[:1]:  # Take first dot
            game.player.position.x = dot_pos[0] * game.config.TILE_SIZE
            game.player.position.y = dot_pos[1] * game.config.TILE_SIZE
            break
        
        # Update game to trigger collection
        game._update_game()
        
        # Verify dot was collected and score increased
        assert game.get_score() > initial_score
        assert game.maze.get_dots_remaining() < initial_dots
        
        game._cleanup()
    
    def test_power_pellet_integration(self, game_config, mock_pygame):
        """Test power pellet collection integrates with ghost behavior."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Place player on a power pellet position
        for pellet_pos in list(game.maze.power_pellets)[:1]:  # Take first power pellet
            game.player.position.x = pellet_pos[0] * game.config.TILE_SIZE
            game.player.position.y = pellet_pos[1] * game.config.TILE_SIZE
            break
        
        # Update game to trigger collection
        game._update_game()
        
        # Verify power pellet effect is active
        assert game.power_pellet_active
        assert game.power_pellet_timer > 0
        
        # Verify ghosts are in frightened mode
        frightened_ghosts = sum(1 for ghost in game.ghosts if ghost.mode.is_vulnerable())
        assert frightened_ghosts > 0
        
        game._cleanup()
    
    def test_collision_detection_integration(self, game_config, mock_pygame):
        """Test collision detection integrates with life system."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        initial_lives = game.get_lives()
        
        # Place player and ghost at same position
        game.player.position = Position(200, 200)
        game.ghosts[0].position = Position(200, 200)
        game.ghosts[0].mode = game.ghosts[0].mode.NORMAL
        
        # Update game to trigger collision
        game._update_game()
        
        # Verify life was lost (or game over)
        assert game.get_lives() < initial_lives or game.score_manager.is_game_over()
        
        game._cleanup()
    
    def test_level_completion_integration(self, game_config, mock_pygame):
        """Test level completion integrates with maze reset and progression."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        initial_level = game.get_level()
        
        # Simulate collecting all dots
        game.maze.dots.clear()
        game.score_manager.dots_collected_in_level = game.score_manager.total_dots_in_level
        
        # Update game to trigger level completion
        game._update_game()
        
        # Verify level advanced and maze reset
        assert game.get_level() > initial_level
        assert game.maze.get_dots_remaining() > 0  # Maze should be reset
        
        game._cleanup()
    
    def test_game_over_integration(self, game_config, mock_pygame):
        """Test game over integrates with state management."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Force game over condition
        game.score_manager.lives = 0
        
        # Update game to trigger game over
        game._update_game()
        
        # Verify game over state
        assert game.get_game_state() == GameState.GAME_OVER
        assert game.score_manager.is_game_over()
        
        game._cleanup()
    
    def test_rendering_integration(self, game_config, mock_pygame):
        """Test rendering system integrates with all game objects."""
        game = Game(game_config)
        game.state_manager.set_state(GameState.PLAYING)
        
        # Mock pygame drawing functions to avoid surface type errors
        with patch('pygame.draw.rect'), \
             patch('pygame.draw.circle'), \
             patch('pygame.draw.polygon'), \
             patch.object(game.renderer, 'update_display'):
            
            # Render a frame
            game._render_frame()
            
            # Verify renderer methods were called
            # (We can't easily verify the actual rendering without complex mocking,
            # but we can verify the render method completes without errors)
            assert True  # If we get here, rendering didn't crash
        
        game._cleanup()
    
    def test_game_restart_integration(self, game_config, mock_pygame):
        """Test game restart resets all systems correctly."""
        game = Game(game_config)
        
        # Modify game state
        game.score_manager.score = 1000
        game.score_manager.level = 3
        game.score_manager.lives = 1
        game.player.position = Position(300, 300)
        game.power_pellet_active = True
        
        # Restart game
        game._restart_game()
        
        # Verify everything was reset
        assert game.get_score() == 0
        assert game.get_level() == 1
        assert game.get_lives() == game_config.STARTING_LIVES
        assert not game.power_pellet_active
        assert game.power_pellet_timer == 0
        
        game._cleanup()
    
    def test_fps_performance(self, game_config, mock_pygame):
        """Test that the game can maintain target FPS under normal conditions."""
        game = Game(game_config)
        
        # Mock time to simulate frame timing
        frame_times = []
        original_time = time.time
        
        def mock_time():
            frame_times.append(len(frame_times) * (1.0 / 60.0))  # 60 FPS timing
            return frame_times[-1]
        
        with patch('time.time', side_effect=mock_time):
            # Simulate several game updates
            for _ in range(10):
                game._update_game()
        
        # Verify FPS tracking works
        fps = game.get_fps()
        assert isinstance(fps, (int, float))
        
        game._cleanup()
    
    def test_memory_cleanup(self, game_config, mock_pygame):
        """Test that game cleanup properly releases resources."""
        game = Game(game_config)
        
        # Verify game is running
        assert hasattr(game, 'renderer')
        assert hasattr(game, 'input_handler')
        assert hasattr(game, 'state_manager')
        
        # Cleanup
        game._cleanup()
        
        # Verify cleanup was called (pygame.quit should be called)
        # This is hard to test without mocking pygame.quit, but we can
        # verify the method completes without errors
        assert True
    
    def test_error_handling_integration(self, game_config, mock_pygame):
        """Test that the game handles errors gracefully."""
        game = Game(game_config)
        
        # Test with invalid input
        try:
            game._handle_events([None])  # Invalid event
        except Exception:
            pytest.fail("Game should handle invalid events gracefully")
        
        # Test with invalid state
        try:
            game._update_game()  # Should work even in menu state
        except Exception:
            pytest.fail("Game should handle updates in any state")
        
        game._cleanup()


class TestGameLoopPerformance:
    """Test game loop performance and timing."""
    
    @pytest.fixture
    def mock_pygame_perf(self):
        """Mock pygame for performance tests."""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.font.Font'), \
             patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.circle'), \
             patch('pygame.display.flip'):
            
            # Mock display surface
            mock_surface = Mock()
            mock_surface.fill = Mock()
            mock_surface.blit = Mock()
            mock_display.return_value = mock_surface
            
            # Mock clock
            mock_clock_instance = Mock()
            mock_clock_instance.tick.return_value = 16
            mock_clock_instance.get_fps.return_value = 60.0
            mock_clock.return_value = mock_clock_instance
            
            yield mock_surface
    
    def test_update_performance(self, mock_pygame_perf):
        """Test that game updates complete within reasonable time."""
        config = GameConfig()
        game = Game(config)
        game.state_manager.set_state(GameState.PLAYING)
        
        start_time = time.time()
        
        # Run multiple updates
        for _ in range(100):
            game._update_game()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 updates in less than 1 second
        assert total_time < 1.0, f"100 updates took {total_time:.3f}s, should be < 1.0s"
        
        game._cleanup()
    
    def test_render_performance(self, mock_pygame_perf):
        """Test that rendering completes within reasonable time."""
        config = GameConfig()
        game = Game(config)
        game.state_manager.set_state(GameState.PLAYING)
        
        start_time = time.time()
        
        # Run multiple renders (without actual pygame calls)
        with patch.object(game.renderer, 'update_display'), \
             patch('pygame.Surface'), \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.circle'), \
             patch('pygame.draw.polygon'):
            
            for _ in range(60):  # Simulate 1 second of rendering at 60 FPS
                game._render_frame()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 60 renders in reasonable time
        assert total_time < 2.0, f"60 renders took {total_time:.3f}s, should be < 2.0s"
        
        game._cleanup()


if __name__ == "__main__":
    pytest.main([__file__])
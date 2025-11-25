#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audio Manager for Judgment in Fifteen Days
Handles background music and sound effects
"""

import os
import pygame


class AudioManager:
    """Manages all audio playback in the game."""
    
    def __init__(self, base_path=None):
        """Initialize the audio manager.
        
        Args:
            base_path: Base directory path where audio files are located.
                      If None, uses the parent directory of this file.
        """
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Set base path
        if base_path is None:
            # Default to project root (parent of 'game' folder)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(current_dir)
        
        self.base_path = base_path
        
        # Audio file paths
        self.bgm_path = os.path.join(base_path, "BGM.mp3")
        self.click_path = os.path.join(base_path, "click.mp3")
        
        # Load sound effects
        self.click_sound = None
        if os.path.exists(self.click_path):
            try:
                self.click_sound = pygame.mixer.Sound(self.click_path)
                # Set click sound volume (0.0 to 1.0)
                self.click_sound.set_volume(0.7)
            except Exception as e:
                print(f"Warning: Failed to load click sound: {e}")
        
        # BGM state
        self.bgm_loaded = False
        self.bgm_playing = False
        
    def start_bgm(self):
        """Start playing background music in loop."""
        if not os.path.exists(self.bgm_path):
            print(f"Warning: BGM file not found at {self.bgm_path}")
            return
        
        try:
            if not self.bgm_loaded:
                pygame.mixer.music.load(self.bgm_path)
                self.bgm_loaded = True
            
            if not self.bgm_playing:
                # Play music in infinite loop (-1 means loop forever)
                pygame.mixer.music.play(-1)
                # Set BGM volume (0.0 to 1.0)
                pygame.mixer.music.set_volume(0.5)
                self.bgm_playing = True
                print("BGM started playing")
        except Exception as e:
            print(f"Warning: Failed to start BGM: {e}")
    
    def stop_bgm(self):
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
            self.bgm_playing = False
            print("BGM stopped")
        except Exception as e:
            print(f"Warning: Failed to stop BGM: {e}")
    
    def pause_bgm(self):
        """Pause background music."""
        try:
            pygame.mixer.music.pause()
            print("BGM paused")
        except Exception as e:
            print(f"Warning: Failed to pause BGM: {e}")
    
    def unpause_bgm(self):
        """Resume background music."""
        try:
            pygame.mixer.music.unpause()
            print("BGM resumed")
        except Exception as e:
            print(f"Warning: Failed to unpause BGM: {e}")
    
    def play_click(self):
        """Play click sound effect."""
        if self.click_sound:
            try:
                # Play sound effect (doesn't affect BGM)
                self.click_sound.play()
            except Exception as e:
                print(f"Warning: Failed to play click sound: {e}")
    
    def set_bgm_volume(self, volume):
        """Set background music volume.
        
        Args:
            volume: Volume level from 0.0 (silent) to 1.0 (full volume)
        """
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            print(f"Warning: Failed to set BGM volume: {e}")
    
    def set_click_volume(self, volume):
        """Set click sound volume.
        
        Args:
            volume: Volume level from 0.0 (silent) to 1.0 (full volume)
        """
        if self.click_sound:
            try:
                volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
                self.click_sound.set_volume(volume)
            except Exception as e:
                print(f"Warning: Failed to set click volume: {e}")
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            print("Audio manager cleaned up")
        except Exception as e:
            print(f"Warning: Failed to cleanup audio: {e}")

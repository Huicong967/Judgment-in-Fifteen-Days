"""
Image manager for the game.
处理游戏图片加载和管理。
"""

import os
from typing import Optional, Dict, Tuple
from PIL import Image, ImageDraw


class ImageManager:
    """Manages game images and provides fallback placeholders."""
    
    ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
    
    # Default dimensions for different image types
    DEFAULT_SIZES = {
        'background': (800, 600),
        'character': (300, 400),
        'item': (150, 150),
        'button': (200, 60),
    }
    
    def __init__(self):
        """Initialize image manager."""
        self.image_cache = {}
        self._create_assets_directory()
    
    def _create_assets_directory(self):
        """Create assets directory structure if it doesn't exist."""
        subdirs = ['backgrounds', 'characters', 'items', 'buttons', 'ui']
        
        for subdir in subdirs:
            path = os.path.join(self.ASSETS_DIR, subdir)
            os.makedirs(path, exist_ok=True)
    
    def get_image(self, image_type: str, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[Image.Image]:
        """Load an image or return a placeholder if not found.
        
        Args:
            image_type: Type of image ('background', 'character', 'item', 'button', 'ui')
            name: Name of the image file (without extension)
            size: Optional size (width, height). Uses default if not provided.
        
        Returns:
            PIL Image object or placeholder image
        """
        # Use default size if not provided
        if size is None:
            size = self.DEFAULT_SIZES.get(image_type, (200, 200))
        
        cache_key = f"{image_type}_{name}_{size[0]}x{size[1]}"
        
        # Return cached image if available
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # Try to load real image
        image_path = os.path.join(self.ASSETS_DIR, image_type, f'{name}.png')
        
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path).resize(size, Image.Resampling.LANCZOS)
                self.image_cache[cache_key] = img
                return img
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        
        # Return placeholder if image not found
        placeholder = self._create_placeholder(image_type, name, size)
        self.image_cache[cache_key] = placeholder
        return placeholder
    
    def _create_placeholder(self, image_type: str, name: str, size: Tuple[int, int]) -> Image.Image:
        """Create a placeholder image.
        
        Args:
            image_type: Type of image
            name: Name of the image
            size: Image size
        
        Returns:
            PIL Image object
        """
        # Create base image with dark background
        img = Image.new('RGB', size, color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Add border
        border_color = '#00d4ff'
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=2)
        
        # Add text
        text = f"[{image_type}]\n{name}"
        
        try:
            # Try to use a better font if available
            # font = ImageFont.truetype("arial.ttf", 12)
            # For now, use default font
            draw.text((10, 10), text, fill='#00d4ff')
        except:
            pass
        
        return img
    
    def get_background(self, name: str) -> Image.Image:
        """Get a background image.
        
        Args:
            name: Background name
        
        Returns:
            PIL Image object
        """
        return self.get_image('background', name, self.DEFAULT_SIZES['background'])
    
    def get_character(self, name: str) -> Image.Image:
        """Get a character image.
        
        Args:
            name: Character name
        
        Returns:
            PIL Image object
        """
        return self.get_image('character', name, self.DEFAULT_SIZES['character'])
    
    def get_item(self, name: str) -> Image.Image:
        """Get an item image.
        
        Args:
            name: Item name
        
        Returns:
            PIL Image object
        """
        return self.get_image('item', name, self.DEFAULT_SIZES['item'])
    
    def get_button(self, name: str) -> Image.Image:
        """Get a button image.
        
        Args:
            name: Button name
        
        Returns:
            PIL Image object
        """
        return self.get_image('button', name, self.DEFAULT_SIZES['button'])
    
    def composite(self, background: Image.Image, *images: Tuple[Image.Image, Tuple[int, int]]) -> Image.Image:
        """Composite multiple images on top of a background.
        
        Args:
            background: Base background image
            *images: Tuples of (image, (x, y)) to composite
        
        Returns:
            Composite PIL Image object
        """
        result = background.copy()
        
        for img, (x, y) in images:
            if img:
                result.paste(img, (x, y), img if img.mode == 'RGBA' else None)
        
        return result
    
    def clear_cache(self):
        """Clear image cache."""
        self.image_cache.clear()


# Global image manager instance
_image_manager = None


def get_image_manager() -> ImageManager:
    """Get or create global image manager instance.
    
    Returns:
        Global ImageManager instance
    """
    global _image_manager
    
    if _image_manager is None:
        _image_manager = ImageManager()
    
    return _image_manager

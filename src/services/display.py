from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import textwrap
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class DisplayGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.CHUCK_IMAGE_URL = "https://i.seadn.io/gae/MD2INKicV62FvEbGiNKyMdoRkDguSxL9JkCkGjgyJT0IzFe4VpNb-5nqWCvzpObAQHOkpjp8mmGL00cGLEkQx4ZC-8JrmlRBDth5Sg?auto=format&dpr=1&w=1000"
        self.cached_chuck_image = None
        
        try:
            # Main display fonts
            self.title_font = ImageFont.truetype(font='arial.ttf', size=48)
            self.fact_font = ImageFont.truetype(font='arial.ttf', size=32)
            self.meta_font = ImageFont.truetype(font='arial.ttf', size=16)
        except Exception as e:
            logger.warning(f'Failed to load TrueType font: {e}')
            self.title_font = ImageFont.load_default()
            self.fact_font = ImageFont.load_default()
            self.meta_font = ImageFont.load_default()
        
        # Pre-load and process Chuck Norris image
        self._load_chuck_image()

    def _load_chuck_image(self):
        """Load and process Chuck Norris image"""
        try:
            # Download image
            response = requests.get(self.CHUCK_IMAGE_URL)
            image = Image.open(BytesIO(response.content))
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Resize to appropriate height (maintain aspect ratio)
            target_height = 120
            aspect_ratio = image.width / image.height
            target_width = int(target_height * aspect_ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Apply dithering
            image = image.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
            
            self.cached_chuck_image = image
            logger.info("Successfully loaded and processed Chuck Norris image")
            
        except Exception as e:
            logger.error(f"Failed to load Chuck Norris image: {str(e)}")
            self.cached_chuck_image = None

    def create_display(self, data: Dict[str, Any]) -> Optional[bytes]:
        try:
            image = Image.new('1', (self.width, self.height), 1)  # 1 = white background
            draw = ImageDraw.Draw(image)
            
            if not data or 'fact' not in data:
                return self.create_error_display('No Chuck Norris fact available')
            
            # Draw content
            self._draw_header_with_image(draw, image)
            self._draw_fact(draw, data)
            self._draw_footer(draw, data)
            
            buffer = io.BytesIO()
            image.save(buffer, format='BMP')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f'Error generating display: {str(e)}')
            return self.create_error_display(str(e))

    def _draw_header_with_image(self, draw: ImageDraw, base_image: Image):
        """Draw the header section with Chuck Norris image"""
        if self.cached_chuck_image:
            # Calculate image position (left side)
            image_y = 20
            base_image.paste(self.cached_chuck_image, (20, image_y))
            
            # Draw title to the right of the image
            title_text = "Chuck Norris Fact"
            x = 200  # Position after image
            y = 60
            
            draw.text((x, y), title_text, font=self.title_font, fill=0)
            
            # Draw line under the header area
            line_y = image_y + self.cached_chuck_image.height + 20
            draw.line([(20, line_y), (self.width - 20, line_y)], fill=0, width=2)
        else:
            # Fallback if image isn't available
            title_text = "Chuck Norris Fact"
            bbox = draw.textbbox((0, 0), title_text, font=self.title_font)
            title_width = bbox[2] - bbox[0]
            
            x = (self.width - title_width) // 2
            y = 40
            draw.text((x, y), title_text, font=self.title_font, fill=0)
            
            line_y = y + bbox[3] - bbox[1] + 20
            draw.line([(20, line_y), (self.width - 20, line_y)], fill=0, width=2)

    def _draw_fact(self, draw: ImageDraw, data: Dict[str, Any]):
        """Draw the main fact text with proper boundaries and overflow handling"""
        fact_text = data.get('fact', 'No fact available')
        
        # Define the content area dimensions with proper margins
        header_height = 180 if self.cached_chuck_image else 120
        footer_height = 80
        content_width = self.width - 80  # 40px padding on each side
        content_height = self.height - header_height - footer_height
        
        # Starting font size and minimum size
        max_font_size = 48
        min_font_size = 24
        optimal_font_size = max_font_size
        
        # Find the optimal font size that fits within boundaries
        while optimal_font_size >= min_font_size:
            try:
                test_font = ImageFont.truetype('arial.ttf', optimal_font_size)
            except:
                test_font = ImageFont.load_default()
            
            # Calculate wrap width based on average character width
            avg_char_width = test_font.getlength('x')  # Use 'x' for average width
            chars_per_line = int((content_width - 40) / avg_char_width)  # Add extra padding
            
            # Wrap text
            wrapped_text = textwrap.fill(fact_text, width=chars_per_line)
            
            # Calculate wrapped text dimensions
            bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=test_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Check if text fits within content area with padding
            if text_width <= content_width - 40 and text_height <= content_height - 40:
                break
                
            optimal_font_size -= 2
        
        # Use minimum font size if we couldn't fit the text
        if optimal_font_size < min_font_size:
            optimal_font_size = min_font_size
        
        # Create final font
        try:
            final_font = ImageFont.truetype('arial.ttf', optimal_font_size)
        except:
            final_font = ImageFont.load_default()
        
        # Final text wrapping with proper width calculation
        avg_char_width = final_font.getlength('x')
        chars_per_line = int((content_width - 40) / avg_char_width)
        wrapped_text = textwrap.fill(fact_text, width=chars_per_line)
        
        # Calculate text dimensions for centering
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=final_font)
        final_width = bbox[2] - bbox[0]
        final_height = bbox[3] - bbox[1]
        
        # Center the text with proper margins
        x = (self.width - final_width) // 2
        y = header_height + (content_height - final_height) // 2
        
        # Draw text with proper line spacing
        draw.multiline_text(
            (x, y),
            wrapped_text,
            font=final_font,
            fill=0,
            align='center',
            spacing=int(optimal_font_size * 0.3)  # Adjusted line spacing
        )

    def _draw_footer(self, draw: ImageDraw, data: Dict[str, Any]):
        """Draw the footer with fact ID and timestamp"""
        # Draw fact ID
        fact_id = f"Fact ID: {data.get('fact_id', 'Unknown')}"
        
        # Format timestamp
        timestamp = data.get('timestamp', 'Unknown')
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                pass
        
        # Draw footer line
        footer_y = self.height - 60
        draw.line([(20, footer_y), (self.width - 20, footer_y)], fill=0, width=1)
        
        # Draw footer text
        draw.text(
            (20, footer_y + 10),
            fact_id,
            font=self.meta_font,
            fill=0
        )
        
        timestamp_bbox = draw.textbbox((0, 0), timestamp, font=self.meta_font)
        timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
        draw.text(
            (self.width - timestamp_width - 20, footer_y + 10),
            timestamp,
            font=self.meta_font,
            fill=0
        )

    def create_error_display(self, error_message: str) -> bytes:
        """Create an error display"""
        image = Image.new('1', (self.width, self.height), 1)
        draw = ImageDraw.Draw(image)
        
        # Draw error header
        header_text = 'Error'
        bbox = draw.textbbox((0, 0), header_text, font=self.title_font)
        header_width = bbox[2] - bbox[0]
        
        x = (self.width - header_width) // 2
        y = 40
        draw.text((x, y), header_text, font=self.title_font, fill=0)
        
        # Draw error message
        wrapped_error = textwrap.fill(error_message, width=40)
        bbox = draw.multiline_textbbox((0, 0), wrapped_error, font=self.fact_font)
        error_width = bbox[2] - bbox[0]
        
        x = (self.width - error_width) // 2
        y = (self.height - bbox[3] + bbox[1]) // 2
        
        draw.multiline_text(
            (x, y),
            wrapped_error,
            font=self.fact_font,
            fill=0,
            align='center',
            spacing=10
        )
        
        buffer = io.BytesIO()
        image.save(buffer, format='BMP')
        return buffer.getvalue()
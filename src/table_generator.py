#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard library imports
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List

# Third-party imports
from PIL import Image, ImageDraw, ImageFont  # Pour la génération d'images

class TableGenerator:
    def __init__(self, colors):
        """Initialize the table generator."""
        self.colors = colors
        self.country_column_width = 200  # Increased width for country names
        self.cell_width = 100
        self.cell_height = 40
        self.font_size = 12
        self.title_font_size = 16
        self.padding = 10
        self.border_width = 1  # Width of cell borders
        
        # Colors for header and first column
        self.header_bg_color = 'black'
        self.header_text_color = 'white'
        
        # Try to load a system font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.title_font_size)
        except OSError:
            # Fallback to default font
            self.font = ImageFont.load_default()
            self.title_font = ImageFont.load_default()
    
    def _create_base_image(self, rows, columns, title_height):
        """Create base image with white background."""
        width = self.country_column_width + columns * self.cell_width
        height = title_height + (rows + 1) * self.cell_height
        
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        return image, draw
    
    def _draw_cell_border(self, draw, x, y, width, height):
        """Draw border around a cell."""
        draw.line([(x, y), (x + width, y)], fill='black', width=self.border_width)  # Top
        draw.line([(x, y + height), (x + width, y + height)], fill='black', width=self.border_width)  # Bottom
        draw.line([(x, y), (x, y + height)], fill='black', width=self.border_width)  # Left
        draw.line([(x + width, y), (x + width, y + height)], fill='black', width=self.border_width)  # Right
    
    def _draw_grid(self, draw, rows, columns, title_height):
        """Draw grid lines."""
        total_width = self.country_column_width + columns * self.cell_width
        total_height = (rows + 1) * self.cell_height + title_height
        
        # Draw horizontal lines starting after title
        for row in range(rows + 2):  # +2 for header row and bottom border
            y = title_height + row * self.cell_height
            draw.line([(0, y), (total_width, y)], fill='black', width=self.border_width)
        
        # Draw vertical lines
        x = 0
        # First column (country names)
        draw.line([(x, title_height), (x, total_height)], fill='black', width=self.border_width)
        x += self.country_column_width
        draw.line([(x, title_height), (x, total_height)], fill='black', width=self.border_width)
        
        # Time columns
        for col in range(columns + 1):
            x = self.country_column_width + col * self.cell_width
            draw.line([(x, title_height), (x, total_height)], fill='black', width=self.border_width)
    
    def _draw_text(self, draw, text, x, y, width, fill='black', font=None, align='center'):
        """Draw text in cell."""
        if font is None:
            font = self.font
            
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        if align == 'center':
            text_x = x + (width - text_width) // 2
        else:  # left align for country names
            text_x = x + self.padding
            
        text_y = y + (self.cell_height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=fill, font=font)
    
    def _draw_title(self, draw, reference_tz, width, title_height, timezone_manager):
        """Draw title with reference timezone info."""
        # Get reference country name
        country_name = timezone_manager.get_reference_country_name()
        offset = datetime.now(reference_tz).strftime('%z')
        offset_str = f"GMT {offset[:3]}:{offset[3:]}"
        
        title = f"{'Summer' if datetime.now(reference_tz).dst() else 'Winter'} time in {country_name} ({offset_str})"
        
        # Draw title with yellow background
        draw.rectangle([(0, 0), (width, title_height)], fill='yellow')
        
        # Center title text
        text_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (title_height - text_height) // 2
        
        draw.text((x, y), title, fill='black', font=self.title_font)
    
    def generate_table(
        self,
        table_data: List[Dict],
        output_path: Union[str, Path],
        reference_tz,
        timezone_manager
    ) -> None:
        """Generate timezone table as PNG image.
        
        Args:
            table_data: List of dictionaries containing timezone data
            output_path: Path or string where to save the generated image
            reference_tz: Reference timezone object
            timezone_manager: TimezoneManager instance
            
        Raises:
            ValueError: If no timezone data is provided
            OSError: If the output path is invalid or not writable
        """
        if not table_data:
            raise ValueError("No timezone data provided")
        
        # Get dimensions
        rows = len(table_data)  # One row per timezone
        columns = len(table_data[0]['periods'])  # Number of time periods
        title_height = 50  # Height for title section
        
        # Create image
        image, draw = self._create_base_image(rows, columns, title_height)
        
        # Draw title
        total_width = self.country_column_width + columns * self.cell_width
        self._draw_title(draw, reference_tz, total_width, title_height, timezone_manager)
        
        # Draw grid
        self._draw_grid(draw, rows, columns, title_height)
        
        # Draw headers (hours in reference timezone)
        # Fill header background with black
        draw.rectangle(
            [(self.country_column_width, title_height), 
             (total_width, title_height + self.cell_height)],
            fill=self.header_bg_color
        )
        
        # Draw header text in white
        for col, hour in enumerate(range(8, 20)):  # 8:00 to 19:00
            time_str = f"{hour:02d}:00"
            x = self.country_column_width + col * self.cell_width
            self._draw_text(
                draw, 
                time_str, 
                x, 
                title_height, 
                self.cell_width,
                fill=self.header_text_color
            )
        
        # Draw country names and time periods
        for row, data in enumerate(table_data):
            y = title_height + (row + 1) * self.cell_height
            
            # Fill country name background with black
            draw.rectangle(
                [(0, y), (self.country_column_width, y + self.cell_height)],
                fill=self.header_bg_color
            )
            
            # Draw country name in white
            self._draw_text(
                draw, 
                data['country'], 
                0, 
                y,
                self.country_column_width,
                fill=self.header_text_color,
                align='left'
            )
            
            # Draw time periods
            for col, period in enumerate(data['periods']):
                x = self.country_column_width + col * self.cell_width
                
                # Fill cell with period color
                color = self.colors.get(period['type'], 'white')
                draw.rectangle(
                    [(x, y), (x + self.cell_width, y + self.cell_height)],
                    fill=color
                )
                
                # Draw cell border
                self._draw_cell_border(draw, x, y, self.cell_width, self.cell_height)
                
                # Draw time
                # Format time string based on whether it has minutes
                if period['time'].minute != 0:
                    time_str = period['time'].strftime("%H:%M")
                else:
                    time_str = period['time'].strftime("%H:00")
                    
                self._draw_text(draw, time_str, x, y, self.cell_width)
        
        # Save image
        # Convert string path to Path object and ensure parent directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            image.save(output_path, 'PNG')
        except OSError as e:
            raise OSError(f"Failed to save image to {output_path}: {e}")
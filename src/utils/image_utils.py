"""Image display utilities for terminal."""
import numpy
from PIL import Image
import shutil


def get_terminal_size():
    """Get the current terminal size.
    
    Returns:
        tuple: (columns, lines) of the terminal.
    """
    return shutil.get_terminal_size()


def display_image_in_terminal(image_path):
    """Display an image in the terminal using ANSI escape codes.
    
    Args:
        image_path: Path to the image file to display.
    """
    try:
        columns, lines = get_terminal_size()
    except OSError:
        print("Não foi possível obter o tamanho do terminal. Usando padrão 80x24.")
        columns, lines = 80, 24
        
    target_lines = lines - 1 
    target_columns = columns

    def get_image(path, target_width, target_height):
        """Load and resize image to fit terminal dimensions.
        
        Args:
            path: Path to the image file.
            target_width: Maximum width in terminal columns.
            target_height: Maximum height in terminal lines.
            
        Returns:
            numpy.ndarray: Pixel values array or None if error.
        """
        try:
            image = Image.open(path, "r")
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Erro ao abrir a imagem: {e}")
            return None
        
        max_width_in_pixels = target_width
        max_height_in_pixels = target_height 
        
        image.thumbnail((max_width_in_pixels, max_height_in_pixels), Image.Resampling.LANCZOS)
        
        width, height = image.size
        pixel_values = list(image.getdata())
        
        if image.mode == "RGB":
            channels = 3
        elif image.mode == "L":
            channels = 1
        elif image.mode == "RGBA":
            image = image.convert("RGB")
            channels = 3
            width, height = image.size
            pixel_values = list(image.getdata())
        else:
            return None

        pixel_values = numpy.array(pixel_values).reshape((height, width, channels)) 
        return pixel_values

    image = get_image(image_path, target_columns, target_lines)

    if image is None:
        print(f"Erro: Não foi possível carregar a imagem em '{image_path}' ou o modo de cor é incompatível.")
        return

    img_height, img_width, channels = image.shape

    k = 0 
    for i in range(img_height): 
        if i >= target_lines:
            break 

        for j in range(img_width): 
            if j >= target_columns:
                break 
                    
            if channels == 3:
                r = image[i][j][k]
                g = image[i][j][k+1]
                b = image[i][j][k+2]
            else: 
                r = g = b = image[i][j][k]
                
            background_color_code = f"\033[48;2;{r};{g};{b}m"
            reset_code = "\033[0m"

            colored_char = f"{background_color_code} {reset_code}"
                
            print(colored_char, end="")

        print()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import qrcode
from pyzbar.pyzbar import decode as pyzbar_decode
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import json
import math
import random
from pathlib import Path
import PyPDF2  # For PDF text extraction
import io

class VisualTextEncoder:

    def __init__(self, root):
        self.root = root
        self.root.title("Artistic Text Encoder/Decoder")
        self.root.geometry("900x650")

        # Variables
        self.encoded_image = None
        self.encoding_key = None

        self.setup_gui()

    def setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Encode tab
        encode_frame = ttk.Frame(notebook)
        notebook.add(encode_frame, text='Encode')
        self.setup_encode_tab(encode_frame)

        # Decode tab
        decode_frame = ttk.Frame(notebook)
        notebook.add(decode_frame, text='Decode')
        self.setup_decode_tab(decode_frame)

    def setup_encode_tab(self, parent):
        # Text input
        ttk.Label(parent, text="Text to Encode:").pack(anchor='w', pady=(10, 5))
        self.text_input = scrolledtext.ScrolledText(parent, height=5)
        self.text_input.pack(fill='x', padx=10, pady=(0, 10))

        # PDF upload button
        ttk.Button(parent, text="Upload PDF File", command=self.upload_pdf).pack(pady=5)

        # Encoding method selection
        ttk.Label(parent, text="Artistic Encoding Method:").pack(anchor='w', pady=(10, 5))
        self.encoding_method = ttk.Combobox(parent, values=[
            "QR Code",
            "Morse Code Text",
            "Cosmic Constellation",
            "Chromatic Symphony",
            "Blob Impressionism"
        ])
        self.encoding_method.set("QR Code")
        self.encoding_method.pack(fill='x', padx=10, pady=(0, 10))
        self.encoding_method.bind("<<ComboboxSelected>>", self.on_encoding_method_change)

        # Output settings
        settings_frame = ttk.LabelFrame(parent, text="Output Settings")
        settings_frame.pack(fill='x', padx=10, pady=10)

        # Image size (only for visual methods)
        ttk.Label(settings_frame, text="Image Size:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        size_frame = ttk.Frame(settings_frame)
        size_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(size_frame, text="Width:").pack(side='left')
        self.image_width = ttk.Entry(size_frame, width=6)
        self.image_width.insert(0, "800")
        self.image_width.pack(side='left', padx=(5, 15))

        ttk.Label(size_frame, text="Height:").pack(side='left')
        self.image_height = ttk.Entry(size_frame, width=6)
        self.image_height.insert(0, "600")
        self.image_height.pack(side='left', padx=5)

        # Border width setting
        ttk.Label(settings_frame, text="Border Width:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.border_width = ttk.Entry(settings_frame, width=6)
        self.border_width.insert(0, "20")
        self.border_width.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Randomize key option
        ttk.Label(settings_frame, text="Randomize Output:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.randomize_output = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, variable=self.randomize_output).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Folder name
        ttk.Label(settings_frame, text="Folder Name:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.folder_name = ttk.Entry(settings_frame)
        self.folder_name.insert(0, "encoded_artwork")
        self.folder_name.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        # Output location
        ttk.Label(settings_frame, text="Save Location:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.output_location = ttk.Entry(settings_frame)
        self.output_location.insert(0, str(Path.home() / "Desktop"))
        self.output_location.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(settings_frame, text="Browse", command=self.browse_location).grid(row=4, column=2, padx=5, pady=5)

        settings_frame.columnconfigure(1, weight=1)

        # Encode button
        ttk.Button(parent, text="Create Artistic Encoding", command=self.encode_text).pack(pady=20)

        # Preview frame
        preview_frame = ttk.LabelFrame(parent, text="Artwork Preview")
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.preview_label = ttk.Label(preview_frame, text="Your encoded artwork will appear here")
        self.preview_label.pack(expand=True)

    def on_encoding_method_change(self, event=None):
        method = self.encoding_method.get()
        if method == "QR Code":
            width = self.image_width.get()
            self.image_height.delete(0, tk.END)
            self.image_height.insert(0, width)

    def setup_decode_tab(self, parent):
        # File selection
        file_frame = ttk.LabelFrame(parent, text="Select Files")
        file_frame.pack(fill='x', padx=10, pady=10)

        # Encoded file
        ttk.Label(file_frame, text="Encoded Artwork:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.decode_file_path = ttk.Entry(file_frame)
        self.decode_file_path.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_decode_file).grid(row=0, column=2, padx=5, pady=5)

        # Key file
        ttk.Label(file_frame, text="Decoding Key:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.decode_key_path = ttk.Entry(file_frame)
        self.decode_key_path.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_decode_key).grid(row=1, column=2, padx=5, pady=5)

        file_frame.columnconfigure(1, weight=1)

        # Decode button
        ttk.Button(parent, text="Decode Artwork", command=self.decode_file).pack(pady=20)

        # Decoded text output
        ttk.Label(parent, text="Decoded Text:").pack(anchor='w', padx=10, pady=(10, 5))
        self.decoded_text = scrolledtext.ScrolledText(parent, height=10)
        self.decoded_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                text = self.extract_text_from_pdf(file_path)
                self.text_input.delete('1.0', tk.END)
                self.text_input.insert('1.0', text)
                messagebox.showinfo("Success", "PDF content loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def browse_location(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_location.delete(0, tk.END)
            self.output_location.insert(0, folder)

    def browse_decode_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image files", "*.png *.jpg *.jpeg"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ])
        if file_path:
            self.decode_file_path.delete(0, tk.END)
            self.decode_file_path.insert(0, file_path)

    def browse_decode_key(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.json")])
        if file_path:
            self.decode_key_path.delete(0, tk.END)
            self.decode_key_path.insert(0, file_path)

    def encode_text(self):
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please enter text to encode")
            return

        method = self.encoding_method.get()
        randomize = self.randomize_output.get()

        try:
            if method == "QR Code":
                # Get image dimensions
                width = int(self.image_width.get())
                height = int(self.image_height.get())
                self.encoded_image, self.encoding_key = self.create_qr_code(text, width, height)
            elif method == "Morse Code Text":
                randomize = self.randomize_output.get()
                self.encoded_image, self.encoding_key = self.create_morse_text(text, randomize)
            elif method in ["Cosmic Constellation","Chromatic Symphony"]:
                # Get image dimensions
                width = int(self.image_width.get())
                height = int(self.image_height.get())
                
                if method == "Cosmic Constellation":
                    self.encoded_image, self.encoding_key = self.create_cosmic_constellation(text, width, height, randomize)
                elif method == "Chromatic Symphony":
                    self.encoded_image, self.encoding_key = self.create_chromatic_symphony(text, width, height, randomize)
            elif method == "Blob Impressionism":
                width = int(self.image_width.get())
                height = int(self.image_height.get())
                self.encoded_image, self.encoding_key = self.create_blob_impressionism(text, width, height)

            # Add method to key
            if self.encoding_key:
                 self.encoding_key["method"] = method

            self.save_files()
            self.show_preview()

        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed: {str(e)}")

    def save_files(self):
        # Create output directory
        output_dir = Path(self.output_location.get()) / self.folder_name.get()
        output_dir.mkdir(exist_ok=True)

        # Save based on method
        method = self.encoding_method.get()
        
        if method == "Morse Code Text":
            # Save Morse code as text file
            morse_path = output_dir / "morse_code.txt"
            with open(morse_path, 'w') as f:
                f.write(self.encoding_key["morse_text"])
            # Save key
            key_path = output_dir / "decoding_key.json"
            with open(key_path, 'w') as f:
                json.dump(self.encoding_key, f, indent=2)
            messagebox.showinfo("Success", f"Files saved to:\n{output_dir}")
        else:
            # Save image for visual methods
            img_path = output_dir / "encoded_artwork.png"
            self.encoded_image.save(img_path)
            # Save key
            key_path = output_dir / "decoding_key.json"
            with open(key_path, 'w') as f:
                json.dump(self.encoding_key, f, indent=2)
            messagebox.showinfo("Success", f"Artwork saved to:\n{output_dir}")

    def show_preview(self):
        method = self.encoding_method.get()
        
        if method == "Morse Code Text":
            # Show Morse code text in preview
            morse_text = self.encoding_key["morse_text"]
            # Truncate if too long
            if len(morse_text) > 100:
                preview_text = morse_text[:100] + "..."
            else:
                preview_text = morse_text
                
            self.preview_label.configure(text=preview_text, image='')
        else:
            # Resize for preview
            preview_size = (400, 300)
            preview_img = self.encoded_image.copy()
            preview_img.thumbnail(preview_size, Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.configure(image=photo, text='')
            self.preview_label.image = photo  # Keep a reference

    def decode_file(self):
        file_path = self.decode_file_path.get()
        key_path = self.decode_key_path.get()

        if not file_path or not key_path:
            messagebox.showerror("Error", "Please select both file and key files")
            return

        try:
            # Load key
            with open(key_path, 'r') as f:
                key = json.load(f)

            method = key.get("method", "")

            if method == "QR Code":
                img = Image.open(file_path)
                decoded_text = self.decode_qr_code(img)
            elif method == "Morse Code Text":
                decoded_text = self.decode_morse_text(file_path, key)
            elif method == "Cosmic Constellation":
                img = Image.open(file_path)
                decoded_text = self.decode_cosmic_constellation(img, key)
            elif method == "Chromatic Symphony":
                img = Image.open(file_path)
                decoded_text = self.decode_chromatic_symphony(img, key)
            elif method == "Blob Impressionism":
                img = Image.open(file_path)
                decoded_text = self.decode_blob_impressionism(img, key)
            else:
                messagebox.showerror("Error", f"Unknown encoding method: {method}")
                return

            self.decoded_text.delete('1.0', tk.END)
            self.decoded_text.insert('1.0', decoded_text)

        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed: {str(e)}")

    def create_morse_text(self, text, randomize=False):
        # Comprehensive Morse code dictionary
        standard_morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', 
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
            '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
            '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
            ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
            '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
        }
        
        # Create a randomized mapping if requested
        if randomize:
            # Get all characters from the standard dictionary
            chars = list(standard_morse_dict.keys())
            codes = list(standard_morse_dict.values())
            
            # Ensure we have the same number of codes as characters
            if len(codes) != len(chars):
                # This shouldn't happen, but just in case
                codes = codes[:len(chars)]
            
            # Shuffle the codes to create a random mapping
            random.shuffle(codes)
            
            # Create the randomized dictionary with unique codes
            morse_dict = {}
            used_codes = set()
            
            for i, char in enumerate(chars):
                if i < len(codes) and codes[i] not in used_codes:
                    morse_dict[char] = codes[i]
                    used_codes.add(codes[i])
                else:
                    # If we run out of unique codes, find an unused code
                    available_codes = [code for code in standard_morse_dict.values() if code not in used_codes]
                    if available_codes:
                        selected_code = random.choice(available_codes)
                        morse_dict[char] = selected_code
                        used_codes.add(selected_code)
                    else:
                        # If all codes are used, just use the standard one
                        morse_dict[char] = standard_morse_dict[char]
        else:
            morse_dict = standard_morse_dict
        
        # Convert text to Morse code using the selected dictionary
        morse_text = ' '.join(morse_dict.get(char.upper(), '') for char in text)
        
        # Create a text "image" (just the Morse code text)
        img = Image.new('RGB', (600, 100), 'white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), morse_text, fill='black', font=font)
        
        key = {
            "original_text": text,
            "morse_text": morse_text,
            "morse_dict": morse_dict,
            "randomized": randomize
        }
        return img, key

    def decode_morse_text(self, file_path, key):
        # Read Morse code from text file
        with open(file_path, 'r') as f:
            morse_text = f.read().strip()
        
        # Get Morse dictionary from key
        morse_dict = key.get("morse_dict", {})
        reverse_morse_dict = {v: k for k, v in morse_dict.items()}
        
        # Split Morse code by spaces, treat each code as a letter (including '.-.-')
        morse_codes = morse_text.split(' ')
        decoded_text = ''
        for code in morse_codes:
            if code in reverse_morse_dict:
                decoded_text += reverse_morse_dict[code]
            elif code:  # Non-empty string not in dictionary
                decoded_text += '?'
        return decoded_text

    def create_qr_code(self, text, width, height):
        # Get border width from settings
        border_width = int(self.border_width.get()) if hasattr(self, 'border_width') and self.border_width.get() else 20
        
        # Create QR code with minimal border first
        qr = qrcode.QRCode(version=1, box_size=10, border=1)  # Use minimal border=1
        qr.add_data(text)
        qr.make(fit=True)

        # Generate the QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.convert('RGB')
        
        # Calculate the size of the QR code content area (excluding our custom border)
        content_width = width - 2 * border_width
        content_height = height - 2 * border_width
        
        if content_width <= 0 or content_height <= 0:
            raise ValueError("Border width is too large for the image dimensions")
        
        # Resize QR code to fit in the content area
        qr_img = qr_img.resize((content_width, content_height), Image.Resampling.LANCZOS)
        
        # Create final image with custom border
        final_img = Image.new('RGB', (width, height), 'white')
        
        # Paste the QR code in the center, leaving border space
        paste_x = border_width
        paste_y = border_width
        final_img.paste(qr_img, (paste_x, paste_y))

        key = {
            "original_text": text,
            "border_width": border_width,
            "content_area": (paste_x, paste_y, content_width, content_height)
        }
        return final_img, key

    def decode_qr_code(self, img):
        # Decode QR code using pyzbar
        # Try both RGB and grayscale, and resize to common QR sizes if needed
        sizes_to_try = [256, 384, 512, 768, 1024]
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img
        img_gray = img_rgb.convert('L')

        def try_decode(image):
            decoded_objs = pyzbar_decode(image)
            if decoded_objs:
                try:
                    return decoded_objs[0].data.decode('utf-8')
                except Exception:
                    return str(decoded_objs[0].data)
            return None

        # Try original size
        result = try_decode(img_rgb)
        if not result:
            result = try_decode(img_gray)

        # Try resizing if not successful
        if not result:
            for size in sizes_to_try:
                resized_rgb = img_rgb.resize((size, size), Image.Resampling.LANCZOS)
                resized_gray = img_gray.resize((size, size), Image.Resampling.LANCZOS)
                result = try_decode(resized_rgb)
                if result:
                    break
                result = try_decode(resized_gray)
                if result:
                    break

        if result:
            return result
        else:
            return "No QR code detected or could not decode. Tried multiple sizes. Try using a clear, uncompressed PNG and avoid resizing the QR code image."

    def create_chromatic_symphony(self, text, width, height, randomize=False):
        # Get border width
        border_width = int(self.border_width.get()) if hasattr(self, 'border_width') and self.border_width.get() else 20
        
        # Create image with white background (including border)
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Calculate working area (excluding border)
        work_x = border_width
        work_y = border_width
        work_width = width - 2 * border_width
        work_height = height - 2 * border_width
        
        if work_width <= 0 or work_height <= 0:
            raise ValueError("Border width is too large for the image dimensions")
        
        random.seed(None if randomize else 42)
        
        # Layer 1: Create gradient background (fill working area)
        if randomize:
            # Random gradient colors
            color1 = tuple(random.randint(50, 255) for _ in range(3))
            color2 = tuple(random.randint(50, 255) for _ in range(3))
            color3 = tuple(random.randint(50, 255) for _ in range(3))
            color4 = tuple(random.randint(50, 255) for _ in range(3))
        else:
            color1 = (135, 206, 250)  # Light sky blue
            color2 = (255, 192, 203)  # Light pink
            color3 = (144, 238, 144)  # Light green
            color4 = (255, 218, 185)  # Peach
        
        # Create gradient by blending colors across the working area
        for y in range(work_height):
            for x in range(work_width):
                # Normalize coordinates to 0-1
                nx = x / work_width
                ny = y / work_height
                
                # Bilinear interpolation between four corner colors
                top_color = tuple(int(color1[i] * (1-nx) + color2[i] * nx) for i in range(3))
                bottom_color = tuple(int(color3[i] * (1-nx) + color4[i] * nx) for i in range(3))
                final_color = tuple(int(top_color[i] * (1-ny) + bottom_color[i] * ny) for i in range(3))
                
                draw.point((work_x + x, work_y + y), fill=final_color)
        
        # Layer 2: Generate colorful geometric background shapes within working area
        num_shapes = 60 if randomize else 30
        for _ in range(num_shapes):
            shape_type = random.choice(['rect', 'ellipse', 'polygon'])
            color = tuple(random.randint(80, 220) for _ in range(3))
            alpha = random.randint(100, 180)  # Semi-transparent
            
            if shape_type == 'rect':
                x0 = random.randint(work_x, work_x + work_width - 60)
                y0 = random.randint(work_y, work_y + work_height - 60)
                x1 = min(work_x + work_width, x0 + random.randint(30, 100))
                y1 = min(work_y + work_height, y0 + random.randint(30, 100))
                # Create semi-transparent overlay
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([x0, y0, x1, y1], fill=(*color, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            elif shape_type == 'ellipse':
                x0 = random.randint(work_x, work_x + work_width - 60)
                y0 = random.randint(work_y, work_y + work_height - 60)
                x1 = min(work_x + work_width, x0 + random.randint(30, 100))
                y1 = min(work_y + work_height, y0 + random.randint(30, 100))
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.ellipse([x0, y0, x1, y1], fill=(*color, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            else:  # polygon
                num_points = random.randint(3, 6)
                points = []
                for _ in range(num_points):
                    px = random.randint(work_x, work_x + work_width)
                    py = random.randint(work_y, work_y + work_height)
                    points.append((px, py))
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.polygon(points, fill=(*color, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Layer 3: Place irregular geometric shapes with text encoding (no touching)
        draw = ImageDraw.Draw(img)  # Refresh draw object
        n = len(text)
        notes = []
        colors = []
        chars = []
        shapes_data = []
        
        placed_shapes = []  # Store (x, y, max_radius) for collision detection
        
        for idx, char in enumerate(text):
            # Determine shape size first
            base_size = random.randint(15, 35) if randomize else 25
            # Calculate maximum radius this shape could have (worst case for collision detection)
            max_shape_radius = base_size + 5  # Add small buffer
            
            # Try to find a position where this shape won't touch any existing shapes
            attempts = 0
            max_attempts = 100
            
            while attempts < max_attempts:
                # Generate random position within working area (with margin for shape size)
                margin = max_shape_radius + 10
                x = random.randint(work_x + margin, work_x + work_width - margin)
                y = random.randint(work_y + margin, work_y + work_height - margin)
                
                # Check if this shape would touch any existing shapes
                valid_position = True
                for px, py, prev_radius in placed_shapes:
                    distance = math.sqrt((x - px)**2 + (y - py)**2)
                    # Ensure shapes don't touch: distance between centers must be > sum of radii + small buffer
                    min_distance = max_shape_radius + prev_radius + 3 # 3px buffer to ensure no touching
                    if distance <= min_distance:
                        valid_position = False
                        break
                
                if valid_position:
                    break
                attempts += 1
            
            # If we couldn't find a good position after many attempts, use a fallback grid approach
            if attempts >= max_attempts:
                # Calculate grid position as fallback
                grid_cols = math.ceil(math.sqrt(n))
                grid_rows = math.ceil(n / grid_cols)
                cell_width = work_width / grid_cols
                cell_height = work_height / grid_rows
                
                row = idx // grid_cols
                col = idx % grid_cols
                x = work_x + int((col + 0.5) * cell_width)
                y = work_y + int((row + 0.5) * cell_height)
                
                # Ensure within bounds
                x = max(work_x + max_shape_radius, min(work_x + work_width - max_shape_radius, x))
                y = max(work_y + max_shape_radius, min(work_y + work_height - max_shape_radius, y))
            
            placed_shapes.append((x, y, max_shape_radius))
            
            # Generate color for character
            if randomize:
                color = tuple(random.randint(50, 255) for _ in range(3))
            else:
                color = (ord(char) * 83 % 256, ord(char) * 89 % 256, ord(char) * 97 % 256)
            
            colors.append(color)
            notes.append((x, y))
            chars.append(char)
            
            # Create irregular geometric shape (no borders)
            shape_types = ['star', 'hexagon', 'diamond', 'triangle', 'pentagon', 'irregular_blob']
            shape_type = random.choice(shape_types)
            
            if shape_type == 'star':
                # Create 5-pointed star
                points = []
                for i in range(10):  # 10 points for star (5 outer, 5 inner)
                    angle = (i * math.pi) / 5
                    if i % 2 == 0:  # Outer points
                        radius = base_size
                    else:  # Inner points
                        radius = base_size * 0.4
                    px = x + radius * math.cos(angle)
                    py = y + radius * math.sin(angle)
                    points.append((px, py))
                draw.polygon(points, fill=color)
                shapes_data.append(('star', x, y, base_size, points))
                
            elif shape_type == 'hexagon':
                points = []
                for i in range(6):
                    angle = (i * math.pi) / 3
                    px = x + base_size * math.cos(angle)
                    py = y + base_size * math.sin(angle)
                    points.append((px, py))
                draw.polygon(points, fill=color)
                shapes_data.append(('hexagon', x, y, base_size, points))
                
            elif shape_type == 'diamond':
                points = [
                    (x, y - base_size),      # Top
                    (x + base_size, y),      # Right
                    (x, y + base_size),      # Bottom
                    (x - base_size, y)       # Left
                ]
                draw.polygon(points, fill=color)
                shapes_data.append(('diamond', x, y, base_size, points))
                
            elif shape_type == 'triangle':
                points = [
                    (x, y - base_size),                    # Top
                    (x - base_size * 0.866, y + base_size * 0.5),  # Bottom left
                    (x + base_size * 0.866, y + base_size * 0.5)   # Bottom right
                ]
                draw.polygon(points, fill=color)
                shapes_data.append(('triangle', x, y, base_size, points))
                
            elif shape_type == 'pentagon':
                points = []
                for i in range(5):
                    angle = (i * 2 * math.pi) / 5 - math.pi/2  # Start from top
                    px = x + base_size * math.cos(angle)
                    py = y + base_size * math.sin(angle)
                    points.append((px, py))
                draw.polygon(points, fill=color)
                shapes_data.append(('pentagon', x, y, base_size, points))
                
            else:  # irregular_blob
                # Create irregular blob using multiple overlapping circles
                num_blobs = random.randint(3, 6)
                blob_points = []
                for i in range(num_blobs):
                    blob_x = x + random.randint(-base_size//3, base_size//3)
                    blob_y = y + random.randint(-base_size//3, base_size//3)
                    blob_size = random.randint(base_size//2, base_size)
                    draw.ellipse([blob_x - blob_size//2, blob_y - blob_size//2, 
                                blob_x + blob_size//2, blob_y + blob_size//2], fill=color)
                    blob_points.append((blob_x, blob_y, blob_size))
                shapes_data.append(('irregular_blob', x, y, base_size, blob_points))
        
        key = {
            "notes": notes,
            "colors": colors,
            "chars": chars,
            "width": width,
            "height": height,
            "work_area": (work_x, work_y, work_width, work_height),
            "border_width": border_width,
            "randomized": randomize,
            "shapes_data": shapes_data,
        }
        return img, key

    def decode_chromatic_symphony(self, img, key):
        colors = key["colors"]
        notes = key.get("notes", [])
        chars = key.get("chars", [])
        shapes_data = key.get("shapes_data", [])
        border_width = key.get("border_width", 20)
        tolerance = 25  # Color tolerance for matching
        
        text = ""
        img_rgb = img.convert('RGB')
        
        for idx, expected_color in enumerate(colors):
            if idx < len(notes):
                x, y = notes[idx][:2]
                found_pixel = None
                
                # Search within a reasonable radius around the center for the expected color
                search_radius = 20  # Search within shape area
                for dx in range(-search_radius, search_radius + 1):
                    for dy in range(-search_radius, search_radius + 1):
                        if dx*dx + dy*dy <= search_radius*search_radius:  # Within circular area
                            px = int(x + dx)
                            py = int(y + dy)
                            if 0 <= px < img_rgb.width and 0 <= py < img_rgb.height:
                                pixel_color = img_rgb.getpixel((px, py))
                                # Check if pixel matches expected color within tolerance
                                if all(abs(pixel_color[i] - expected_color[i]) <= tolerance for i in range(3)):
                                    found_pixel = pixel_color
                                    break
                    if found_pixel:
                        break
                
                if found_pixel is not None:
                    # Use the character from the key
                    if idx < len(chars):
                        text += chars[idx]
                    else:
                        text += '?'
                else:
                    text += '?'  # No matching color found
            else:
                text += '?'  # Missing note
                
        return text

    def create_cosmic_constellation(self, text, width, height, randomize=False):
        # New method: Each character/group is a primary star, with up to 7 secondary stars
        # Get border width from argument or default
        border_width = 20
        try:
            border_width = int(self.border_width.get())
        except Exception:
            pass
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        # Draw black background inside border
        draw.rectangle([border_width, border_width, width - border_width, height - border_width], fill='black')
        n = len(text)
        max_secondary = 10
        primary_stars = []
        connections = []
        random.seed(None if randomize else 42)

        # Place primary stars using grid layout to minimize intersections
        margin = 60
        grid_cols = math.ceil(math.sqrt(n))
        grid_rows = math.ceil(n / grid_cols)
        cell_w = (width - 2 * margin) // grid_cols
        cell_h = (height - 2 * margin) // grid_rows
        used_positions = set()
        for i, char in enumerate(text):
            row = i // grid_cols
            col = i % grid_cols
            x = margin + col * cell_w + cell_w // 2
            y = margin + row * cell_h + cell_h // 2
            # Add small random jitter to avoid perfect grid
            x += random.randint(-cell_w//4, cell_w//4)
            y += random.randint(-cell_h//4, cell_h//4)
            # Ensure no overlap
            while (x, y) in used_positions:
                x += random.randint(-10, 10)
                y += random.randint(-10, 10)
            used_positions.add((x, y))
            primary_stars.append({
                "char": char,
                "pos": (x, y),
                "connections": []
            })

        # Assign unique (ones, zeros) pairs to each unique character
        unique_chars = list(dict.fromkeys(text))
        char_to_combo = {}
        used_combinations = set()
        combo_list = []
        # Generate all possible (ones, zeros) pairs
        for total in range(1, max_secondary + 1):
            for ones in range(0, total + 1):
                zeros = total - ones
                combo_list.append((ones, zeros))
        combo_idx = 0
        for char in unique_chars:
            # Assign next available combination
            while combo_idx < len(combo_list):
                ones, zeros = combo_list[combo_idx]
                key_str = f"{ones},{zeros}"
                if key_str not in used_combinations:
                    char_to_combo[char] = (ones, zeros)
                    used_combinations.add(key_str)
                    break
                combo_idx += 1

        # Adjust line thickness and length for consistency
        line_thickness = 3  # Set consistent thickness for all lines
        primary_to_secondary_length_factor = 1.2  # Slightly increase length of primary to secondary lines

        # Draw primary stars
        for star in primary_stars:
            x, y = star["pos"]
            draw.ellipse([x-12, y-12, x+12, y+12], fill="yellow", outline="white", width=line_thickness)

        # Draw primary to primary star lines first
        for i in range(n):
            x1, y1 = primary_stars[i]["pos"]
            distances = []
            for j in range(n):
                if j != i:
                    x2, y2 = primary_stars[j]["pos"]
                    dist = (x2-x1)**2 + (y2-y1)**2
                    distances.append((dist, j))
            distances.sort()
            connected = 0
            for _, j in distances:
                if connected >= 3:
                    break
                x2, y2 = primary_stars[j]["pos"]
                dx = x2 - x1
                dy = y2 - y1
                length = math.sqrt(dx*dx + dy*dy)
                if length == 0:
                    continue
                ext_factor = 1.12
                ex1 = int(x1 - dx * 0.06)
                ey1 = int(y1 - dy * 0.06)
                ex2 = int(x2 + dx * (ext_factor-1+0.06))
                ey2 = int(y2 + dy * (ext_factor-1+0.06))
                intersects = False
                for (a1, a2) in connections:
                    if (min(ex1,ex2)-5 <= max(a1[0],a2[0]) and max(ex1,ex2)+5 >= min(a1[0],a2[0]) and
                        min(ey1,ey2)-5 <= max(a1[1],a2[1]) and max(ey1,ey2)+5 >= min(a1[1],a2[1])):
                        intersects = True
                        break
                if not intersects:
                    draw.line([ex1, ey1, ex2, ey2], fill="white", width=line_thickness)
                    connections.append(((ex1, ey1), (ex2, ey2)))
                    primary_stars[i]["connections"].append(j)
                    connected += 1

        # Draw primary to secondary star lines with a distinct color
        secondary_line_color = "blue"  # Use a distinct color for primary to secondary lines
        char_map = {}
        for idx, star in enumerate(primary_stars):
            x, y = star["pos"]
            char = star["char"]
            ones, zeros = char_to_combo[char]
            key_str = f"{ones},{zeros}"
            char_map[key_str] = char
            num_secondary = ones + zeros
            sec_info = []
            used_angles = []
            base_angle = random.uniform(0, 2*math.pi)
            angle_spread = math.pi * 1.5
            bit_pattern = ['1'] * ones + ['0'] * zeros
            for s in range(num_secondary):
                attempts = 0
                while True:
                    angle = (base_angle + angle_spread * (s+1)/(num_secondary+1) + random.uniform(-0.2, 0.2)) % (2*math.pi)
                    too_close = any(abs((angle - ua + math.pi) % (2*math.pi) - math.pi) < 0.3 for ua in used_angles)
                    if not too_close or attempts > 10:
                        break
                    attempts += 1
                bit = bit_pattern[s]
                line_len = int((20 if bit == '0' else 40) * primary_to_secondary_length_factor)
                sx = x + int(line_len * math.cos(angle))
                sy = y + int(line_len * math.sin(angle))
                draw.ellipse([sx-7, sy-7, sx+7, sy+7], fill="cyan", outline="white", width=line_thickness)
                draw.line([x, y, sx, sy], fill=secondary_line_color, width=line_thickness)
                sec_info.append({"pos": (sx, sy), "len": line_len, "bit": bit, "angle": angle})
                used_angles.append(angle)
            star["num_secondary"] = num_secondary
            star["secondary_info"] = sec_info
        # Only store primary star positions and character map
        key = {
            "primary_stars": [{"pos": star["pos"]} for star in primary_stars],
            "char_map": char_map,
            "method": "Cosmic Constellation",
            "width": width,
            "height": height,
            "max_secondary": max_secondary,
            "randomized": randomize
        }
        return img, key

    def decode_cosmic_constellation(self, img, key):
        # Image-based decoding for cosmic constellation
        primary_stars = key.get("primary_stars", [])
        char_map = key.get("char_map", {})
        text = ""
        img_rgb = img.convert('RGB')
        black_threshold = 30
        primary_to_secondary_length_factor = 1.2
        short_len = int(20 * primary_to_secondary_length_factor)
        long_len = int(40 * primary_to_secondary_length_factor)
        distance_threshold = (short_len + long_len) // 2
        secondary_dot_radius = 7  # Should match encoder
        secondary_line_color = (0, 0, 255)  # Blue
        for idx, star in enumerate(primary_stars):
            x, y = star["pos"]
            pixel = img_rgb.getpixel((x, y))
            if all(v < black_threshold for v in pixel):
                text += "?"
                continue
            # Step 1: Find cyan secondary star regions (0,255,255) within radius
            search_radius = 50
            cyan_pixels = []
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    sx, sy = x + dx, y + dy
                    if sx < 0 or sy < 0 or sx >= img_rgb.width or sy >= img_rgb.height:
                        continue
                    pixel = img_rgb.getpixel((sx, sy))
                    if abs(pixel[0] - 0) < 20 and abs(pixel[1] - 255) < 20 and abs(pixel[2] - 255) < 20:
                        cyan_pixels.append((sx, sy))
            # Step 2: Cluster cyan pixels into circles (secondary stars)
            secondary_centers = []
            used = set()
            for i, (px, py) in enumerate(cyan_pixels):
                if i in used:
                    continue
                # Find all pixels within a circle radius
                cluster = [(px, py)]
                used.add(i)
                for j, (qx, qy) in enumerate(cyan_pixels):
                    if j in used:
                        continue
                    if math.hypot(px - qx, py - qy) < secondary_dot_radius*1.5:
                        cluster.append((qx, qy))
                        used.add(j)
                # Find center of cluster
                if cluster:
                    cx = int(sum(p[0] for p in cluster) / len(cluster))
                    cy = int(sum(p[1] for p in cluster) / len(cluster))
                    secondary_centers.append((cx, cy))
                if len(secondary_centers) >= key.get("max_secondary", 7):
                    break
            # Step 3: Calculate distances from primary star to secondary centers
            ones = 0
            zeros = 0
            for sec_idx, (sx, sy) in enumerate(secondary_centers):
                dist = int(((sx - x) ** 2 + (sy - y) ** 2) ** 0.5)
                if dist > distance_threshold:
                    ones += 1
                else:
                    zeros += 1
            key_str = f"{ones},{zeros}"
            char = char_map.get(key_str, "?")
            text += char
        return text

    def decode_blob_impressionism(self, img, key):
        centers = key.get("centers", [])
        char_area_map = key.get("char_area_map", {})
        tolerance = 6  # Area tolerance for matching
        img_gray = img.convert('L')
        decoded_text = ""
        import numpy as np
        w, h = img_gray.size
        img_np = np.array(img_gray)
        for idx, (x, y) in enumerate(centers):
            # Create mask for flood fill
            mask = np.zeros((h, w), dtype=np.uint8)
            stack = [(x, y)]
            while stack:
                px, py = stack.pop()
                if px < 0 or py < 0 or px >= w or py >= h:
                    continue
                if mask[py, px]:
                    continue
                pixel = img_np[py, px]
                if pixel < 40:  # Black blob threshold
                    mask[py, px] = 1
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                stack.append((px + dx, py + dy))
            area = int(np.sum(mask))
            # Find character with lowest area difference
            min_diff = None
            best_char = "?"
            for a, c in char_area_map.items():
                try:
                    a_int = int(a)
                except Exception:
                    a_int = a
                diff = abs(a_int - area)
                if min_diff is None or diff < min_diff:
                    min_diff = diff
                    best_char = c
            decoded_text += best_char
        return decoded_text
    
    def create_blob_impressionism(self, text, width, height):
        # Settings
        border_width = int(self.border_width.get()) if hasattr(self, 'border_width') and self.border_width.get() else 20
        min_distance = 10  # Minimum distance between blobs
        work_x = border_width
        work_y = border_width
        work_width = width - 2 * border_width
        work_height = height - 2 * border_width
        if work_width <= 0 or work_height <= 0:
            raise ValueError("Border width is too large for the image dimensions")
        min_area = max(30, int(0.005 * work_width * work_height))
        max_area = max(80, int(0.04 * work_width * work_height))
        # Create image with light grey background
        img = Image.new('RGB', (width, height), (230, 230, 230))
        draw = ImageDraw.Draw(img)
        # Draw border as a solid white rectangle
        if border_width > 0:
            draw.rectangle([0, 0, width-1, height-1], outline='white', width=border_width)
            # Fill inside border with light grey again to avoid double border
            draw.rectangle([border_width, border_width, width-border_width-1, height-border_width-1], fill=(230, 230, 230))
        # Generate unique areas for each character
        unique_chars = list(dict.fromkeys(text))
        n_unique = len(unique_chars)
        # Assign unique area to each unique character
        area_step = max(3, int(0.02 * work_width * work_height / n_unique))
        unique_areas = list(range(min_area, min_area + n_unique * area_step, area_step))
        random.shuffle(unique_areas)
        char_to_area = {char: unique_areas[i] for i, char in enumerate(unique_chars)}
        char_area_map = {str(unique_areas[i]): char for i, char in enumerate(unique_chars)}
        centers = []
        areas = []
        placed_blobs = []
        import numpy as np
        total_blob_area = 0
        for idx, char in enumerate(text):
            area = char_to_area[char]
            radius = int((area / math.pi) ** 0.5)
            attempts = 0
            max_attempts = 100
            while attempts < max_attempts:
                x = random.randint(work_x + radius + min_distance, work_x + work_width - radius - min_distance)
                y = random.randint(work_y + radius + min_distance, work_y + work_height - radius - min_distance)
                valid = True
                for cx, cy, cr in placed_blobs:
                    dist = math.hypot(x - cx, y - cy)
                    if dist < cr + radius + min_distance:
                        valid = False
                        break
                if valid:
                    break
                attempts += 1
            if attempts == max_attempts:
                # fallback: grid placement
                grid_cols = math.ceil(math.sqrt(len(text)))
                grid_rows = math.ceil(len(text) / grid_cols)
                cell_w = work_width / grid_cols
                cell_h = work_height / grid_rows
                row = idx // grid_cols
                col = idx % grid_cols
                x = work_x + int((col + 0.5) * cell_w)
                y = work_y + int((row + 0.5) * cell_h)
            # Draw irregular blob shape
            num_points = random.randint(8, 16)
            angle_step = 2 * math.pi / num_points
            points = []
            for i in range(num_points):
                angle = i * angle_step
                # Vary radius for blob effect
                r = radius * (0.7 + 0.6 * random.random())
                px = x + r * math.cos(angle)
                py = y + r * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, fill='black')
            # Measure true area using flood fill and numpy
            img_gray = img.convert('L')
            w, h = img_gray.size
            mask = np.zeros((h, w), dtype=np.uint8)
            stack = [(x, y)]
            while stack:
                px, py = stack.pop()
                if px < 0 or py < 0 or px >= w or py >= h:
                    continue
                if mask[py, px]:
                    continue
                pixel = img_gray.getpixel((px, py))
                if pixel < 40:
                    mask[py, px] = 1
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                stack.append((px + dx, py + dy))
            measured_area = int(np.sum(mask))
            centers.append((x, y))
            areas.append(measured_area)
            placed_blobs.append((x, y, radius))
            # Update char_area_map for this character with measured area
            char_area_map[str(measured_area)] = char
            total_blob_area += measured_area
        drawable_area = work_width * work_height
        if total_blob_area > 0.8 * drawable_area:
            messagebox.showwarning("Warning", "Total blob area exceeds 80% of drawable area. Encoding may give issues.")
        key = {
            "centers": centers,
            "areas": areas,
            "char_area_map": char_area_map,
            "method": "Blob Impressionism",
            "width": width,
            "height": height,
            "border_width": border_width
        }
        return img, key

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualTextEncoder(root)
    root.mainloop()
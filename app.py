from flask import Flask, render_template, request, send_file
from huffmancode import HuffmanCoding
import os
import tempfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    try:
        # Create a new HuffmanCoding instance for each request
        huffman = HuffmanCoding()
        
        # Read and compress the file content
        text = file.read().decode('utf-8')
        encoded_text, codes = huffman.compress(text)

        # Create temporary files with unique names
        compressed_path = os.path.join(UPLOAD_FOLDER, f'compressed_{os.urandom(8).hex()}.bin')
        codes_path = os.path.join(UPLOAD_FOLDER, f'codes_{os.urandom(8).hex()}.txt')

        # Save the compressed data
        with open(compressed_path, 'w') as f:
            f.write(encoded_text)

        # Save the Huffman codes for later decompression
        with open(codes_path, 'w') as f:
            for char, code in codes.items():
                f.write(f"{repr(char)}:{code}\n")

        # Send the compressed file and clean up
        response = send_file(compressed_path,
                           as_attachment=True,
                           download_name='compressed.bin')
        
        # Clean up temporary files after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(compressed_path)
                os.remove(codes_path)
            except:
                pass

        return response

    except Exception as e:
        return f'Error during compression: {str(e)}', 500

@app.route('/decompress', methods=['POST'])
def decompress():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    try:
        # Create a new HuffmanCoding instance for each request
        huffman = HuffmanCoding()
        
        # Read the compressed content
        encoded_text = file.read().decode('utf-8')

        # Create a temporary file for decompressed output
        decompressed_path = os.path.join(UPLOAD_FOLDER, f'decompressed_{os.urandom(8).hex()}.txt')

        # Load the most recent Huffman codes
        codes_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith('codes_')]
        if not codes_files:
            return 'No codes file found for decompression', 400
            
        latest_codes = max(codes_files, key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)))
        codes_path = os.path.join(UPLOAD_FOLDER, latest_codes)

        with open(codes_path, 'r') as f:
            for line in f:
                char, code = line.strip().split(':')
                char = eval(char)  # safely convert string representation back to character
                huffman.reverse_codes[code] = char

        # Decompress the text
        decoded_text = huffman.decompress(encoded_text)

        # Save and send the decompressed text
        with open(decompressed_path, 'w') as f:
            f.write(decoded_text)

        response = send_file(decompressed_path,
                           as_attachment=True,
                           download_name='decompressed.txt')

        # Clean up temporary files after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(decompressed_path)
            except:
                pass

        return response

    except Exception as e:
        return f'Error during decompression: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)
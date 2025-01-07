class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

class HuffmanCoding:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_codes = {}

    def make_frequency_dict(self, text):
        """Create frequency dictionary for each character in text"""
        frequency = {}
        for character in text:
            if character not in frequency:
                frequency[character] = 0
            frequency[character] += 1
        return frequency

    def make_heap(self, frequency):
        """Create a priority queue from frequency dict"""
        from heapq import heappush
        self.heap = []  # Reset heap for new compression
        for key in frequency:
            node = HuffmanNode(key, frequency[key])
            heappush(self.heap, (node.freq, id(node), node))

    def merge_nodes(self):
        """Merge nodes until we get the root of Huffman Tree"""
        from heapq import heappush, heappop
        while len(self.heap) > 1:
            freq1, _, node1 = heappop(self.heap)
            freq2, _, node2 = heappop(self.heap)

            merged = HuffmanNode(None, freq1 + freq2)
            merged.left = node1
            merged.right = node2

            heappush(self.heap, (merged.freq, id(merged), merged))

    def make_codes_helper(self, node, current_code):
        """Recursive helper function to generate Huffman codes"""
        if node is None:
            return

        if node.char is not None:
            self.codes[node.char] = current_code
            self.reverse_codes[current_code] = node.char
            return

        self.make_codes_helper(node.left, current_code + "0")
        self.make_codes_helper(node.right, current_code + "1")

    def make_codes(self):
        """Generate Huffman codes for characters"""
        if not self.heap:
            return
        _, _, root = self.heap[0]
        self.codes = {}  # Reset codes for new compression
        self.reverse_codes = {}  # Reset reverse_codes for new compression
        self.make_codes_helper(root, "")

    def get_encoded_text(self, text):
        """Get encoded text using Huffman codes"""
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text

    def compress(self, text):
        """Compress the input text"""
        frequency = self.make_frequency_dict(text)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()

        encoded_text = self.get_encoded_text(text)
        return encoded_text, self.codes

    def decompress(self, encoded_text):
        """Decompress the encoded text"""
        current_code = ""
        decoded_text = ""

        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_codes:
                character = self.reverse_codes[current_code]
                decoded_text += character
                current_code = ""

        return decoded_text
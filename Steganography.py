from cryptography.fernet import Fernet
from PIL import Image, ImageChops
import numpy as np
from typing import Tuple


class Steganography:
    def __init__(self):
        # const and message
        self.bit_per_pixel: int = 2
        self.char_len: int = 7
        self.message_raw: str = ''
        # encode message
        self.message: str = ''
        self.binary_message: str = ''
        self.binary_message_list: [str] = []
        self.picture_values: np.array = None
        self.picture_values_with_message: np.array = None
        # tuple data for picture shape
        self.picture_shape: Tuple = ()
        self.private_key: str = ''
        self.encrypted_message: str = ''
        self.generate_key()

    # change const values for configuration
    def config(self, bit_per_pixel: int = 2, char_len: int = 7):
        self.bit_per_pixel = bit_per_pixel
        self.char_len = char_len

    # load message to instance, encrypt with key and convert into bits
    def load_message(self, message_input: str):
        if len(message_input) == len(message_input.encode('utf-8')) and len(message_input) != 0 and all(
                ord(char) < 128 for char in message_input):
            self.message_raw = message_input
            # store byte array
            self.message = self.message_raw.encode('utf-8')
            # encrypt message and pass to message raw
            self.encrypt_message()
            self.message_raw = self.encrypted_message
            # create binary representation of encrypted message
            self.binary_message = self.text_to_bits(self.message_raw)
            self.create_bin_list()
        else:
            # throw exception iv message is not ascii or is empty
            raise Exception("Invalid message")

    # convert message to binary string
    def convert_message(self):
        binary_string: str = ''
        for letter in self.message:
            binary_string += bin(letter)[2:]
        self.binary_message = binary_string

    # create list of bits to save in each pixel
    # length of element in list is equal to bits per pixel
    def create_bin_list(self):
        binary_list_buffer: [str] = []
        for i in range(0, len(self.binary_message), self.bit_per_pixel):
            temp_fragment = self.binary_message[i:i + self.bit_per_pixel]
            # fill empty pixel with '0'
            if len(temp_fragment) != self.bit_per_pixel:
                temp_fragment += '0' * (self.bit_per_pixel - len(temp_fragment))
            binary_list_buffer.append(temp_fragment)
        # copy buffer to instance member
        self.binary_message_list = binary_list_buffer.copy()

    # load image into instance as numpy array
    def load_image(self, image_path: str):
        try:
            im = Image.open(image_path)
            self.picture_values = np.copy(np.asarray(im))
            self.picture_values_with_message = np.copy(self.picture_values)
            self.picture_shape = self.picture_values.shape
        except FileNotFoundError:
            print("Wrong image path")

    # save image with actual instance bitmap
    def save_image(self, image_path: str):
        pass

    # prototype of first convert function
    def bits2string(self, bit_string: str) -> str:
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(bit_string)] * self.char_len))

    # convert text into bits
    def text_to_bits(self, text: str, encoding='utf-8', errors='surrogatepass') -> str:
        bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    # convert bits into text
    def text_from_bits(self, bits: str, encoding='utf-8', errors='surrogatepass') -> str:
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

    # save each list element into pixel
    def write_message(self):
        message_counter: int = 0
        if self.message != '':
            # try except block for handling multiple break statement
            try:
                for a in range(self.picture_shape[0]):
                    for b in range(self.picture_shape[1]):
                        for c in range(self.picture_shape[2]):
                            # break loops if there is no more data to store
                            if message_counter >= len(self.binary_message_list):
                                raise Exception
                            # slice LSBits of original picture bitmap and fill it with bits from message
                            temp_value = '{:08b}'.format(self.picture_values[a, b, c])[:-self.bit_per_pixel] + \
                                         self.binary_message_list[message_counter]
                            message_counter += 1
                            # update pixel in modded picture
                            self.picture_values_with_message[a, b, c] = int(temp_value, 2)
            # using exception as break for nested loops
            except Exception:
                pass

    # read hidden message from picture
    def read_message(self) -> str:
        message_buffer: str = ''
        message_counter: int = 0
        # try except block for handling multiple break statement
        try:
            for a in range(self.picture_shape[0]):
                for b in range(self.picture_shape[1]):
                    for c in range(self.picture_shape[2]):
                        # break loops if there is no more data to read
                        if message_counter >= len(self.binary_message_list):
                            raise Exception
                        # read LSBits from picture and add into string buffer
                        temp_value = '{:08b}'.format(self.picture_values_with_message[a, b, c])[-self.bit_per_pixel:]
                        message_counter += 1
                        message_buffer += temp_value
        # using exception as break for nested loops
        except Exception as error:
            pass
        # return string from bits buffer
        return self.text_from_bits(message_buffer)

    # generate custom private key for encryption
    def generate_key(self):
        generated_key = Fernet.generate_key()
        self.private_key = generated_key

    # read private key for encryption from file
    def load_key(self, key_path: str):
        with open(key_path, 'rb') as file:
            self.private_key = file.read()

    # encrypt raw message with given private key
    def encrypt_message(self):
        fernet = Fernet(self.private_key)
        self.encrypted_message = fernet.encrypt(self.message).decode()

    # decrypt raw message with given private key
    def decrypt_message(self, message: str) -> str:
        fernet = Fernet(self.private_key)
        return fernet.decrypt(message).decode()


if __name__ == '__main__':

    msg = '''this is test message'''

    s = Steganography()
    s.load_message(msg)
    print(s.message_raw)
    print(s.binary_message)
    print(s.private_key)
    s.load_image('dog.jpg')
    s.write_message()

    im1 = Image.fromarray(s.picture_values)
    im2 = Image.fromarray(s.picture_values_with_message)

    im1.show()
    im2.show()

    print("encrypted message:")
    out = s.read_message().encode()
    print(out)
    out_true = s.decrypt_message(out)
    print(out_true)

    print("image comparison:")
    diff = ImageChops.difference(im1, im2)

    if diff.getbbox():
        print("images are different")
    else:
        print("images are the same")

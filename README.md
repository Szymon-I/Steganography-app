# Steganography-app
Warning : project in development

This application is my own implementation of steganography.
It allows to save byte stream to given image with additional cryptography (private key).
Bassicaly it saves each bits of byte stream into less significant bits of int values of rgb matrix (image).
As a result we receive modified image with hidden additional information, 
that cannot be distinguished from the original with the naked eye, or even algorithms without original image.
With encoded every value of rgb matrix and using 2 bits per color value, total distorion is about 1.17% of orginal (for example dog image).

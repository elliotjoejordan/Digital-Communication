import heapq as h
from bitstring import BitArray
import sys
from collections import defaultdict
from time import clock


# Code reads in file name, and assigns variables for write-out and read-in names based on existing extension and name
name = sys.argv[-1]
if str(name[-4:]) == '.txt':
    hcType = name[:-4] +'.hc'
    txtType = name[:-4] + '.txt'
    txtType2 = name[:-4] + '_2.txt'

else:
    hcType = name
    txtType = name[:-3] + '.txt'
    txtType2 = name[:-3] + '_2.txt'



def createTree(iterable):
    # Takes as input a dictionary of character-frequency pairs
    # Creates a heap 'binaryTree' which is ordered by frequency and contains character-codeword tuples
    # At each iteration, combines the two most frequent characters
    # adds a '0' or '1' to their codewords based on whether they are the left or right child
    # Builds codewords as it creates the tree
    binaryTree = [[freq, [letter, '']] for letter, freq in iterable.items()]
    h.heapify(binaryTree)
    while len(binaryTree) >1:
        part1 = h.heappop(binaryTree)
        for x in part1[1:]:
            x[1] = '0' + x[1]
        part2 = h.heappop(binaryTree)
        for y in part2[1:]:
            y[1] = '1' + y[1]
        h.heappush(binaryTree, [part1[0] + part2[0]] + part1[1:] + part2[1:])
    # Returns the heap sorted first by codeword size, and second by alphabet - For canonical encoding
    return sorted(h.heappop(binaryTree)[1:], key=lambda p: (len(p[-1]), p))



def createCode(codeHeap, data):
    # Uses codewords and raw data to encode data
    # Makes codewords into a dictionary for ease of reference
    strOut = ''
    q = dict(codeHeap)
    for char in data:
        try:
            strOut += q[char]
        except:
            pass
    # Returns encoded string
    return strOut

def canonical(encoded):
    # Starts with codewords sorted by length then alphabet for the corresponding character
    # Rewrites first codeword as zeros of the same length
    # each element is the binary value of the previous element +1, and padded with zeros
    len1 = len(encoded[0][1])
    encoded[0][1] = ''
    for i in range(len1):
        encoded[0][1] += '0'
    for i in range(1,len(encoded)):
        length = len(encoded[i][1])
        val = encoded[i-1][1]
        valLen = len(val)
        encoded[i][1] = ''
        new = bin(int(val, 2) + 1) # Adds 1 to value in binary
        new = new[2:]
        while len(new) < valLen:
            new = '0' + new # Pads front of binary number with zeros first as needed to ensure the same length as the previous codeword
        while len(new) < length:
            new += '0' # Pads end of binary number with zeros to equal the length of the current codeword
        encoded[i][1] = new
    # Returns a canonically encoded tree
    return encoded



def  encode():
    # Call functions to create tree, then uses on data to create and save a binary encoded version
    print('encoding...')
    # Read input data file
    # load file and convert to string
    file = open(txtType, "r")
    fileString = file.read()
    file.close()

    data = fileString
    # Loops through characters to calculate frequencies
    frequencies = defaultdict(int)
    for character in data:
        frequencies[character] +=1
    # Uses frequencies to create canonical tree for encoding
    encoded = createTree(frequencies)
    encoded = canonical(encoded)
    keyForDecode = []
    # Adds character-length pairs to front of binary string to be used for canonical decoding
    for x in encoded:
        keyForDecode.append(bin(len(x[1]))[2:].zfill(8))
        keyForDecode.append(bin(ord(x[0]))[2:].zfill(8))
    binary = ''
    for i in keyForDecode:
        binary += i
    # Adds '}' to mark the end of the key
    binary += bin(ord('}'))[2:].zfill(8)
    # Adds encoded string
    binary += createCode(encoded, data)
    dif = len(binary)%8
    if dif == 0:
        dif = 8
    zeroes = 8 - dif
    # Adds number of zeroes to the front which will need to be removed from the end (because encoded in 8-bit chunks)
    binary = bin(ord(str(zeroes)))[2:].zfill(8) + binary
    output = BitArray(bin=binary)

    # Write output to file .hc
    file2 = open(hcType, "wb")
    output.tofile(file2)
    file2.close()
    print('encoded time: ' , clock())

### DECODING ###


def getLengths(binary, lengths, bitsToGo):
    # Recursive function which reads the character-length pairs from the front of the binary file
    # Recursion stops when it reaches '}'
    if chr(int(binary[bitsToGo:(bitsToGo+8)], 2)) == '}':
        bitsToGo += 8
        lengths.append(bitsToGo)
        return lengths
    else:
        s1 = int(binary[bitsToGo:(bitsToGo+8)], 2)
        s2 = chr(int(binary[(bitsToGo+8):(bitsToGo+16)], 2))
        lengths.append([s2, s1]) # character and length added to list
        bitsToGo += 16 # current location incremented
        getLengths(binary, lengths, bitsToGo)
        return lengths


def decode():
    # Reads a file to decode
    # reads lengths off front of binary string, as well as the number of zeros needing to be removed from the end
    # Uses lengths to reconstruct canonical tree
    # Uses tree to translate the binary encoded string back to text
    # Saves and outputs text
    print('decoding...')
    file3 = open(hcType, "rb")
    returned = file3.read()
    file3.close()
    now = clock()
    string = ''
    for char in returned:
        string += str(format(char, '08b')) # Required to return from binary format to a string
    zeroes = chr(int(string[:8], 2))
    string = string[8:]
    lengths = []
    bitsToGo = 0
    # Bits to go is used in place of needing to alter (and rewrite) the full binary
    lengthAndString = getLengths(string, lengths, bitsToGo)
    bitsToGo = lengthAndString[-1]
    lengths = lengthAndString[:-1]
    string = string[bitsToGo:]
    # Removes outstandng zeros if necesary
    if zeroes != '0':
        string = string[:-int(zeroes)]

    # Uses lengths to reconstruct codewords
    encoded = []
    str1 = ''
    for i in range(int(lengths[0][1])):
        str1 += '0'
    encoded.append([lengths[0][0], str1])
    for i in range(1,len(lengths)):
        length = int(lengths[i][1])
        val = encoded[i-1][1]
        valLen = len(val)
        new = bin(int(val, 2) + 1)
        new = new[2:]
        while len(new) < valLen:
            new = '0' + new
        while len(new) < length:
            new += '0'
        encoded.append([lengths[i][0], new])
    treeDict = {k: v for v, k in encoded}
    # Recreates tree as dictionary for lookup when decoding
    text = ''
    letter = ''
    for i in string:
        letter += i
        if letter in treeDict.keys():
            text += treeDict[letter]
            letter = ''
    # Writes decoded file
    file2 = open(txtType2, "w+")
    file2.truncate(0)
    file2.seek(0)
    file2.write(text)
    file2.close()
    print('decoding time: ', clock()-now)


# Decides based on input whether to encode, decode, or both
if sys.argv[1] == 'encode':
    if name[-4:] != '.txt':
        print('non-text file rejected')
    else:
        encode()
elif sys.argv[1] == 'decode':
    if name[-3:] != '.hc':
        print('non-hc file rejected')
    else:
        decode()
else:
    if name[-4:] != '.txt':
        print('non-text file rejected')
    else:
        encode()
        decode()

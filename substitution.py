#!/usr/bin/python

import functools, math, string, re, random, heapq
from segment import *

trigramLetterProb = OneGramDist('count-3l.txt')
bigramLetterProb = OneGramDist('count-2l.txt')

def letterNGrams(msg, n):
   return [msg[i:i+n] for i in range(len(msg) - (n-1))]

def trigramStringProb(msg):
   return sum(math.log10(trigramLetterProb(trigram)) 
              for trigram in letterNGrams(msg, 3))

alphabet = "abcdefghijklmnopqrstuvwxyz"
def encrypt(msg, key): return msg.translate(string.maketrans(alphabet, key))
def decrypt(msg, key): return msg.translate(string.maketrans(key, alphabet))
def keySwap(key, a, b): return key.translate(string.maketrans(a+b, b+a))

def localMaximum(msg, key, decryptionFitness, numSteps):
   decryption = decrypt(msg, key)
   value = decryptionFitness(decryption)
   neighbors = iter(neighboringKeys(key, decryption))

   for step in range(numSteps):
      nextKey = neighbors.next()
      nextDecryption = decrypt(msg, nextKey)
      nextValue = decryptionFitness(nextDecryption)

      if nextValue > value:
         key, decryption, value = nextKey, nextDecryption, nextValue
         neighbors = iter(neighboringKeys(key, decryption))
         print(decryption[:80])

   return decryption

# an iterator over some neighboring keys, heuristically chosen by 
# repairing uncommon bigrams in the decoded message
def neighboringKeys(key, decryptedMsg):
   value = bigramLetterProb
   bigrams = sorted(letterNGrams(decryptedMsg, 2), key=value)

   for c1, c2 in bigrams:
      for a in shuffled(alphabet):
         if c1 == c2 and value(a+a) > value(c1+c2):
            yield keySwap(key, a, c1)
         else:
            if value(a+c2) > value(c1+c2):
               yield keySwap(key, a, c1)
            if value(c1+a) > value(c1+c2):
               yield keySwap(key, a, c2)

   while True:
      yield keySwap(key, random.choice(alphabet), random.choice(alphabet))


def shuffled(s):
   sList = list(s)
   random.shuffle(sList)
   return ''.join(sList)

def preprocessInputMessage(chars):
   return ''.join(re.findall('[a-z]+', chars.lower()))

def crackSubstitution(msg, numSteps = 7000, restarts = 20):
   msg = preprocessInputMessage(msg)
   print("decrypting message: %s" % msg)

   startingKeys = [shuffled(alphabet) for i in range(restarts)]
   localMaxes = [localMaximum(msg, key, trigramStringProb, numSteps) 
                 for key in startingKeys]
   
   for x in localMaxes:
      (prob, words) = segmentWithProb(x)
      print(trigramLetterProb(x), prob, words)

   prob, words = max(segmentWithProb(decryption) for decryption in localMaxes)
   return ' '.join(words)

def testDecryption(msg):
   crackSubstitution(encrypt(msg, shuffled(alphabet)))

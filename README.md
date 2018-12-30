# mtg-inventory
Scryfall Magic card database with API:
https://scryfall.com/

## Sum Squared
If your perceptual hash is 42 floating-point digits, you need to use Sum Squared to compare.

http://www.fmwconcepts.com/imagemagick/phashcompare/index.php

## ImageMagick
Appears to support perceptual hashing

https://stackoverflow.com/questions/49211893/computing-distance-of-perceptual-hashes

## ImageHash
https://github.com/JohannesBuchner/imagehash

## Image-Match
https://github.com/ascribe/image-match

This looks really good, but I couldn't easily get it installed on OSX.

## PHash
http://www.phash.org/

This had some decent results
* FOD photo uncropped vs FOD ideal: 323 hamming
* FOD photo cropped vs FOD ideal: 323 hamming
* FOD photo cropped vs forest ideal: 356 hamming
* FOD ideal vs forest ideal: 375 hamming

The correct match had the best hamming.

Some clues for building on OSX:
https://stackoverflow.com/questions/41667861/brew-formula-for-phash#comment70699875_41667861

And maybe this one for MacPorts:
https://stackoverflow.com/a/11499397

# brian
A retrieval/classification framework developed to improve accuracy by utilizing
population cues.

## background
This was developed as part of my dissertation on shape retrieval. The
dissertation will give the most in-depth overview of all algorithms in the
framework, while the conference paper covers the most interesting parts

1. [Improving Shape Classification Using Perceptual and
Population Cues](http://cse.sc.edu/~temlyaka/publications/wacv13_temlyakov.pdf)
- Dissertation (PDF)
2. [Shape and Image Retrieval by Organizing Instances Using Population
Cues](http://cse.sc.edu/~temlyaka/publications/wacv13_temlyakov.pdf) -  IEEE
Workshop on the Applications of Computer Vision (WACV), Clearwater, FL, 2013
(PDF)

Data: [SS+IDSC data](http://cse.sc.edu/~temlyaka/datasets/data.zip)
Assuming some familiarity with previous works and the
[MPEG-7](http://cse.sc.edu/~temlyaka/datasets.html) dataset.

The algorithms only need a similiarty matrix that can be used to rank 
the instances of the dataset.

## usage

The driver.py has sample code snippets to illustrate algorithm usage.

## License

Copyright 2013 Andrew Temlyakov. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are
permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of
conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above
copyright notice, this list
of conditions and the following disclaimer in the
documentation and/or other materials
provided with the distribution.

THIS SOFTWARE IS PROVIDED BY ANDREW TEMLYAKOV ''AS IS''
AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL JARRELL WAGGONER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

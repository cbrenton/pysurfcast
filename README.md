# pysurfcast

pysurfcast is a Python script that fetches surf forecast data for a specified surf spot using the [Spitcast API](http://www.spitcast.com/api/docs/) and outputs it in a number of formats for various uses.

pysurfcast displays a visualization of surf forecasts for a specified surf spot either in a terminal or as an image.

pysurfcast is not affiliated with Spitcast. However, the author of pysurfcast thinks that Spitcast is awesome. Without Spitcast, none of this would be possible.

pysurfcast is in sort of an awkward phase in its life. It is undergoing strange changes that are sometimes a little bit scary. New hormones are beginning to flow through its body, which make pysurfcast a little bit crazy at times.

Please don't make fun of pysurfcast; it's very sensitive.

## Requirements
 * **[Python Imaging Library](http://www.pythonware.com/products/pil/)**
 * **Python 2.6** or above

## Running
Options:

 * **-h**: Print help message and exit.
 * **-p**: Echo the spot name to the terminal.
 * **-s [spotId]**: Get forecast data for the spot specified by spotID.
 * **-t**: Output the forecast as text instead of an image.
 * **-v**: Use verbose mode. Currently does nothing.

Examples:

 * Output the forecast for spot 163 (Morro Bay) as an image and echo "Morro Bay" to the terminal:

    ./pysurfcast -s 163 -p

 * Output the forecast for spot 147 (The Hook) as text in the terminal:

    ./pysurfcast -s 147 -t

Copyright (c) 2011, Chris Brenton

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of California Polytechnic State University nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CHRIS BRENTON BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# UDPiper
Tiny UDPipe+Mystem-wrapper based on an official [example](https://github.com/ufal/udpipe/blob/master/bindings/python/examples/run_udpipe.py)


## Installation 

    $ pip install git+https://github.com/detcorpus/udpiper
    

## Usage

    $ udpiper --help
    $ wget -O ru-ud23.udpipe "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2898/russian-syntagrus-ud-2.3-181115.udpipe?sequence=71&isAllowed=y"
    $ udpiper -m ru-ud23.udpipe -i *.txt
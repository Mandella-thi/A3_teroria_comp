Esse programa é uma modificação de um programa já existente, foi acresentado o calculo de expressões matemáticas
#AST visualizer

Lucas Aoki Ra: 821239078,
Iago Guimarães de Oliveira Ra: 8222244160, 
Angelica Bicego Ferreira Ra:321220089,  
Thiago Garcia dos Santos Ra: 821215213
é dificil instalar a biblioteca graphviz no windows, para isso é mais fácil instalar com o chocolatey.

The script `astvisualizer.py` contained in this repository visualizes a Python AST trees.

## Installation

First install the following requirements:
  * Python 3
  * the dependencies listed in requirements.txt (`pip install -r requirements` or `pip3 install -r requirements` depending on your OS)

Run the script `astvisualizer.py`. It accepts the input on stdin. Alternatively you might specify a file name as first parameter.

## Usage

By default `astvisualizer.py` reads the Python code from stdin. 

If you only want to visualize a short snippet you can also pass it directly on the command line, f.e. `astvisualizer.py "print(3/2)"`.

If you want to visualize an existing Python source code file, pass the file name using the `-f` switch, f.e. `astvisualizer.py -f test.py`.

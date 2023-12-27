import sys

from regex import RegEx, Lambda, Union, Char, Concat, Star, Plus, Empty
from .errors import SyntaxError

#lo agregamos nosotros
from .ply.yacc import yacc
from .ply.lex import lex

def numeritos():
    temp = Char("0")
    for i in range(1,10):
        temp = Union(temp, Char(str(i)))
    return temp

def letras(inicio, fin):
    res = Char(inicio)
    for c in range(ord(inicio)+1, ord(fin)+1):
        letra = Char(chr(c))
        res = Union(res, letra)
    return res

num1 = numeritos()
abc1 = letras('a', 'z')
abc2 = letras('A', 'Z')    #dejamos precalculado [a-z], [A-Z], y [0-9]

# simRes = {"+", "?", "\\", "(",")", "[", "]", "|"}


# Gramatica
# R' -> lambda | R | []
# R -> (R|A) | A
# A -> AB | B
# B -> CS | C  
# S -> symbol | llavenumllave | llavenumnumllave
# C -> de | doblev | V | (R) | [U] 
# U -> V U | V 
# V -> num | char | guion | reservado

# guion:          r'-'
# space:          r'\s'
# symbol:         ['?', '*', '+'] 
# charnum:        [a-zA-Z0-9]
# num:            [0-9]*
# de:             r'\\d'
# doblev:         r'\\w'


#-----------------------------lexer------------------------------------------------------------
__all__ = ["lexer", "toDens", "tokenize"]

# Lista de tokens reconocibles por el lexer
tokens = ['SYMBOL','UNION','PARA', 'PARC', 'CORA', 'CORC', 'LLAVENUMLLAVE','LLAVENUMNUMLLAVE', 'GUION', 'NUM', 'CHAR', 'RESERVADO', 'DOBLEV', 'DE']#, 'ID']# + list(reserved.values()) #, 'SLASH', 'ID'] 

# Reglas para el analizador léxico
t_ignore = '\t'

# Regexes para reconocer tokens simples
t_UNION = r'\|'
t_PARA = r'\('
t_PARC = r'\)'
t_CORA = r'\['
t_CORC = r'\]'
t_GUION = r'-'
t_DE = r'(\\(d))'
t_DOBLEV = r'(\\(w))'

def t_LLAVENUMLLAVE(t):
    r'{(\d)}'
    t.value = str(t.value)
    t.value = [int(t.value[1]), int(t.value[1])]
    return t

def t_LLAVENUMNUMLLAVE(t):   #Tokens usados para que el parser detecte {num,num} y no tomar los { o } asi poder parsearlos por separado
    r'{(\d),(\d)}'
    t.value = str(t.value)
    t.value = [int(t.value[1]), int(t.value[3])]
    return t

def t_NUM(n):
    r'((\d)+(\d)*)'
    n.value = int(n.value)
    return n 

def t_CHAR(c):    
    r"([a-zA-Z]|_|\s|{|})"
    c.value = c.value 
    return c

t_SYMBOL = r'(\+|\*|\?)' 

def t_RESERVADO(c):
    r'((\\(\+))|(\\(\|))|(\\(\?))|(\\(\\))|(\\(\())|(\\(\)))|(\\(\[))|(\\(\]))|(\\(\*)))'
    c.value = c.value[-1]
    return c

# Ignoramos saltos de línea y llevamos registro del número de línea actual
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Manejo básico de errores: omitimos caracteres extraños
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    print(
        f'Ignoring illegal character {t.value[0]!r} at position {t.lexpos}', file=sys.stderr)
    t.lexer.skip(1)

# Construimos el lexer
lexer = lex()

#-------------------------------------------------------------------------------------------------------
__all__ = ["parse_regex", "SyntaxError"]

precedence = (
    ('left', 'UNION'),
)
# R' -> lambda
def p_rprima_nada (p):
    '''
    rprima : 
    '''
    p[0] = Lambda()
    
# R' -> []
def p_rprima_empty (p):
    '''
    rprima : CORA CORC
    '''
    p[0] = Empty()
   
# R' -> R
def p_rprima_rgenerador (p):
    '''
    rprima : rgenerador
    '''
    p[0] = p[1]
   

# R -> (R|A)
def p_rgenerador_pipe(p):
    '''
    rgenerador : rgenerador UNION aconcatados
    ''' 
    p[0] = Union(p[1], p[3])
    
    
    
# R -> A
def p_rgenerador_aconcatados(p):
    '''
    rgenerador : aconcatados
    '''
    p[0] = p[1]
    
    

# A -> B 
def p_aconcatados_balores(p):
    '''
    aconcatados : balores
    '''
    p[0] = p[1]
    
    


# A -> AB
def p_aconcatados_acon_balores(p):
    '''
    aconcatados : aconcatados balores
    '''

    p[0] = Concat(p[1],p[2])
    
   

# B -> CS
def p_balores_chars_sym(p):   #chequa que simbolo hay en S para asi poder hacer la accion correcta
    '''
    balores : chars sym
    '''
    if (p[2] == '*'): 
        p[0] = Star(p[1])
    elif (p[2] == '+'): 
        p[0] = Plus(p[1])
    elif (p[2] == '?'):
        p[0] = Union(p[1],Lambda())
    elif (type(p[2]) is list):
        if (p[2] == [0,0] or (p[2][1] < p[2][0])):
            p[0] = Lambda()
        else:
            temp = p[1]
            if p[2][0] == 0:
                temp = Lambda()
            else: 
                for i in range(p[2][0] - 1): 
                    temp = Concat(temp, p[1])
            
            p[0] = temp #aaa
            for i in range(p[2][0], p[2][1]):
                temp = Concat(temp, p[1])
                p[0] = Union(p[0], temp) 
    
    

# B -> C
def p_balores_casos(p):
    '''
    balores : chars
    '''
    p[0] = p[1]
    
  

# S -> symbol
def p_sym_symbol(p):
    '''
    sym : SYMBOL
    '''
    p[0] = p[1]
    

# S -> llavenumllave
def p_sym_num(p):
    '''
    sym : LLAVENUMLLAVE
    '''
    p[0] = p[1]
    

# S -> llavenumnumllave 
def p_sym_num_num(p):
    '''
    sym : LLAVENUMNUMLLAVE
    '''
    p[0] = p[1]
    


# C -> DE
def p_chars_d(p):
    '''
    chars : DE
    '''
    p[0] = num1

def p_chars_w(p):
    '''
    chars : DOBLEV
    '''
    tempNum = num1
    temp_az = abc1
    temp_az_mayus = abc2

    p[0] = Union(Char("_"), Union(tempNum, Union(temp_az, temp_az_mayus)))
    

# C -> V
def p_chars_char(p):
    '''
    chars : valor
    '''
    p[0] = p[1][1]
   

# C -> (R)
def p_chars_rgenerador(p):
    '''
    chars : PARA rprima PARC
    '''
    p[0] = p[2]
   

# C -> [U]
def p_chars_cora_tguion(p):
    '''
    chars : CORA unboxing CORC
    ''' 
    p[0] = p[2][2]
    if (p[2][3]):
        p[0] = Union(Char("-"),p[0])   
  
    

# U -> V
def p_unboxing_fin(p):
    '''
    unboxing : valor
    '''
    # establezco info en p[0] = (ultimoValorEnRegEx, loAnteUltimo, RegEx, fueGuion) que se utilizará en la recursion
    print(p[1])
    p[0] = (p[1][0], "CORC", p[1][1], False) #(1, 'CORC', Char("1"))

# U -> V U 
def p_unboxing_recursion(p):
    '''
    unboxing : valor unboxing
    '''
    #En p[1] tengo el valor que quiero unir al RegEx* y en p[2] tengo la tripla que me dice (loUltimoPuesto, loAnteultimo, RegEx)
    aUnir = p[1]
    loUltimoPuesto = p[2][0]
    loAnteUltimoPuesto = p[2][1]
    ultimoRegex = p[2][2]
    fueGuion = p[2][3]
    
    # *: pero va a depender de ciertas condiciones, 1ero) veo si loUltimoPuesto fue un "-", && si el tipo(valAUnir) == tipo(loAnteUltimoPuesto) ,
    # entonces voy a querer devolver Union(Regex,)  
    if (fueGuion and type(aUnir[0])==type(loAnteUltimoPuesto)): #quiero hacer un rango
        
        inicio = aUnir[0]
        fin = loAnteUltimoPuesto
        
        if(type(loAnteUltimoPuesto) != str): #si es int/nat, quiero que sea char para poder recorrelo lexicografico los ascii
            inicio = str(aUnir[0])
            fin = str(loAnteUltimoPuesto)
        
        if(ord(inicio) <= ord(fin)): #solo voy a hacerlo si es posible recorrer los ascii
            res = Char(inicio)

            for c in range(ord(inicio)+1, ord(fin)): #el rango va SIN el ultimo elemento, porque en los otros pasos si NO soy un rango, ya agregue el valor al RegEx
                letra = Char(chr(c))
                res = Union(res, letra)
            
            p[0] = (aUnir[0], loUltimoPuesto, Union(res ,ultimoRegex), False)
        else: #si no se puede, error
            raise SyntaxError
    elif (aUnir[0] == "-"): # si el valAUnir es "-", activo el bit de fueGuion
        p[0] = (aUnir[0], loUltimoPuesto, ultimoRegex, True) #y a su vez salva el caso de iniciar con "-"
    else: # si no quiero hacer rango, y NO fui un guion, entonces quiero que el nuevo RegEx sea Union(RegEx_anterior, aUnir[1])
        p[0] = (aUnir[0], loUltimoPuesto, Union(aUnir[1] ,ultimoRegex), False)
 
    

# V -> num
def p_valor_num(p):
    '''
    valor : NUM
    '''    
    p[0] = (p[1], Char(str(p[1])))
   
    
    
# V -> char | guion | reservado
def p_valor_char(p):
    '''
    valor : CHAR
          | GUION
          | RESERVADO
    '''    
    p[0] = (p[1], Char(p[1]))
  
    


def p_error(t):
 
    raise SyntaxError

parser = yacc(debug=True)

def parse_regex(regex_str: str) -> RegEx:
    # Forma parte de la segunda entrega.
    parse_result = parser.parse(regex_str)
    print("RegEx al final:")
    print(parse_result.__str__())
    return(parse_result)
    # raise NotImplementedError



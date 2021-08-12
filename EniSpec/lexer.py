import ply
import ply.lex

tokens = (
   'COMMA',
   'LPAREN',
   'RPAREN',
   'PLUS',
   'TIMES',
   'DIV',
   'AND',
   'OR',
   'BITWISEAND',
   'BITWISEOR',
   'BITWISENOT',
   'SHIFTLEFT',
   'SHIFTRIGHT',
   'EQ',
   'NE',
   'NOT',
   'SEMI',
   'ASSIGN',
   'DOT',
   'LCB',
   'RCB',
   'LB',
   'RB',
   'ARROW',
   'IFF',
   'ID',
   'INTLIT',
   'COLON',
   'LE',
   'LT',
   'GE',
   'GT',
   'MINUS',
   'MOD'
 )
 
reserved = all_reserved = {
    'relation': 'RELATION',
    'action': 'ACTION',        
    'type' : 'TYPE',
    'requires' : 'REQUIRES',
    'return': 'RETURN',
    'returns' : 'RETURNS',
    'constant' : 'CONSTANT',
    'forall' : 'FORALL',
    'exists' : 'EXISTS',
    'delete' : 'DELETE',
    'insert' : 'INSERT',
    'init' : 'INIT',
    'after' : 'AFTER',
    'sizeof' : 'SIZEOF',
    'baseaddr' : 'BASEADDR',
    "fun" : "FUNCTION",
    "extern" : "EXTERN",
    "let" : "LET",
    "in" : "IN",
    "call" : "CALL",
    "error" : "ERROR",
    "if" : "IF",
    "then" : "THEN",
    "else" : "ELSE",
    "struct" : "STRUCT",
    "fuzz" : "FUZZ",
    "atomic" : "ATOMIC",
    "await" : "AWAIT"
}

tokens += tuple(all_reserved.values())


t_COMMA    = r'\,'
t_PLUS    = r'\+'
t_TIMES   = r'\*'
t_DIV   = r'\/'
t_MINUS   = r'\-'
t_MOD   = r'\%'
t_LT      = r'\<'
t_LE      = r'\<='
t_GT      = r'\>'
t_GE      = r'\>='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_OR = r'\|\|'
t_AND = r'\&\&'
t_BITWISEOR = r'\|'
t_BITWISEAND = r'\&'
t_BITWISENOT = r'\~'
t_SHIFTLEFT = r'\>>'
t_SHIFTRIGHT = r'\<<'
t_EQ = r'\=='
t_NE = r'\!='
t_NOT = r'\!'
t_SEMI = r'\;'
t_ASSIGN = r'\:='
t_DOT = r'\.'
t_LCB  = r'\{'
t_RCB  = r'\}'
t_LB  = r'\['
t_RB  = r'\]'
t_ARROW = r'\->'
t_IFF = r'\<->'
t_COLON = r':'

t_ignore  = ' \t\r'
t_ignore_COMMENT = r'\#.*'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*|".*?"'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    return t

def t_INTLIT(t):
    r'[0-9]+'
    return t

def t_error(t):
    print ("Illegal character '%s'" % t.value[0])
    raise Exception(t.lineno,"illegal character '{}'".format(t.value[0]))    

lexer = None

def get_lexer(forbid_rebuild: bool = False) -> ply.lex.Lexer:
    global lexer
    if not lexer:
        lexer = ply.lex.lex(debug=False)
    return lexer


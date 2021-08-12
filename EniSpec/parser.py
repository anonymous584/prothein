import ply
import ply.yacc
from lexer import tokens
import lexer
import syntax
import utils
from typing import Any, List, Optional, overload, Sequence, Tuple, Union

precedence = (
    ('left', 'SEMI'),
    ('nonassoc', 'STRUCT'),
    ('nonassoc', 'ELSE'),
    ('nonassoc', 'IN'),
    ('nonassoc', 'IFF'),
    ('right', 'ARROW'),
    ('left', 'AND', 'OR'),
    ('left', 'NOT'),    
    ('left', 'EQ','NE'),
    ('left', 'LE','LT','GE','GT'),    
    ('left', 'COLON'),
    ('left', 'PLUS', 'MINUS'), 
    ('left', 'SHIFTLEFT', 'SHIFTRIGHT'), 
    ('left', 'BITWISENOT'),
    ('left', 'BITWISEOR', 'BITWISEAND'), 
    ('left', 'TIMES', 'DIV', 'MOD'),
    ('left', 'DOT')
)

def p_program(p: Any) -> None:
    'program : stmts'
    p[0] = syntax.Program(p[1])

def p_stmts_empty(p: Any) -> None:
    'stmts : empty'
    p[0] = []

def p_empty(p:Any) -> None:
    'empty : '
    pass

def p_stmts_stmt(p: Any) -> None:
    'stmts : stmts stmt'
    p[0] = p[1] + [ p[2] ]

def p_stmt_init(p:Any) -> None:
    'stmt : AFTER INIT LCB exprlist RCB'
    p[0] = syntax.InitDecl(p[4])

def p_stmt_type(p:Any) -> None:
    'stmt : TYPE ID'
    p[0] = syntax.TypeNode(p[2])

def p_stmt_extern_function(p:Any) -> None:
    'stmt : EXTERN FUNCTION ID aritydef RETURNS aritydef SEMI '
    p[0] = syntax.ExternFunctionDecl(p[3], p[4], p[6])

def p_stmt_function(p:Any) -> None:
    'stmt : FUNCTION ID aritydef RETURNS aritydef ASSIGN LCB action RCB'
    p[0] = syntax.ActionDecl(p[2], p[3], p[5], p[8])

def p_stmt_definition(p:Any) -> None:
    'stmt : CONSTANT ID COLON ID ASSIGN INTLIT'
    p[0] = syntax.ConstantDecl(p[2], p[4], p[6])

def p_stmt_relation(p:Any) -> None:
    'stmt : RELATION ID aritydef RETURNS aritydef'
    p[0] = syntax.RelationDecl(p[2], p[3], p[5])

def p_stmt_action(p:Any) -> None:    
    'stmt : ACTION ID aritydef RETURNS aritydef ASSIGN LCB action RCB' 
    p[0] = syntax.ActionDecl(p[2], p[3], p[5], p[8], None)

def p_stmt_action_predicates(p:Any) -> None:    
    'stmt : ACTION ID aritydef RETURNS aritydef FUZZ LCB logicexpr RCB ASSIGN LCB action RCB'     
    p[0] = syntax.ActionDecl(p[2], p[3], p[5], p[12], p[8])

def p_action_body(p:Any) -> None:
    'action : exprlist'
    p[0] = p[1]

def p_exprlist_empty(p:Any) -> None:
    'exprlist : empty'
    p[0] = []

def p_exprlist_list(p:Any) -> None:
    'exprlist : exprlist expr SEMI'
    p[0] = p[1] + [ p[2] ]

def p_expr_paren(p:Any) -> None:
    'expr : LPAREN logicexpr RPAREN'
    p[0] = p[2]

def p_expr_requires(p:Any) -> None:
    'expr : REQUIRES logicexpr'
    p[0] = syntax.RequireExpr(p[2])

def p_expr_err_requires(p:Any) -> None:
    'expr : LB ERROR RB REQUIRES logicexpr'
    p[0] = syntax.ErrorRequireExpr(p[5])

def p_expr_requires_no_err(p:Any) -> None:
    'expr : REQUIRES NOT ERROR'
    p[0] = syntax.RequireNoErrExpr()

def p_expr_return_exprterm(p:Any) -> None:
    'expr : RETURN exprterm'
    p[0] = syntax.ReturnExpr(p[2])

def p_expr_return(p:Any) -> None:
    'expr : RETURN'
    p[0] = syntax.ReturnExpr()    

def p_expr_atomic(p:Any) -> None:
    'expr : ATOMIC LPAREN exprterm RPAREN LCB exprlist RCB'
    p[0] = syntax.AtomicExpr(p[3], p[6])

def p_expr_await(p:Any) -> None:
    'expr : AWAIT expr'
    p[0] = syntax.AwaitExpr(p[2])

def p_expr_if(p:Any) -> None:
    'expr : IF logicexpr THEN LCB exprlist RCB'
    p[0] = syntax.IfThenElseExpr(p[2], p[5])

def p_expr_ifelse(p:Any) -> None:
    'expr : IF logicexpr THEN LCB exprlist RCB ELSE LCB exprlist RCB'
    p[0] = syntax.IfThenElseExpr(p[2], p[5], p[9])

def p_expr_let(p:Any) -> None:
    'expr : LET ID ASSIGN exprterm IN LCB exprlist RCB'
    p[0] = syntax.LetExpr(p[2], None, p[4], p[7])    

def p_expr_let_with_type(p:Any) -> None:
    'expr : LET ID COLON type ASSIGN exprterm IN LCB exprlist RCB'
    p[0] = syntax.LetExpr(p[2], p[4], p[6], p[9])    

# NOTE: this syntax is used to enforce a specifc type size. Useful, for example, for buffers, e.g., MAX_PATH in FS spec. 
def p_expr_let_explicit_type_size(p:Any) -> None:
    'expr : LET ID COLON type LPAREN exprterm RPAREN IN LCB exprlist RCB'
    p[0] = syntax.LetExpr(p[2], p[4], p[6], p[10], True)    

def p_expr_func_invoke(p:Any) -> None:
    'expr : CALL ID arity'
    p[0] = syntax.InlineCallFunction(p[2],p[3])

def p_expr_externfunc_invoke(p:Any) -> None:
    'expr : EXTERN CALL ID arity'
    p[0] = syntax.CallFunction(p[3],p[4])

def p_expr_assign(p:Any) -> None:
    'expr : exprterm ASSIGN exprterm'
    p[0] = syntax.AssignExpr(p[1], p[3])

def p_expr_relation_delete(p:Any) -> None:
    'expr : DELETE exprterm'
    p[0] = syntax.DeleteSymbolDecl(p[2])    

def p_expr_relation_insert(p:Any) -> None:
    'expr : INSERT exprterm'
    p[0] = syntax.InsertSymbolDecl(p[2])    

def p_term_exists_iterator(p):
    'logicexpr : EXISTS ID IN exprterm COLON COLON logicexpr'
    p[0] = syntax.ExistsExpr(p[2], p[4], p[7])

def p_term_forall_iterator(p):
    'logicexpr : FORALL ID IN exprterm COLON COLON logicexpr'
    p[0] = syntax.ForAllExpr(p[2], p[4], p[7])
    # p[0] = syntax.ForAllIterableExpr(p[2], p[4], p[6])

def p_expr_unaryexpr(p:Any) -> None:
    'logicexpr : NOT logicexpr'
    p[0] = syntax.UnaryLogicExpr(p[1], p[2])

def p_logicexpr_exprterm(p:Any) -> None:
    'logicexpr : exprterm'
    p[0] = p[1] #syntax.LogicExpr(p[1])

def p_logicexpr_paren(p:Any) -> None:
    '''logicexpr : LPAREN logicexpr RPAREN'''
    p[0] = p[2]

def p_logicexpr_logicop(p:Any) -> None:
    '''logicexpr : logicexpr AND logicexpr 
                 | logicexpr OR  logicexpr'''
    p[0] = syntax.BinaryLogicExpr(p[2], p[1], p[3])

def p_expr_binexpr(p:Any) -> None:
    '''logicexpr : logicexpr EQ logicexpr
                 | logicexpr NE logicexpr
                 | logicexpr IFF logicexpr
                 | logicexpr ARROW logicexpr
                 | logicexpr LT logicexpr
                 | logicexpr GT logicexpr
                 | logicexpr LE logicexpr
                 | logicexpr GE logicexpr'''
    p[0] = syntax.BinaryLogicExpr(p[2], p[1], p[3])

def p_exprterm_binop_arith_paren(p:Any) -> None:
    '''exprterm : LPAREN exprterm PLUS       exprterm RPAREN
                | LPAREN exprterm MINUS      exprterm RPAREN
                | LPAREN exprterm TIMES      exprterm RPAREN
                | LPAREN exprterm MOD        exprterm RPAREN
                | LPAREN exprterm BITWISEOR  exprterm RPAREN
                | LPAREN exprterm BITWISEAND exprterm RPAREN                
                | LPAREN exprterm SHIFTLEFT exprterm RPAREN      
                | LPAREN exprterm SHIFTRIGHT exprterm RPAREN      
                | LPAREN exprterm DIV        exprterm RPAREN'''
    p[0]= syntax.BinaryExpr(p[3], p[2], p[4])

def p_expr_relation_array(p:Any) -> None:
    'exprterm : exprterm LB exprterm COLON exprterm RB'
    p[0] = syntax.RangeExpr(p[1],p[3],p[5])

def p_exprterm_externfunc_invoke(p:Any) -> None:
    'exprterm : EXTERN CALL ID arity'
    p[0] = syntax.CallFunction(p[3],p[4])

def p_exprterm_func_invoke(p:Any) -> None:
    'exprterm : CALL ID arity'
    p[0] = syntax.InlineCallFunction(p[2],p[3])

def p_expr_relation_array_single(p:Any) -> None:
    'exprterm : exprterm LB exprterm RB'
    # p[0] = syntax.RangeExpr(p[1],p[3], syntax.BinaryExpr(syntax.BINOPS['PLUS'], 1, p[3]))
    p[0] = syntax.DereferenceExpr(p[1], p[3])

def p_exprterm__negative(p:Any) -> None:
    '''exprterm : MINUS exprterm
              | BITWISENOT exprterm'''
    p[0] = syntax.UnaryExpr(p[1], p[2])

def p_exprterm__negative_paren(p:Any) -> None:
    '''exprterm : MINUS LPAREN exprterm RPAREN
              | BITWISENOT LPAREN exprterm RPAREN'''
    p[0] = syntax.UnaryExpr(p[1], p[3])

def p_exprterm_sizeof(p:Any) -> None:
    'exprterm : SIZEOF LPAREN exprterm RPAREN'
    p[0] = syntax.SizeofExpr(p[3])

def p_exprterm_base_addr(p:Any) -> None:
    'exprterm : BASEADDR LPAREN exprterm RPAREN'
    p[0] = syntax.BaseAddrExpr(p[3])

def p_expr_num(p:Any) -> None:
    'exprterm : INTLIT'
    p[0] = syntax.NumberDecl(p[1])

def p_expr_concrete_value(p:Any) -> None:
    'exprterm : ID'
    p[0] = p[1] #syntax.SymbolDecl(p[1])

def p_expr_member(p:Any) -> None:
    'exprterm : exprterm DOT exprterm'
    p[0] = syntax.ComplexSymbolDecl(p[1],p[3])

def p_expr_relation_exists(p:Any) -> None:
    'exprterm : exprterm arity'
    p[0] = syntax.ArityExpr(p[1],p[2])

def p_aritydef_aritylist(p: Any) -> None:
    'aritydef : LPAREN aritydeflist RPAREN'
    p[0] = p[2]

def p_aritydeflist_empty(p: Any) -> None:
    'aritydeflist : empty'
    p[0] = []

def p_aritydeflist_single(p: Any) -> None:
    'aritydeflist : aritydef_nonempty'
    p[0] = [p[1]]

def p_aritydeflist_multi(p: Any) -> None:
    'aritydeflist : aritydeflist COMMA aritydef_nonempty'
    p[0] = p[1] + [ p[3] ]    

def p_aritydef_nonempty_one_type(p: Any) -> None:
    'aritydef_nonempty : ID COLON type'
    p[0] = syntax.SymbolDecl(p[1], p[3])

def p_arity_aritylist(p: Any) -> None:
    'arity : LPAREN aritylist RPAREN'
    p[0] = p[2]

def p_aritylist_empty(p: Any) -> None:
    'aritylist : empty'
    p[0] = []

def p_aritylist_single(p: Any) -> None:
    'aritylist : arity_nonempty'
    p[0] = [ p[1] ]

def p_aritylist_multi(p: Any) -> None:
    'aritylist : aritylist COMMA arity_nonempty'
    p[0] = p[1] + [ p[3] ]    

def p_arity_nonempty_one(p: Any) -> None:
    'arity_nonempty : exprterm'
    # p[0] = syntax.SymbolDecl(p[1])
    p[0] = p[1]

def p_arity_nonempty_anything(p: Any) -> None:
    'arity_nonempty : TIMES'
    p[0] = p[1]

def p_basetype_simple(p: Any) -> None:
    'basetype : ID'
    p[0] = p[1]

def p_basetype_struct(p: Any) -> None:
    'basetype : STRUCT ID'
    p[0] = p[1] + " " + p[2]

def p_basetype_relation(p: Any) -> None:
    'basetype : RELATION ID'
    p[0] = p[1] + " " + p[2]

def p_type_array_unbound(p: Any) -> None:
    'type : basetype LB RB'
    p[0] = p[1] + "*"

def p_type_array_bound(p: Any) -> None:
    'type : basetype LB exprterm RB'            
    p[0] = p[1] + "*"

def p_type_basetype(p: Any) -> None:
    'type : basetype'            
    p[0] = p[1]

def p_error(token):    
    if token is not None:
        utils.print_error(loc=None, msg="syntax error detected for line {} value {}".format(token.lineno, token.value))
    else:
        utils.print_error(loc=None, msg="syntax error detected: unexpected end of input")

program_parser = None

def get_parser() -> ply.yacc.LRParser:
    global program_parser
    if not program_parser:
        program_parser = ply.yacc.yacc(start='program', debug=True)

    return program_parser

expr_parser = None

def get_expr_parser() -> ply.yacc.LRParser:
    global expr_parser
    if not expr_parser:
        expr_parser = ply.yacc.yacc(start='expr', debug=False)

    return expr_parser

def parse_expr(input: str):
    l = lexer.get_lexer()
    p = get_expr_parser()
    return p.parse(input=input, lexer=l)

if __name__ == "__main__":
    l = lexer.get_lexer()
    p = get_parser()
    with open("/home/meni/dev/enclave_interface/soteria/examples/file.sot") as f:
        prog: syntax.Program = p.parse(input=f.read(), lexer=l)   
        print(prog)
        print("hello world") 
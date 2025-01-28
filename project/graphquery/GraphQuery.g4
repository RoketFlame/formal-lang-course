grammar GraphQuery;

prog : stmt* EOF;

stmt: declare | bind | add | remove;

declare : LET VAR IS GRAPH ;

bind : LET VAR EQUAL expr ;

remove : REMOVE (VERTEX | EDGE | VERTICES) expr FROM VAR ;

add : ADD (VERTEX | EDGE) expr TO VAR ;

expr : NUM | CHAR | VAR | edge_expr | set_expr | regexp | select ;

set_expr : L_SQ_BR expr (COMMA expr)* R_SQ_BR ;

edge_expr : L_BR expr COMMA expr COMMA expr R_BR ;

regexp: term (PIPE term)*;

term: factor ((DOT | AMPERSAND) factor)*;

factor: primary (CIRCUMFLEX range)*;

primary: CHAR | VAR | L_BR regexp R_BR;

range : L_SQ_BR NUM ELLIPSIS NUM? R_SQ_BR ;

select : v_filter? v_filter? RETURN VAR (COMMA VAR)? WHERE VAR REACHABLE FROM VAR IN VAR BY expr ;

v_filter : FOR VAR IN expr ;

LET:            'let' ;
IS:             'is' ;
GRAPH:          'graph' ;
REMOVE:         'remove' ;
WHERE:          'where' ;
REACHABLE:      'reachable' ;
RETURN:         'return' ;
BY:             'by' ;
VERTEX:         'vertex' ;
EDGE:           'edge' ;
VERTICES:       'vertices' ;
FROM:           'from' ;
ADD:            'add' ;
TO:             'to' ;
FOR:            'for' ;
IN:             'in' ;

EQUAL:          '=' ;
L_SQ_BR:        '[' ;
L_BR:           '(' ;
R_SQ_BR:        ']' ;
R_BR:           ')' ;
COMMA:          ',' ;
CIRCUMFLEX:     '^' ;
DOT:            '.' ;
AMPERSAND:      '&' ;
ELLIPSIS:       '..' ;
PIPE:           '|' ;

VAR : [a-zA-Z] [a-zA-Z0-9]* ;
NUM : [0-9]+ ;
CHAR : '"' [a-z] '"' | '\'' [a-z] '\'' ;

WS : [ \t\r\n]+ -> skip ;
EOF_TOKEN: '<EOF>' -> skip;

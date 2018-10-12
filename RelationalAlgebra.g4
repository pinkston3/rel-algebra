grammar RelationalAlgebra;


SELECT  : [sS][iI][gG][mM][aA] ;
PROJECT : [pP][iI] ;
RENAME  : [rR][hH][oO] ;

GROUP_AGGREGATE : [gG][rR][oO][uU][pP] ;

CROSS   : [cC][rR][oO][sS][sS] ;
TIMES   : [tT][iI][mM][eE][sS] ;
DIVIDE  : [dD][iI][vV][iI][dD][eE] ;

BOWTIE          : [bB][oO][wW][tT][iI][eE] ;
LEFT_BOWTIE     : [lL][bB][oO][wW][tT][iI][eE] ;
RIGHT_BOWTIE    : [rR][bB][oO][wW][tT][iI][eE] ;
FULL_BOWTIE     : [fF][bB][oO][wW][tT][iI][eE] ;

UNION   : [uU][nN][iI][oO][nN] ;
INTERSECT : [iI][nN][tT][eE][rR][sS][eE][cC][tT] ;
MINUS   : [mM][iI][nN][uU][sS] ;

AND     : [aA][nN][dD] ;
AS      : [aA][sS] ;
FALSE   : [fF][aA][lL][sS][eE] ;
NOT     : [nN][oO][tT] ;
NULL    : [nN][uU][lL][lL] ;
OR      : [oO][rR] ;
TRUE    : [tT][rR][uU][eE] ;


relStmts : relStmt* ;


relStmt :
      relName=NAME ('(' attrNames+=NAME (',' attrNames+= NAME)* ')')?
      '<-' relExpr ';'                              # RelStmtAssign
    | relExpr ';'                                   # RelStmtNoAssign
    | SCHEMA_NAME '=' '(' NAME (',' NAME)* ')' ';'  # RelStmtSchema
    ;

relExpr :
      SELECT '[' scalarExpr ']' '(' relExpr ')'          # RelExprSelect

    | PROJECT '[' projectExpr (',' projectExpr)* ']'
              '(' relExpr ')'                            # RelExprProject

    | RENAME '[' namedScalarExpr (',' namedScalarExpr)* ']'
             '(' relExpr ')'                             # RelExprRename

    | ('[' groups+=scalarExpr (',' groups+=scalarExpr)* ']')?
      GROUP_AGGREGATE '[' aggregates+=namedScalarExpr (',' aggregates+=namedScalarExpr)* ']'
             '(' relExpr ')'                             # RelExprGroupAggregate

    | relExpr       BOWTIE ('[' scalarExpr ']')? relExpr # RelExprInnerJoin
    | relExpr  LEFT_BOWTIE ('[' scalarExpr ']')? relExpr # RelExprLeftOuterJoin
    | relExpr RIGHT_BOWTIE ('[' scalarExpr ']')? relExpr # RelExprRightOuterJoin
    | relExpr  FULL_BOWTIE ('[' scalarExpr ']')? relExpr # RelExprFullOuterJoin

    | relExpr (CROSS | TIMES) relExpr    # RelExprCrossProduct
    | relExpr DIVIDE relExpr             # RelExprDivision

    | relExpr UNION relExpr              # RelExprSetUnion
    | relExpr INTERSECT relExpr          # RelExprSetIntersect
    | relExpr MINUS relExpr              # RelExprSetDifference

    | NAME                               # RelExprRelationVariable
    | '{' (rowExpr (',' rowExpr)*)? '}'  # RelExprConstantRelation

    | '(' relExpr ')'                    # RelExprParens
    ;


rowExpr :
    '(' literalValue ( ',' literalValue )* ')' ;


projectExpr :
      schemaExpr                        # ProjectSchemaExpr
    | namedScalarExpr                   # ProjectNamedScalarExpr
    ;


schemaExpr :
      schemaExpr UNION schemaExpr       # SchemaExprSetUnion
    | schemaExpr INTERSECT schemaExpr   # SchemaExprSetIntersect
    | schemaExpr MINUS schemaExpr       # SchemaExprSetDifference
    | SCHEMA_NAME                       # SchemaExprName
    | '(' schemaExpr ')'                # SchemaExprParens
    ;


namedScalarExpr : scalarExpr (AS NAME)? ;

scalarExpr :
      NAME '(' (scalarExpr (',' scalarExpr)* )? ')'     # ScalarExprFunction
    | attrName                                          # ScalarExprAttribute
    | literalValue                                      # ScalarExprLiteral

    | '-' scalarExpr                                    # ScalarExprUnarySign
    | scalarExpr op=('*' | '/') scalarExpr              # ScalarExprMul
    | scalarExpr op=('+' | '-') scalarExpr              # ScalarExprAdd

    | scalarExpr op=('>' | '<' | '>=' | '<=' | '!=' | '=' | '==' | '<>')
      scalarExpr                                        # ScalarExprCompare

    | (NOT | '!') scalarExpr                            # ScalarExprNot
    | scalarExpr (AND | '&&') scalarExpr                # ScalarExprAnd
    | scalarExpr (OR | '||') scalarExpr                 # ScalarExprOr

    | '(' scalarExpr ')'                                # ScalarExprParens
    ;


attrName :
      attr=NAME                         # AttrNameSimple
    | table=NAME '.' attr=NAME          # AttrNameQualified
    ;

literalValue :
      NUMBER                            # LiteralNumber
    | STRING                            # LiteralString
    | TRUE                              # LiteralTrue
    | FALSE                             # LiteralFalse
    | NULL                              # LiteralNull
    ;

NAME        : [a-z][a-zA-Z0-9_]* ;
SCHEMA_NAME : [A-Z][a-zA-Z0-9_]* ;

NUMBER : [+-]? [0-9]+ ('.' [0-9]+)? ;
STRING : '"' .*? '"' ;

WS : [ \t\r\n]+ -> skip ;


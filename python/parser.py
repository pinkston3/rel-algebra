from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import *

from RelationalAlgebraLexer import RelationalAlgebraLexer
from RelationalAlgebraParser import RelationalAlgebraParser
from RelationalAlgebraVisitor import RelationalAlgebraVisitor


class UnderlineListener(ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        stack = recognizer.getRuleInvocationStack()
        stack.reverse()

        msg = "Line %d, column %d:  %s\n" % (line, column, msg)

        tokens = recognizer.getInputStream()
        input = tokens.tokenSource.inputStream.strdata
        lines = input.split('\n')
        errorLine = lines[line - 1]

        msg += errorLine + "\n"

        tok_start = offendingSymbol.start
        tok_end = offendingSymbol.stop

        if tok_start >= 0 and tok_end >= 0:
            msg += (" " * column) + ("^" * (tok_end - tok_start + 1))

        self.errors.append(msg)


def parse_str(ra_str):
    input_stream = InputStream(ra_str)
    lexer = RelationalAlgebraLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = RelationalAlgebraParser(token_stream)
    return parser



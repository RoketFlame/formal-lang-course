from antlr4 import (
    CommonTokenStream,
    InputStream,
    ParserRuleContext,
    ParseTreeWalker,
)

from project.graphquery.GraphQueryLexer import GraphQueryLexer
from project.graphquery.GraphQueryParser import GraphQueryParser
from project.graphquery.listeners import (
    NodeCountListener,
    SyntaxErrorListener,
    TreeToProgramListener,
)


def program_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    input_stream = InputStream(program)
    error_listener = SyntaxErrorListener()

    lexer = GraphQueryLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = GraphQueryParser(tokens)

    lexer.addErrorListener(error_listener)
    parser.addErrorListener(error_listener)

    tree = parser.prog()
    return tree, not error_listener.has_errors


def nodes_count(tree: ParserRuleContext) -> int:
    node_listener = NodeCountListener()
    walker = ParseTreeWalker()
    walker.walk(node_listener, tree)
    return node_listener.count


def tree_to_program(tree: ParserRuleContext) -> str:
    listener = TreeToProgramListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return listener.getProgram()

from antlr4 import (
    ParseTreeListener,
    TerminalNode,
)
from antlr4.error.ErrorListener import ErrorListener


class NodeCountListener(ParseTreeListener):
    def __init__(self):
        self.count = 0

    def enterEveryRule(self, ctx):
        self.count += 1


class TreeToProgramListener(ParseTreeListener):
    def __init__(self) -> None:
        self.result: list[str] = []

    def visitTerminal(self, node: TerminalNode) -> None:
        self.result.append(node.getText())

    def getProgram(self) -> str:
        return " ".join(self.result)


class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.has_errors = True

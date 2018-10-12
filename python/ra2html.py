import io, sys

from antlr4 import *
from antlr4.InputStream import InputStream

from RelationalAlgebraLexer import RelationalAlgebraLexer
from RelationalAlgebraParser import RelationalAlgebraParser
from RelationalAlgebraVisitor import RelationalAlgebraVisitor

from parser import *


class RelationalAlgebraToHtml(RelationalAlgebraVisitor):

    def visitRelStmts(self, ctx:RelationalAlgebraParser.RelStmtsContext):
        return "<br />".join([self.visit(stmt) for stmt in ctx.relStmt()])


    def visitRelStmtAssign(self, ctx:RelationalAlgebraParser.RelStmtAssignContext):
        s = "<em>%s</em>" % ctx.relName.text
        if ctx.attrNames is not None and len(ctx.attrNames) > 0:
            s += "("
            s += ", ".join([a.text for a in ctx.attrNames])
            s += ")"

        s += " &larr; " + self.visit(ctx.relExpr())

        return s


    def visitRelStmtNoAssign(self, ctx:RelationalAlgebraParser.RelStmtNoAssignContext):
        return self.visit(ctx.relExpr())


    def visitRelStmtSchema(self, ctx:RelationalAlgebraParser.RelStmtSchemaContext):
        s = "<em>%s</em> = (" % ctx.SCHEMA_NAME().getText()
        s += ", ".join(["<em>%s</em>" % n.getText() for n in ctx.NAME()])
        s += ")"

        return s


    def visitRelExprRelationVariable(self, ctx:RelationalAlgebraParser.RelExprRelationVariableContext):
        return "<span class='relvar'>%s</span>" % ctx.NAME().getText()

    def visitRelExprDivision(self, ctx:RelationalAlgebraParser.RelExprDivisionContext):
        return self.visit(ctx.relExpr(0)) + " &divide; " + self.visit(ctx.relExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprConstantRelation.
    def visitRelExprConstantRelation(self, ctx:RelationalAlgebraParser.RelExprConstantRelationContext):
        return "{" + ", ".join([self.visit(r) for r in ctx.rowExpr()]) + "}"


    # RelationalAlgebraParser#RelExprRename.
    def visitRelExprRename(self, ctx:RelationalAlgebraParser.RelExprRenameContext):
        s = "&rho;<sub>"
        s += ", ".join([self.visit(e) for e in ctx.namedScalarExpr()])
        s += "</sub>"
        s += "(" + self.visit(ctx.relExpr()) + ")"
        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprGroupAggregate.
    def visitRelExprGroupAggregate(self, ctx:RelationalAlgebraParser.RelExprGroupAggregateContext):
        s = ""
        if ctx.groups is not None:
            s += "<sub>"
            s += ", ".join([self.visit(g) for g in ctx.groups])
            s += "</sub>"

        s += "<span class='group_operator'>G</span>"

        s += "<sub>"
        s += ", ".join([self.visit(a) for a in ctx.aggregates])
        s += "</sub>"

        s += "(" + self.visit(ctx.relExpr()) + ")"

        return s

    # Visit a parse tree produced by RelationalAlgebraParser#RelExprParens.
    def visitRelExprParens(self, ctx:RelationalAlgebraParser.RelExprParensContext):
        return "(" + self.visit(ctx.relExpr()) + ")"

    # === PROJECT OPERATION ==================================================

    # Visit a parse tree produced by RelationalAlgebraParser#RelExprProject.
    def visitRelExprProject(self, ctx:RelationalAlgebraParser.RelExprProjectContext):
        s = "&Pi;<sub>"
        s += ", ".join([self.visit(e) for e in ctx.projectExpr()])
        s += "</sub>(" + self.visit(ctx.relExpr()) + ")"
        return s

    def visitProjectSchemaExpr(self, ctx:RelationalAlgebraParser.ProjectSchemaExprContext):
        return self.visit(ctx.schemaExpr())

    def visitProjectNamedScalarExpr(self, ctx:RelationalAlgebraParser.ProjectNamedScalarExprContext):
        return self.visit(ctx.namedScalarExpr())

    # === SCHEMA OPERATIONS ==================================================

    def visitSchemaExprSetUnion(self, ctx:RelationalAlgebraParser.SchemaExprSetUnionContext):
        return self.visit(ctx.schemaExpr(0)) + " &cup; " + self.visit(ctx.schemaExpr(1))

    def visitSchemaExprSetIntersect(self, ctx:RelationalAlgebraParser.SchemaExprSetIntersectContext):
        return self.visit(ctx.schemaExpr(0)) + " &cap; " + self.visit(ctx.schemaExpr(1))

    def visitSchemaExprSetDifference(self, ctx:RelationalAlgebraParser.SchemaExprSetDifferenceContext):
        return self.visit(ctx.schemaExpr(0)) + " - " + self.visit(ctx.schemaExpr(1))

    def visitSchemaExprName(self, ctx:RelationalAlgebraParser.SchemaExprNameContext):
        return "<em>" + ctx.SCHEMA_NAME().getText() + "</em>"

    def visitSchemaExprParens(self, ctx:RelationalAlgebraParser.SchemaExprParensContext):
        return "(" + self.visit(ctx.schemaExpr()) + ")"

    # === RELATIONAL SET OPERATIONS ==========================================

    # RelationalAlgebraParser#RelExprSetUnion.
    def visitRelExprSetUnion(self, ctx:RelationalAlgebraParser.RelExprSetUnionContext):
        return self.visit(ctx.relExpr(0)) + " &cup; " + self.visit(ctx.relExpr(1))

    # Visit a parse tree produced by RelationalAlgebraParser#RelExprSetIntersect.
    def visitRelExprSetIntersect(self, ctx:RelationalAlgebraParser.RelExprSetIntersectContext):
        return self.visit(ctx.relExpr(0)) + " &cap; " + self.visit(ctx.relExpr(1))

    # Visit a parse tree produced by RelationalAlgebraParser#RelExprSetDifference.
    def visitRelExprSetDifference(self, ctx:RelationalAlgebraParser.RelExprSetDifferenceContext):
        return self.visit(ctx.relExpr(0)) + " - " + self.visit(ctx.relExpr(1))

    # === JOINS ==============================================================

    def visitRelExprCrossProduct(self, ctx:RelationalAlgebraParser.RelExprCrossProductContext):
        return self.visit(ctx.relExpr(0)) + " &times; " + self.visit(ctx.relExpr(1))

    def visitRelExprInnerJoin(self, ctx:RelationalAlgebraParser.RelExprInnerJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &bowtie;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s

    def visitRelExprLeftOuterJoin(self, ctx:RelationalAlgebraParser.RelExprLeftOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d5;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s

    def visitRelExprRightOuterJoin(self, ctx:RelationalAlgebraParser.RelExprRightOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d6;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s

    def visitRelExprFullOuterJoin(self, ctx:RelationalAlgebraParser.RelExprFullOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d7;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprSelect.
    def visitRelExprSelect(self, ctx:RelationalAlgebraParser.RelExprSelectContext):
        return "&sigma;<sub>" + self.visit(ctx.scalarExpr()) + "</sub>(" + \
            self.visit(ctx.relExpr()) + ")"


    # Visit a parse tree produced by RelationalAlgebraParser#rowExpr.
    def visitRowExpr(self, ctx:RelationalAlgebraParser.RowExprContext):
        return "(" + ", ".join([self.visit(v) for v in ctx.literalValue()]) + ")"


    # RelationalAlgebraParser#namedScalarExpr.
    def visitNamedScalarExpr(self, ctx:RelationalAlgebraParser.NamedScalarExprContext):
        s = self.visit(ctx.scalarExpr())
        if ctx.NAME() is not None:
            s += " <b>as</b> <em>%s</em>" % ctx.NAME().getText()

        return s


    # RelationalAlgebraParser#ScalarExprAttribute.
    def visitScalarExprAttribute(self, ctx:RelationalAlgebraParser.ScalarExprAttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprUnarySign.
    def visitScalarExprUnarySign(self, ctx:RelationalAlgebraParser.ScalarExprUnarySignContext):
        return "-" + self.visit(ctx.scalarExpr())


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprFunction.
    def visitScalarExprFunction(self, ctx:RelationalAlgebraParser.ScalarExprFunctionContext):
        s = "<span class='func_name'>%s</span>(" % ctx.NAME().getText()
        s += ", ".join([self.visit(e) for e in ctx.scalarExpr()])
        s += ")"

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprOr.
    def visitScalarExprOr(self, ctx:RelationalAlgebraParser.ScalarExprOrContext):
        return self.visit(ctx.scalarExpr(0)) + " &or; " + self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprAdd.
    def visitScalarExprAdd(self, ctx:RelationalAlgebraParser.ScalarExprAddContext):
        return self.visit(ctx.scalarExpr(0)) + (" %s " % ctx.op.text) + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprNot.
    def visitScalarExprNot(self, ctx:RelationalAlgebraParser.ScalarExprNotContext):
        return "&not;" + self.visit(ctx.scalarExpr())


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprMul.
    def visitScalarExprMul(self, ctx:RelationalAlgebraParser.ScalarExprMulContext):
        s = self.visit(ctx.scalarExpr(0))

        if ctx.op.text == "*":
            s += " &times; "
        else:
            assert op.txt == "/"
            s += " / "

        s += self.visit(ctx.scalarExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprCompare.
    def visitScalarExprCompare(self, ctx:RelationalAlgebraParser.ScalarExprCompareContext):
        op_map = {
            "="  : "=",
            "==" : "=",
            "!=" : "&ne;",
            "<>" : "&ne;",
            ">"  : "&gt;",
            "<"  : "&lt;",
            ">=" : "&ge;",
            "<=" : "&le;",
        }

        op = op_map[ctx.op.text]
        return self.visit(ctx.scalarExpr(0)) + \
               " <span class='operator'>" + op + "</span> " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprAnd.
    def visitScalarExprAnd(self, ctx:RelationalAlgebraParser.ScalarExprAndContext):
        return self.visit(ctx.scalarExpr(0)) + " &and; " + self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprLiteral.
    #def visitScalarExprLiteral(self, ctx:RelationalAlgebraParser.ScalarExprLiteralContext):
    #    return self.visitChildren(ctx)


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprParens.
    def visitScalarExprParens(self, ctx:RelationalAlgebraParser.ScalarExprParensContext):
        return "(" + self.visit(ctx.scalarExpr()) + ")"


    # Visit a parse tree produced by RelationalAlgebraParser#AttrNameSimple.
    def visitAttrNameSimple(self, ctx:RelationalAlgebraParser.AttrNameSimpleContext):
        return "<span class='attr_name'>%s</span>" % ctx.NAME().getText()


    # Visit a parse tree produced by RelationalAlgebraParser#AttrNameQualified.
    def visitAttrNameQualified(self, ctx:RelationalAlgebraParser.AttrNameQualifiedContext):
        return ".".join(["<span class='attr_name'>%s</span>" % n.getText() for n in ctx.NAME()])


    # Visit a parse tree produced by RelationalAlgebraParser#LiteralNumber.
    def visitLiteralNumber(self, ctx:RelationalAlgebraParser.LiteralNumberContext):
        return "<span class='number'>%s</span>" % ctx.NUMBER().getText()


    # Visit a parse tree produced by RelationalAlgebraParser#LiteralString.
    def visitLiteralString(self, ctx:RelationalAlgebraParser.LiteralStringContext):
        return "<span class='string'>%s</span>" % ctx.STRING().getText()


    # RelationalAlgebraParser#LiteralTrue.
    def visitLiteralTrue(self, ctx:RelationalAlgebraParser.LiteralTrueContext):
        return "<span class='boolean'>true</span>"


    # RelationalAlgebraParser#LiteralFalse.
    def visitLiteralFalse(self, ctx:RelationalAlgebraParser.LiteralFalseContext):
        return "<span class='boolean'>false</span>"


    # RelationalAlgebraParser#LiteralNull.
    def visitLiteralNull(self, ctx:RelationalAlgebraParser.LiteralNullContext):
        return "<span class='null'>null</span>"


def format_relational_algebra(ra_str):
    error_listener = UnderlineListener()

    parser = parse_str(ra_str)

    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    parse_tree = parser.relStmts()
    visitor = RelationalAlgebraToHtml()

    html = visitor.visit(parse_tree)

    if error_listener.errors:
        errors = "<div class='errors'>Errors encountered during parse:<br /><br />"

        for msg in error_listener.errors:
            errors += "<pre>" + msg + "</pre>"

        errors += "</div>"

        html += errors

    return html


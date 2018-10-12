import io, sys

from antlr4 import *
from antlr4.InputStream import InputStream

from RelationalAlgebraLexer import RelationalAlgebraLexer
from RelationalAlgebraParser import RelationalAlgebraParser
from RelationalAlgebraVisitor import RelationalAlgebraVisitor


def get_expr_name(ctx):
    name = None

    if isinstance(ctx, RelationalAlgebraParser.NamedScalarExprContext):
        if ctx.NAME() is not None:
            name = ctx.NAME().getText()

        ctx = ctx.scalarExpr()

    if name is None and \
       isinstance(ctx, RelationalAlgebraParser.ScalarExprAttributeContext):
        name = ctx.attrName().getText()

    return name


class RelationValue:
    def __init__(self, attributes=None, rows=[]):
        self.attributes = attributes
        self.rows = set(rows)

    def __check_attrs(self, attributes):
        if attributes is None:
            return

        s = set()
        for a in attributes:
            if a is None:
                raise ValueError('Attribute name cannot be None.')

            if a in s:
                raise ValueError('Attribute \"%s\" is ambiguous.' % a)

            s.add(a)


    def num_attrs(self):
        return len(self.attributes)

    def set_relation_name(self, rel_name):
        attr_names = []
        for a in self.attributes:
            p = a.split('.')
            n = p[-1]
            if n in attr_names:
                raise ValueError("Cannot set relation name to %s:  " + \
                    "Attribute name %s appears multiple times" % \
                    (rel_name, n))

            attr_names.append(n)

        self.attributes = [rel_name + '.' + n for n in attr_names]


    def get_attrs(self):
        return list(self.attributes)

    def set_attrs(self, attrs):
        if self.attributes is not None and len(attrs) != len(self.attributes):
           raise ValueError("Relation-value has %d attributes, but %d "
               "were specified" % (len(self.attributes), len(attrs)))

        self.__check_attrs(attrs)
        self.attributes = list(attrs)


    def has_unnamed_attrs(self):
        if self.attributes is None:
            return True

        for a in self.attributes:
            if a is None:
                return True

        return False

    def get_attr_index(self, name):
        if '.' in name:
            # This will raise a ValueError if the name is not found.
            return self.attributes.index(name)

        i_found = None
        for i, a in enumerate(self.attributes):
            p = a.split('.')

            if name == p[-1]:
                if i_found is not None:
                    raise ValueError('Attribute name %s is ambiguous' % name)

                i_found = i

        if i_found is None:
            raise ValueError('No attribute with name %s' % name)

        return i_found


    def add_row(self, row):
        if type(row) != tuple:
            raise ValueError("row must be a tuple; got " + str(type(row)))

        if self.attributes is None:
            self.attributes = [None] * len(row)

        if len(row) != len(self.attributes):
           raise ValueError("Relation-value has %d attributes; row has %d "
               "attributes" % (len(self.attributes), len(row)))

        self.rows.add(row)

    def num_rows(self):
        return len(self.rows)

    def get_rows(self):
        return set(self.rows)

    def pretty_print(self):
        s = ''

        if self.attributes is not None:
            s += "(" + ",".join([a if a is not None else "unnamed" \
                                 for a in self.attributes]) + ")"

        print(s)
        print('-' * len(s))

        if len(self.rows) > 0:
            for r in self.rows:
                print(r)
        else:
            print('no rows')


class Database:
    def __init__(self):
        self.relation_variables = {}

    def get_relvar_names(self):
        return list(self.relation_variables.keys())

    def get_relvar(self, name):
        return self.relation_variables.get(name)

    def set_relvar(self, name, relval):
        if relval.has_unnamed_attrs():
            raise ValueError("Relation-value has unnamed attributes.")

        self.relation_variables[name] = relval

    def del_relvar(self, name):
        del self.relation_variables[name]


class RelationalAlgebraEvaluator(RelationalAlgebraVisitor):

    def __init__(self, database):
        self.database = database


    def visitRelStmtAssign(self, ctx:RelationalAlgebraParser.RelStmtAssignContext):
        # Evaluate the name and attribute-names, if present.
        relvar_name = ctx.relName.text
        attrNames = [relvar_name + "." + a.text for a in ctx.attrNames]

        # Evaluate the RHS relation-value.
        relval = self.visit(ctx.relExpr())

        if len(attrNames) > 0:
            # Names of attributes were specified in the assignment statement.
            relval.set_attrs(attrNames)
        else:
            # Attribute names aren't specified.  See if there is an old
            # relation-value with attribute names, and if so, pull the names
            # from there.

            old_relval = self.database.get_relvar(name)
            if old_relval is not None:
                relval.set_attrs(old_relval.get_attrs())

        self.database.set_relvar(relvar_name, relval)
        return relval


    def visitRelStmtNoAssign(self, ctx:RelationalAlgebraParser.RelStmtNoAssignContext):
        return self.visit(ctx.relExpr())


    def visitRelExprRelationVariable(self, ctx:RelationalAlgebraParser.RelExprRelationVariableContext):
        return self.database.get_relvar(ctx.NAME().getText())


    def visitRelExprDivision(self, ctx:RelationalAlgebraParser.RelExprDivisionContext):
        lhs = self.visit(ctx.relExpr(0))
        rhs = self.visit(ctx.relExpr(1))

        # TODO:  Implement!

        return RelationValue([])


    # Compute the cross-product of two relation-values.
    def visitRelExprCrossProduct(self, ctx:RelationalAlgebraParser.RelExprCrossProductContext):
        lhs = self.visit(ctx.relExpr(0))
        lhs_attrs = lhs.get_attrs()

        rhs = self.visit(ctx.relExpr(1))
        rhs_attrs = rhs.get_attrs()

        result_attrs = lhs_attrs + rhs_attrs
        result = RelationValue(result_attrs)

        for lhs_row in lhs.get_rows():
            for rhs_row in rhs.get_rows():
                result.add_row(lhs_row + rhs_row)

        return result


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprConstantRelation.
    def visitRelExprConstantRelation(self, ctx:RelationalAlgebraParser.RelExprConstantRelationContext):
        relval = RelationValue()
        for r in ctx.rowExpr():
            relval.add_row(self.visit(r))

        return relval


    # RelationalAlgebraParser#RelExprRename.
    def visitRelExprRename(self, ctx:RelationalAlgebraParser.RelExprRenameContext):
        relval = self.visit(ctx.relExpr())
        # TODO:  Rename the result before returning it.
        return relval


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

        return s


    # Compute the set-union of two relation-values.
    def visitRelExprSetUnion(self, ctx:RelationalAlgebraParser.RelExprSetUnionContext):
        lhs = self.visit(ctx.relExpr(0))
        rhs = self.visit(ctx.relExpr(1))
        if lhs.num_attrs() != rhs.num_attrs():
            raise ValueError("Arity of LHS is %d, but RHS is %d" % (lhs.num_attrs(), rhs.num_attrs()))

        return RelationValue(lhs.get_attrs(), lhs.rows | rhs.rows)


    # Compute the set-intersection of two relation-values.
    def visitRelExprSetIntersect(self, ctx:RelationalAlgebraParser.RelExprSetIntersectContext):
        lhs = self.visit(ctx.relExpr(0))
        rhs = self.visit(ctx.relExpr(1))
        if lhs.num_attrs() != rhs.num_attrs():
            raise ValueError("Arity of LHS is %d, but RHS is %d" % \
                             (lhs.num_attrs(), rhs.num_attrs()))

        return RelationValue(lhs.get_attrs(), lhs.rows & rhs.rows)


    # Compute the set-difference of two relation-values.
    def visitRelExprSetDifference(self, ctx:RelationalAlgebraParser.RelExprSetDifferenceContext):
        lhs = self.visit(ctx.relExpr(0))
        rhs = self.visit(ctx.relExpr(1))
        if lhs.num_attrs() != rhs.num_attrs():
            raise ValueError("Arity of LHS is %d, but RHS is %d" % \
                             (lhs.num_attrs(), rhs.num_attrs()))

        return RelationValue(lhs.get_attrs(), lhs.rows - rhs.rows)


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprParens.
    def visitRelExprParens(self, ctx:RelationalAlgebraParser.RelExprParensContext):
        return self.visit(ctx.relExpr())


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprProject.
    def visitRelExprProject(self, ctx:RelationalAlgebraParser.RelExprProjectContext):
        input_relval = self.visit(ctx.relExpr())

        attr_names = []
        eval_strs = []
        for e in ctx.namedScalarExpr():
            attr_names.append(get_expr_name(e))
            eval_strs.append(self.visit(e))

        output_relval = RelationValue(attr_names)

        for row in input_relval.get_rows():
            # Set up the environment to evaluate each of the project exprs.
            project_env = {}
            for i, a in enumerate(input_relval.get_attrs()):
                project_env[a] = row[i]

            # Evaluate each project-expression to assemble the output row.
            out_row = tuple([eval(s, project_env) for s in eval_strs])
            output_relval.add_row(out_row)

        return output_relval



    # Visit a parse tree produced by RelationalAlgebraParser#RelExprLeftOuterJoin.
    def visitRelExprLeftOuterJoin(self, ctx:RelationalAlgebraParser.RelExprLeftOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d5;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprRightOuterJoin.
    def visitRelExprRightOuterJoin(self, ctx:RelationalAlgebraParser.RelExprRightOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d6;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprFullOuterJoin.
    def visitRelExprFullOuterJoin(self, ctx:RelationalAlgebraParser.RelExprFullOuterJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &#x27d7;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprInnerJoin.
    def visitRelExprInnerJoin(self, ctx:RelationalAlgebraParser.RelExprInnerJoinContext):
        s = self.visit(ctx.relExpr(0)) + " &bowtie;"
        if ctx.scalarExpr() is not None:
            s += "<sub>" + self.visit(ctx.scalarExpr()) + "</sub>"

        s += " " + self.visit(ctx.relExpr(1))

        return s


    # Visit a parse tree produced by RelationalAlgebraParser#RelExprSelect.
    def visitRelExprSelect(self, ctx:RelationalAlgebraParser.RelExprSelectContext):
        pred_str = self.visit(ctx.scalarExpr())
        input_relval = self.visit(ctx.relExpr())

        output_relval = RelationValue(input_relval.get_attrs())

        for row in input_relval.get_rows():
            # Set up the environment to evaluate the predicate.
            pred_env = {}
            for i, a in enumerate(input_relval.get_attrs()):
                pred_env[a] = row[i]

            # Evaluate the predicate.  If it's True, include the row.
            pred_val = eval(pred_str, pred_env)
            if pred_val == True:
                output_relval.add_row(row)

        return output_relval


    # Visit a parse tree produced by RelationalAlgebraParser#rowExpr.
    def visitRowExpr(self, ctx:RelationalAlgebraParser.RowExprContext):
        # Generate a tuple containing all values in the row-expression.
        # Individual values are strings, so eval() them to get to a value.
        return tuple(eval(self.visit(v)) for v in ctx.literalValue())


    # RelationalAlgebraParser#namedScalarExpr.
    def visitNamedScalarExpr(self, ctx:RelationalAlgebraParser.NamedScalarExprContext):
        return self.visit(ctx.scalarExpr())


    # RelationalAlgebraParser#ScalarExprAttribute.
    def visitScalarExprAttribute(self, ctx:RelationalAlgebraParser.ScalarExprAttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprUnarySign.
    def visitScalarExprUnarySign(self, ctx:RelationalAlgebraParser.ScalarExprUnarySignContext):
        return "-" + self.visit(ctx.scalarExpr())


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprFunction.
    def visitScalarExprFunction(self, ctx:RelationalAlgebraParser.ScalarExprFunctionContext):
        return ctx.NAME().getText() + "(" + \
               ", ".join([self.visit(e) for e in ctx.scalarExpr()]) + ")"


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprOr.
    def visitScalarExprOr(self, ctx:RelationalAlgebraParser.ScalarExprOrContext):
        return self.visit(ctx.scalarExpr(0)) + " or " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprAdd.
    def visitScalarExprAdd(self, ctx:RelationalAlgebraParser.ScalarExprAddContext):
        return self.visit(ctx.scalarExpr(0)) + " " + ctx.op.text + " " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprNot.
    def visitScalarExprNot(self, ctx:RelationalAlgebraParser.ScalarExprNotContext):
        return "not " + self.visit(ctx.scalarExpr())


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprMul.
    def visitScalarExprMul(self, ctx:RelationalAlgebraParser.ScalarExprMulContext):
        return self.visit(ctx.scalarExpr(0)) + " " + ctx.op.text + " " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprCompare.
    def visitScalarExprCompare(self, ctx:RelationalAlgebraParser.ScalarExprCompareContext):
        op_map = {
            "="  : "==",
            "==" : "==",
            "!=" : "!=",
            "<>" : "!=",
            ">"  : ">",
            "<"  : "<",
            ">=" : ">=",
            "<=" : "<=",
        }

        op = op_map[ctx.op.text]
        return self.visit(ctx.scalarExpr(0)) + " " + op + " " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprAnd.
    def visitScalarExprAnd(self, ctx:RelationalAlgebraParser.ScalarExprAndContext):
        return self.visit(ctx.scalarExpr(0)) + " and " + \
               self.visit(ctx.scalarExpr(1))


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprLiteral.
    #def visitScalarExprLiteral(self, ctx:RelationalAlgebraParser.ScalarExprLiteralContext):
    #    return self.visitChildren(ctx)


    # Visit a parse tree produced by RelationalAlgebraParser#ScalarExprParens.
    def visitScalarExprParens(self, ctx:RelationalAlgebraParser.ScalarExprParensContext):
        return "(" + self.visit(ctx.scalarExpr()) + ")"


    # Visit a parse tree produced by RelationalAlgebraParser#AttrNameSimple.
    def visitAttrNameSimple(self, ctx:RelationalAlgebraParser.AttrNameSimpleContext):
        return ctx.NAME().getText()


    # Visit a parse tree produced by RelationalAlgebraParser#AttrNameQualified.
    def visitAttrNameQualified(self, ctx:RelationalAlgebraParser.AttrNameQualifiedContext):
        return ".".join([n.getText() for n in ctx.NAME()])


    # Visit a parse tree produced by RelationalAlgebraParser#LiteralNumber.
    def visitLiteralNumber(self, ctx:RelationalAlgebraParser.LiteralNumberContext):
        return ctx.NUMBER().getText()


    # Visit a parse tree produced by RelationalAlgebraParser#LiteralString.
    def visitLiteralString(self, ctx:RelationalAlgebraParser.LiteralStringContext):
        return ctx.STRING().getText()


    # RelationalAlgebraParser#LiteralTrue.
    def visitLiteralTrue(self, ctx:RelationalAlgebraParser.LiteralTrueContext):
        return "True"


    # RelationalAlgebraParser#LiteralFalse.
    def visitLiteralFalse(self, ctx:RelationalAlgebraParser.LiteralFalseContext):
        return "False"


    # RelationalAlgebraParser#LiteralNull.
    def visitLiteralNull(self, ctx:RelationalAlgebraParser.LiteralNullContext):
        return "None"


def eval_ra_expr(database, ra_str):
    input_stream = InputStream(ra_str)
    lexer = RelationalAlgebraLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = RelationalAlgebraParser(token_stream)

    parse_tree = parser.relStmt()
    visitor = RelationalAlgebraEvaluator(database)
    return visitor.visit(parse_tree)


if __name__ == '__main__':
    db = Database()

    while True:
        try:
            inp = input("RA:  ")
            if inp in ['exit', 'quit']:
                break

            result = eval_ra_expr(db, inp)
            result.pretty_print()
        except Exception as e:
            print("ERROR:  " + str(e))
            raise e


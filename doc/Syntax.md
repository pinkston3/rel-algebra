# Relational Algebra Syntax

This program implements a simple language for specifying Relational Algebra
expressions.  This document specifies the syntax of these expressions.

## Keywords

Keywords are used to indicate various operations that can be performed with
relational algebra.  In this documentation we follow the convention that
keywords are written in all uppercase, but the parser is case-insensitive
when it comes to keywords.

Note that this language is intended as an instructional tool, so operations
are named based on their symbols rather than on their function.  This is to
help users internalize the operations that go with the corresponding symbols.

## Names

The relational algebra syntax supports the specification of both relation
schemas and query expressions.  As in the course slides and textbook, names
must follow specific guidelines.

*   Relation-schema names must always start with a capital letter, and are
    comprised of letters, numbers and the underscore character `_`.  For
    example, `Account_schema` is a valid schema name.

*   Relation-names used for relation-variables and names used in renaming
    expressions must always start with a lowercase letter, and are comprised
    of letters, numbers and the underscore character `_`.  For example,
    `account` is a valid relation-variable name.

*   All attribute names must start with a lowercase letter, and are comprised
    of letters, numbers and the underscore character `_`.  For example,
    `branch_name` is a valid attribute name.

## Statements

At the top level, relational algebra statements can take one of these forms.
Note that all statements must end with a semicolon; otherwise the parser won't
know where the statement ends.  Also, placement of whitespace is usually
irrelevant, but the below examples are written in a style to promote clarity.

To compute a relation-value from an algebra expression, type in the expression:

        expr ;

To store the computed relation-value into a relation-variable, use the arrow
operator `<-` like this:

        relvar_name <- expr ;

To specify a relation schema, use the equals operator `=` like this:

        Schema_name = (attr1_name , attr2_name , ...) ;

## Operations - General Patterns

Relational algebra operations are specified in the same basic way that they
are in the textbook and lecture slides, although the symbol names are written
out instead of using the various Greek letters and symbols directly.

Relational operators that take one argument (such as select, project and
rename) require that argument to be enclosed in parentheses.

Many relational operators allow or require additional details, such as
predicates, expressions for projecting/grouping/aggregating, etc.  These
details are always enclosed in square-brackets `[]` to set them apart from
the rest of the query.

## Literal Values

The relational algebra program supports a limited number of types.

*   Numbers are any valid integer or decimal number.

*   Strings are sequences of characters enclosed by double-quotes `"`.
    Note that there is no support for escape sequences, so strings cannot
    contain double-quotes or other special characters.

*   Boolean values may be specified as `true` or `false` (case insensitive).

*   The _null_ value (meaning "unknown or unspecified value) may be specified
    as `null` (case insensitive).

## Constant Relations

A constant relation may be written using a syntax similar to the one described
in class:

        { (1, "a"), (2, "b"), (3, "c") }

The set of rows is enclosed with curly-braces, and each individual row is
enclosed with parentheses.  Rows are separated by commas.  As one might expect,
all values in a constant relation must be literal values; no attribute names
may be used.

Constant relations may be used anywhere that a relation-value must appear in
an expression.  They can be used to assign rows to a relation-variable, or
feed input into a relational algebra query.

**Note that the constant relation specifies no relvar name or attribute
names!**  These can be added e.g. by using a rename operation.

## Select

Select operations use the `SIGMA` keyword:

        SIGMA[a > 5](r)

Note that the predicate is enclosed in square-brackets, and appears immediately
after the keyword.  (Whitespace is irrelevant.)  Here are some additional
details:

*   Comparisons may use any of the typical operators:  `>`, `<`, `>=`, `<=`,
    `=` (or `==` if you prefer), and `!=` (or `<>` if you prefer).

*   The predicate may include multiple comparisons combined with the `AND`,
    `OR` and `NOT` keywords (or `&&`, `||` and `!` if you prefer).

*   Basic arithmetic expressions are supported, including `+`, `-`, `*` and
    `/` for addition, subtraction, multiplication, and division.  Remainder
    is not supported at this time.

## Project

Project operations use the `PI` keyword:

        PI[b, c](r)

Project operations also support basic arithmetic, as described in the
**Select** section.  Thus, this operator is a _generalized project_.

Individual values may also be named using the notation described in class
and in the textbook, for example:

        PI[a + 5 AS a_plus_five](r)

## Rename

Rename operations use the `RHO` keyword:

        RHO[s](r)

In this example, `s` is the new relation name, but the attributes retain
their names.  Rename operations also support specifying new attribute names,
like this:

        RHO[s(b, c)](r)

Now, a relation `r(a, b)` would be renamed to `s(b, c)`.

## Set Operations

All of the relational set-operations are supported, using keywords to specify
the operation being performed.

This is a set union:

        r UNION s

This is a set intersection:

        r INTERSECT s

This is a set difference:

        r MINUS s

As usual, the left and right relations must have compatible schemas for this
to be a legal operation.

## Joins

A wide range of join operations are supported by the relational algebra syntax.

### Cartesian Products

A Cartesian product may be specified with the `CROSS` or `TIMES` keyword.
For example:

        r CROSS s
        r TIMES s

### Natural Joins

A natural inner join may be specified with the `BOWTIE` keyword:

        r BOWTIE s

The join may be changed to a left/right/full outer join by modifying the
keyword used:

        r LBOWTIE s
        r RBOWTIE s
        r FBOWTIE s

### Theta Joins

Any of the natural-join expressions may be turned into a theta-join expression
by specifying a predicate immediately after the `BOWTIE` keyword, like this:

        r BOWTIE[r.a = s.b] s
        r FBOWTIE[r.a = s.b] s

## Relational Division

Relational division is specified with the `DIVIDE` keyword:

        r DIVIDE s

## Grouping and Aggregation

Grouping and aggregation is specified with the `GROUP` keyword:

        [a, b]GROUP[min(c) AS min_c, max(d) AS max_d](r)

This expression specifies grouping on the attributes `(a, b)`, and computing
the aggregates `min(c)` and `max(d)` on the groups.

To operate on the entire input relation, the leading square-brackets `[]`
may be excluded.  For example:

        GROUP[min(c) AS min_c, max(d) AS max_d](r)

This expression computes `min(c)` and `max(d)` over all of `r`, without
applying any grouping first.



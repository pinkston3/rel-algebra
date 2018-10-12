import pkgutil, sys

from pset import load_problem_file, PartType
from parser import *


def check_problem(problems, pid, out):
    sub = problems.get(pid, [])

    for s in sub:
        if s[0] == PartType.COMMENT:
            print(" * %d lines of comments" % len(s[1]), file=out)

        else:
            assert s[0] == PartType.ANSWER
            desc = " * %d lines of relational algebra" % len(s[1])

            # Try to parse the text

            text = '\n'.join(s[1])
            error_listener = UnderlineListener()

            parser = parse_str(text)

            parser.removeErrorListeners()
            parser.addErrorListener(error_listener)
            parse_tree = parser.relStmts()

            if error_listener.errors:
                err_msgs = "\n".join([m for m in error_listener.errors])
                desc += " - ERRORS ENCOUNTERED\n\n" + err_msgs
            else:
                desc += " - parsed successfully"

            print(desc, file=out)


def check_problem_file(filename, out=sys.stdout, problem_ids=None):
    problems = load_problem_file(filename)

    if problem_ids is None:
        problem_ids = list(problems.keys())
        problem_ids = [pid for pid in problem_ids if pid is not None]
        problem_ids.sort()

    if problems.get(None, []):
        # Check the header contents.
        print("\nHeader", file=out)
        check_problem(problems, None, out)

    for pid in problem_ids:
        print("\n" + pid, file=out)
        check_problem(problems, pid, out)


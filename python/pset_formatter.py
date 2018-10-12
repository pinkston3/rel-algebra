import os, pkgutil, sys

from pset import load_problem_file, PartType


def format_problem(problems, pid, answer_formatter, out):
    sub = problems.get(pid, [])
    for s in sub:
        if s[0] == PartType.COMMENT:
            print("<div class='comment'>", file=out)

            text = '\n'.join(s[1])
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            print(text, file=out)

            print("</div>", file=out)

        else:
            assert s[0] == PartType.ANSWER

            print("<div class='answer'>", file=out)

            text = '\n'.join(s[1])
            text = answer_formatter(text)

            print(text, file=out)

            print("</div>", file=out)


def format_problem_file(filename, answer_formatter,
                        out=sys.stdout, problem_ids=None, embed_css=True):
    problems = load_problem_file(filename)

    if problem_ids is None:
        # Pull out all problem IDs that are not None, and sort them.
        problem_ids = list(problems.keys())
        problem_ids = [pid for pid in problem_ids if pid is not None]
        problem_ids.sort()

    print("<html><head>", file=out)

    if embed_css:
        # with open('ra.css') as f:
        #     print("<style>", file=out)
        # 
        #     lines = f.readlines()
        #     for line in lines:
        #         print(line[:-1], file=out)
        # 
        #     print("</style>", file=out)

        css_data = pkgutil.get_data(__name__, 'ra.css')
        if css_data is not None:
            print("<style>", file=out)
            out.write(css_data.decode("utf-8"))
            print("</style>", file=out)

    else:
        print("<link rel='stylesheet' type='text/css' href='ra.css'>", file=out)

    print("</head><body>", file=out)

    print("<h1>File:  %s</h1>" % os.path.basename(filename), file=out)

    if None in problems:
        format_problem(problems, None, answer_formatter, out)

    for pid in problem_ids:
        print(pid)

        print("<h2 id='%s'>%s</h2>" % (pid, pid), file=out)
        format_problem(problems, pid, answer_formatter, out)

    print("</body>", file=out)
    print("</html>", file=out)


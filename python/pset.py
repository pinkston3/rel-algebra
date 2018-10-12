from enum import Enum


class PartType(Enum):
    ANSWER = 1
    COMMENT = 2


def load_problem_file(filename):

    problems = {}

    with open(filename) as f:

        # Any initial comments or code will be under the key None.
        problem = None
        parts = []
        problems[problem] = parts

        prev_line_type = None

        while True:
            # Read the next line of the file.  If we have hit EOF,
            # break out of the loop.
            line = f.readline()
            if line == '':
                break

            # Skip blank lines
            line = line.strip()
            if line == '':
                continue

            # Analyze the current line
            if line.startswith('-- [Problem'):
                problem = line[4:-1].strip()

                if problem in problems:
                    raise ValueError("Problem %s already appeared earlier" % problem)

                parts = []
                problems[problem] = parts

                prev_line_type = None

            elif line.startswith('--'):
                comment = line[2:].strip()

                if prev_line_type != PartType.COMMENT:
                    parts.append( (PartType.COMMENT, []) )

                parts[-1][1].append(comment)

                prev_line_type = PartType.COMMENT

            else:
                answer = line.strip()

                if prev_line_type != PartType.ANSWER:
                    parts.append( (PartType.ANSWER, []) )

                parts[-1][1].append(answer)

                prev_line_type = PartType.ANSWER

    return problems


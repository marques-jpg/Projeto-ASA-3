import sys

from pulp import LpInteger, LpMinimize, LpProblem, LpStatusOptimal, LpVariable, PULP_CBC_CMD, lpSum, value


def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    iterator = iter(input_data)
    try:
        n_teams = int(next(iterator))
        n_played = int(next(iterator))
    except StopIteration:
        return

    current_points = [0] * n_teams

    remaining_games = {}
    for i in range(n_teams):
        for j in range(i + 1, n_teams):
            remaining_games[(i, j)] = 2

    for _ in range(n_played):
        try:
            t1 = int(next(iterator)) - 1
            t2 = int(next(iterator)) - 1
            result = int(next(iterator))
        except StopIteration:
            break

        pair = tuple(sorted((t1, t2)))
        if pair in remaining_games:
            remaining_games[pair] -= 1
            if remaining_games[pair] < 0:
                remaining_games[pair] = 0

        if result == 0:
            current_points[t1] += 1
            current_points[t2] += 1
        elif result == (t1 + 1):
            current_points[t1] += 3
        elif result == (t2 + 1):
            current_points[t2] += 3

    games_list = [((i, j), c) for (i, j), c in remaining_games.items() if c > 0]
    vars_wins = {}
    vars_draws = {}
    base_constraints = []
    team_point_terms = [[] for _ in range(n_teams)]
    matches_by_team = [[] for _ in range(n_teams)]

    for (i, j), count in games_list:
        w = LpVariable(f"w_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)
        d = LpVariable(f"d_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)

        vars_wins[(i, j)] = w
        vars_draws[(i, j)] = d

        base_constraints.append(w + d <= count)

        team_point_terms[i].append(3 * w + d)
        team_point_terms[j].append(3 * (count - w - d) + d)

        matches_by_team[i].append((j, (i, j)))
        matches_by_team[j].append((i, (i, j)))

    solver = PULP_CBC_CMD(msg=0, presolve=True, threads=0)

    for target_team in range(n_teams):
        target_matches_list = matches_by_team[target_team]
        target_remaining_matches = sum(remaining_games[pair] for _, pair in target_matches_list)

        prob = LpProblem("Projeto3", LpMinimize)
        for c in base_constraints:
            prob += c

        target_win_terms = []

        for _opp, pair in target_matches_list:
            (u, v) = pair  # u < v
            w = vars_wins[pair]
            d = vars_draws[pair]
            count = remaining_games[pair]

            if target_team == u:
                prob += (w + d == count)
                target_win_terms.append(w)
            else:
                prob += (w == 0)
                target_win_terms.append(count - w - d)

        w_expr = lpSum(target_win_terms) if target_win_terms else 0

        points_target = current_points[target_team] + (2 * w_expr) + target_remaining_matches

        for opp in range(n_teams):
            if opp == target_team:
                continue
            prob += (current_points[opp] + lpSum(team_point_terms[opp]) <= points_target)

        prob += w_expr

        status = prob.solve(solver)

        min_wins_found = int(value(w_expr)) if status == LpStatusOptimal else -1
        print(min_wins_found)


if __name__ == "__main__":
    main()
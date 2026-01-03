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
    vars_losses = {}
    base_constraints = []
    team_point_terms = [[] for _ in range(n_teams)]
    matches_by_team = [[] for _ in range(n_teams)]

    for (i, j), count in games_list:
        x = LpVariable(f"x_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)
        y = LpVariable(f"y_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)
        z = LpVariable(f"z_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)

        vars_wins[(i, j)] = x
        vars_draws[(i, j)] = y
        vars_losses[(i, j)] = z

        base_constraints.append(x + y + z == count)

        team_point_terms[i].append(3 * x + y)
        team_point_terms[j].append(3 * z + y)

        matches_by_team[i].append((j, (i, j)))
        matches_by_team[j].append((i, (i, j)))

    solver = PULP_CBC_CMD(msg=0, presolve=True, threads=0)

    for target_team in range(n_teams):
        target_matches_list = matches_by_team[target_team]
        target_remaining_matches = sum(remaining_games[pair] for _, pair in target_matches_list)

        prob = LpProblem("Projeto3", LpMinimize)
        for c in base_constraints:
            prob += c

        target_wins_vars = []
        target_losses_vars = []

        for opp, pair in target_matches_list:
            (u, v) = pair
            if target_team == u:
                target_wins_vars.append(vars_wins[pair])
                target_losses_vars.append(vars_losses[pair])
            else:
                target_wins_vars.append(vars_losses[pair])
                target_losses_vars.append(vars_wins[pair])

        w_var = LpVariable(
            f"w_target_{target_team}",
            lowBound=0,
            upBound=target_remaining_matches,
            cat=LpInteger,
        )

        prob += (w_var == lpSum(target_wins_vars)) if target_wins_vars else (w_var == 0)
        if target_losses_vars:
            prob += (lpSum(target_losses_vars) == 0)

        points_target = current_points[target_team] + (2 * w_var) + target_remaining_matches

        for opp in range(n_teams):
            if opp == target_team:
                continue
            prob += (current_points[opp] + lpSum(team_point_terms[opp]) <= points_target)

        prob += w_var

        status = prob.solve(solver)

        min_wins_found = int(value(w_var)) if status == LpStatusOptimal else -1
        print(min_wins_found)


if __name__ == "__main__":
    main()
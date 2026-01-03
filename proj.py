import sys

from pulp import GLPK_CMD, LpInteger, LpMinimize, LpProblem, LpStatusOptimal, LpVariable, lpSum, value


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

    for target_team in range(n_teams):
        target_remaining_matches = 0
        target_matches_list = []

        for i in range(n_teams):
            if i == target_team:
                continue
            pair = tuple(sorted((target_team, i)))
            count = remaining_games[pair]
            target_remaining_matches += count
            if count > 0:
                target_matches_list.append((i, pair))

        prob = LpProblem("Projeto3", LpMinimize)

        vars_wins = {}
        vars_draws = {}
        vars_losses = {}

        for (i, j), count in remaining_games.items():
            if count <= 0:
                continue
            x = LpVariable(f"x_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)
            y = LpVariable(f"y_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)
            z = LpVariable(f"z_{i}_{j}", lowBound=0, upBound=count, cat=LpInteger)

            vars_wins[(i, j)] = x
            vars_draws[(i, j)] = y
            vars_losses[(i, j)] = z

            prob += (x + y + z == count)

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
            future_points_opp = []

            for (u, v), count in remaining_games.items():
                if count == 0:
                    continue

                if u == opp:
                    future_points_opp.append(3 * vars_wins[(u, v)])
                    future_points_opp.append(vars_draws[(u, v)])
                elif v == opp:
                    future_points_opp.append(3 * vars_losses[(u, v)])
                    future_points_opp.append(vars_draws[(u, v)])

            prob += (current_points[opp] + lpSum(future_points_opp) <= points_target)

        prob += w_var

        status = prob.solve(GLPK_CMD(msg=0))

        if status == LpStatusOptimal:
            min_wins_found = int(value(w_var))
        else:
            min_wins_found = -1

        print(min_wins_found)


if __name__ == "__main__":
    main()
import itertools
import random

# TODO reset scores button
# TODO remove active player
# TODO remove active machine
# TODO remove match?
# TODO confirmation pop-ups
# TODO reset tournament button?
# TODO manually enter match?


class Machine:
    def __init__(self, name, enabled):
        self.name = name
        self.active = False
        self.enabled = enabled

    def __repr__(self):
        return f"<Machine {self.name} ({'X' if self.active else 'O'})>"

    def serialize(self):
        return {
            "name": self.name,
            "active": self.active,
            "enabled": self.enabled,
        }


class Player:
    def __init__(
        self, name, machines, num_wins=0, num_losses=0, num_played=0, enabled=True,
    ):
        self.name = name
        self.num_wins = num_wins
        self.num_losses = num_losses
        self.num_played = num_played
        self.active = False
        self.enabled = enabled
        self.opponents = set()  # other players already faced
        self.machines = machines  # machines still to play
        self._ratio = 0
        self.calc_ratio()

    def calc_ratio(self):
        if self.num_played:
            self._ratio = round(float(self.num_wins) / self.num_played, 2)

    def __repr__(self):
        return (
            f"<Player {self.name} {self.num_wins} / {self.num_losses} "
            f"({'X' if self.active else 'O'})>"
        )

    @property
    def ratio(self):
        return self._ratio

    def serialize(self):
        return {
            "name": self.name,
            "active": self.active,
            "num_wins": self.num_wins,
            "num_losses": self.num_losses,
            "num_played": self.num_played,
            "opponents": [o.name for o in self.opponents],
            "machines": [m.name for m in self.machines],
            "enabled": self.enabled,
            "ratio": self._ratio,
        }


class Match:
    def __init__(self, match_id, player_a, player_b, machine, winner=None):
        self.id = match_id
        self.player_a = player_a
        self.player_b = player_b
        self.machine = machine
        self.winner = winner

        if winner is None:
            player_a.active = True
            player_b.active = True
            machine.active = True

    def __repr__(self):
        return (
            f"{self.player_a.name} v {self.player_b.name} "
            f"on {self.machine.name}"
        )

    def serialize(self):
        winner_name = None
        if self.winner is not None:
            winner_name = self.winner.name
        return {
            "id": self.id,
            "player_a": self.player_a.name,
            "player_b": self.player_b.name,
            "machine_name": self.machine.name,
            "winner": winner_name,
        }

    def set_winner(self, winner):
        assert self.winner is None
        self.winner = winner

        if winner == self.player_a:
            self.player_a.num_wins += 1
            self.player_b.num_losses += 1
        else:
            self.player_b.num_wins += 1
            self.player_a.num_losses += 1

        self.player_a.active = False
        self.player_a.num_played += 1
        self.player_a.calc_ratio()

        self.player_b.active = False
        self.player_b.num_played += 1
        self.player_b.calc_ratio()

        self.machine.active = False


class Tournament:
    def __init__(self):
        self._players = {}
        self._avail_players = []

        self._machines = {}
        self._enabled_machines = set()

        self._matches = []

        self._sort_by_rank = True

    def sort_by(self, by_rank=True):
        self._sort_by_rank = by_rank

    def add_player(self, name):
        name = name.strip()
        if name in self._players:
            return f"Player '{name}' already exists!"

        player = Player(name, set(self._enabled_machines))

        self._players[name] = player
        self._avail_players.append(player)

        return f"Added new player '{name}'"

    def enable_player(self, name, enable):
        name = name.strip()
        player = self._players.get(name)
        if player is None:
            return f"Player '{name}' doesn't exist!"

        player.enabled = enable
        if enable:
            if player not in self._avail_players:
                self._avail_players.append(player)
        else:
            if player in self._avail_players:
                self._avail_players.remove(player)

        return f"Updated player '{name}' to {enable}"

    def add_machine(self, name, enabled=True):
        """Add a new machine to the tournament."""
        name = name.strip()
        if name in self._machines:
            return f"Machine '{name}' already exists!"

        machine = Machine(name, enabled)
        self._machines[name] = machine
        self._enabled_machines.add(machine)

        for player in self._players.values():
            player.machines.add(machine)

    def enable_machine(self, name, enable):
        name = name.strip()
        machine = self._machines.get(name)
        if machine is None:
            return f"Machine '{name}' doesn't exist!"

        machine.enabled = enable
        if enable:
            self._enabled_machines.add(machine)
        else:
            self._enabled_machines.remove(machine)

    def add_machine_to_player(self, player_name, machine_name):
        machine_name = machine_name.strip()
        machine = self._machines.get(machine_name)
        if machine is None:
            return f"Machine '{machine_name}' doesn't exist!"

        player_name = player_name.strip()
        player = self._players.get(player_name)
        if player is None:
            return f"Player '{player_name}' doesn't exist!"

        player.machines.add(machine)

    def shuffle(self):
        random.shuffle(self._avail_players)

    def next_match(self):
        """Determine the next match, consisting of two players and a machine.

        Prioritize players earlier in the queue rather than trying to maximize
        number of matches since players earlier in the queue might have
        been waiting longer.
        """
        if len(self._avail_players) < 2:
            return "Unable to find another match!"

        # check each player in the queue
        for player_a, player_b in itertools.combinations(self._avail_players, 2):
            # check if players have already played one another
            if player_b in player_a.opponents:
                continue

            if not player_a.enabled:
                self._avail_players.remove(player_a)
                continue

            if not player_b.enabled:
                self._avail_players.remove(player_b)
                continue

            # check if the players have a machine in common
            common_machines = player_a.machines.intersection(player_b.machines)
            if not common_machines:
                continue

            for machine in common_machines:
                if machine.active or not machine.enabled:
                    continue

                match_id = len(self._matches)
                match = Match(match_id, player_a, player_b, machine)
                self._matches.insert(0, match)

                self._avail_players.remove(player_a)
                self._avail_players.remove(player_b)
                player_a.machines.remove(machine)
                player_b.machines.remove(machine)
                player_a.opponents.add(player_b)
                player_b.opponents.add(player_a)
                return str(match)

        return "Unable to find another match!"

    def complete_match(self, match_id, winner_name):
        match = self._matches[match_id]
        winner = self._players[winner_name]
        match.set_winner(winner)

        num_players = len(self._players)

        # re-add the two players to the queue
        self._avail_players.append(match.player_a)
        self._avail_players.append(match.player_b)

        # if the players have faced all other opponents, then reset their opponents lists
        if (len(match.player_a.opponents) + 1) == num_players:
            match.player_a.opponents = set()
        if (len(match.player_b.opponents) + 1) == num_players:
            match.player_b.opponents = set()

        # if the players have played all machines then reset their machines
        if not any(machine.enabled for machine in match.player_a.machines):
            match.player_a.machines = self._enabled_machines
        if not any(machine.enabled for machine in match.player_b.machines):
            match.player_b.machines = self._enabled_machines

    def print_state(self):
        print("Active Matches:")
        for match in self._matches:
            print(f"  {match}")

        print("")
        print("Players:")
        for player in self._players.values():
            print(player)
            for machine in player.machines:
                print(f"  {machine.name}")

        print("")
        print("Machines:")
        for machine in self._machines.values():
            print(machine)

    def get_player_data(self, player_name):
        # TODO handle player not available
        player = self._players[player_name]

        # get opponent data
        players = list(self._players.values())
        players.sort(key=lambda p: p.name)
        opponents = []
        for opponent in players:
            if opponent == player or not opponent.enabled:
                continue

            faced = opponent in player.opponents
            opponent = opponent.serialize()
            opponent["faced"] = faced
            opponents.append(opponent)

        # get played machines list
        machines = list(self._machines.values())
        machines.sort(key=lambda m: m.name)
        played_machines = []
        for machine in machines:
            if not machine.enabled:
                continue

            played = machine not in player.machines
            machine = machine.serialize()
            machine["played"] = played
            played_machines.append(machine)

        # get played matches
        matches = []
        for match in self._matches:
            if match.player_a != player and match.player_b != player:
                continue
            won = match.winner == player
            swap = match.player_a != player
            match = match.serialize()
            match["won"] = won
            if swap:
                match["player_a"], match["player_b"] = match["player_b"], match["player_a"]
            matches.append(match)

        return {
            "player": player.serialize(),
            "machines": played_machines,
            "opponents": opponents,
            "matches": matches,
        }

    def serialize(self):
        # sort the players
        players = list(self._players.values())
        if self._sort_by_rank:
            players.sort(key=lambda p: (-p.enabled, -p.ratio, p.num_played, p.name))
        else:
            len_avail_players = len(self._avail_players)
            players.sort(key=lambda p: (
                self._avail_players.index(p) if p in self._avail_players else len_avail_players,
                -p.enabled,
                p.name
            ))

        # sort the machines
        machines = list(self._machines.values())
        machines.sort(key=lambda m: (-m.enabled, m.active, m.name))

        return {
            "machines": [machine.serialize() for machine in machines],
            "avail_players": [player.name for player in self._avail_players],
            "players": [player.serialize() for player in players],
            "matches": [match.serialize() for match in self._matches],
            "sort_by_rank": self._sort_by_rank,
        }

    def restore(self, data):
        self.sort_by(data["sort_by_rank"])

        # restore machine objects
        for machine_data in data["machines"]:
            self.add_machine(
                machine_data["name"], enabled=machine_data["enabled"]
            )

        # restore player objects
        for player_data in data.get("players", []):
            player = Player(
                player_data["name"], set(),
                num_wins=player_data["num_wins"],
                num_losses=player_data["num_losses"],
                num_played=player_data["num_played"],
                enabled=player_data["enabled"],
            )
            self._players[player.name] = player

            for opponent_name in player_data["opponents"]:
                opponent = self._players.get(opponent_name)
                if opponent is not None:
                    player.opponents.add(opponent)
                    opponent.opponents.add(player)

            for machine_id in player_data["machines"]:
                player.machines.add(self._machines[machine_id])

        # rebuild available players queue
        for player_name in data.get("avail_players", []):
            self._avail_players.append(self._players[player_name])

        # restore matches. if winner is not None, it will reset the active flags
        for match_id, match_data in enumerate(data.get("matches", [])):
            player_a = self._players[match_data["player_a"]]
            player_b = self._players[match_data["player_b"]]
            machine = self._machines[match_data["machine_name"]]
            winner_name = match_data["winner"]
            winner = self._players.get(winner_name)
            match = Match(match_id, player_a, player_b, machine, winner=winner)
            self._matches.append(match)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

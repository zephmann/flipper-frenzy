import itertools

# TODO reset tournament button?
# TODO reset scores button?
# TODO manually enter match?


class Machine:
    def __init__(self, machine_id, name):
        self.id = machine_id
        self.name = name
        self.active = False
        self.played = False

    def __repr__(self):
        return f"<Machine {self.name} ({'X' if self.active else 'O'})>"

    def serialize(self):
        return {
            "name": self.name,
            "active": self.active,
            "played": self.played,
        }


class Player:
    def __init__(
        self, name, machines, num_wins=0, num_played=0
    ):
        self.name = name
        self.num_wins = num_wins
        self.num_played = num_played
        self.active = False
        self.opponents = set()  # other players already faced
        self.machines = machines  # machines still to play

    def __repr__(self):
        return (
            f"<Player {self.name} {self.num_wins} / {self.num_played} "
            f"({'X' if self.active else 'O'})>"
        )

    def serialize(self):
        return {
            "name": self.name,
            "active": self.active,
            "num_wins": self.num_wins,
            "num_played": self.num_played,
            "opponents": [o.name for o in self.opponents],
            "machines": [m.id for m in self.machines],
        }


class Match:
    def __init__(self, match_id, player_a, player_b, machine, winner=None):
        self.id = match_id
        self.player_a = player_a
        self.player_b = player_b
        self.machine = machine
        self.winner = winner

        machine.played = True
        if winner is None:
            player_a.active = True
            player_b.active = True
            machine.active = True

    def __repr__(self):
        return (
            f"<Match {self.player_a.name} v {self.player_b.name} "
            f"on {self.machine.name}>"
        )

    def serialize(self):
        winner_name = None
        if self.winner is not None:
            winner_name = self.winner.name
        return {
            "id": self.id,
            "player_a": self.player_a.name,
            "player_b": self.player_b.name,
            "machine_id": self.machine.id,
            "machine_name": self.machine.name,
            "winner": winner_name,
        }

    def set_winner(self, winner):
        assert self.winner is None

        self.winner = winner
        winner.num_wins += 1

        self.player_a.active = False
        self.player_a.num_played += 1

        self.player_b.active = False
        self.player_b.num_played += 1

        self.machine.active = False


class Tournament:
    def __init__(self):
        self._avail_players = []
        self._players = {}

        self._machines = []

        self._matches = []

    def add_player(self, name):
        assert name not in self._players
        player = Player(name, set(self._machines))
        self._avail_players.append(player)
        self._players[name] = player

    def remove_player(self, name):
        if name not in self._players:
            return f"Unable to find player '{name}'"
        if self._players[name].active or self._players[name].num_played:
            return f"Player has already started!"
        player = self._players.pop(name)
        self._avail_players.remove(player)
        return f"Removed player '{name}'"

    def add_machine(self, name):
        """Add a new machine to the tournament."""
        machine_id = len(self._machines)
        machine = Machine(machine_id, name)
        self._machines.append(machine)

        for player in self._players.values():
            player.machines.add(machine)

    def remove_machine(self, name):
        # todo replace with map?
        for machine in self._machines:
            if machine.name == name:
                break
        else:
            return f"Unable to find machine '{name}'"
        if machine.played:
            return f"Machine has already been played!"
        self._machines.remove(machine)
        for player in self._players.values():
            if machine in player.machines:
                player.machines.remove(machine)

        return f"Removed machine '{name}'"

    def next_match(self):
        """Determine the next match, consisting of two players and a machine.

        Prioritize players earlier in the queue rather than trying to maximize
        number of matches since players earlier in the queue might have
        been waiting longer.
        """
        if len(self._avail_players) < 2:
            return "Not enough players!"

        # check each player in the queue
        for player_a, player_b in itertools.combinations(self._avail_players, 2):
            # check if players have already played one another
            if player_b in player_a.opponents:
                continue

            # check if the players have a machine in common
            common_machines = player_a.machines.intersection(player_b.machines)
            if not common_machines:
                continue

            for machine in common_machines:
                if machine.active:
                    continue

                match_id = len(self._matches)
                match = Match(match_id, player_a, player_b, machine)
                self._matches.append(match)

                self._avail_players.remove(player_a)
                self._avail_players.remove(player_b)
                player_a.machines.remove(machine)
                player_b.machines.remove(machine)
                player_a.opponents.add(player_b)
                player_b.opponents.add(player_a)
                return "Match created!"

        return "Unable to find another match!"

    def complete_match(self, match_id, winner_name):
        match = self._matches[match_id]
        winner = self._players[winner_name]
        match.set_winner(winner)

        num_players = len(self._players)

        self._avail_players.append(match.player_a)
        if (len(match.player_a.opponents) + 1) == num_players:
            match.player_a.opponents = set()
        if not match.player_a.machines:
            match.player_a.machines = set(self._machines)

        self._avail_players.append(match.player_b)
        if (len(match.player_b.opponents) + 1) == num_players:
            match.player_b.opponents = set()
        if not match.player_b.machines:
            match.player_b.machines = set(self._machines)

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
        for machine in self._machines:
            print(machine)

    def serialize(self):
        return {
            "machines": [machine.serialize() for machine in self._machines],
            "avail_players": [player.name for player in self._avail_players],
            "players": [player.serialize() for player in self._players.values()],
            "matches": [match.serialize() for match in self._matches],
        }

    def restore(self, data):
        # restore machine objects
        for machine in data["machines"]:
            self.add_machine(machine["name"])

        # restore player objects
        for player_data in data["players"]:
            player = Player(
                player_data["name"], set(),
                num_wins=player_data["num_wins"],
                num_played=player_data["num_played"],
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
        for player_name in data["avail_players"]:
            self._avail_players.append(self._players[player_name])

        # restore matches. if winner is not None, it will reset the active flags
        for match_id, match_data in enumerate(data["matches"]):
            player_a = self._players[match_data["player_a"]]
            player_b = self._players[match_data["player_b"]]
            machine = self._machines[match_data["machine_id"]]
            winner_name = match_data["winner"]
            winner = self._players.get(winner_name)
            match = Match(match_id, player_a, player_b, machine, winner=winner)
            self._matches.append(match)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import itertools


class Machine:
    def __init__(self, name):
        self.name = name
        self.active = False

    def __repr__(self):
        return f"<Machine {self.name} ({'X' if self.active else 'O'})>"


class Player:
    def __init__(self, name: str, machines: set):
        self.name = name
        self.num_wins = 0
        self.num_played = 0
        self.active = False
        self.opponents = set()  # other players already faced
        self.machines = machines  # machines still to play

    def __repr__(self):
        return f"<Player {self.name} {self.num_wins} ({'X' if self.active else 'O'})>"


class Match:
    def __init__(self, player_a, player_b, machine):
        self.player_a = player_a
        self.player_b = player_b
        self.machine = machine
        self.winner = None

        player_a.active = True
        player_b.active = True
        machine.active = True

    def __repr__(self):
        return (
            f"<Match {self.player_a.name} v {self.player_b.name} "
            f"on {self.machine.name}>"
        )


class Tournament:
    def __init__(self):
        self._restart()

    def _restart(self):
        self._avail_players = []
        self._players = []

        self._machines = []

        self._matches = []

    def add_players(self, names):
        """Add a new player to the tournament."""
        if isinstance(names, str):
            names = [names]

        for name in names:
            player = Player(name, set(self._machines))
            self._avail_players.append(player)
            self._players.append(player)

    def add_machine(self, name):
        """Add a new machine to the tournament."""
        machine = Machine(name)
        self._machines.append(machine)

        for player in self._players:
            player.machines.add(machine)

    def next_match(self):
        """Determine the next match, consisting of two players and a machine.

        Prioritize players earlier in the queue rather than trying to maximize
        number of matches since players earlier in the queue might have
        been waiting longer.
        """
        if len(self._avail_players) < 2:
            print("Not enough players!")
            return

        # check each player in the queue
        for player_a, player_b in itertools.combinations(self._avail_players, 2):
            print(f"Player A: {player_a.name}")
            print(f"  Player B: {player_b.name}")
            # check if players have already played one another
            if player_b in player_a.opponents:
                print("    Already played each other!")
                continue

            # check if the players have a machine in common
            common_machines = player_a.machines.intersection(player_b.machines)
            if not common_machines:
                print("    Players have no machines in common!")
                continue

            for machine in common_machines:
                print(f"    Machine: {machine}")
                if machine.active:
                    print("      Machine is in use!")
                    continue

                match = Match(player_a, player_b, machine)
                self._matches.append(match)

                print(f"\nFound a match! {match}")

                self._avail_players.remove(player_a)
                self._avail_players.remove(player_b)
                player_a.machines.remove(machine)
                player_b.machines.remove(machine)
                player_a.opponents.add(player_b)
                player_b.opponents.add(player_a)
                return

        print("Unable to find another match!")

    def print_state(self):
        print("Active Matches:")
        for match in self._matches:
            print(f"  {match}")

        print("")
        print("Players:")
        for player in self._players:
            print(player)
            for machine in player.machines:
                print(f"  {machine.name}")

        print("")
        print("Machines:")
        for machine in self._machines:
            print(machine)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

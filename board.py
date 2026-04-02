from __future__ import annotations


class Position:
    """A coordinate on the board. Rows use letters, columns use numbers"""

    def __init__(self, row: int, column: int):
        """Takes row and column indices"""
        self.row = row
        self.column = column

    @classmethod
    def from_string(_class, string: str) -> Position:
        """Parse a notation string like 'A1' or 'K11' into a Position"""
        row = ord(string[0].upper()) - ord('A')
        column = int(string[1:]) - 1
        return _class(row, column)

    def __str__(self) -> str:
        return f"{chr(self.row + ord('A'))}{self.column + 1}"
    
    def __repr__(self) -> str:
        return f"Position({self})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.row == other.row and self.column == other.column

    def get_column_string(self) -> str:
        """Returns string representing just the column."""
        return str(self.column + 1)
    
    def get_row_string(self) -> str:
        """Returns string representing just the row."""
        return str(chr(self.row + ord('A')))


class Board:
    """A Hnefatafl board with pieces tracked as Position lists"""

    _ORTHOGONAL_DIRECTIONS: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    DEFAULT_WIDTH, DEFAULT_HEIGHT = (11, 11)

    DEFAULT_KING: Position = Position(5, 5)

    DEFAULT_ATTACKERS: list[Position] = [
        # North edge
        Position(0, 3), Position(0, 4), Position(0, 5),
        Position(0, 6), Position(0, 7), Position(1, 5),
        # South edge
        Position(10, 3), Position(10, 4), Position(10, 5),
        Position(10, 6), Position(10, 7), Position(9, 5),
        # West edge
        Position(3, 0), Position(4, 0), Position(5, 0),
        Position(6, 0), Position(7, 0), Position(5, 1),
        # East edge
        Position(3, 10), Position(4, 10), Position(5, 10),
        Position(6, 10), Position(7, 10), Position(5, 9),
    ]

    DEFAULT_DEFENDERS: list[Position] = [
        Position(4, 5), Position(6, 5), Position(5, 4), Position(5, 6),
        Position(4, 4), Position(6, 6), Position(4, 6), Position(6, 4),
        Position(3, 5), Position(7, 5), Position(5, 3), Position(5, 7),
    ]

    DEFAULT_ESCAPE_SPACES: list[Position] = [
        Position(0, 0),
        Position(0, DEFAULT_HEIGHT - 1),
        Position(DEFAULT_WIDTH - 1, 0),
        Position(DEFAULT_WIDTH - 1, DEFAULT_HEIGHT - 1),
    ]

    DEFAULT_RESTRICTED_SPACES: list[Position] = [
        DEFAULT_KING,
    ]

    def __init__(
        self,
        king: Position = DEFAULT_KING,
        attackers: list[Position] = DEFAULT_ATTACKERS,
        defenders: list[Position] = DEFAULT_DEFENDERS,
        escape_spaces: list[Position] = DEFAULT_ESCAPE_SPACES,
        restricted_spaces: list[Position] = DEFAULT_RESTRICTED_SPACES,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
    ):
        """All arguments are optional — omit any to get the standard starting layout"""
        self.width: int = width
        self.height: int = height
        self.king: Position = king
        self.attackers: list[Position] = attackers
        self.defenders: list[Position] = defenders
        self.escape_spaces: list[Position] = escape_spaces
        self.restricted_spaces: list[Position] = restricted_spaces

        for position in [self.king] + self.attackers + self.defenders:
            self._assert_in_bounds(position)
        
        """If this game has been won, this result will change to 'attacker' or 'defender'"""
        self.winner: str = None
        """Will be either 'attacker' or 'defender' depending whos turn it is"""
        self._current_player = "attacker" # Attacker always starts

        self.turn_log: list[str] = []

    def _is_in_bounds(self, position: Position) -> bool:
        """Return True if the position sits within the board's edges"""
        return (
            0 <= position.row < self.height
            and 0 <= position.column < self.width
        )

    def _assert_in_bounds(self, position: Position) -> None:
        """Raise ValueError if the position falls outside the board edges"""
        if not self._is_in_bounds(position):
            raise ValueError(
                f"{position} must be within {self.height}x{self.width} board"
            )

    def get_all_pieces(self) -> list[Position]:
        """Returns positions of all pieces, both attackers and defenders"""
        return list(self.defenders) + list(self.attackers) + [self.king]

    def get_piece_at(self, position: Position) -> str | None:
        """Return 'king', 'attacker', 'defender', or None for piece at given position"""
        if self.king == position:
            return "king"
        if position in self.attackers:
            return "attacker"
        if position in self.defenders:
            return "defender"
        return None

    def is_occupied(self, position: Position) -> bool:
        """Return True if any piece is at the given position"""
        return self.get_piece_at(position) is not None

    def is_escape(self, position: Position) -> bool:
        """Return True if the position is an escape space"""
        return position in self.escape_spaces

    def is_restricted(self, position: Position) -> bool:
        """Return True if the position is restricted (Only the king may enter)"""
        return position in self.restricted_spaces

    def get_valid_moves(self, position: Position) -> list[Position]:
        """
        Return all squares a piece can slide orthogonally to from the given position.
        Raises ValueError if there is no piece at the given position.
        """
        self._assert_in_bounds(position)
        piece = self.get_piece_at(position)
        if piece is None:
            raise ValueError(f"No piece at {position}.")

        moves: list[Position] = []
        for delta_row, delta_column in self._ORTHOGONAL_DIRECTIONS:
            row = position.row + delta_row
            column = position.column + delta_column

            while 0 <= row < self.height and 0 <= column < self.width:
                candidate = Position(row, column)
                if self.is_occupied(candidate):
                    break
                if self.is_escape(candidate) and piece != "king"\
                or self.is_restricted(candidate) and piece != "king":
                    # Moves may pass through restricted spots, but not land on them
                    row += delta_row
                    column += delta_column
                    continue
                moves.append(candidate)
                row += delta_row
                column += delta_column
        return moves

    def move_piece(self, origin: Position, destination: Position) -> None:
        """
        Move the piece at origin to destination.
        Raises ValueError if origin is empty, destination is occupied,
        either position is out of bounds, or the move is not valid.
        """
        self._assert_in_bounds(origin)
        self._assert_in_bounds(destination)

        piece = self.get_piece_at(origin)
        if piece is None:
            raise ValueError(f"No piece at {origin} to move.")
        if self.is_occupied(destination):
            raise ValueError(f"{destination} is already occupied.")
        if destination not in self.get_valid_moves(origin):
            raise ValueError(
                f"{origin} cannot reach {destination}."
            )

        if piece == "king":
            self.king = destination
        elif piece == "attacker":
            self.attackers[self.attackers.index(origin)] = destination
        elif piece == "defender":
            self.defenders[self.defenders.index(origin)] = destination

    def remove_piece(self, position: Position) -> None:
        """
        Remove whatever piece is at the given position. Typically called
        after a capture. Raises ValueError if nothing is there, or if you
        try to remove the king.
        """
        piece = self.get_piece_at(position)
        if piece is None:
            raise ValueError(f"No piece at {position} to remove.")
        if piece == "king":
            raise ValueError(
                "The king cannot be removed."
            )
        if piece == "attacker":
            self.attackers.remove(position)
        elif piece == "defender":
            self.defenders.remove(position)

    def get_captures(self, position: Position) -> list[Position]:
        """
        Given the position of a piece, return all opposing pieces it can capture
        right now. Raises ValueError if there is no piece at the position.
        """
        self._assert_in_bounds(position)
        piece = self.get_piece_at(position)
        if piece is None:
            raise ValueError(f"No piece at {position}.")

        captured: list[Position] = []

        for delta_row, delta_column in self._ORTHOGONAL_DIRECTIONS:
            neighbor = Position(
                position.row + delta_row,
                position.column + delta_column,
            )
            if not self._is_in_bounds(neighbor):
                continue

            neighbor_piece = self.get_piece_at(neighbor)
            if neighbor_piece is None or neighbor_piece == "king":
                continue
            if piece in ("defender", "king") and neighbor_piece != "attacker":
                continue
            if piece == "attacker" and neighbor_piece != "defender":
                continue

            sandwich = Position(
                neighbor.row + delta_row,
                neighbor.column + delta_column,
            )
            if not self._is_in_bounds(sandwich):
                continue

            sandwich_piece = self.get_piece_at(sandwich)
            if neighbor_piece == "attacker" and sandwich_piece in ("defender", "king")\
            or neighbor_piece == "defender" and sandwich_piece == "attacker"\
            or sandwich_piece is None and (self.is_restricted(sandwich) or self.is_escape(sandwich)):
                captured.append(neighbor)

        return captured

    def check_king_capture(self) -> bool:
        """
        Return True if the king is currently surrounded on all four
        orthogonal sides by attackers, empty restricted spaces, or empty
        escape spaces. If the king is at a board edge, that open side
        counts as a gap — the king cannot be captured there.
        """
        for delta_row, delta_column in self._ORTHOGONAL_DIRECTIONS:
            neighbor = Position(
                self.king.row + delta_row,
                self.king.column + delta_column,
            )
            if not self._is_in_bounds(neighbor):
                return False

            piece = self.get_piece_at(neighbor)
            is_attacker = piece == "attacker"
            is_empty_special = piece is None and (
                self.is_restricted(neighbor) or self.is_escape(neighbor)
            )
            if not (is_attacker or is_empty_special):
                return False
        return True

    def print_debug(self) -> None:
        """Print an ASCII version of the board for visual debug"""
        header = "  " + "".join(
            str(column + 1).center(3) for column in range(self.width)
        )
        print(header)
        for row in range(self.height):
            row_label = chr(row + ord('A'))
            row_string = ""
            for column in range(self.width):
                position = Position(row, column)
                piece = self.get_piece_at(position)
                if piece == "king":
                    character = "K"
                elif piece == "attacker":
                    character = "A"
                elif piece == "defender":
                    character = "D"
                elif self.is_escape(position):
                    character = "E"
                elif self.is_restricted(position):
                    character = "X"
                else:
                    character = "."
                row_string += f" {character} "
            print(f"{row_label} {row_string}")

    def __repr__(self) -> str:
        return f"Board({self.width}x{self.height})"

    def swap_current_player(self) -> None:
        """
        Flips current player from 'attacker' to 'defender',
        or 'defender' to 'attacker'.
        """
        if self._current_player == "attacker":
            self._current_player = "defender"
        else:
            self._current_player = "attacker"

    def get_current_player(self) -> str:
        """Returns 'attacker' or 'defender' depending on whos turn it is."""
        return self._current_player
    
    def is_attacker_turn(self) -> bool:
        """Returns true if is attacker's turn"""
        return self._current_player == "attacker"

    def is_defender_turn(self) -> bool:
        """Returns true if is defender's turn"""
        return self._current_player == "defender"

    def has_been_won(self) -> bool:
        """Returns true if game has a winner."""
        return not self.winner == None

    def get_turn_number(self) -> int:
        """
        Returns number of turns played, based off of turn log.
        Turns are based off of both Attacker and Defender moving,
        so 1 or 2 turns recorded in the turn log will both be
        considered part of the 1st turn.
        """
        return int(float(len(self.turn_log) + 1) / 2 + 0.5)
    
    def get_complete_turn_log(self) -> str:
        """
        Returns str combining complete turn log.
        Every 2 turns are split by a new line.
        """
        output: str = ""
        for n in range(len(self.turn_log)):
            output += self.turn_log[n]
            # 2 turns are logged per line
            if n % 2:
                output += "\n"
            else:
                output += " "
        # Trim trailing white-spaces
        output = output.removesuffix("\n")
        output = output.removesuffix(" ")
        return output

    def is_valid_move(self, origin: Position, destination: Position) -> bool:
        """Returns true if valid move can be made from origin to destination"""
        return self.is_occupied(origin)\
        and not self.is_occupied(destination)\
        and destination in self.get_valid_moves(origin)

    def play_turn(self, origin: Position, destination: Position) -> None:
        """
        Attempts to make a move if possible. Incrementing turn and
        recording it to the turn log. Will throw error if move is invalid,
        or if attempting to move opposing player's piece.
        """
        if origin == None or destination == None:
            raise ValueError("Must have both and origin and destination to attempt a move.")
        if not self._current_player == self.get_piece_at(origin):
            if not self._current_player == "defender"\
            and self.get_piece_at(origin) == "king":
                raise ValueError("Cannot make a move with opposing player's piece.")
        # Move piece
        self.move_piece(origin, destination)
        # Check captures
        captures: list[Position] = self.get_captures(destination)
        for capture in captures:
            self.remove_piece(capture)
        # Increment to next turn
        log: str = f"{origin}-{destination}"
        for capture in captures:
            log += f"x{capture}"
        # Check king capture
        if self._current_player == "attacker" and self.check_king_capture():
            self.winner = "attacker"
        # Check escape
        if self.king in self.escape_spaces:
            self.winner = "defender"
        # Increment turn
        self.swap_current_player()
        self.turn_log.append(log)
        # Check if opposition has no valid moves
        if self.winner == None:
            has_valid_move: bool = False
            if self._current_player == "attacker": # Check attacker pieces
                for piece in self.get_all_pieces():
                    if piece in self.attackers\
                    and not self.get_valid_moves(piece) == []:
                        has_valid_move = True
                        break
            else: # Check defender pieces
                for piece in self.get_all_pieces():
                    if piece in self.defenders\
                    and not self.get_valid_moves(piece) == []:
                        has_valid_move = True
                        break
                if not self.get_valid_moves(self.king) == []:
                   has_valid_move = True
            if not has_valid_move:
                if self._current_player == "attacker":
                    self.winner = "defender"
                else:
                    self.winner = "attacker"

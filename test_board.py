import pytest
from board import Board, Position, Piece

@pytest.fixture
def board(): return Board()

class TestPosition:
    def test_equality(self):
        assert Position(0, 0) == Position(0, 0)
        assert Position(3, 4) != Position(4, 3)

    def test_to_string(self):
        assert str(Position(0, 0)) == "A1"
        assert str(Position(10, 10)) == "K11"
        assert str(Position(4, 4)) == "E5"

    def test_from_string(self):
        assert Position.from_string("A1") == Position(0, 0)
        assert Position.from_string("K11") == Position(10, 10)
        assert Position.from_string("E5") == Position(4, 4)

    def test_from_and_to_string(self):
        positions = [Position(0, 0), Position(5, 5), Position(10, 10), Position(3, 7)]
        for position in positions:
            assert Position.from_string(str(position)) == position

    def test_from_string_case_insensitive(self):
        assert Position.from_string("a1") == Position.from_string("A1")

class TestBoardInit:
    def test_default_king(self, board):
        assert board.king == Board.DEFAULT_KING

    def test_default_attacker_count(self, board):
        assert len(board.attackers) == len(Board.DEFAULT_ATTACKERS)

    def test_default_defender_count(self, board):
        assert len(board.defenders) == len(Board.DEFAULT_DEFENDERS)
    
    def test_custom_king(self):
        custom_board = Board(king=Position(0, 0))
        assert custom_board.king == Position(0, 0)

    def test_custom_attackers(self):
        custom_board = Board(attackers=[Position(0, 1), Position(0, 2)])
        assert len(custom_board.attackers) == 2

    def test_out_of_bounds_piece_raises(self):
        with pytest.raises(ValueError):
            Board(king=Position(99, 99))

    def test_custom_dimensions(self):
        custom_board = Board(
            width=7, height=7, king=Position(3, 3),
            attackers=[], defenders=[]
        )
        assert custom_board.width == 7
        assert custom_board.height == 7

class TestPieceLookups:
    def test_get_piece_at_king(self, board):
        assert board.get_piece_at(Board.DEFAULT_KING) == Piece.King

    def test_get_piece_at_attacker(self, board):
        for piece in Board.DEFAULT_ATTACKERS:
            assert board.get_piece_at(piece) == Piece.Attacker

    def test_get_piece_at_defender(self, board):
        for piece in Board.DEFAULT_DEFENDERS:
            assert board.get_piece_at(piece) == Piece.Defender

    def test_get_piece_at_empty(self, board):
        assert board.get_piece_at(Position(0, 0)) is None

    def test_is_occupied_true(self, board):
        assert board.is_occupied(Board.DEFAULT_KING)

    def test_is_occupied_false(self, board):
        assert not board.is_occupied(Position(0, 0))

    def test_get_all_pieces_count(self, board):
        expected_count: int = len(Board.DEFAULT_ATTACKERS) + len(Board.DEFAULT_DEFENDERS) + 1
        assert len(board.get_all_pieces()) == expected_count

class TestValidMoves:
    def test_no_piece_raises(self, board):
        with pytest.raises(ValueError):
            board.get_valid_moves(Position(0, 0))

    def test_moves_blocked_by_pieces(self, board):
        moves = board.get_valid_moves(Position(0, 5))
        assert all(
            move.row == 0 or move.column == 5 for move in moves
        )

    def test_non_king_blocked_by_restricted(self):
        test_board = Board(attackers=[Position(5, 2)], defenders=[])
        moves = test_board.get_valid_moves(Position(5, 2))
        assert Position(5, 5) not in moves

    def test_king_can_enter_restricted(self):
        test_board = Board(king=Position(5, 2), attackers=[], defenders=[])
        moves = test_board.get_valid_moves(Position(5, 2))
        assert Position(5, 5) in moves

    def test_moves_dont_leave_board(self, board):
        moves = board.get_valid_moves(Position(0, 3))
        for move in moves:
            assert 0 <= move.row < board.height
            assert 0 <= move.column < board.width

class TestMovePiece:
    def test_basic_attacker_move(self):
        test_board = Board(
            attackers=[Position(0, 1)], defenders=[], king=Position(5, 5)
        )
        test_board.move_piece(Position(0, 1), Position(0, 2))
        assert Position(0, 2) in test_board.attackers
        assert Position(0, 1) not in test_board.attackers

    def test_basic_defender_move(self):
        test_board = Board(
            attackers=[], defenders=[Position(3, 3)], king=Position(5, 5)
        )
        test_board.move_piece(Position(3, 3), Position(3, 6))
        assert Position(3, 6) in test_board.defenders

    def test_king_move(self):
        test_board = Board(attackers=[], defenders=[], king=Position(5, 5))
        test_board.move_piece(Position(5, 5), Position(5, 6))
        assert test_board.king == Position(5, 6)

    def test_move_from_empty_raises(self, board):
        with pytest.raises(ValueError):
            board.move_piece(Position(0, 1), Position(0, 2))

    def test_move_to_occupied_raises(self, board):
        with pytest.raises(ValueError):
            board.move_piece(Position(0, 5), Position(0, 4))

    def test_move_out_of_bounds_raises(self, board):
        with pytest.raises(ValueError):
            board.move_piece(Position(0, 5), Position(0, 99))

    def test_invalid_move_raises(self):
        test_board = Board(
            attackers=[Position(0, 1)], defenders=[], king=Position(5, 5)
        )
        with pytest.raises(ValueError):
            test_board.move_piece(Position(0, 1), Position(1, 2))

class TestRemovePiece:
    def test_remove_attacker(self, board):
        target = board.attackers[0]
        board.remove_piece(target)
        assert target not in board.attackers

    def test_remove_defender(self, board):
        target = board.defenders[0]
        board.remove_piece(target)
        assert target not in board.defenders

    def test_remove_empty_raises(self, board):
        with pytest.raises(ValueError):
            board.remove_piece(Position(0, 1))

    def test_remove_king_raises(self, board):
        with pytest.raises(ValueError):
            board.remove_piece(Position(5, 5))

    def test_all_pieces_count_decreases(self, board):
        before = len(board.get_all_pieces())
        board.remove_piece(board.attackers[0])
        assert len(board.get_all_pieces()) == before - 1

class TestGetCaptures:
    def test_attacker_captures_defender_sandwiched_by_friendly(self):
        test_board = Board(
            attackers=[Position(3, 3)],
            defenders=[Position(3, 2)],
        )
        test_board.attackers.append(Position(3, 1))
        assert Position(3, 2) in test_board.get_captures(Position(3, 3))

    def test_attacker_captures_defender_sandwich_is_restricted(self):
        test_board = Board(
            attackers=[Position(5, 3)],
            defenders=[Position(5, 4)],
            king=Position(9, 9),
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        assert Position(5, 4) in test_board.get_captures(Position(5, 3))

    def test_attacker_captures_defender_sandwich_is_escape(self):
        test_board = Board(
            attackers=[Position(0, 8)],
            defenders=[Position(0, 9)],
            king=Position(5, 5),
            escape_spaces=[Position(0, 10)],
            restricted_spaces=[],
        )
        assert Position(0, 9) in test_board.get_captures(Position(0, 8))

    def test_attacker_no_capture_when_not_sandwiched(self):
        test_board = Board(
            attackers=[Position(3, 3)],
            defenders=[Position(3, 2)],
        )
        assert test_board.get_captures(Position(3, 3)) == []

    def test_attacker_does_not_capture_own_piece(self):
        test_board = Board(
            attackers=[Position(3, 3), Position(3, 2), Position(3, 1)],
            defenders=[],
            king=Position(9, 9),
        )
        assert test_board.get_captures(Position(3, 3)) == []

    def test_defender_captures_attacker_sandwiched_by_friendly(self):
        test_board = Board(
            attackers=[Position(4, 5)],
            defenders=[Position(3, 5), Position(5, 5)],
            king=Position(9, 9),
            restricted_spaces=[],
            escape_spaces=[],
        )
        assert Position(4, 5) in test_board.get_captures(Position(3, 5))

    def test_defender_captures_attacker_sandwich_is_restricted(self):
        test_board = Board(
            attackers=[Position(4, 5)],
            defenders=[Position(3, 5)],
            king=Position(9, 9),
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        assert Position(4, 5) in test_board.get_captures(Position(3, 5))

    def test_defender_captures_attacker_sandwich_is_escape(self):
        test_board = Board(
            attackers=[Position(0, 9)],
            defenders=[Position(0, 8)],
            king=Position(5, 5),
            escape_spaces=[Position(0, 10)],
            restricted_spaces=[],
        )
        assert Position(0, 9) in test_board.get_captures(Position(0, 8))

    def test_defender_does_not_capture_own_piece(self):
        test_board = Board(
            attackers=[],
            defenders=[Position(3, 3), Position(3, 2), Position(3, 1)],
            king=Position(9, 9),
        )
        assert test_board.get_captures(Position(3, 3)) == []

    def test_king_can_help_capture_attacker(self):
        test_board = Board(
            attackers=[Position(5, 5)],
            defenders=[Position(5, 4)],
            king=Position(5, 6),
            restricted_spaces=[],
            escape_spaces=[],
        )
        assert Position(5, 5) in test_board.get_captures(Position(5, 6))

    def test_multiple_captures_in_one_move(self):
        test_board = Board(
            attackers=[Position(3, 5), Position(1, 5)],
            defenders=[Position(2, 5), Position(4, 5)],
            king=Position(9, 9),
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        captures = test_board.get_captures(Position(3, 5))
        assert Position(2, 5) in captures
        assert Position(4, 5) in captures

    def test_king_not_returned_by_get_captures(self):
        test_board = Board(
            attackers=[Position(5, 3), Position(5, 7)],
            defenders=[],
            king=Position(5, 5),
            restricted_spaces=[],
            escape_spaces=[],
        )
        assert Position(5, 5) not in test_board.get_captures(Position(5, 3))

    def test_get_captures_no_piece_raises(self):
        test_board = Board(attackers=[], defenders=[], king=Position(5, 5))
        with pytest.raises(ValueError):
            test_board.get_captures(Position(0, 0))


class TestKingCapture:
    def _surround_king(
        self, king: Position, neighbors: list[Position]
    ) -> Board:
        """Build a board with attackers at the given neighbor positions."""
        return Board(
            king=king,
            attackers=neighbors,
            defenders=[],
        )

    def test_king_captured_surrounded_by_four_attackers(self):
        king = Position(5, 5)
        test_board = self._surround_king(king, [
            Position(4, 5), Position(6, 5),
            Position(5, 4), Position(5, 6),
        ])
        assert test_board.check_king_capture() is True

    def test_king_not_captured_one_side_open(self):
        king = Position(5, 5)
        test_board = self._surround_king(king, [
            Position(4, 5), Position(6, 5), Position(5, 4),
        ])
        assert test_board.check_king_capture() is False

    def test_king_captured_with_restricted_space_as_side(self):
        king = Position(5, 4)
        test_board = Board(
            king=king,
            attackers=[Position(4, 4), Position(6, 4), Position(5, 3)],
            defenders=[],
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        assert test_board.check_king_capture() is True

    def test_king_at_edge_cannot_be_captured(self):
        king = Position(0, 5)
        test_board = self._surround_king(king, [
            Position(1, 5), Position(0, 4), Position(0, 6),
        ])
        assert test_board.check_king_capture() is False

    def test_king_not_captured_by_defenders(self):
        king = Position(5, 5)
        test_board = Board(
            king=king,
            attackers=[],
            defenders=[
                Position(4, 5), Position(6, 5),
                Position(5, 4), Position(5, 6),
            ],
            restricted_spaces=[],
            escape_spaces=[],
        )
        assert test_board.check_king_capture() is False

    def test_king_not_captured_with_occupied_restricted(self):
        king = Position(5, 4)
        test_board = Board(
            king=king,
            attackers=[Position(4, 4), Position(6, 4), Position(5, 3)],
            defenders=[Position(5, 5)],
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        assert test_board.check_king_capture() is False

    def test_king_surrounded_by_three_attackers_and_escape(self):
        king = Position(1, 9)
        test_board = Board(
            king=king,
            attackers=[Position(0, 9), Position(2, 9), Position(1, 8)],
            defenders=[],
            restricted_spaces=[],
            escape_spaces=[Position(0, 10), Position(1, 10)],
        )
        assert test_board.check_king_capture() is True

class TestTurnManagement:
    def test_swap_current_player(self, board):
        board.swap_current_player()
        assert board.get_current_player() == "defender"
        board.swap_current_player()
        assert board.get_current_player() == "attacker"

    def test_is_attacker_turn_initially(self, board):
        assert board.is_attacker_turn() is True

    def test_is_defender_turn_initially_false(self, board):
        assert board.is_defender_turn() is False

    def test_is_defender_turn_after_swap(self, board):
        board.swap_current_player()
        assert board.is_defender_turn() is True

    def test_is_attacker_turn_after_swap_false(self, board):
        board.swap_current_player()
        assert board.is_attacker_turn() is False

class TestTurnNumber:
    def test_turn_number_starts_at_one(self, board):
        assert board.get_turn_number() == 1

    def test_turn_number_after_one_half_turn(self, board):
        board.turn_log.append("A4-A3")
        assert board.get_turn_number() == 1

    def test_turn_number_after_full_turn(self, board):
        board.turn_log.append("A4-A3")
        board.turn_log.append("F4-F3")
        assert board.get_turn_number() == 2

    def test_turn_number_after_three_half_turns(self, board):
        board.turn_log.append("A4-A3")
        board.turn_log.append("F4-F3")
        board.turn_log.append("A3-A2")
        assert board.get_turn_number() == 2


class TestTurnLog:
    def test_turn_log_empty_at_start(self, board):
        assert board.turn_log == []

    def test_turn_log_records_move(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        test_board.play_turn(Position(0, 3), Position(0, 2))
        assert len(test_board.turn_log) == 1

    def test_get_complete_turn_log_single_entry(self, board):
        board.turn_log = ["A4-A3"]
        assert board.get_complete_turn_log().find("\n") == -1

    def test_get_complete_turn_log_two_entries_on_one_line(self, board):
        board.turn_log = ["A4-A3", "F4-F3"]
        assert board.get_complete_turn_log().find("\n") == -1

    def test_get_complete_turn_log_three_entries(self, board):
        board.turn_log = ["A4-A3", "F4-F3", "A3-A2"]
        result = board.get_complete_turn_log()
        assert board.get_complete_turn_log().find("\n") != -1

    def test_get_complete_turn_log_no_trailing_whitespace(self, board):
        board.turn_log = ["A4-A3"]
        result = board.get_complete_turn_log()
        assert result == result.strip()

class TestPlayTurn:
    def test_play_turn_moves_piece(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        test_board.play_turn(Position(0, 3), Position(0, 2))
        assert Position(0, 2) in test_board.attackers

    def test_play_turn_swaps_player(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        test_board.play_turn(Position(0, 3), Position(0, 2))
        assert test_board.get_current_player() == "defender"

    def test_play_turn_none_origin_raises(self, board):
        with pytest.raises(ValueError):
            board.play_turn(None, Position(0, 2))

    def test_play_turn_none_destination_raises(self, board):
        with pytest.raises(ValueError):
            board.play_turn(Position(0, 3), None)

    def test_attacker_cannot_move_defender_piece(self):
        test_board = Board(
            attackers=[], defenders=[Position(3, 3)], king=Position(5, 5)
        )
        with pytest.raises(ValueError):
            test_board.play_turn(Position(3, 3), Position(3, 4))

    def test_defender_cannot_move_attacker_piece(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        test_board.swap_current_player()
        with pytest.raises(ValueError):
            test_board.play_turn(Position(0, 3), Position(0, 2))

    def test_play_turn_performs_capture(self):
        test_board = Board(
            attackers=[Position(3, 4), Position(3, 1)],
            defenders=[Position(3, 2)],
            king=Position(9, 9),
            restricted_spaces=[],
            escape_spaces=[],
        )
        piece_count = len(test_board.get_all_pieces())
        test_board.play_turn(Position(3, 4), Position(3, 3))
        assert piece_count == len(test_board.get_all_pieces()) + 1

    def test_defender_can_move_king(self):
        test_board = Board(
            attackers=[], defenders=[], king=Position(5, 5),
            restricted_spaces=[], escape_spaces=[]
        )
        test_board.swap_current_player()
        test_board.play_turn(Position(5, 5), Position(5, 6))
        assert test_board.king == Position(5, 6)

class TestWinConditions:
    def test_no_winner_at_start(self, board):
        assert board.has_been_won() is False

    def test_defender_wins_on_escape(self):
        test_board = Board(
            king=Position(0, 1),
            attackers=[],
            defenders=[],
            escape_spaces=[Position(0, 0)],
            restricted_spaces=[Position(0, 0)],
        )
        test_board.swap_current_player()
        test_board.play_turn(Position(0, 1), Position(0, 0))
        assert test_board.winner == "defender"
        assert test_board.has_been_won() is True

    def test_attacker_wins_on_king_capture(self):
        test_board = Board(
            king=Position(5, 5),
            attackers=[
                Position(4, 5), Position(6, 5),
                Position(5, 4), Position(5, 7),
            ],
            defenders=[],
            restricted_spaces=[],
            escape_spaces=[],
        )
        test_board.play_turn(Position(5, 7), Position(5, 6))
        assert test_board.winner == "attacker"
        assert test_board.has_been_won() is True

    def test_attacker_wins_by_stalemate(self):
        test_board = Board(
            king=Position(5, 5),
            attackers=[Position(5, 4), Position(5, 6),
                       Position(4, 5), Position(7, 5)],
            defenders=[],
        )
        test_board.play_turn(Position(7, 5), Position(6, 5))
        assert test_board.winner == "attacker"

    def test_defender_wins_by_attacker_stalemate(self):
        # Only attacker has no valid moves
        test_board = Board(
            king=Position(9, 9),
            attackers=[Position(0, 0)],
            defenders=[Position(0, 1), Position(1, 0)],
            restricted_spaces=[],
            escape_spaces=[],
        )
        test_board.swap_current_player()
        test_board.play_turn(Position(9, 9), Position(9, 8))
        assert test_board.winner == "defender"

class TestIsValidMove:
    def test_valid_move_returns_true(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        assert test_board.is_valid_move(Position(0, 3), Position(0, 2)) is True

    def test_empty_origin_returns_false(self, board):
        assert board.is_valid_move(Position(0, 1), Position(0, 2)) is False

    def test_occupied_destination_returns_false(self, board):
        assert board.is_valid_move(Position(4, 5), Position(5, 5)) is False

    def test_diagonal_move_returns_false(self):
        test_board = Board(
            attackers=[Position(0, 3)], defenders=[], king=Position(5, 5)
        )
        assert test_board.is_valid_move(Position(0, 3), Position(1, 4)) is False

    def test_restricted_destination_returns_false_for_attacker(self):
        test_board = Board(
            attackers=[Position(5, 2)], defenders=[],
            king=Position(9, 9),
            restricted_spaces=[Position(5, 5)],
            escape_spaces=[],
        )
        assert test_board.is_valid_move(Position(5, 2), Position(5, 5)) is False

    def test_escape_destination_valid_for_king(self):
        test_board = Board(
            king=Position(0, 1),
            attackers=[],
            defenders=[],
            escape_spaces=[Position(0, 0)],
            restricted_spaces=[Position(0, 0)],
        )
        assert test_board.is_valid_move(Position(0, 1), Position(0, 0)) is True

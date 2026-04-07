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

    def test_king_counts_as_sandwich_for_defender_capture(self):
        test_board = Board(
            attackers=[Position(5, 3)],
            defenders=[Position(5, 4)],
            king=Position(5, 5),
            restricted_spaces=[],
            escape_spaces=[],
        )
        assert Position(5, 4) in test_board.get_captures(Position(5, 3))

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

// Global variables
var game = new Chess();
var board = null;
var possibleMoves = [];
var reviewFinished = false;

// Initialize on page load
$(document).ready(function() {
    initBoard();
    loadPositionFromServer();

    $('#undo-btn').click(function() { undoMove(); });
    $('#restart-btn').click(function() { restartReview(); });

    // Reset session when navigating to Practice from Review
    $('#practice-btn').click(function(e) {
        e.preventDefault();
        var practiceUrl = $(this).attr('href');

        // Clear the session by restarting, then navigate
        $.ajax({
            url: restartUrl,
            type: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            success: function() {
                // Navigate to practice page after resetting
                window.location.href = practiceUrl;
            },
            error: function() {
                // Navigate anyway even if reset fails
                window.location.href = practiceUrl;
            }
        });
    });
});

// Initialize chessboard.js (read-only, no drag)
function initBoard() {
    var config = {
        draggable: false,  // CRITICAL: No drag-and-drop
        position: 'start',
        pieceTheme: pieceTheme,
        orientation: playerColor === 'w' ? 'white' : 'black'
    };
    board = Chessboard('chessboard', config);
}

// Load position from server
function loadPositionFromServer() {
    $.ajax({
        url: getPositionUrl,
        type: 'GET',
        success: function(response) {
            game.load(response.fen);
            board.position(response.fen);
            possibleMoves = response.possible_moves;
            updateMoveButtons(response.possible_moves);
            updateNagIndicators(response.nag, response.is_checkmate, response.start_flag);
            reviewFinished = response.possible_moves.length === 0;
        },
        error: function(xhr, status, error) {
            console.error('Error loading position:', error);
            alert('Error loading board position.');
        }
    });
}

// Update move buttons dynamically
function updateMoveButtons(moves) {
    var container = $('#move-buttons-container');
    container.empty();

    if (moves.length === 0) {
        container.html('<div class="finished-badge">FINISHED</div>');
        return;
    }

    var isWhiteTurn = game.turn() === 'w';
    var buttonClass = isWhiteTurn ? 'btn-white-move' : 'btn-black-move';

    moves.forEach(function(move) {
        var button = $('<button>')
            .addClass('btn mx-1 ' + buttonClass)
            .text(move)
            .click(function() { executeMove(move); });
        container.append(button);
    });
}

// Execute move via AJAX
function executeMove(move) {
    $.ajax({
        url: executeMoveUrl,
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ move: move }),
        success: function(response) {
            game.load(response.fen);
            board.position(response.fen);
            possibleMoves = response.possible_moves;
            updateMoveButtons(response.possible_moves);
            updateNagIndicators(response.nag, response.is_checkmate, false);
            reviewFinished = response.finished;
        },
        error: function(xhr, status, error) {
            console.error('Error executing move:', error);
            alert('Error executing move.');
        }
    });
}

// Undo move
function undoMove() {
    $.ajax({
        url: undoMoveUrl,
        type: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        success: function(response) {
            game.load(response.fen);
            board.position(response.fen);
            possibleMoves = response.possible_moves;
            updateMoveButtons(response.possible_moves);
            updateNagIndicators(response.nag, response.is_checkmate, response.moves_count === 0);
            reviewFinished = false;
        },
        error: function(xhr, status, error) {
            console.error('Error undoing move:', error);
            alert('Error undoing move.');
        }
    });
}

// Restart review
function restartReview() {
    $.ajax({
        url: restartUrl,
        type: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        success: function(response) {
            game.load(response.fen);
            board.position(response.fen);
            possibleMoves = response.possible_moves;
            updateMoveButtons(response.possible_moves);
            updateNagIndicators(response.nag, response.is_checkmate, true);
            reviewFinished = false;
        },
        error: function(xhr, status, error) {
            console.error('Error restarting review:', error);
            alert('Error restarting review.');
        }
    });
}

// Update NAG indicators
function updateNagIndicators(nag, isCheckmate, isStart) {
    var leftCol = $('#nag-indicator-left');
    var rightCol = $('#nag-indicator-right');

    leftCol.empty();
    rightCol.empty();

    if (isStart) return;

    var imagePath = nagImagesPath;

    if (nag === '!') imagePath += 'great.png';
    else if (nag === '!!') imagePath += 'brilliant.png';
    else if (nag === '!?') imagePath += 'only_move.png';
    else if (nag === '?!') imagePath += 'innacuracy.png';
    else if (nag === '?') imagePath += 'mistake.png';
    else if (nag === '??') imagePath += 'blunder.png';
    else if (isCheckmate) {
        var whiteTurn = game.turn() === 'w';
        imagePath += whiteTurn ? 'checkmate_black.png' : 'checkmate_white.png';
    } else {
        imagePath += 'correct.png';
    }

    var imgHtml = '<img src="' + imagePath + '" width="128" height="128" class="img-fluid nag-image" alt="Indicator">';
    leftCol.html(imgHtml);
    rightCol.html(imgHtml);
}

// Piece theme
function pieceTheme(piece) {
    var pieceMap = {
        'wP': 'white_pawn.png', 'wN': 'white_knight.png', 'wB': 'white_bishop.png',
        'wR': 'white_rook.png', 'wQ': 'white_queen.png', 'wK': 'white_king.png',
        'bP': 'black_pawn.png', 'bN': 'black_knight.png', 'bB': 'black_bishop.png',
        'bR': 'black_rook.png', 'bQ': 'black_queen.png', 'bK': 'black_king.png'
    };
    return '/static/repertoire/pieces/' + pieceMap[piece];
}

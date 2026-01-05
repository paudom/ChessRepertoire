// Global variables
var game = new Chess();
var board = null;
var isPlayerTurn = true;
var practiceFinished = false;
var squareToHighlight = null;
var pendingMove = null; // Store pending promotion move
var promotionModal = null; // Store modal instance
var statsUpdateInterval = null; // Statistics polling interval

// Statistics functions - polls server every 2 seconds for updated stats
function initStatistics() {
    statsUpdateInterval = setInterval(updateStatistics, 2000);
    updateStatistics(); // Initial update
}

function updateStatistics() {
    $.ajax({
        url: getStatisticsUrl,
        type: 'GET',
        success: function(response) {
            $('#stat-accuracy').text(response.accuracy.toFixed(1) + '%');
            $('#stat-correct').text(response.correct_moves);
            $('#stat-incorrect').text(response.incorrect_moves);
            $('#stat-hints').text(response.hints_used);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching statistics:', error);
        }
    });
}

function showCompletionModal(stats) {
    $('#final-accuracy').text(stats.accuracy.toFixed(1) + '%');
    $('#final-correct').text(stats.correct_moves);
    $('#final-incorrect').text(stats.incorrect_moves);
    $('#final-hints').text(stats.hints_used);
    $('#completionModal').modal('show');
}

// Initialize board when page loads
$(document).ready(function() {
    initBoard();
    initPromotionModal();
    loadPositionFromServer();
    initStatistics(); // Initialize statistics polling

    // Event handlers for buttons
    $('#restart-btn').click(function() {
        restartPractice();
    });

    $('#hint-btn').click(function() {
        showHint();
    });
});

// Initialize chessboard.js
function initBoard() {
    var config = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: pieceTheme,
        orientation: playerColor === 'w' ? 'white' : 'black'
    };

    board = Chessboard('chessboard', config);
}

// Custom piece theme to use existing PNG images
function pieceTheme(piece) {
    var pieceMap = {
        'wP': 'white_pawn.png',
        'wN': 'white_knight.png',
        'wB': 'white_bishop.png',
        'wR': 'white_rook.png',
        'wQ': 'white_queen.png',
        'wK': 'white_king.png',
        'bP': 'black_pawn.png',
        'bN': 'black_knight.png',
        'bB': 'black_bishop.png',
        'bR': 'black_rook.png',
        'bQ': 'black_queen.png',
        'bK': 'black_king.png'
    };

    return '/static/repertoire/pieces/' + pieceMap[piece];
}

// Initialize promotion modal and event handlers
function initPromotionModal() {
    var modalElement = document.getElementById('promotionModal');
    promotionModal = new bootstrap.Modal(modalElement, {
        backdrop: 'static',
        keyboard: false
    });

    setPieceImages();

    $('.promotion-piece').click(function() {
        var piece = $(this).data('piece');
        onPromotionPieceSelected(piece);
    });
}

function setPieceImages() {
    var color = playerColor === 'w' ? 'white' : 'black';
    var basePath = '/static/repertoire/pieces/';
    $('#promo-queen-img').attr('src', basePath + color + '_queen.png');
    $('#promo-rook-img').attr('src', basePath + color + '_rook.png');
    $('#promo-bishop-img').attr('src', basePath + color + '_bishop.png');
    $('#promo-knight-img').attr('src', basePath + color + '_knight.png');
}

function isPawnPromotion(source, target) {
    var piece = game.get(source);
    if (!piece || piece.type !== 'p') return false;
    var targetRank = target.charAt(1);
    return (piece.color === 'w' && targetRank === '8') ||
           (piece.color === 'b' && targetRank === '1');
}

function onPromotionPieceSelected(piece) {
    if (!pendingMove) return;
    promotionModal.hide();
    completeMoveWithPromotion(pendingMove.source, pendingMove.target, piece);
    pendingMove = null;
}

function completeMoveWithPromotion(source, target, promotionPiece) {
    var move = game.move({from: source, to: target, promotion: promotionPiece});
    if (move === null) {
        console.error('Promotion move failed');
        board.position(game.fen());
        isPlayerTurn = true;
        return;
    }
    board.position(game.fen());
    isPlayerTurn = false;
    validateMoveWithServer(move.san, move);
}

// Validate drag start
function onDragStart(source, piece, position, orientation) {
    // Don't allow moves if game is over or not player's turn
    if (practiceFinished || !isPlayerTurn) {
        return false;
    }

    // Don't allow opponent's pieces to be dragged
    if ((playerColor === 'w' && piece.search(/^b/) !== -1) ||
        (playerColor === 'b' && piece.search(/^w/) !== -1)) {
        return false;
    }

    // Highlight legal destination squares
    highlightLegalMoves(source);
}

// Handle piece drop
function onDrop(source, target) {
    // Remove legal move highlights
    removeHighlights();

    // Check if this is a pawn promotion
    if (isPawnPromotion(source, target)) {
        pendingMove = {source: source, target: target};
        promotionModal.show();
        return 'snapback'; // Piece will be placed after selection
    }

    // Regular move
    var move = game.move({from: source, to: target});
    if (move === null) return 'snapback';

    isPlayerTurn = false;
    validateMoveWithServer(move.san, move);
}

// Update board position after snap animation
function onSnapEnd() {
    board.position(game.fen());
}

// Highlight legal moves for a piece
function highlightLegalMoves(square) {
    var moves = game.moves({
        square: square,
        verbose: true
    });

    // Highlight each legal destination square
    for (var i = 0; i < moves.length; i++) {
        highlightSquare(moves[i].to);
    }
}

// Add highlight class to a square
function highlightSquare(square) {
    var $square = $('#chessboard .square-' + square);
    $square.addClass('highlight-legal');
}

// Remove all highlights
function removeHighlights() {
    $('#chessboard .square-55d63').removeClass('highlight-legal');
    $('#chessboard .square-55d63').removeClass('highlight-hint');
}

// Validate move with server via AJAX
function validateMoveWithServer(sanMove, moveObj) {
    $.ajax({
        url: validateMoveUrl,
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': csrfToken
        },
        data: JSON.stringify({
            move: sanMove
        }),
        success: function(response) {
            if (response.correct) {
                // Show correct status
                updateStatus('correct');
                updateStatistics(); // Update stats after correct move

                // Check if there's an opponent move
                if (response.opponent_move) {
                    // Wait 500ms then make opponent's move
                    setTimeout(function() {
                        makeOpponentMove(response.opponent_move);
                    }, 500);
                } else {
                    // Practice finished
                    practiceFinished = true;
                    updateStatus('finished');

                    // Show completion modal with final statistics
                    setTimeout(function() {
                        $.ajax({
                            url: getStatisticsUrl,
                            type: 'GET',
                            success: showCompletionModal
                        });
                    }, 1000);
                }
            } else {
                // Move is incorrect - undo it
                game.undo();
                board.position(game.fen());
                updateStatus('incorrect');
                isPlayerTurn = true;
                updateStatistics(); // Update stats after incorrect move
            }
        },
        error: function(xhr, status, error) {
            console.error('Error validating move:', error);
            alert('Error validating move. Please try again.');
            // Undo move on error
            game.undo();
            board.position(game.fen());
            isPlayerTurn = true;
        }
    });
}

// Make opponent's move
function makeOpponentMove(sanMove) {
    // Execute move in chess.js
    var move = game.move(sanMove);

    if (move === null) {
        console.error('Invalid opponent move:', sanMove);
        return;
    }

    // Update board with animation
    board.position(game.fen());

    // Check for checkmate
    if (game.game_over()) {
        if (game.in_checkmate()) {
            practiceFinished = true;
            updateStatus('checkmate');
        } else {
            practiceFinished = true;
            updateStatus('finished');
        }
    } else {
        // Re-enable player turn
        isPlayerTurn = true;
    }
}

// Load current position from server
function loadPositionFromServer() {
    $.ajax({
        url: getPositionUrl,
        type: 'GET',
        success: function(response) {
            // Load FEN into chess.js and board
            game.load(response.fen);
            board.position(response.fen);

            // Set player turn flag
            isPlayerTurn = response.is_player_turn;

            // Check if finished
            if (response.finished) {
                practiceFinished = true;
                updateStatus('finished');
            } else if (response.is_checkmate) {
                practiceFinished = true;
                updateStatus('checkmate');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading position:', error);
            alert('Error loading board position.');
        }
    });
}

// Show hint - highlight legal moves
function showHint() {
    if (practiceFinished) {
        return;
    }

    removeHighlights();

    $.ajax({
        url: getHintsUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(response) {
            // Convert square numbers to square names
            var legalMoves = response.legal_moves;

            // Highlight source squares
            for (var i = 0; i < legalMoves.length; i++) {
                var fromSquare = squareNumToName(legalMoves[i].from);
                var $square = $('#chessboard .square-' + fromSquare);
                $square.addClass('highlight-hint');
            }

            updateStatus('hint');
            updateStatistics(); // Update stats after hint
        },
        error: function(xhr, status, error) {
            console.error('Error getting hints:', error);
            alert('Error getting hints.');
        }
    });
}

// Restart practice
function restartPractice() {
    removeHighlights();

    // Clear pending promotion
    if (pendingMove) {
        promotionModal.hide();
        pendingMove = null;
    }

    $.ajax({
        url: restartUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(response) {
            // Load starting FEN
            game.load(response.fen);
            board.position(response.fen);

            // Reset flags
            practiceFinished = false;
            isPlayerTurn = response.is_player_turn;

            // Clear status
            $('#status-container').html('');
            updateStatistics(); // Update stats after restart
            $('#completionModal').modal('hide'); // Hide completion modal
        },
        error: function(xhr, status, error) {
            console.error('Error restarting:', error);
            alert('Error restarting practice.');
        }
    });
}

// Update status indicator
function updateStatus(status) {
    var html = '';

    switch(status) {
        case 'correct':
            html = '<div class="status-correct">CORRECT</div>';
            break;
        case 'incorrect':
            html = '<div class="status-incorrect">INCORRECT</div>';
            break;
        case 'hint':
            html = '<div class="status-hint">HINT</div>';
            break;
        case 'finished':
            html = '<div class="status-finished">FINISHED</div>';
            break;
        case 'checkmate':
            html = '<div class="status-checkmate">CHECKMATE</div>';
            break;
    }

    $('#status-container').html(html);
}

// Convert python-chess square number to square name (e.g., 0 -> a1)
function squareNumToName(squareNum) {
    var files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    var ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];

    var file = files[squareNum % 8];
    var rank = ranks[Math.floor(squareNum / 8)];

    return file + rank;
}

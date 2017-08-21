var app = angular.module("myApp", []);

app.controller('MainController', ['$scope', '$http', function($scope, $http) {
    $scope.inactive = true;
    $scope.loading = false;
    $scope.new_game = true;
    $scope.game_over = false;
    $scope.chance = true;
    $scope.message = '';
    $scope.winning = [[], [], [], [], [], [], [], [] ,[] ,[]];
    $scope.score_player = 0;
    $scope.score_computer = 0;

    $scope.blank_board = [
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    ];

    $scope.board = angular.copy($scope.blank_board);

    $scope.click = function(row, col) {
        // Do nothing if the game is over
        if ($scope.game_over) {
            return;
        }

        if ($scope.board[row][col] === ' ') {
            $scope.board[row][col] = 'X';

            var winner = has_won('X');

            // Player should never win
            if (winner === 'X') {
                $scope.message = 'You won! :)';
                $scope.score_player++;
                $scope.game_over = true;
                return;
            }
            else if (winner === 'T') {
                $scope.message = 'You tied!';
                $scope.game_over = true;
                return;
            }
            console.log($scope.inactive,$scope.loading,$scope.new_game,$scope.game_over,winner);
            $scope.inactive = true;
            $scope.loading = true;
            $http.post('/move', { player: 'X', computer: 'O', board: $scope.board, chance: $scope.chance}).then(function(response) {
                $scope.loading = false;

                if (response.data.hasOwnProperty('computer_row') && response.data.hasOwnProperty('computer_col')) {
                    $scope.board[response.data.computer_row][response.data.computer_col] = 'O'
                }

                var winner = has_won('O');
                if (winner === 'O') {
                    $scope.message = 'You lost :(';
                    $scope.score_computer++;
                    $scope.game_over = true
                }
                else if (winner === 'T') {
                    $scope.message = 'You tied!';
                    $scope.game_over = true;
                }

                $scope.inactive = false;
            }, function(response) {
                $scope.loading = false;
                alert('Server error');
            });
        }
    };

    $scope.inactive = false;

    $scope.restart = function() {
        $scope.loading = false;
        $scope.board = angular.copy($scope.blank_board);
        $scope.game_over = false;
        $scope.message = '';
        $scope.winning = [[], [], [], [], [], [], [], [] ,[] ,[]];
        $scope.new_game = true;
        $scope.chance = true;
    };

    $scope.player_goes_first = function() {
        $scope.new_game = false;
        $scope.chance = false;
    };


    $scope.computer_goes_first = function() {
        $scope.new_game = false;
        $scope.loading = true;
        $scope.chance = true;

        $http.post('/move', { player: 'X', computer: 'O', board: $scope.board, chance: $scope.chance }).then(function(response) {
            $scope.loading = false;

            if (response.data.hasOwnProperty('computer_row') && response.data.hasOwnProperty('computer_col')) {
                $scope.board[response.data.computer_row][response.data.computer_col] = 'O'
            }

            $scope.inactive = false;
        }, function(response) {
            $scope.loading = false;
            alert('Server error');
        });
    };

    // Returns the winning vertical combination or false
    var has_won = function(mark) {

        var total_zero = 0;
        var ct;
        for (var r = 0; r < 10; r++) {
            for (var c = 0; c < 10; c++) {
                // horizontal
                ct = 0;
                if ($scope.board[r][c] === ' ') total_zero++;
                for (var k = 0; k < 5 && c+k < 10; ++k) {
                    if($scope.board[r][c+k] === mark) {
                        ct++;
                    }
                }
                if (ct===5) {
                    console.log(r,c,k);
                    for (var k = 0; k < 5; ++k) {
                        $scope.winning[r][c+k] = 1;

                    }
                    return mark;
                }

                // vertical
                ct = 0;
                for (var k = 0; k < 5 && r+k < 10; ++k) {
                    if($scope.board[r+k][c] === mark) {
                        ct++;
                    }
                }
                if (ct===5) {
                    console.log(r,c,k);
                    for (var k = 0; k < 5; ++k) {
                        $scope.winning[r+k][c] = 1;

                    }
                    return mark;
                }

                // diagonal
                ct = 0;
                for (var k = 0; k < 5 && r+k < 10 && c+k < 10; ++k) {
                    if($scope.board[r+k][c+k] === mark) {
                        ct++;
                    }
                }
                if (ct===5) {
                    console.log(r,c,k);
                    for (var k = 0; k < 5; ++k) {
                        $scope.winning[r+k][c+k] = 1;

                    }
                    return mark;
                }

                ct = 0;
                for (var k = 0; k < 5 && r+k < 10 && c-k >= 0; ++k) {
                    if($scope.board[r+k][c-k] === mark) {
                        ct++;
                    }
                }
                if (ct===5) {
                    console.log(r,c,k);
                    for (var k = 0; k < 5; ++k) {
                        $scope.winning[r+k][c-k] = 1;

                    }
                    return mark;
                }
            }
        }

        if (total_zero === 0) return 'T';

        return '_';
    };


    var is_board_full = function() {
        for (var r = 0; r < 10; r++) {
            for (var c = 0; c < 10; c++) {
                if ($scope.board[r][c] === ' ') {
                    return false;
                }
            }
        }

        return true;
    }

}]);
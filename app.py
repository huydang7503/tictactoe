from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

def check_for_win(player, current_board):
    # Check rows
    for i in range(0, 3):
        if current_board[1 + i * 3] == current_board[2 + i * 3] == current_board[3 + i * 3] == player:
            return True
    # Check columns
    for i in range(0, 3):
        if current_board[1 + i] == current_board[4 + i] == current_board[7 + i] == player:
            return True
    # Check diagonals
    if current_board[1] == current_board[5] == current_board[9] == player or current_board[3] == current_board[5] == current_board[7] == player:
        return True
    return False

def check_for_draw(current_board):
    return all(value != " " for value in current_board.values())

def minimax(current_board, is_maximizing):
    if check_for_win("O", current_board):
        return 1

    if check_for_win("X", current_board):
        return -1

    if check_for_draw(current_board):
        return 0

    if is_maximizing:
        best_score = -1
        for key in current_board.keys():
            if current_board[key] == " ":
                current_board[key] = "O"
                score = minimax(current_board, False)
                current_board[key] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = 1
        for key in current_board.keys():
            if current_board[key] == " ":
                current_board[key] = "X"
                score = minimax(current_board, True)
                current_board[key] = " "
                best_score = min(score, best_score)
        return best_score
def play_computer():
    best_score = -10
    best_move = 0
    temp_board = session['board'].copy()

    for key in temp_board.keys():
        if temp_board[key] == " ":
            temp_board[key] = "O"
            score = minimax(temp_board, False)
            temp_board[key] = " "
            if score > best_score:
                best_score = score
                best_move = key

    session['board'][best_move] = "O"

def get_game_state():
    if 'board' not in session:
        reset_game_state()

def reset_game_state():
    session['board'] = {1: " ", 2: " ", 3: " ",
                        4: " ", 5: " ", 6: " ",
                        7: " ", 8: " ", 9: " "}
    session['turn'] = "X"
    session['game_end'] = False
    session['mode'] = "multiPlayer"

def game_logic(cell):
    get_game_state()  # Đảm bảo trạng thái game được khởi tạo từ session
    board = session['board']
    turn = session['turn']
    game_end = session['game_end']
    mode = session['mode']

    if board[cell] == " ":
        board[cell] = turn

        if check_for_win(turn, board):
            result = f"{turn} wins the game!"
            game_end = True
        elif check_for_draw(board):
            result = "Game Draw!"
            game_end = True
        else:
            result = None

        if mode != "multiPlayer":
            if turn == "X":
                play_computer()
                if check_for_win("O", board):
                    result = "Computer wins the game!"
                    game_end = True
                elif check_for_draw(board):
                    result = "Game Draw!"
                    game_end = True
                turn = "X"
        else:
            turn = "O" if turn == "X" else "X"
        # Cập nhật session với trạng thái mới
        session['board'] = board
        session['turn'] = turn
        session['game_end'] = game_end
        session.modified = True  # Đánh dấu session đã được thay đổi

        return {"result": result, "board": board, "game_end": game_end}
    return {}

@app.route("/")
def home():
    get_game_state()
    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play():
    cell = int(request.form.get("cell", 0))
    result = game_logic(cell)
    session.modified = True
    return jsonify(result)

@app.route("/restart", methods=["POST"])
def restart():
    reset_game_state()
    session.modified = True
    return jsonify({"board": session['board'], "turn": session['turn'], "game_end": session['game_end']})

@app.route("/mode", methods=["POST"])
def change_mode():
    mode = request.form.get("mode", "multiPlayer")
    session['mode'] = mode
    session.modified = True
    return jsonify({"mode": mode})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

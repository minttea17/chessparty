import chess
import chess.svg
from cairosvg import svg2png
import telebot
from telebot import types
import sqlite3
import config
import os

bot = telebot.TeleBot(config.token)
conn = sqlite3.connect('user_states.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_states
             (user_id INTEGER PRIMARY KEY, state INTEGER)''')
c.close()

def save_game_state(board, turn):
    with open('game_state.txt', 'w') as file:
        file.write(f"{board.fen()}\n{turn}")

def load_game_state():
    global board
    global turn
    with open('game_state.txt', 'r') as file:
        fen, turn = file.read().splitlines()
        board = chess.Board(fen)
        return board, int(turn)

turn = 1
board = chess.Board()
if os.path.exists('game_state.txt'):
    board, turn = load_game_state()

svg_code = chess.svg.board(board)
svg2png(bytestring=svg_code, write_to='board.png')
photo = open('board.png', 'rb')
bot.send_photo(config.channel_id, photo)
bot.send_message(config.channel_id, "New game started!")

save_game_state(board, turn)

def create_connection():
    conn = sqlite3.connect('user_states.db')
    c = conn.cursor()
    return conn, c

def check_board():
    global board
    if board.is_checkmate():
        return "checkmate"
    elif board.is_stalemate():
        return "stalemate"
    elif board.is_insufficient_material():
        return "insufficient"
    elif board.is_fivefold_repetition():
        return "fivefold_repetition"
    elif board.is_seventyfive_moves():
        return "seventyfive_moves"
    elif board.is_check():
        return "check"
    else:
        return "regular"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, config.start)

@bot.message_handler(commands=['play'])
def send_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conn, c = create_connection()
    c.execute("SELECT state FROM user_states WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result:
        bot.send_message(chat_id, config.ready)
    else:
        markup = types.InlineKeyboardMarkup()
        black_button = types.InlineKeyboardButton("Black", callback_data='black')
        white_button = types.InlineKeyboardButton("White", callback_data='white')
        markup.row(black_button, white_button)
        bot.send_message(chat_id, config.play, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    conn, c = create_connection()

    c.execute("SELECT state FROM user_states WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result:
        bot.answer_callback_query(call.id, "You have already choosen the side!")

    elif call.data == 'black':
        bot.answer_callback_query(call.id, "You chose Black.")
        c.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (user_id, 0))
        conn.commit()
    elif call.data == 'white':
        bot.answer_callback_query(call.id, "You chose White.")
        c.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (user_id, 1))
        conn.commit()

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global board
    global turn
    user_id = message.from_user.id
    conn, c = create_connection()
    c.execute("SELECT state FROM user_states WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        bot.send_message(message.chat.id, config.unknown)
        return
    if result[0] != turn:
        bot.send_message(message.chat.id, config.notturn)
        return
    legal = []
    for i in board.legal_moves:
        legal.append(board.san(i))

    try:
        board.push_san(message.text)
    except:
        bot.send_message(message.chat.id, config.illegal+
                            ", ".join(legal))
        return

    svg_code = chess.svg.board(board)
    svg2png(bytestring=svg_code, write_to='board.png')
    photo = open('board.png', 'rb')
    status = check_board()

    bot.send_photo(message.chat.id, photo)
    bot.send_message(message.chat.id, config.moves[status]+
                     "\nList of possible moves: "+", ".join(legal))
    photo = open('board.png', 'rb')
    bot.send_photo(config.channel_id, photo)
    bot.send_message(config.channel_id, message.text+"\n"+config.moves[status]+
                     "\nList of possible moves: "+", ".join(legal))
    if turn == 0:
        turn = 1
    else:
        turn = 0    

    if status not in ["regular", "check"]:
        # Restart the game.
        board = chess.Board()
        turn = 1
        svg_code = chess.svg.board(board)
        svg2png(bytestring=svg_code, write_to='board.png')
        photo = open('board.png', 'rb')
        bot.send_photo(config.channel_id, photo)
        bot.send_message(config.channel_id, "New game started!")

    save_game_state(board, turn)

bot.polling()

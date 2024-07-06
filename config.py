token = "xxx"
channel_id = "@xxx"
start = '''
🎮 Multiplayer chess on Telegram.
Check out the current game status in our channel: @chesspartych

Play now: /play
'''
ready = '''
🚀 You are all set to play!
You can make any legal move in standard chess format.
For example: e4
'''
play = '''
⚔️ You must choose your side:
Black or White.

Choose wisely! You can't change it later.
'''
unknown = "❓ Unknown command.\nTry: /help"
illegal = "⛔ Illegal move.\nList of possible moves: "
notturn = "🕒 It's not your turn."
moves = {"regular": "Regular move.",
         "check": "Check! Cool.",
         "checkmate": "Checkmate! Congratulations!",
         "stalemate": "Stalemate. Things happen..",
         "insufficient": "Only the strongest remained.. Insufficient material.",
         "fivefold_repetition": "That's a time loop. Fivefold repetition.",
         "seventyfive_moves": "75 moves without a pawn push or capture."}
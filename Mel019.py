from typing import List, Union
import numpy as np
from IPython.display import clear_output
import time
import os
import random

BLACK = -1  # 黒
WHITE = 1   # 白
EMPTY = 0   # 空

def init_board(N:int=8):
    """
    ボードを初期化する
    N: ボードの大きさ　(N=8がデフォルト値）
    """
    board = np.zeros((N, N), dtype=int)
    C0 = N//2
    C1 = C0-1
    board[C1, C1], board[C0, C0] = WHITE, WHITE  # White
    board[C1, C0], board[C0, C1] = BLACK, BLACK  # Black
    return board

def count_board(board, piece=EMPTY):
    return np.sum(board == piece)

# Emoji representations for the pieces
BG_EMPTY = "\x1b[42m"
BG_RESET = "\x1b[0m"

stone_codes = [
    f'{BG_EMPTY}⚫️{BG_RESET}',
    f'{BG_EMPTY}🟩{BG_RESET}',
    f'{BG_EMPTY}⚪️{BG_RESET}',
]

def stone(piece):
    return stone_codes[piece+1]

def display_clear():
    os.system('clear')
    clear_output(wait=True)

BLACK_NAME=''
WHITE_NAME=''

def display_board(board, clear=True, sleep=0, black=None, white=None):
    """
    オセロ盤を表示する
    """
    global BLACK_NAME, WHITE_NAME
    if clear:
        clear_output(wait=True)
    if black:
        BLACK_NAME=black
    if white:
        WHITE_NAME=white
    for i, row in enumerate(board):
        for piece in row:
            print(stone(piece), end='')
        if i == 1:
            print(f'  {BLACK_NAME}')
        elif i == 2:
            print(f'   {stone(BLACK)}: {count_board(board, BLACK):2d}')
        elif i == 3:
            print(f'  {WHITE_NAME}')
        elif i == 4:
            print(f'   {stone(WHITE)}: {count_board(board, WHITE):2d}')
        else:
            print()  # New line after each row
    if sleep > 0:
        time.sleep(sleep)

def all_positions(board):
    N = len(board)
    return [(r, c) for r in range(N) for c in range(N)]

# Directions to check (vertical, horizontal)
directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]

def is_valid_move(board, row, col, player):
    # Check if the position is within the board and empty
    N = len(board)
    if row < 0 or row >= N or col < 0 or col >= N or board[row, col] != 0:
        return False

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < N and 0 <= c < N and board[r, c] == -player:
            while 0 <= r < N and 0 <= c < N and board[r, c] == -player:
                r, c = r + dr, c + dc
            if 0 <= r < N and 0 <= c < N and board[r, c] == player:
                return True
    return False

def get_valid_moves(board, player):
    return [(r, c) for r, c in all_positions(board) if is_valid_move(board, r, c, player)]

def flip_stones(board, row, col, player):
    N = len(board)
    stones_to_flip = []
    for dr, dc in directions:
        directional_stones_to_flip = []
        r, c = row + dr, col + dc
        while 0 <= r < N and 0 <= c < N and board[r, c] == -player:
            directional_stones_to_flip.append((r, c))
            r, c = r + dr, c + dc
        if 0 <= r < N and 0 <= c < N and board[r, c] == player:
            stones_to_flip.extend(directional_stones_to_flip)
    return stones_to_flip

def display_move(board, row, col, player):
    stones_to_flip = flip_stones(board, row, col, player)
    board[row, col] = player
    display_board(board, sleep=0.3)
    for r, c in stones_to_flip:
        board[r, c] = player
        display_board(board, sleep=0.1)
    display_board(board, sleep=0.6)

def find_eagar_move(board, player):
    valid_moves = get_valid_moves(board, player)
    max_flips = 0
    best_result = None
    for r, c in valid_moves:
        stones_to_flip = flip_stones(board, r, c, player)
        if max_flips < len(stones_to_flip):
            best_result = (r, c)
            max_flips = len(stones_to_flip)
    return best_result

class OthelloAI(object):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def __repr__(self):
        return f"{self.face}{self.name}"

    def move(self, board: np.array, piece: int)->tuple[int, int]:
        valid_moves = get_valid_moves(board, piece)
        return valid_moves[0]

    def say(self, board: np.array, piece: int)->str:
        if count_board(board, piece) >= count_board(board, -piece):
            return 'やったー'
        else:
            return 'がーん'

class OchibiAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board: np.array, piece: int)->tuple[int, int]:
        valid_moves = get_valid_moves(board, piece)
        return valid_moves[0]


def board_play(player: OthelloAI, board, piece: int):
    display_board(board, sleep=0)
    if len(get_valid_moves(board, piece)) == 0:
        print(f"{player}は、置けるところがありません。スキップします。")
        return True
    try:
        start_time = time.time()
        r, c = player.move(board.copy(), piece)
        end_time = time.time()
    except:
        print(f"{player.face}{player.name}は、エラーを発生させました。反則まけ")
        return False
    if not is_valid_move(board, r, c, piece):
        print(f"{player}が返した({r},{c})には、置けません。反則負け。")
        return False
    display_move(board, r, c, piece)
    return True

def comment(player1: OthelloAI, player2: OthelloAI, board):
    try:
        print(f"{player1}: {player1.say(board, BLACK)}")
    except:
        pass
    try:
        print(f"{player2}: {player2.say(board, WHITE)}")
    except:
        pass

def game(player1: OthelloAI, player2: OthelloAI,N=6):
    board = init_board(N)
    display_board(board, black=f'{player1}', white=f'{player2}')
    while count_board(board, EMPTY) > 0:
        if not board_play(player1, board, BLACK):
            break
        if not board_play(player2, board, WHITE):
            break
    comment(player1, player2, board)
  
# ## ここから追加 ##
# ## ここから追加 ##

board = init_board(N=8)
# board

# display_board(board)

# get_valid_moves(board, WHITE)

import random

class RandomAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board, color: int)->tuple[int, int]:
        """
        ボードが与えられたとき、どこに置くか(row,col)を返す
        """
        valid_moves = get_valid_moves(board, color)
        # ランダムに選ぶ
        selected_move = random.choice(valid_moves)
        return selected_move

class OthelloAI(object):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def __repr__(self):
        return f"{self.face}{self.name}"

    def move(self, board: np.array, color: int)->tuple[int, int]:
        """
        ボードの状態と色(color)が与えられたとき、
        どこに置くか返す(row, col)
        """
        valid_moves = get_valid_moves(board, color)
        return valid_moves[0]

    def say(self, board: np.array, piece: int)->str:
        if count_board(board, piece) >= count_board(board, -piece):
            return 'やったー'
        else:
            return 'がーん'

import sys

def display_board2(board, marks):
    """
    オセロ盤を表示する
    """
    global BLACK_NAME, WHITE_NAME
    clear_output(wait=True)
    for row, rows in enumerate(board):
        for col, piece in enumerate(rows):
            if (row, col) in marks:
                print(marks[(row,col)], end='')
            else:
                print(stone(piece), end='')
        if row == 1:
            print(f'  {BLACK_NAME}')
        elif row == 2:
            print(f'   {stone(BLACK)}: {count_board(board, BLACK):2d}')
        elif row == 3:
            print(f'  {WHITE_NAME}')
        elif row == 4:
            print(f'   {stone(WHITE)}: {count_board(board, WHITE):2d}')
        else:
            print()  # New line after each row

## Youは自分で操作する（プレイヤーとして対戦する場合）
class You(OthelloAI):

    def move(self, board, color: int)->tuple[int, int]:
        """
        ボードの状態と色(color)が与えられたとき、
        どこに置くか人間に尋ねる(row, col)
        """
        valid_moves = get_valid_moves(board, color)
        MARK = '①②③④⑤⑥⑦⑧⑨'
        marks={}
        for i, rowcol in enumerate(valid_moves):
            if i < len(MARK):
                marks[rowcol] = MARK[i]
                marks[i+1] = rowcol
        display_board2(board, marks)
        n = int(input('どこにおきますか？ '))
        return marks[n]

# ## 16:48追加

def count_board(board, piece=EMPTY):
    return np.sum(board == piece)

def display_board(board, clear=True, sleep=0, black=None, white=None):
    """
    オセロ盤を表示する
    """
    global BLACK_NAME, WHITE_NAME
    if clear:
        clear_output(wait=True)
    if black:
        BLACK_NAME = black
    if white:
        WHITE_NAME = white
    for i, row in enumerate(board):
        for piece in row:
            print(stone(piece), end='')
        if i == 1:
            print(f'  {BLACK_NAME}')
        elif i == 2:
            print(f'   {stone(BLACK)}: {count_board(board, BLACK):2d}')
        elif i == 3:
            print(f'  {WHITE_NAME}')
        elif i == 4:
            print(f'   {stone(WHITE)}: {count_board(board, WHITE):2d}')
        else:
            print()  # New line after each row
    if sleep > 0:
        time.sleep(sleep)

class OthelloAI:
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board, color):
        # ここに移動のロジックを実装（基本的な実装）
        # この例では、有効な手の中からランダムに選択します
        valid_moves = get_valid_moves(board, color)
        return random.choice(valid_moves) if valid_moves else None

    def say(self, board, color):
        # ここに話すロジックを実装
        pass

class OchibiAI(OthelloAI):
    def __init__(self, face, name):
        super().__init__(face, name)

    def move(self, board, color):
        # OchibiAIの移動ロジックを実装
        # この例では、有効な手の中からランダムに選択します
        valid_moves = get_valid_moves(board, color)
        return random.choice(valid_moves) if valid_moves else None

class You(OthelloAI):
    def __init__(self, face, name):
        super().__init__(face, name)

    def move(self, board, color):
        # 人間プレイヤーの移動ロジックを実装
        # この例では、ユーザーに手の入力を求めます
        valid_moves = get_valid_moves(board, color)
        if not valid_moves:
            return None
        print("有効な手:", valid_moves)
        move = None
        while move not in valid_moves:
            try:
                row = int(input("行を入力してください: "))
                col = int(input("列を入力してください: "))
                move = (row, col)
            except ValueError:
                print("無効な入力です。もう一度入力してください。")
        return move

# # 各AIクラスのインスタンスを作成
# # teruchi = OthelloAI('🍦', 'てるち')
# # momo = OchibiAI('💲', 'ももぽん')

# # ゲームの実行
# #game(teruchi, momo, N=8)



## 自作AI ##
## 自作AI ##

class SeaAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    # def evaluate_board(board, player):
    #     return count_board(board, player)

    def evaluate_board(self, board, player):
        return count_board(board, player)

    # def minimax(board, depth, player):
    #     if depth == 0 or count_board(board, EMPTY) == 0:
    #         return evaluate_board(board, player), None

    def minimax(self, board, depth, player):
        if depth == 0 or count_board(board, EMPTY) == 0:
            return self.evaluate_board(board, player), None

        best_move = None
        if player == BLACK:
            max_eval = -float('inf')
            for move in get_valid_moves(board, player):
                new_board = board.copy()
                make_move(new_board, move, player)
                eval, _ = minimax(new_board, depth - 1, -player)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in get_valid_moves(board, player):
                new_board = board.copy()
                make_move(new_board, move, player)
                eval, _ = minimax(new_board, depth - 1, -player)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    # def make_move(board, move, player):
    def make_move(self, board, move, player):
        r, c = move
        stones_to_flip = flip_stones(board, r, c, player)
        board[r, c] = player
        for r, c in stones_to_flip:
            board[r, c] = player

class MinimaxAI(OthelloAI):
    # def __init__(self, face, name, depth=3):
    #     super().__init__(face, name)
    #     self.depth = depth

    def __init__(self, face, name, depth=5):  # 探索の深さを増やす
        super().__init__(face, name)
        self.depth = depth

    # def move(self, board, player):
    #     _, best_move = minimax(board, self.depth, player)
    #     return best_move

    def move(self, board, player):
        _, best_move = self.minimax(board, self.depth, player)
        return best_move



## 追加①アルファベータ枝刈りの追加 ##

def minimax(self, board, depth, alpha, beta, player):
    if depth == 0 or count_board(board, EMPTY) == 0:
        return self.evaluate_board(board, player), None

    valid_moves = get_valid_moves(board, player)
    if not valid_moves:
        return self.evaluate_board(board, player), None

    best_move = None
    if player == BLACK:
        max_eval = -float('inf')
        for move in valid_moves:
            new_board = board.copy()
            make_move(new_board, move, player)
            eval, _ = self.minimax(new_board, depth - 1, alpha, beta, -player)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = board.copy()
            make_move(new_board, move, player)
            eval, _ = self.minimax(new_board, depth - 1, alpha, beta, -player)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move



## 追加②評価関数の改善 ##

def evaluate_board(self, board, player):
    # より洗練された評価ロジック
    # 例えば、角や辺の占有、安定性、移動可能性などを考慮
    score = 0
    # 角の占有
    score += 25 * (board[0,0] == player)
    score += 25 * (board[0,7] == player)
    score += 25 * (board[7,0] == player)
    score += 25 * (board[7,7] == player)
    # その他の評価ロジック...
    return score



## 追加③より洗練された評価関数 ##

def evaluate_board(self, board, player):
    score = 0
    opp_player = -player

    # 角の占有
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    for x, y in corners:
        if board[x, y] == player:
            score += 100  # 角は非常に価値が高い
        elif board[x, y] == opp_player:
            score -= 100

    # エッジの安定性やモビリティなど、他の要素に対する評価を追加
    # ...

    # モビリティの評価
    valid_moves_count = len(get_valid_moves(board, player))
    score += valid_moves_count * 5  # 例: 合法手1つにつき5点

    # フロンティアディスクの評価
    # ...

    # ゲームのフェーズに応じた戦略
    # ...

    return score



## 追加④オープニングブックの使用 ##

class OthelloAI:
    # ...

    def __init__(self, face, name):
        # ...
        self.opening_book = self.load_opening_book()
        self.is_opening_phase = True

    def load_opening_book(self):
        # ここにオープニングブックのデータをロードするコード
        # 例: {ボードの状態: 最適な手, ...}
        return {
            "..........*......O......***....": (5, 4),
            # その他のオープニング手
        }

    def move(self, board, player):
        if self.is_opening_phase:
            # オープニングブックを使用して手を選択
            opening_move = self.opening_book.get(board_to_string(board))
            if opening_move:
                return opening_move
            else:
                # オープニングブックの手がない場合は通常の戦略に移行
                self.is_opening_phase = False

        # ミニマックスアルゴリズムまたは他の戦略を使用
        return self.minimax_strategy(board, player)

    # ミニマックス戦略の実装
    # ...

def board_to_string(board):
    # ボードを文字列に変換する関数
    return ''.join(['O' if x == 1 else '*' if x == -1 else '.' for x in board.flatten()])



## 追加⑤エンドゲームのデータベース ##

class OthelloAI:
    # ...

    def __init__(self, face, name):
        # ...
        self.endgame_database = self.load_endgame_database()

    def load_endgame_database(self):
        # ここにエンドゲームのデータベースをロードするコード
        # 例: {ボードの状態: 最適な手, ...}
        return {
            "..........*......O......***....": (5, 4),
            # その他のエンドゲームの手
        }

    def move(self, board, player):
        # ...
        # ゲームの終盤かどうかの判断
        if self.is_endgame(board):
            endgame_move = self.endgame_database.get(board_to_string(board))
            if endgame_move:
                return endgame_move

        # 通常の戦略
        return self.minimax_strategy(board, player)

    def is_endgame(self, board):
        # ゲームが終盤かどうかを判断するロジック
        # 例: 空きマスの数が少ない場合など
        return count_board(board, EMPTY) <= 10

    # ミニマックス戦略の実装
    # ...

def board_to_string(board):
    # ボードを文字列に変換する関数
    return ''.join(['O' if x == 1 else '*' if x == -1 else '.' for x in board.flatten()])



## 追加⑥機械学習の活用 ##

class OthelloAI:
    def __init__(self):
        self.model = self.create_model()
        # その他の初期化処理...

    def create_model(self):
        # ニューラルネットワークモデルの作成
        model = ...
        return model

    def train(self, training_data):
        # 学習プロセス
        for episode in range(number_of_episodes):
            state = self.reset_environment()
            done = False
            while not done:
                action = self.choose_action(state)
                next_state, reward, done = self.step(action)
                self.remember(state, action, reward, next_state, done)
                state = next_state
            self.replay()  # 経験再生

    def choose_action(self, state):
        # 行動選択ロジック
        if np.random.rand() <= epsilon:
            return self.random_action()
        else:
            return self.model.predict_action(state)

    def step(self, action):
        # ゲームの1ステップを進める
        # ...
        return next_state, reward, done

    # その他の補助関数
    # ...

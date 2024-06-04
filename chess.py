import pygame
import chess
import chess.engine
import sys

# Инициализация Pygame
pygame.init()

# Установим размеры окна
width, height = 1200, 800  # Увеличим ширину окна
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Учебные шахматы')

# Цвета
white = (255, 255, 255)
black = (0, 0, 0)
highlight_color = (0, 255, 0)  # Зеленый цвет для выделения
dialog_color = (200, 200, 200)  # Цвет для диалогового окна
best_move_color = (255, 165, 0)  # Оранжевый цвет для лучшего хода

# Размер клетки
square_size = height // 8

# Инициализация шахматной доски
board = chess.Board()

# Уровень сложности ИИ
difficulty = 'hard'  # 'easy', 'medium', 'hard'

# Укажите правильный путь к исполняемому файлу Stockfish
engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")

# Функция для переноса текста
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_width, _ = font.size(word + ' ')
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
    lines.append(' '.join(current_line))
    
    return lines

# Обновленная функция draw_dialog_box
def draw_dialog_box(show_best_move, best_move, explanation):
    dialog_box_rect = pygame.Rect(8 * square_size, 0, width - 8 * square_size, height)
    pygame.draw.rect(screen, dialog_color, dialog_box_rect)
    
    font = pygame.font.Font(None, 24)  # Уменьшен размер шрифта для лучшей читаемости
    hint_text = "Подсказка\nНажмите для лучшего хода"
    hint_lines = hint_text.split('\n')
    
    for i, line in enumerate(hint_lines):
        text = font.render(line, True, black)
        screen.blit(text, (8 * square_size + 10, 10 + i * 30))  # Уменьшен интервал между строками
    
    if show_best_move and best_move:
        best_move_text = f"Лучший ход:\n{best_move.uci()}"
        text = font.render(best_move_text, True, black)
        screen.blit(text, (8 * square_size + 10, 100))

        explanation_lines = wrap_text(explanation, font, width - 8 * square_size - 20)
        
        for i, line in enumerate(explanation_lines):
            text = font.render(line, True, black)
            screen.blit(text, (8 * square_size + 10, 140 + i * 30))  # Уменьшен интервал между строками

# Функция для подсветки хода ИИ
def highlight_ai_move(move):
    from_square = move.from_square
    to_square = move.to_square
    
    from_row, from_col = divmod(from_square, 8)
    to_row, to_col = divmod(to_square, 8)
    
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(from_col * square_size, from_row * square_size, square_size, square_size), 5)
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(to_col * square_size, to_row * square_size, square_size, square_size), 5)

# Функция для подсветки лучшего хода
def highlight_best_move(move):
    from_square = move.from_square
    to_square = move.to_square
    
    from_row, from_col = divmod(from_square, 8)
    to_row, to_col = divmod(to_square, 8)
    
    pygame.draw.rect(screen, best_move_color, pygame.Rect(from_col * square_size, from_row * square_size, square_size, square_size), 5)
    pygame.draw.rect(screen, best_move_color, pygame.Rect(to_col * square_size, to_row * square_size, square_size, square_size), 5)

# Остальные функции и основной цикл
def draw_board():
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * square_size, r * square_size, square_size, square_size))
    
    # Рисуем координаты
    font = pygame.font.Font(None, 24)
    for i in range(8):
        # Вертикальные координаты (1-8)
        label = font.render(str(8 - i), True, black if i % 2 == 0 else white)
        screen.blit(label, (5, i * square_size + 5))
        
        # Горизонтальные координаты (a-h)
        label = font.render(chr(ord('a') + i), True, black if i % 2 == 0 else white)
        screen.blit(label, (i * square_size + square_size - 15, height - 25))

def draw_pieces(board, selected_square=None):
    pieces = board.piece_map()
    for square, piece in pieces.items():
        r, c = divmod(square, 8)
        piece_symbol = piece.symbol()
        if piece_symbol.isupper():
            piece_image = pygame.image.load(f'images/{piece_symbol}.png')
        else:
            piece_image = pygame.image.load(f'images/{piece_symbol.upper()}2.png')
        
        if square == selected_square:
            piece_image = pygame.transform.scale(piece_image, (square_size + 10, square_size + 10))
            screen.blit(piece_image, pygame.Rect(c * square_size - 5, r * square_size - 5, square_size + 10, square_size + 10))
        else:
            piece_image = pygame.transform.scale(piece_image, (square_size, square_size))
            screen.blit(piece_image, pygame.Rect(c * square_size, r * square_size, square_size, square_size))

def highlight_moves(board, selected_square):
    if selected_square is not None:
        legal_moves = board.legal_moves
        for move in legal_moves:
            if move.from_square == selected_square:
                to_square = move.to_square
                r, c = divmod(to_square, 8)
                pygame.draw.rect(screen, highlight_color, pygame.Rect(c * square_size, r * square_size, square_size, square_size), 3)

def comment_move(move, board):
    piece = board.piece_at(move.from_square)
    piece_name = piece.symbol().upper() if piece else 'неизвестная фигура'
    return f"{piece_name} перемещен с {move.uci()[:2]} на {move.uci()[2:]}."

def display_comment(comment):
    font = pygame.font.Font(None, 36)
    text = font.render(comment, True, black)
    screen.blit(text, (10, height - 40))

def get_best_move_for_player(board, engine):
    try:
        limit = chess.engine.Limit(time=1.0)  # Время анализа 1 секунда
        result = engine.play(board, limit)
        move = result.move
        analysis = engine.analyse(board, limit)
        score = analysis["score"].relative.score()
        print(f"Полученный ход: {move}, Оценка: {score}")  # Отладочная информация
        return move, score
    except Exception as e:
        print(f"Ошибка при получении лучшего хода: {e}")
        return None, None

def get_detailed_move_explanation(move, board):
    piece = board.piece_at(move.from_square)
    target_piece = board.piece_at(move.to_square)
    
    explanation = []
    
    if target_piece:
        explanation.append(f"Этот ход атакует {target_piece.symbol().upper()} на {move.uci()[2:]}, что создает угрозу для противника.")
    else:
        explanation.append("Этот ход улучшает вашу позицию, создавая давление на фигуры противника.")
    
    # Проверка защиты фигур
    board.push(move)
    defenders = list(board.attackers(board.turn, move.to_square))
    board.pop()
    if defenders:
        explanation.append(f"Этот ход защищает фигуру на {move.uci()[2:]}, которую атакуют {len(defenders)} фигуры противника.")
    else:
        explanation.append(f"Этот ход перемещает фигуру на {move.uci()[2:]}.")

    # Проверка на шах
    board.push(move)
    if board.is_check():
        explanation.append("Этот ход ставит шах королю противника.")
    board.pop()

    # Проверка контроля центра
    if move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5]:
        explanation.append("Этот ход помогает контролировать центр доски, что дает стратегическое преимущество.")
    
    # Проверка развития фигур
    if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
        explanation.append("Этот ход развивает фигуру, что помогает подготовить атаку или улучшить защиту.")
    
    # Проверка силы позиций коней
    if piece and piece.piece_type == chess.KNIGHT and move.to_square in [chess.F3, chess.C3, chess.F6, chess.C6]:
        explanation.append("Кони на этих позициях особенно сильны, так как они контролируют важные поля.")
    
        # Проверка силы позиций ладей
    if piece and piece.piece_type == chess.ROOK and move.to_square in [chess.D1, chess.D8, chess.E1, chess.E8]:
        explanation.append("Ладьи особенно сильны на открытых линиях и в центре доски.")
    
    # Проверка силы позиций ферзя
    if piece and piece.piece_type == chess.QUEEN:
        explanation.append("Ферзь является самой мощной фигурой и на этой позиции он может угрожать многим фигурам противника.")
    
    # Проверка безопасности короля
    if piece and piece.piece_type == chess.KING:
        explanation.append("Этот ход улучшает безопасность вашего короля.")
    
    return " ".join(explanation)

def check_hint_click(x, y):
    return 8 * square_size <= x <= width and 0 <= y <= height

def ai_move(board, engine):
    try:
        result = engine.play(board, chess.engine.Limit(time=1.0))  # Время анализа 1 секунда
        move = result.move
        print(f"ИИ сделал ход: {move}")
        return move
    except Exception as e:
        print(f"Ошибка при получении хода ИИ: {e}")
        return None

# Основной игровой цикл
selected_square = None
running = True
show_best_move = False
best_move = None
explanation = ""
move_made = False
last_ai_move = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if check_hint_click(x, y):
                if not show_best_move:
                    best_move, score = get_best_move_for_player(board, engine)
                    if score is not None:
                        explanation = get_detailed_move_explanation(best_move, board)
                    else:
                        explanation = "Не удалось получить оценку хода."
                    show_best_move = True
                else:
                    show_best_move = False
            else:
                col = x // square_size
                row = y // square_size
                square = row * 8 + col
                if selected_square is None:
                    selected_square = square
                    print(f"Выбрана клетка: {square}")
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        # Проверка на превращение пешки
                        if board.piece_at(selected_square).piece_type == chess.PAWN and (square // 8 == 0 or square // 8 == 7):
                            move = chess.Move(selected_square, square, promotion=chess.QUEEN)
                        if move in board.legal_moves:
                            board.push(move)
                            print(f"Сделан ход: {move}")
                            print(f"Текущая позиция: {board.fen()}")
                            comment = comment_move(move, board)
                            move_made = True
                            selected_square = None
                            # Ход ИИ
                            ai_move_made = ai_move(board, engine)
                            if ai_move_made:
                                board.push(ai_move_made)
                                last_ai_move = ai_move_made
                                print(f"ИИ сделал ход: {ai_move_made}")
                                print(f"Текущая позиция после хода ИИ: {board.fen()}")
                                comment = comment_move(ai_move_made, board)
                                move_made = True
                                # Сброс отображения лучшего хода после хода ИИ
                                best_move = None
                                show_best_move = False
                            else:
                                print(f"Ошибка при выполнении хода ИИ")
                        else:
                            print(f"Неверный ход: {move}")
                    else:
                        # Обработка промоции пешки
                        if board.piece_at(selected_square) is not None and board.piece_at(selected_square).piece_type == chess.PAWN and (square // 8 == 0 or square // 8 == 7):
                            for promotion_piece in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                                move = chess.Move(selected_square, square, promotion=promotion_piece)
                                if move in board.legal_moves:
                                    board.push(move)
                                    print(f"Сделан ход: {move}")
                                    print(f"Текущая позиция: {board.fen()}")
                                    comment = comment_move(move, board)
                                    move_made = True
                                    break
                            else:
                                print(f"Неверный ход: {move}")
                        else:
                            print(f"Неверный ход: {move}")
                    selected_square = None

    draw_board()
    highlight_moves(board, selected_square)
    draw_pieces(board, selected_square)
    if move_made:
        display_comment(comment)
        move_made = False

    draw_dialog_box(show_best_move, best_move, explanation)

    if show_best_move and best_move:
        highlight_best_move(best_move)

    if last_ai_move:
        highlight_ai_move(last_ai_move)

    pygame.display.flip()

pygame.quit()
engine.quit()
sys.exit()


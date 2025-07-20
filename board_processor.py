import cv2
import numpy as np
import subprocess
import os
from functools import cmp_to_key

def show_detected_squares(squares):
    """
    squares: 偵測到的方框列表 [(x, y, w, h), ...]
    """
    max_x = max(x + w for x, y, w, h in squares)
    max_y = max(y + h for x, y, w, h in squares)
    
    # 創建黑色畫布
    img = np.zeros((max_y + 50, max_x + 50, 3), dtype=np.uint8)
    
    # 繪製每個方框
    for i, (x, y, w, h) in enumerate(squares):
        # 繪製綠色矩形框，線寬2
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # 在方框中間標註編號
        cv2.putText(img, str(i), (x + w//2 - 10, y + h//2 + 10 ), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
    
    # 顯示總方框數量
    text = f"Detected squares: {len(squares)}"
    cv2.putText(img, text, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # 自動縮放到適當大小（最大800像素）
    height, width = img.shape[:2]
    max_display_size = 800
    
    if max(height, width) > max_display_size:
        scale = max_display_size / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # 顯示圖片
    cv2.imshow('Detected Squares', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_chessboard_grid(image_path):
    """
    從輸入圖片中偵測棋盤格，並將每個格子的顏色轉換為整數編碼。
    回傳 (int_board, color_board)
    若偵測失敗則回傳 (None, None)
    """
    img = cv2.imread(image_path)
    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 使用自適應閾值+邊緣偵測
    blur0 = cv2.GaussianBlur(gray, (3, 3), 0)
    edges0 = cv2.Canny(blur0, 50, 100)

    # 使用自適應閾值+邊緣偵測
    blur1 = cv2.GaussianBlur(gray, (3, 3), 0)
    edges1 = cv2.Canny(blur1, 50, 100)
    #進行閉運算補齊裂縫
    kernel1 = np.ones((2, 2), np.uint8)
    edges1 = cv2.morphologyEx(edges1, cv2.MORPH_CLOSE, kernel1)

    blur2 = cv2.GaussianBlur(gray, (3, 3), 0)
    edges2 = cv2.Canny(blur2, 50, 100)
    #進行閉運算補齊裂縫
    kernel2 = np.ones((3, 3), np.uint8)
    edges2 = cv2.morphologyEx(edges2, cv2.MORPH_CLOSE, kernel2)

    # 找到所有輪廓
    # contours中的每個元素是一個輪廓，包含該輪廓的所有邊界點座標
    # 合併edges0, edges1, edges2
    contours0, _ = cv2.findContours(edges0, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours1, _ = cv2.findContours(edges1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(edges2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours0 + contours1 + contours2
    print(f"檢測到 {len(contours)} 條輪廓")

    # 過濾出方形輪廓
    squares = []
    for cnt in contours:
        rect = cv2.boundingRect(cnt)  #何形狀輪廓的最小外接矩形（邊與座標軸平行）
        x, y, w, h = rect
        area = cv2.contourArea(cnt)
        fill_ratio = area / (w * h)
        aspect_ratio = w / float(h)
        if fill_ratio > 0.85  and 0.7 < aspect_ratio < 1.3 and area > 100:
            squares.append(rect)

    if len(squares) == 0:
        return None, None
    
    #清除不符合條件的方形
    squares_by_area = sorted(squares, key=lambda rect: rect[2]*rect[3])
    unique_squares = []
    median_area = squares_by_area[len(squares_by_area)//2][2] * squares_by_area[len(squares_by_area)//2][3] 
    for rect in squares_by_area:
        x1, y1, w1, h1 = rect
        is_duplicate = False
        for unique_rect in unique_squares:
            x2, y2, w2, h2 = unique_rect
            center_dist = ((x1 + w1/2 - (x2 + w2/2))**2 + (y1 + h1/2 - (y2 + h2/2))**2)**0.5 # 計算兩個矩形中心點的距離
            if center_dist < min(w1, h1, w2, h2) * 0.2:  # 如果距離小於最小邊長的 20%
                is_duplicate = True
                break
        if not is_duplicate and median_area * 0.8 < w1 * h1 < median_area * 1.2: 
            unique_squares.append(rect)
    squares = unique_squares


    #按座標排序
    def cmp(a, b):
        threshold = a[3] * 0.3
        if abs(a[1] - b[1]) < threshold:  #y座標差距過小視為同一行
            return -1 if a[0] < b[0] else 1
        else:
            return -1 if a[1] < b[1] else 1
        
    #判斷棋盤邊界
    squares = sorted(squares, key=cmp_to_key(cmp))

    centers_x = [x + w//2 for x, y, w, h in squares]
    centers_y = [y + h//2 for x, y, w, h in squares]
    centers_x.sort()
    centers_y.sort()
    
    distance_x = 0
    distance_y = 0
    for i in range(len(squares)//2, len(squares)-2):
        if abs(squares[i][1] - squares[i+1][1]) < 0.3 * squares[i][3]:  # 如果同row
            distance_x = squares[i+1][0] - squares[i][0]  # 計算相鄰兩個方框的距離
        else: # 如果不同row
            distance_y = squares[i+1][1] - squares[i][1]
        if distance_x != 0 and distance_y != 0:
            break
    estimated_grid_size = int(len(squares) ** 0.5)
    
    min_x = centers_x[len(centers_x)//2] - (estimated_grid_size//2 + 0.2) * distance_x
    max_x = centers_x[len(centers_x)//2] + (estimated_grid_size//2 + 0.2) * distance_x
    min_y = centers_y[len(centers_y)//2] - (estimated_grid_size//2 + 0.2) * distance_y
    max_y = centers_y[len(centers_y)//2] + (estimated_grid_size//2 + 0.2) * distance_y
    
    # 過濾在邊界範圍外的方框
    in_border_squares = []
    for rect in squares:
        x, y, w, h = rect
        center_x, center_y = x + w//2, y + h//2
        if min_x <= center_x <= max_x and min_y <= center_y <= max_y:
            in_border_squares.append(rect) 
    squares = in_border_squares

    # 按照 y 座標排序，然後按照 x 座標排序
    squares = sorted(squares, key=cmp_to_key(cmp))

    # 嘗試建立 5~12 的格數二維陣列
    board = None
    color_board = None
    if len(squares) in (5**2, 6**2, 7**2, 8**2, 9**2, 10**2, 11**2, 12**2):
        grid_size = int(len(squares) ** 0.5)
        board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        color_board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        for i, (x, y, w, h) in enumerate(squares):
            cx, cy = x + w // 4, y + h // 7
            color = original[cy, cx]  #在方塊左上角提取顏色
            board[i // grid_size][i % grid_size] = color.tolist()
            color_board[i // grid_size][i % grid_size] = color.tolist()
    
    if board is None:
        return None, None
    
    #將BGR顏色映射到整數
    all_colors = []
    for i in range(grid_size):
        for j in range(grid_size):
            is_duplicate = False
            for color in all_colors:
                #如果顏色很相近視為同一種顏色
                if abs(board[i][j][0]-color[0]) + abs(board[i][j][1]-color[1]) + abs(board[i][j][2]-color[2]) < 20:
                    board[i][j][0] = color[0]
                    board[i][j][1] = color[1]
                    board[i][j][2] = color[2]
                    is_duplicate = True
                    break
            if not is_duplicate:
                all_colors.append(tuple(board[i][j]))
    color_to_int = {color: idx for idx, color in enumerate(all_colors)}
    int_board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    for i in range(grid_size):
        for j in range(grid_size):
            color = tuple(board[i][j])
            int_board[i][j] = color_to_int[color]

    return int_board, color_board

def solve_with_cpp(int_board):
    """
    呼叫 C++ 程式，將 int_board 傳給 C++，取得所有解答。
    回傳anser_board，每個元素為一組解答的棋盤
    若無解或發生錯誤則回傳 None
    """

    # 檢查 solver 是否已編譯
    solver_engine_exe = "solver_engine.exe" if os.name == 'nt' else "./solver_engine"
    if not os.path.exists(solver_engine_exe):
        print("編譯 C++ 解題程序...")
        compile_cmd = "g++ solver_engine.cpp -o solver_engine"
        subprocess.run(compile_cmd, shell=True, check=True)
    
    # 準備輸入數據
    input_data = f"{len(int_board)}\n"  # 棋盤大小
    for i in range(len(int_board)):
        for j in range(len(int_board[i])):
            input_data += f"{int_board[i][j]} "
        input_data += "\n"
    
    # 執行解題程序並傳入棋盤數據
    process = subprocess.Popen(
        solver_engine_exe, 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 發送輸入並獲取輸出
    stdout, stderr = process.communicate(input=input_data)
    
    if stderr:
        print(f"執行C++程式時發生錯誤: {stderr}")
        return None
    
    lines = stdout.strip().split("\n")  # 按行分割
    if "no anser" in lines[0]:
        return None
    
    anser_count = len(lines)//len(int_board)
    anser_board = [[] for _ in range(anser_count)]
    for i in range(anser_count):
        for j in range(len(int_board)):
            anser_board[i].append([int(x) for x in lines[i*len(int_board)+j].split()])

    #[i][j][k] 第i組解答的第j row 第k column
    return anser_board

def draw_solution_with_crowns(board, color_board, output_path="solution_with_crowns.png"):
    """
    在原始棋盤圖案 (color_board) 上繪製解答，將 board 中值為 113 的位置標記為圓形皇冠，並在每個方格之間添加黑框。
    
    board: 解答棋盤 (list of list of int)
    color_board: 原始棋盤圖案 (list of list of [B, G, R])
    output_path: 保存圖像的路徑
    """

    # 獲取棋盤大小
    board_size = len(board)
    cell_size = 500 // board_size  # 每個格子的大小
    image_size = cell_size * board_size  # 圖像大小為 500*500

    # 創建圖像，基於 color_board 填充顏色
    img = np.zeros((image_size, image_size, 3), dtype=np.uint8)
    for i in range(board_size):
        for j in range(board_size):
            # 計算格子的左上角和右下角座標
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            
            # 確保不超出邊界
            x2 = min(x2, image_size-1)
            y2 = min(y2, image_size-1)

            # 填充格子顏色
            color = color_board[i][j]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)

            # 繪製黑框
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 1)

    # 繪製皇冠 (board 中值為 113 的位置)
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == 113:
                # 計算格子中心點
                cx, cy = j * cell_size + cell_size // 2, i * cell_size + cell_size // 2
                
                # 繪製圓形皇冠
                crown_radius = cell_size // 4
                cv2.circle(img, (cx, cy), crown_radius, (0, 215, 255), -1)  # 金黃色圓形
                cv2.circle(img, (cx, cy), crown_radius - 5, (0, 0, 0), 2)  # 黑色邊框

    # 保存圖像
    cv2.imwrite(output_path, img)
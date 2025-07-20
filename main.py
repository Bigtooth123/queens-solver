from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from board_processor import detect_chessboard_grid, solve_with_cpp, draw_solution_with_crowns
import os
import glob
import datetime
import uuid
import socket
import uvicorn

def generate_unique_file_id():
    """生成唯一檔案ID，並檢查重複"""
    max_attempts = 10
    
    for i in range(max_attempts):
        file_id = str(uuid.uuid4())[:8]
        
        # 檢查 uploads 資料夾中是否已存在
        existing_files = glob.glob(f"uploads/*{file_id}*")
        
        if not existing_files:
            return file_id
    
    # 如果10次都重複，使用完整UUID確保唯一
    print("多次重複，使用完整UUID")
    return str(uuid.uuid4()).replace('-', '')

def get_private_ip():
    """獲取本機私有IP地址"""
    try:
        # 創建一個 socket 連接到外部地址
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        private_ip = sock.getsockname()[0]
        sock.close()
        return private_ip
    except Exception:
        return "127.0.0.1"
    
app = FastAPI(title="Queens Solver API", description="N-Queens問題求解器")

# 確保必要資料夾存在
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

@app.post("/upload")
async def upload_and_solve(file: UploadFile = File(...)):
    """處理圖片上傳並求解Queens問題"""
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n\n[{current_time}] 收到新的求解請求: {file.filename}")
        
        # 檢查檔案類型
        if not file.content_type.startswith("image/"):
            return JSONResponse({
                "success": False,
                "message": "請上傳圖片檔案 (PNG, JPG, JPEG)",
                "result_images": [],
                "timestamp": current_time
            })
        
        # 生成唯一檔案名
        file_id = generate_unique_file_id()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存上傳的圖片
        file_extension = os.path.splitext(file.filename)[1].lower()
        if not file_extension:
            file_extension = ".png"
        
        input_filename = f"input_{timestamp}_{file_id}{file_extension}"
        input_path = os.path.join("uploads", input_filename)
        
        # 儲存檔案
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"圖片已保存到: {input_path}")
        
        #只保留100個上傳的圖片
        upload_files = glob.glob("uploads/*")
        if len(upload_files) > 100:
            upload_files.sort(key=os.path.getctime)
            for old_file in upload_files[:len(upload_files)-100]:
                try:
                    os.remove(old_file)
                except:
                    pass

        # 只保留1000個結果
        result_files = glob.glob("results/result_*.png")
        if len(result_files) > 1000:
            result_files.sort(key=os.path.getctime)
            for old_file in result_files[:len(result_files)-1000]:
                try:
                    os.remove(old_file)
                except:
                    pass
        
        # 準備輸出檔名
        filename_prefix = f"result_{timestamp}_{file_id}"
        
        print(f"開始求解...")
        board, color_board = detect_chessboard_grid(input_path)
        if board is None:
            print("未能識別棋盤格")
            return JSONResponse({
                "success": False,
                "message": "未能識別棋盤格，請確認圖片中包含清晰的方格棋盤",
                "result_images": [],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        print(f"棋盤偵測成功: {len(board)}x{len(board[0])}")
        
        print("執行 C++ 解題程序...")
        anser_board = solve_with_cpp(board)
        
        if anser_board is None:
            print("此棋盤配置無解")
            return JSONResponse({
                "success": False,
                "message": "此棋盤配置無解，請嘗試其他棋盤",
                "result_images": [],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        print(f"求解成功，共找到 {len(anser_board)} 組解答")
        
        # 生成結果圖片
        result_images = []
        for i in range(len(anser_board)):
            output_filename = f"{filename_prefix}_{i+1}.png"
            output_path = os.path.join("results", output_filename)
            
            draw_solution_with_crowns(
                anser_board[i], 
                color_board, 
                output_path=output_path
            )
            
            # 建立可存取的 URL
            result_url = f"/results/{output_filename}"
            result_images.append(result_url)
            print(f"解答 {i+1} 已保存: {output_path}")
        
        return JSONResponse({
            "success": True,
            "message": f"成功找到 {len(anser_board)} 個解答！",
            "result_images": result_images,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })        
        
    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": f"伺服器錯誤: {str(e)}",
            "result_images": [],
            "timestamp": current_time
        })

# 掛載圖片
app.mount("/results", StaticFiles(directory="results"), name="results")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 靜態檔案
app.mount("/", StaticFiles(directory="static", html=True), name="static")
    
if __name__ == "__main__":
    private_ip = get_private_ip()
    print(f"本地訪問: http://localhost")
    print(f"本地訪問: http://127.0.0.1")
    print(f"區域網路: http://{private_ip}")
    print("=" * 50)
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=80,
        reload=False,
        access_log=True
    )
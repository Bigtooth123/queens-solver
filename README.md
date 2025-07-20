# Queens Solver

Queens Solver is a web application that solves the Queens game on a colored chessboard from an uploaded image. It automatically detects the chessboard grid in the image, processes the board, and finds all possible solutions.

## Features

- Upload an image containing a colored chessboard and automatically detect the chessboard grid using OpenCV.
- Solves Queens problem using a C++ engine.
- Displays all possible solutions visually on the web interface.

## Queens Game Rules

- Each row, each column, and each color block must contain exactly one queen.
- Queens cannot be placed on adjacent squares, even diagonally.

## Project Structure

- `main.py`: FastAPI backend server.
- `board_processor.py`: Image processing and solver integration.
- `solver_engine.cpp`: N-Queens solver for colored chessboards.
- `static/`: Frontend files (HTML, CSS, JS).
- `uploads/`: Uploaded images (auto-created).
- `results/`: Generated solution images (auto-created).

## Setup & Run

1. **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the server:**
    ```sh
    python main.py
    ```

3. **Access the web UI:**
    - Open your browser and go to `http://127.0.0.1`(local) or your LAN IP. (Accessible from other networks if publicly available.)

4. **Usage:**
    - Upload an image containing chessboard.
    - Click the solve button.
    - View all possible solutions with result images.

## Notes

- The C++ solver will be compiled automatically if not present. Make sure you have a C++ compiler installed on your system.
- Supported board sizes: 5x5 to 12x12.

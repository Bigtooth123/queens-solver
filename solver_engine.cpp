#include <bits/stdc++.h>

using namespace std;

//at most have 12 color from 0 to 11
int board[12][12];
bool color[12] = {false, false, false, false, false, false, false, false, false, false, false, false};
bool find_ans = false;

bool is_ok(int row, int col, int board_size){
    for(int i = 0; i < board_size; i++){
        if(board[row][i] == 'q'){
            return false;
        }
        if(board[i][col] == 'q'){
            return false;
        }
    }
    if(color[board[row][col]] == true){
        return false;
    }
    if(row+1 < board_size && col+1 < board_size && board[row+1][col+1] == 'q'){
        return false;
    }
    if(row+1 < board_size && col-1 >= 0 && board[row+1][col-1] == 'q'){
        return false;
    }
    if(row-1 >= 0 && col+1 < board_size && board[row-1][col+1] == 'q'){
        return false;
    }
    if(row-1 >= 0 && col-1 >= 0 && board[row-1][col-1] == 'q'){
        return false;
    }

    return true;
}

void queens(int row, int board_size){
    if(row == board_size){
        for(int i = 0; i < board_size; i++){
            for(int j = 0; j < board_size; j++){
                cout << board[i][j] << " ";
            }
            cout << "\n";
        }
        find_ans = true;
        return;
    }
    for(int col = 0; col < board_size; col++){
        if(is_ok(row, col, board_size)){
            int temp = board[row][col];
            color[temp] = true;
            board[row][col] = 'q';
            queens(row+1, board_size);
            color[temp] = false;
            board[row][col] = temp;
        }
    }
}

int main(){
    int board_size;
    cin >> board_size;
    int num_of_color = 0;
    for(int i = 0; i < board_size; i++) {
        for(int j = 0; j < board_size; j++) {
            cin >> board[i][j];
            if(board[i][j] > num_of_color){
                num_of_color = board[i][j];
            }
        }
    }

    if(num_of_color+1 != board_size){
        cout << "no anser";
        return 0;
    }

    queens(0, board_size);

    if(find_ans == false){
        cout << "no anser";
    }
    
    return 0;
}
import tkinter as tk
import string
import os, sys
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

class Board(tk.Frame):

    def __init__(self, parent, length, width):
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.length = length
        self.width = width
        self.config(height=100*self.length, width=100*self.width)
        self.pack()
        
        self.square_color = None
        self.squares = {}
        self.ranks = string.ascii_lowercase
        self.white_images = {}
        self.black_images = {}
        self.white_pieces = ["pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7"]
        self.black_pieces = ["pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"]
        self.buttons_pressed = 0
        self.turns = 0
        self.sq1 = None
        self.sq2 = None 
        self.sq1_button = None
        self.sq2_button = None
        self.piece_color = None
        self.wk_moved = False
        self.bk_moved = False
        self.wr1_moved = False
        self.wr2_moved = False
        self.br1_moved = False
        self.br2_moved = False
        self.castled = False
        self.set_squares()

    def select_piece(self, button):
        if button["image"] in self.white_pieces and self.buttons_pressed == 0:
            self.piece_color = "white"
        elif button["image"] in self.black_pieces and self.buttons_pressed == 0:
            self.piece_color = "black"      
        
        if (self.piece_color == "white" and self.turns % 2 == 0) or (self.piece_color == "black" and self.turns % 2 == 1) or self.buttons_pressed == 1:
            if self.buttons_pressed == 0:
                self.sq1 = list(self.squares.keys())[list(self.squares.values()).index(button)]
                self.sq1_button = button
                self.buttons_pressed += 1
             
            elif self.buttons_pressed==1:
                self.sq2 = list(self.squares.keys())[list(self.squares.values()).index(button)]
                self.sq2_button = button
                if self.sq2 == self.sq1:
                    self.buttons_pressed = 0
                    return
                
                if self.allowed_piece_move() and self.friendly_fire() == False:
                    prev_sq1 = self.sq1
                    prev_sq1_button_piece = self.sq1_button["image"]
                    prev_sq2 = self.sq2
                    prev_sq2_button_piece = self.sq2_button["image"]
                    self.squares[self.sq2].config(image=self.sq1_button["image"])
                    self.squares[self.sq2].image = self.sq1_button["image"]
                    self.squares[self.sq1].config(image=self.white_images["blank.png"])
                    self.squares[self.sq1].image = self.white_images["blank.png"]
                    if  self.in_check() == True and self.castled == False:
                        self.squares[prev_sq2].config(image=prev_sq2_button_piece)
                        self.squares[prev_sq2].image = prev_sq2_button_piece
                        self.squares[prev_sq1].config(image=prev_sq1_button_piece)
                        self.squares[prev_sq1].image = prev_sq1_button_piece
                        self.buttons_pressed = 0
                        return
                    else:
                        if prev_sq1_button_piece == "pyimage3":
                            self.wk_moved = True
                        if prev_sq1_button_piece == "pyimage10":
                            self.bk_moved = True
                        if prev_sq1_button_piece == "pyimage7" and prev_sq1 == "a1":
                            self.wr1_moved = True
                        if prev_sq1_button_piece == "pyimage7" and prev_sq1 == "h1":
                            self.wr2_moved = True
                        if prev_sq1_button_piece == "pyimage14" and prev_sq1 == "a8":
                            self.br1_moved = True
                        if prev_sq1_button_piece == "pyimage14" and prev_sq1 == "h8":
                            self.br2_moved = True
                        self.buttons_pressed = 0
                        self.turns += 1                     
                        if (button["image"] == "pyimage5" and prev_sq2.count("8")==1) or (button["image"] == "pyimage12" and prev_sq2.count("1")==1):
                            self.promotion_menu(self.piece_color)
                        self.castled = False
        else:
            self.buttons_pressed = 0
            return

    def promotion_menu(self, color):
        def return_piece(piece):
            self.squares[self.sq2].config(image=piece)
            self.squares[self.sq2].image = piece
            promo.destroy()
            return
        
        promo = tk.Tk()
        promo.title("Choose what to promote your pawn to")
        if color=="white":
            promo_knight = tk.Button(promo, text="Knight", command=lambda: return_piece("pyimage4"))
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(promo, text="Bishop", command=lambda: return_piece("pyimage1"))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(promo, text="Rook", command=lambda: return_piece("pyimage7"))
            promo_rook.grid(row=1, column=0)
            promo_queen = tk.Button(promo, text="Queen", command=lambda: return_piece("pyimage6"))
            promo_queen.grid(row=1, column=1)
        elif color=="black":
            promo_knight = tk.Button(promo, text="Knight", command=lambda: return_piece("pyimage11"))
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(promo, text="Bishop", command=lambda: return_piece("pyimage8"))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(promo, text="Rook", command=lambda: return_piece("pyimage14"))
            promo_rook.grid(row=1, column=0)
            promo_queen = tk.Button(promo, text="Queen", command=lambda: return_piece("pyimage13"))
            promo_queen.grid(row=1, column=1)
        promo.mainloop()
        return
            
    def friendly_fire(self):
        piece_2_color = self.sq2_button["image"]
        if self.piece_color == "white" and piece_2_color in self.white_pieces:
            return True
        if self.piece_color == "black" and piece_2_color in self.black_pieces:
            return True
        else:
            return False
        
    def clear_path(self, piece):
        if piece == "rook" or piece == "queen":   
            if self.sq1[0] == self.sq2[0]:
                pos1 = min(int(self.sq1[1]), int(self.sq2[1]))
                pos2 = max(int(self.sq1[1]), int(self.sq2[1]))
                for i in range(pos1+1, pos2):
                    square_on_path = self.squares[self.sq1[0]+str(i)].cget("image")
                    if square_on_path != "pyimage2":
                        return False
                    
            elif self.sq1[1] == self.sq2[1]:
                pos1 = min(self.ranks.find(self.sq1[0]), self.ranks.find(self.sq2[0]))
                pos2 = max(self.ranks.find(self.sq1[0]), self.ranks.find(self.sq2[0]))

                for i in range(pos1+1, pos2):
                    square_on_path = self.squares[self.ranks[i]+self.sq1[1]].cget("image")
                    if square_on_path != "pyimage2":
                        return False
                    
        if piece == "bishop" or piece == "queen":
            x1 = self.ranks.find(self.sq1[0])
            x2 = self.ranks.find(self.sq2[0])
            y1 = int(self.sq1[1])
            y2 = int(self.sq2[1])
            
            if  y1<y2:
                if x1<x2:
                    for x in range(x1+1, x2):
                        y1 += 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
                elif x1>x2:
                    for x in range(x1-1, x2, -1):
                        y1 += 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
            elif y1>y2:
                if x1<x2:
                    for x in range(x1+1, x2):
                        y1 -= 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
                if x1>x2:
                    for x in range(x1-1, x2, -1):
                        y1 -= 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
        return True
                
        
    def allowed_piece_move(self):
        wb, wk, wn, wp, wq, wr = "pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7"
        bb, bk, bn, bp, bq, br = "pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"

        if self.sq1_button["image"] == "pyimage2" or self.sq1_button["image"] == "pyimage9":
            return False
        
        if (self.sq1_button["image"] == wb or self.sq1_button["image"] == bb) and self.clear_path("bishop"):
            if abs(int(self.sq1[1]) - int(self.sq2[1])) == abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])):
                return True

        if self.sq1_button["image"] == wn or self.sq1_button["image"] == bn:
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) == 2) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 1):
                return True
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) == 1) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 2):
                return True
        
        if self.sq1_button["image"] == wk or self.sq1_button["image"] == bk:
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) < 2) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0]))) < 2:
                return True
            if self.castle() is True:
                return True
        
        if self.sq1_button["image"] == wp:
            if "2" in self.sq1:
                if (int(self.sq1[1])+1 == int(self.sq2[1]) or int(self.sq1[1])+2 == int(self.sq2[1])) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2":
                    in_front = self.squares[self.sq1[0] + str(int(self.sq1[1])+1)]
                    if in_front["image"] == "pyimage2":
                        return True
            if int(self.sq1[1])+1 == int(self.sq2[1]) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2":
                    return True
            if int(self.sq1[1])+1 == int(self.sq2[1]) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0]))) == 1 and self.sq2_button["image"] != "pyimage2":
                    return True

                
        if self.sq1_button["image"] == bp:
            if "7" in self.sq1:
                if (int(self.sq1[1]) == int(self.sq2[1])+1 or int(self.sq1[1]) == int(self.sq2[1])+2) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2":
                    return True
            if int(self.sq1[1]) == int(self.sq2[1])+1 and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2":
                    return True
            if int(self.sq1[1]) == int(self.sq2[1])+1 and abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 1 and self.sq2_button["image"] != "pyimage2":
                    return True

        if (self.sq1_button["image"] == wq or self.sq1_button["image"] == bq) and self.clear_path("queen"):
            if int(self.sq1[1]) == int(self.sq2[1]) or self.sq1[0] == self.sq2[0]:
                return True
            if abs(int(self.sq1[1]) - int(self.sq2[1])) == abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])):
                return True
        
        if self.sq1_button["image"] == wr or self.sq1_button["image"] == br:
            if (int(self.sq1[1]) == int(self.sq2[1]) or self.sq1[0] == self.sq2[0]) and self.clear_path("rook"):
                return True  
        return False
    
    def castle(self):
        if self.wk_moved == False:
            if self.wr1_moved == False and self.sq2 == "c1":
                for x in range(1,4):
                    square_button = self.squares[self.ranks[x]+str(1)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["a1"].config(image="pyimage2")
                    self.squares["a1"].image = "pyimage2"
                    self.squares["d1"].config(image="pyimage7")
                    self.squares["d1"].image = ("pyimage7")
                    self.castled = True
                    return True
            if self.wr2_moved == False and self.sq2 == "g1":
                for x in range(5,7):
                    square_button = self.squares[self.ranks[x]+str(1)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["h1"].config(image="pyimage2")
                    self.squares["h1"].image = "pyimage2"
                    self.squares["f1"].config(image="pyimage7")
                    self.squares["f1"].image = ("pyimage7")
                    self.castled = True
                    return True
        if self.bk_moved == False:
            if self.br1_moved == False and self.sq2 == "c8":
                for x in range(1,3):
                    square_button = self.squares[self.ranks[x]+str(8)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["a8"].config(image="pyimage2")
                    self.squares["a8"].image = "pyimage2"
                    self.squares["d8"].config(image="pyimage14")
                    self.squares["d8"].image = ("pyimage14")
                    self.castled = True
                    return True
            if self.br2_moved == False and self.sq2 == "g8":
                for x in range(5,7):
                    square_button = self.squares[self.ranks[x]+str(8)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["h8"].config(image="pyimage2")
                    self.squares["h8"].image = "pyimage2"
                    self.squares["f8"].config(image="pyimage14")
                    self.squares["f8"].image = ("pyimage14")
                    self.castled = True
                    return True
        else:
            return False
   
        self.bk_moved = False
        self.wr1_moved = False
        self.wr2_moved = False
        self.br1_moved = False
        self.br2_moved = False

    def in_check(self):
        previous_sq1 = self.sq1
        previous_sq1_button = self.sq1_button
        previous_sq2 = self.sq2
        previous_sq2_button = self.sq2_button
        
        def return_previous_values():
            self.sq1 = previous_sq1
            self.sq1_button = previous_sq1_button
            self.sq2 = previous_sq2
            self.sq2_button = previous_sq2_button
            
        if self.piece_color == "white":
            self.sq2 = self.find_king("pyimage3")
            for key in self.squares:
                self.sq1 = key
                self.sq1_button = self.squares[self.sq1]
                if self.sq1_button["image"] in self.black_pieces:
                    if self.allowed_piece_move():
                        return True
        if self.piece_color == "black":
            self.sq2 = self.find_king("pyimage10")
            for key in self.squares:
                self.sq1 = key
                self.sq1_button = self.squares[self.sq1] 
                if self.sq1_button["image"] in self.white_pieces:
                    if self.allowed_piece_move():
                        return True
        return_previous_values()
        return False
    
    def find_king(self, king):
        for square  in self.squares:
            button = self.squares[square]
            if button["image"] == king:
                return square
    
    def set_squares(self):

        for x in range(8):
            for y in range(8):
                if x%2==0 and y%2==0:
                    self.square_color="tan4" 
                elif x%2==1 and y%2==1:
                    self.square_color="tan4"
                else:
                    self.square_color="burlywood1"
                    
                B = tk.Button(self, bg=self.square_color, activebackground="lawn green")
                B.grid(row=8-x, column=y)
                pos = self.ranks[y]+str(x+1)
                self.squares.setdefault(pos, B)
                self.squares[pos].config(command= lambda key=self.squares[pos]: self.select_piece(key))               
        
    def import_pieces(self):
        path = os.path.join(os.path.dirname(__file__), "White")
        w_dirs = os.listdir(path)
        for file in w_dirs:
            img = Image.open(path+"\\"+file)
            img = img.resize((80,80), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image=img)
            self.white_images.setdefault(file, img)

        path = os.path.join(os.path.dirname(__file__), "Black")
        b_dirs = os.listdir(path)
        for file in b_dirs:
            img = Image.open(path+"\\"+file)
            img = img.resize((80,80), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image=img)
            self.black_images.setdefault(file, img)

    def set_pieces(self):
        dict_rank1_pieces = {"a1":"r.png", "b1":"n.png", "c1":"b.png", "d1":"q.png", "e1":"k.png", "f1":"b.png", "g1":"n.png", "h1":"r.png"}
        dict_rank2_pieces = {"a2":"p.png", "b2":"p.png", "c2":"p.png", "d2":"p.png", "e2":"p.png", "f2":"p.png", "g2":"p.png", "h2":"p.png"}     
        dict_rank7_pieces = {"a7":"p.png", "b7":"p.png", "c7":"p.png", "d7":"p.png", "e7":"p.png", "f7":"p.png", "g7":"p.png", "h7":"p.png"}
        dict_rank8_pieces = {"a8":"r.png", "b8":"n.png", "c8":"b.png", "d8":"q.png", "e8":"k.png", "f8":"b.png", "g8":"n.png", "h8":"r.png"}

        for key in dict_rank1_pieces:
            starting_piece = dict_rank1_pieces[key]
            self.squares[key].config(image=self.white_images[starting_piece])
            self.squares[key].image = self.white_images[starting_piece]
            
        for key in dict_rank2_pieces:
            starting_piece = dict_rank2_pieces[key]
            self.squares[key].config(image=self.white_images[starting_piece])
            self.squares[key].image = self.white_images[starting_piece]
            
        for key in dict_rank7_pieces:
            starting_piece = dict_rank7_pieces[key]
            self.squares[key].config(image=self.black_images[starting_piece])
            self.squares[key].image = self.black_images[starting_piece]
            
        for key in dict_rank8_pieces:
            starting_piece = dict_rank8_pieces[key]
            self.squares[key].config(image=self.black_images[starting_piece])
            self.squares[key].image = self.black_images[starting_piece]

        for rank in range(3,7):
            for file in range(8):
                starting_piece = "blank.png"
                pos = self.ranks[file]+str(rank)
                self.squares[pos].config(image=self.white_images[starting_piece])
                self.squares[pos].image = self.white_images[starting_piece]

root = tk.Tk()
root.geometry("1960x1080")
board = Board(root, 8, 8)
board.import_pieces()
board.set_pieces()
board.mainloop()
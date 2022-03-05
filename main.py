import tkinter as tk
import array as arr
import time
import random as rd
import json
from tkinter import font
class Minesweeper():
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.configure(background='grey')
        self.buttonFrame = tk.Frame(self.root)
        self.buttonFrame.grid(row=1,column=0,columnspan=6)
        self.buttonFrame.configure(background="grey", padx=5, pady=5)
        self.startButton = tk.Button(self.buttonFrame, text="Start New game", command=self.initGame, bg="lightgrey",) # Boutton pour commencer le jeu
        self.levelButton = tk.Button(self.buttonFrame, text="Difficulity", command=self.chooseDifficulty,bg="lightgrey") # Boutton pour ouvrir une fenetre pour selectionner le niveau du jeu
        self.saveToJsonButton = tk.Button(self.buttonFrame, text="saveToJson", command=self.saveToJson, bg="lightgrey") #Boutton pour sauvegarder les données (on les sauvegarde sous format JSON)
        self.loadFromJsonButton = tk.Button(self.buttonFrame, text="loadFromJson", command=self.loadFromJson,bg="lightgrey") # Boutton pour charger les données à partir d'un fichier json
        self.showScore = tk.Button(self.buttonFrame, text="Score board", command=self.showScoreBoard, bg="black",fg="white")
        self.isGameOver = True
        self.flagPhoto = tk.PhotoImage(file=r'assets/flag_logo.gif')
        self.bombPhoto = tk.PhotoImage(file=r'assets/bomb.gif')
        self.username = ''
        self.rectWidth = 20
        self.rectHeight = 20
        self.userLastName = ''
        self.currentDifficulty = 4
        #Des scores juste pour les tests, on peut commencer le jeu sans aucun score.
        self.topScores = [
            [('Test', 'Nom', 6, 1), ('Test2', 'Nom2', 6, 20), ('Test3', 'Nom5', 4, 20), ('Test2z', 'Nom287', 3, 300),
             ('Test2997', 'Nom299', 1, 300)], [],[],[],[]]
        self.isTopScorer = False
        self.levelWindow = None
        self.maxTopScoreBoardLength = 5
        self.startButton.grid(row=0, column=0, padx=5, pady=5)
        self.levelButton.grid(row=0, column=1, padx=5, pady=5)
        self.showScore.grid(row=0, column=2, padx=5, pady=5)
        self.saveToJsonButton.grid(row=0, column=3, padx=5, pady=5)
        self.loadFromJsonButton.grid(row=0, column=4, padx=5, pady=5)
        self.rows = 25
        self.columns = 50
        self.setExtremeDiff()
        # self.levelsCanvas = Canvas(self.root, )
        # self.canvas = tk.Canvas(self.root, width=1040,
        #                         height=540, highlightthickness=0)
        self.canvas = tk.Canvas(self.root, width=self.columns * self.rectWidth,
                                height=self.rows * self.rectHeight, highlightthickness=0)
        self.drawMineSweeper()
        self.canvas.grid(row=2,column=0,pady=2)
           
        self.root.mainloop()
    def loadFromJson(self):
        self.isGameOver = True
        json_object = {}
        with open('sample.json', 'r') as openfile:
            json_object = json.load(openfile)
        self.isGameOver =  json_object['isGameOver']
        self.positionsMines =  json_object['positionsMines']
        self.positionDrapeaux =  json_object['positionDrapeaux']
        self.casesCreuses =  json_object['casesCreuses']
        self.numberOfMines =  json_object['numberOfMines']
        self.nbVoisins =  json_object['nbVoisins']
        self.currentDifficulty =  json_object['currentDifficulty']
        self.maxTopScoreBoardLength =  json_object['maxTopScoreBoardLength']
        self.counter =  json_object['counter']
        self.score =  json_object['score']
        self.isTopScorer =  json_object['isTopScorer']
        self.topScores =  json_object['topScores']
        self.startGame()
        if(self.isGameOver):
            self.runGameOver()
        
    def closeLevelWindow(self):
        if(self.levelWindow != None):
            self.levelWindow.destroy()
            
    def setEasyDiff(self):
        # Difficulté facile > 100 mines pour placer
        self.numberOfMines=100
        self.currentDifficulty = 0
        print('current Diff: ', self.currentDifficulty)
        self.closeLevelWindow()
        
    def setNormalDiff(self):
        # Difficulté moyenne > 125 mines pour placer
        self.numberOfMines=125
        self.currentDifficulty = 1
        print('current Diff: ', self.currentDifficulty)
        self.closeLevelWindow()

    def setIntermediateDiff(self):
        # Difficulté intermediaire > 150 mines pour placer
        self.numberOfMines=150
        self.currentDifficulty = 2
        print('current Diff: ', self.currentDifficulty)
        self.closeLevelWindow()

    def setHardDiff(self):
        # Difficulté: difficile > 175 mines pour placer
        self.numberOfMines=175
        self.currentDifficulty = 3
        print('current Diff: ', self.currentDifficulty)
        self.closeLevelWindow()

    def setExtremeDiff(self):
        # Difficulté: Extreme > 300 mines pour placer
        self.numberOfMines=300
        self.currentDifficulty = 4
        print('current Diff: ', self.currentDifficulty)
        self.closeLevelWindow()
    def chooseDifficulty(self):
        self.levelWindow = tk.Toplevel(self.root)
        self.levelWindow.geometry("150x125")
        self.levelWindow.title("Choisir difficulté")
        tk.Button(self.levelWindow,bg="limegreen",text="Facile",width="150",fg="white", command=self.setEasyDiff).pack()
        tk.Button(self.levelWindow,bg="white",text="Normale",width="150",fg="black",command=self.setNormalDiff).pack()
        tk.Button(self.levelWindow,bg="yellow",text="Intermédiare",width="150",command=self.setIntermediateDiff).pack()
        tk.Button(self.levelWindow,bg="orange",text="Difficile",width="150",command=self.setHardDiff).pack()
        tk.Button(self.levelWindow,bg="red",text="Extreme",width="150",command=self.setExtremeDiff).pack()
        
    def calculateScore(self):
        self.score = 0
        for x in range(self.columns):
            for y in range(self.rows):
                if(self.positionDrapeaux[x][y] == 1 and self.positionsMines[x][y] == 1):
                    self.score+=1
    def randomizeBombPositions(self,count):
        # randomize les places des mines à l'aide de randrange. le paramètre count represente la ddifficuté (le nombre de mines qu'on a choisi)
        for x in range(count):
            randCol = rd.randrange(0,self.columns)
            randRow = rd.randrange(0,self.rows)
            self.positionsMines[randCol][randRow] = 1            
    def launchInputNameWindow(self):
        # lance une fenetre pour saisir le nom.Ceci ne se declanche que lorsque le joueur est un top scorer, ou la table de score n'est pas pleine.
        self.inputNameWindow = tk.Toplevel(self.root)
        self.inputNameWindow.title("Top Scores")
        inputText = tk.Text(self.inputNameWindow, height=5, width=10)
        inputText.pack()
        
    def creuserVoisin(self,col,row):
        #Cette methode permet de creuser les voisins automatiquement.
        aCreuser = set() # 
        aCreuser.add((col,row, self.nbVoisins[col][row]))
        blacklist = set() 
        dx = 0
        dy = 0
        #On creuse les cases adjascents à la case (col,row) d'une place,
        # ensuite, si une case a 0 voisins,
        # on l'ajoute à une liste pour faire le meme travail sur cette case,
        # si une case adjascente à nbVoisin > 0, 
        # on la creuse uniquement (il n'est pas ajouté à la liste pour le creusement)
        while len(aCreuser) > 0:
            item = aCreuser.pop()
            # done.add(item)
            if(item[2] > 0) or (item[0],item[1]) in blacklist:
                continue
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if 0<=item[0]+dx<self.columns and 0<=item[1]+dy <self.rows:
                        if self.nbVoisins[item[0]+dx][item[1]+dy] == 0 and self.positionsMines[item[0]+dx][item[1]+dy] == 0:
                            self.marquerCreuse(item[0] + dx, item[1] + dy)
                            aCreuser.add((item[0]+dx,item[1]+dy,self.nbVoisins[item[0]+dx][item[1]+dy]))
                            #On creuse les cases ajascent à l'aire de la boucle
                        elif self.nbVoisins[item[0]+dx][item[1]+dy] > 0 and self.positionsMines[item[0]+dx][item[1]+dy] == 0:
                            self.marquerCreuse(item[0] + dx, item[1] + dy)
                        else:
                            continue
                            # pour ne pas ajouter la meme case plusieurs fois pour la traiter, on l'ajoute à la list blacklist(set)
            blacklist.add((item[0],item[1])) # item[0] et 1 sont les coordonnées de la case qu'on a creusée
                        
                
    def calcVoisinage(self): 
        # cette methode permet de calculer le nbVoisins des cases
        for col in range(self.columns):
            for row in range(self.rows):
              counter = 0
              for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    # Pour ne pas sortir de la grid du jeu, on verifie si les indexes sont < 0 ou > columns et rows
                    if(col+dx < self.columns and col+dx >=0 and row+dy < self.rows and row+dy >=0):
                        if(self.positionsMines[col+dx][row+dy] == 1):
                            self.nbVoisins[col][row]+=1
        print(self.nbVoisins)
    def rightClickReact(self,event):
        # se declanche lors de click sur une case avec un click droit
        if self.isGameOver:
            return
        # on tire le X et le Y depuis l'évenemnt pour extraire ou se trouve le carré correspondant à l'aide de la division euclidienne
        col = event.x//self.rectWidth
        row = event.y//self.rectHeight
        #check if la case a été deja clické:
        if self.casesCreuses[col][row] == 1:
            return
        self.marquerDrapeau(col,row)
    def marquerDrapeau(self,col,row):
        # cette methode marque la case à la ligne <row> et colonne <col> par un drapeau
        #check if la case a été marqué avec drapau:
        if self.positionDrapeaux[col][row] == 1:
            #on annule le drappeau
            self.positionDrapeaux[col][row] = 0
            #on redessine le carré
            self.rect[row, col] = self.canvas.create_rectangle(
            col * self.rectWidth, (row)*self.rectHeight, (col+1)*self.rectWidth, (row+1)*self.rectHeight, fill="white", tags="rect")
        else:
            self.positionDrapeaux[col][row] = 1
            # self.rect[row, col] = self.canvas.create_rectangle(
            # col * self.rectWidth, (row)*self.rectHeight, (col+1)*self.rectWidth, (row+1)*self.rectHeight, fill="white", tags="rect")
            
            self.canvas.create_image((col * self.rectWidth,row * self.rectHeight),anchor=tk.NW, image=self.flagPhoto)
        
    def marquerCreuse(self, col,row):
        # cette methode creuse la case à la ligne <row> et colonne <col>. on la remplace par un rectangle dans le canvas self.canvas 
        self.casesCreuses[col][row] = 1
        self.canvas.create_rectangle(
            col * self.rectWidth, (row)*self.rectHeight, (col+1)*self.rectWidth, (row+1)*self.rectHeight, fill="limegreen", tags="rect")
        if(self.nbVoisins[col][row] > 0):
            self.canvas.create_text(
                col * self.rectWidth+10, (row)*self.rectHeight+10, text=str(self.nbVoisins[col][row]), fill="white")
    def creuserMine(self,col,row):
        self.canvas.create_rectangle(
            col * self.rectWidth, (row)*self.rectHeight, (col+1)*self.rectWidth, (row+1)*self.rectHeight, fill="lightgrey", tags="rect")
        self.canvas.create_image((col * self.rectWidth+3,row * self.rectHeight+1),anchor=tk.NW, image=self.bombPhoto)
        
    def runGameOver(self):
            self.isGameOver = True
            self.canvas.create_rectangle(
                        22*self.rectWidth, 10*self.rectHeight, 28*self.rectWidth, 14*self.rectHeight, fill="red", tags="rect")
            self.canvas.create_text(25*self.rectWidth,12*self.rectHeight, text="Game Over",font=20)
            # self.gameOverLabel = Label(self.root, text="Game over")
            print('you just hit a mine. game over')
    def leftClickReact(self, event):
        # se declanche lors de click sur une case avec un click gauche
        # Dans le cas:
        # soit on clique sur un mine et on perd le jeu
        # soit on a cliqué sur une case deja creusée
        # soit on clique sur une case qu'elle n'est pas creusée
        if self.isGameOver:
            return
        # on tire le X et le Y depuis l'évenemnt pour extraire ou se trouve le carré correspondant à l'aide de la division euclidienne
        col = event.x//self.rectWidth
        row = event.y//self.rectHeight
        #check si est deja creusée, on ne fait rien
        if self.casesCreuses[col][row] == 1:
            return
        #Check si est une mine
        if self.positionsMines[col][row] == 1:
            self.creuserMine(col,row)
            self.runGameOver()
            self.calculateScore()
            self.checkIfPlayerHasTop5Score()
            if self.isTopScorer:
                self.promptRegister("firstName")
                # self.updateBoardWithPlayerTopScore()
                
        else:
            
            #on creuse la case
           self.marquerCreuse(col,row)
           self.creuserVoisin(col,row)
    def test(self, event):
        print('usernameEntry: ', self.textEntry.get(),', event: ', event.char)
    def test2(self, event):
        print('usernameLastEntry: ', self.userLastNameEntry.get(),', event: ', event.char)
    def promptRegister(self,target):
        
        self.postGameOverNameInputWindw = tk.Toplevel(self.root) 
        self.postGameOverNameInputWindw.title("You are in the top 5")
        topLeft = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='red',
              font=('Arial', 14, 'bold'))
        topLeft.grid(row=0,column=0)
        if(target == "firstName"):
            topLeft.insert(tk.END,'    Enter your first name')
        if(target == "lastName"):
            topLeft.insert(tk.END,'    Enter your Last name')
        self.textEntry = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='blue',
              font=('Arial', 16, 'bold'))
        self.textEntry.bind("<Key>", self.test)
        self.textEntry.grid(row=1,column=0)
        self.textEntry.insert(tk.END,'')
        if(target == "firstName"):
            self.confirmButton = tk.Button(self.postGameOverNameInputWindw, text="Confirm", command=self.saveFirstName)
        if(target == "lastName"):
            self.confirmButton = tk.Button(self.postGameOverNameInputWindw, text="Confirm", command=self.saveLastName)
        self.confirmButton.grid(row=2, column=0)
    def saveFirstName(self):
        self.username = self.textEntry.get()
        print('saveFirstName: ', self.username)
        self.postGameOverNameInputWindw.destroy()
        self.promptRegister("lastName")
    def saveLastName(self):
        self.userLastName = self.textEntry.get()        
        print('saveFirstName: ', self.userLastName)
        self.updateBoardWithPlayerTopScore()
        self.postGameOverNameInputWindw.destroy()
    def registerUserName(self):
        self.postGameOverNameInputWindw = tk.Toplevel(self.root) 
        self.postGameOverNameInputWindw.title("You are in the top 5")
        topLeft = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='red',
              font=('Arial', 14, 'bold'))
        topLeft.grid(row=0,column=0)
        topLeft.insert(tk.END,'    Enter your first name')
        topRight = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='red',
              font=('Arial', 14, 'bold'))
        topRight.grid(row=0,column=1)
        topRight.insert(tk.END,'    Enter your last name')
        self.usernameEntry = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='blue',
              font=('Arial', 16, 'bold'))
        self.usernameEntry.bind("<Key>", self.test)
        self.usernameEntry.grid(row=1,column=0)
        self.usernameEntry.insert(tk.END,'Firstname')
        self.userLastNameEntry = tk.Entry(self.postGameOverNameInputWindw, width=20, fg='blue',
              font=('Arial', 16, 'bold'))
        self.userLastNameEntry.grid(row=1,column=1)
        self.userLastNameEntry.insert(tk.END,'LastName')
        self.userLastNameEntry.bind("<Key>", self.test2)
        self.usernameEntry.focus()
        btn = tk.Button(self.postGameOverNameInputWindw, text="OK", width=150)
        btn.grid(row=2,column=0)
        btn.bind("<Button-1>", self.closePostGame)
        self.postGameOverNameInputWindw.bind('<Return>', self.closePostGame)
    def closePostGame(self, event):
        self.username = self.usernameEntry.get()
        print('value', self.username, ', ', self.userLastName)
        self.userLastName = self.userLastNameEntry.get()
        # self.postGameOverNameInputWindw.destroy()
    def showScoreBoard(self):
        print("current diff", self.currentDifficulty)
        print(self.topScores)
        self.topScoreWindow = tk.Toplevel(self.root) 
        # self.topScoreWindow.geometry("150x125")
        self.topScoreWindow.title("Top Scores")
        #Ajout de tete pour top score (<thead>)
        head = ('Nom','Prenom','Score','Temps mis') 
        for j in range(4):
            e = tk.Entry(self.topScoreWindow, width=20, fg='red',
                            font=('Arial', 16, 'bold'))
            
            e.grid(row=0,column=j)
            e.insert(tk.END,head[j])
        if(len(self.topScores[self.currentDifficulty]) == 0):
            return
        for i in range(len(self.topScores[self.currentDifficulty])):
            for j in range(4):
                e = tk.Entry(self.topScoreWindow, width=20, fg='blue',
                               font=('Arial', 16, 'bold'))
                #On ajoute un offset par 1 pour la place de la tete (Nom, prenom..)
                e.grid(row=i+1,column=j)
                e.insert(tk.END, self.topScores[self.currentDifficulty][i][j])
    def checkIfPlayerHasTop5Score(self):
        #On commence depuis la case 0
        if(len(self.topScores[self.currentDifficulty]) < self.maxTopScoreBoardLength-1):
            self.isTopScorer = True
            return
        x=0
        while(x < len(self.topScores[self.currentDifficulty]) and self.topScores[self.currentDifficulty][x][2] > self.score or self.topScores[self.currentDifficulty][x][2] == self.score and self.counter >= self.topScores[self.currentDifficulty][x][3]):
        #on va vers la case suivante Tant que le score courant est inferieur au score de la la case X ou bien on a le meme score mais le joueur précédant à terminé en moins de temps
            x+=1
            continue
        if(x > self.maxTopScoreBoardLength-1):
            #Le joueur n'a pas de place dans le tableau de score (on a  mis un maximum de self.maxTopScoreBoardLength)
            print('Pas de places pour le score courant')
            return
        self.isTopScorer = True
    def updateBoardWithPlayerTopScore(self):
        #On commence depuis la case 0
        if(len(self.topScores[self.currentDifficulty]) == 0):
            self.topScores[self.currentDifficulty].append((
                self.username, self.userLastName, self.score, self.counter))
            self.root.update()
            return
        x = 0
        while(x < len(self.topScores[self.currentDifficulty]) and self.topScores[self.currentDifficulty][x][2] > self.score or self.topScores[self.currentDifficulty][x][2] == self.score and self.counter >= self.topScores[self.currentDifficulty][x][3]):
            #on va vers la case suivante Tant que le score courant est inferieur au score de la la case X ou bien on a le meme score mais le joueur précédant à terminé en moins de temps
            x += 1
            continue
        
        if(x > self.maxTopScoreBoardLength-1):
            #Le joueur n'a pas de place dans le tableau de score (on a  mis un maximum de self.maxTopScoreBoardLength)
            print('Pas de places pour le score courant')
            return
        if(x > len(self.topScores[self.currentDifficulty])):
            self.topScores[self.currentDifficulty].append((
                self.username, self.userLastName, self.score, self.counter))
            self.root.update()
            return
        #On ajoute cette case avec n'importe puisqu'on va écraser les valeurs de droite à gauche ensuite pour faire place au nouveau score
        if(len(self.topScores[self.currentDifficulty]) < self.maxTopScoreBoardLength):
            self.topScores[self.currentDifficulty].append((
                self.username, self.userLastName, self.score, self.counter))
        
        for j in range(len(self.topScores[self.currentDifficulty])-1, x, -1):
            self.topScores[self.currentDifficulty][j] = self.topScores[self.currentDifficulty][j-1]
        self.topScores[self.currentDifficulty][x] = (
            self.username, self.userLastName, self.score, self.counter)
        #On fait la mise a jour de l'élement puisqu'on a modifié Entries (variables)
        self.root.update()
    def saveToJson(self):
        _dict = {
            'isGameOver':self.isGameOver,
            'positionsMines':self.positionsMines,
            'positionDrapeaux':self.positionDrapeaux,
            'nbVoisins':self.nbVoisins,
            'casesCreuses':self.casesCreuses,
            'numberOfMines':self.numberOfMines,
            'currentDifficulty': self.currentDifficulty,
            'maxTopScoreBoardLength': self.maxTopScoreBoardLength,
            'counter': self.counter,
            'score':self.score,
            'isTopScorer':self.isTopScorer,
            'topScores':self.topScores,    
        }
        json_object = json.dumps(_dict, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)
    def initParams(self):
        # initilialise les parametres du jeu
        self.isGameOver = False
        self.positionsMines = [[0]*self.rows for i in range(self.columns)]
        self.positionDrapeaux = [[0]*self.rows for i in range(self.columns)]
        self.nbVoisins = [[0]*self.rows for i in range(self.columns)]
        self.casesCreuses = [[0]*self.rows for i in range(self.columns)]
        self.score = 0 # score du joueur
        self.isTopScorer = False  # est ce que le joueur est depuis les self.maxTopScoreBoardLength dans la difficulté choisi
        
        self.counter = 0 # compter (en secondes)
        
    def initGame(self):
        #initialise le jeu
        self.initParams()
        self.randomizeBombPositions(self.numberOfMines)
        # randomize les places des mines à l'aide de randrange. le count represente la ddifficuté (le nombre de mines qu'on a choisi)
        self.calcVoisinage()
        self.startGame()
    def drawGame(self):
        #dessine les cases  du jeu 
        self.canvas.bind("<Button-1>", self.leftClickReact)
        self.canvas.bind("<Button-3>", self.rightClickReact)
        self.rect = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.rectWidth
                y1 = row * self.rectHeight
                x2 = x1 + self.rectWidth
                y2 = y1 + self.rectHeight
                if(self.positionsMines[column][row] == 1): 
                    #TODO: Pour ne pas afficher oou sont les mines, commentez la ligne ci-dessous et remenez continue 
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="orange", tags="rect")
                    #continue
                    
                elif(self.positionDrapeaux[column][row] == 1):
                    self.positionDrapeaux[column][row] = 0
                    self.marquerDrapeau(column,row)                    
                    print('drapeau found')
                elif self.casesCreuses[column][row]:
                    
                    self.marquerCreuse(column,row)
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="lightgrey", tags="rect")

        self.counterLabel = tk.Label(self.buttonFrame, text=self.counter, padx=5, pady=5, bg="grey",fg="red")
        self.counterLabel.grid(row=0, column=5, padx=0)
    def drawMineSweeper(self):
        #Dessin de "Minesweeper!" avec les mines et les flags qui l'entourent
        #dessine les cases  du jeu 
        self.isGameOver = True
        self.rect = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.rectWidth
                y1 = row * self.rectHeight
                x2 = x1 + self.rectWidth
                y2 = y1 + self.rectHeight
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="yellow", tags="rect")
        self.canvas.create_text(25 * self.rectWidth, 12 * self.rectHeight, text="MineSweeper!", font=("Courier", 44, "italic bold"))
        for column in range(12, 36, 2):
            self.canvas.create_image(
                (column * self.rectWidth, 10 * self.rectHeight), anchor=tk.NW, image=self.flagPhoto)
            self.canvas.create_image(
                ((column+1) * self.rectWidth+3, 10 * self.rectHeight), anchor=tk.NW, image=self.bombPhoto)
            self.canvas.create_image(
                (column * self.rectWidth, 14 * self.rectHeight), anchor=tk.NW, image=self.flagPhoto)
            self.canvas.create_image(
                ((column+1) * self.rectWidth+3, 14 * self.rectHeight), anchor=tk.NW, image=self.bombPhoto)
        for row in range(10, 14, 2):
            self.canvas.create_image(
                (12 * self.rectWidth, row * self.rectHeight), anchor=tk.NW, image=self.flagPhoto)
            self.canvas.create_image(
                ((12) * self.rectWidth +3, (row+1) * self.rectHeight), anchor=tk.NW, image=self.bombPhoto)
            self.canvas.create_image(
                (36 * self.rectWidth, row * self.rectHeight), anchor=tk.NW, image=self.flagPhoto)
            self.canvas.create_image(
                ((36) * self.rectWidth +3, (row+1) * self.rectHeight), anchor=tk.NW, image=self.bombPhoto)
        self.canvas.create_image(
            ((34) * self.rectWidth+5, (12) * self.rectHeight +5), anchor=tk.NW, image=self.bombPhoto) #Flag directement de le point d'exclamation de Minesweeper!
        self.canvas.create_image(
            ((36) * self.rectWidth, (14) * self.rectHeight), anchor=tk.NW, image=self.flagPhoto)

    def startCounter(self):
        #commence le compteur en seconds.
        while self.isGameOver == False:
            time.sleep(1)
            # on declance time.sleep(1) et on incremente après chaque second
            self.counter += 1
            self.counterLabel['text'] = "Compteur: " + str(self.counter)
            self.root.update()
        
    def startGame(self):
        self.drawGame()
        self.startCounter()
       
                    
                    
                    
                    


if __name__=='__main__':

    app = Minesweeper()


#Refs:
# https://www.tutorialspoint.com/binding-function-in-python-tkinter
# https://www.tutorialspoint.com/how-to-insert-an-image-in-a-tkinter-canvas-item
# https://www.geeksforgeeks.org/create-table-using-tkinter/
# https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
# Images utilisées 
# https://www.iconfinder.com/icons/3024770/flag_flags_marker_nation_icon
# https://www.pngall.com/bomb-vector-png/download/54358
# les images ont été retouché (seule la taille) en utilisant GIMP


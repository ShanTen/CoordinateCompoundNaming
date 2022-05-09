class ErrorClass:
    def __init__(self, errorType, details):
        self.errorType = errorType
        self.details = details

    def stringify(self):
        string = f'{self.errorType}:\n{self.details}'
        return string

###############IMPORTS##########################
import json 
import re 
import mendeleev as mend
import pickle
import Bugger as bugBoi

lexInstance = bugBoi.Bugger()

##########Functions#############################

def readLigands():
    LIGANDS_FILE = "./commonLigaands.json"
    with open(LIGANDS_FILE,"rt") as f:
        data = json.loads(f.read())
    return data

def readElements():
    ELEMENTS_FILE = "./elements.bin"
    with open(ELEMENTS_FILE,"rb") as f:
        data = pickle.load(f)
    return data

def getUserDefinedLigandNotations():
    LIGANDS_FILE = "./commonLigaands.json"
    USER_DEFINED_LIGANDS = []
    with open(LIGANDS_FILE,"rt") as f:
        data = json.loads(f.read())
    for d in data: #i in range(len(data))
        if "IsUserDefined" in d:
            USER_DEFINED_LIGANDS.append(d["Ligand"])
    return USER_DEFINED_LIGANDS

#################################################
#Shantanu's Convention
#NOTE: for notes
#TODO: For inline features to add
#################################################

TknOpenSqrBr  = '['
TknCloseSqrBr = ']'

TknOpenParan  = '('
TknCloseParan = ')'

TknOpenUserLigandDetect = "{" 
TknCloseUserLigandDetect = "}" 

TknPlus = "+"
TknMinus = "-"
TknUnderscore = '_'

TknTypeElement = "TKN_ELEMENT"
TknTypeCount = "TKN_COUNT"
TknTypeParanthesis = "TKN_PARAN"
TknTypeSquareBracket = "TKN_SQBR"
TknTypeCharge = "TKN_CHARGE"

TknTypeUnderscore = "_"
TknTypeCurlyBracket = "TKN_CURLY" #unused

TknTypeUserDefLigand = "TKN_USER_DEFINED_LIGAND"
TknTypeLigand = "TKN_LIGAND"

LigandsObject = readLigands()
Ligands = [(x["Ligand"],x["IUPACname"],x["Denticity"]) for x in LigandsObject]
Ligands = list(sorted(Ligands, key = len, reverse = True)) #sorting by length 

UserDefinedLigands = getUserDefinedLigandNotations()

TknElements = readElements()

# DBlockPeriod1 = list(range(21, 30+1))
# DBlockPeriod2 = list(range(40, 48+1))
# DBlockPeriod3 = list(range(72, 80+1))

DblockElements = TknElements  #TknElements[20 : 30] + TknElements[39 : 48] + TknElements[71 : 80]  

IUPACmultipliers = {
    1  : "", #mono
    2  : "di", 
    3  : "tri", 
    4  : "tetra", 
    5  : "penta", 
    6  : "hexa", 
    7  : "hepta", 
    8  : "octa", 
    9  : "non", 
    10 : "deca", 
    11 : "undeca", 
    12 : "dodeca",
    13 :"trideca",
    14 :"tetradeca",
    15 :"pentadeca",
    16 :"hexadeca",
    17 :"heptadeca",
    18 :"octadeca",
    19 :"nonadeca",
    20 :"icosa"
}

IUPACmultipliers_COMP = {
    1  : "", #mono
    2  : "bis", 
    3  : "tris", 
    4  : "tetrakis", 
    5  : "pentakis", 
    6  : "hexakis", 
    7  : "heptakis", 
    8  : "octakis", 
    9  : "nonakis", 
    10 : "decakis", 
    11 : "undecakis", 
    12 : "dodecakis",
    13 :"tridecakis",
    14 :"tetradecakis",
    15 :"pentadecakis",
    16 :"hexadecakis",
    17 :"heptadecakis",
    18 :"octadecakis",
    19 :"nonadecakis",
    20 :"icosaakis"
}

##########################################################################################
#Error Subclasses 
##########################################################################################
class IllegalCharacterError(ErrorClass):
    def __init__(self,_errMsg):
        super().__init__("Illegal Character Error ",_errMsg)

class InvalidLigandError(ErrorClass):
    def __init__(self,_errMsg):
        super().__init__(f"Invalid Ligand Error ",_errMsg)

class IllegalCompoundError(ErrorClass): #Syntax Error Like
    def __init__(self,_errMsg):
        super().__init__("Illegal Compound Error ",_errMsg)
##########################################################################################
#Lexer
##########################################################################################
class Token:
    def __init__(self,_tknType,_tknVal,startPos=None,endPos=None):
        self.type = _tknType
        self.value = _tknVal
    
        if startPos:
            self.startPos = startPos.copy()
            self.endPos = startPos.copy()
            self.endPos.advance()

        if endPos:
            self.endPos = endPos

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

class Ligand:
    def __init__(self, commonName, IUPACName,denticityNum,charge=0,abbreviation=None):
        self.commonName = commonName
        self.IUPACName = IUPACName
        self.charge = charge
        self.denticity = denticityNum #1 for mono, 2 for bi, 3 for tri...
        self.abbreviation = abbreviation
        if abbreviation:
            self.abbreviation = abbreviation

    def __repr__(self):
        return f"""Common Ligand name : {self.commonName}

IUPAC Name: {self.IUPACName} 
Abbreviation : {self.abbreviation or 'Unspecified'} 
Charge : {self.charge}"""    

class Component:
    def __init__(self,component,count):
        self.component = component
        self.count = count
    
    def __repr__(self):
        return f"{self.component}:{self.count}"

class Lexer:
    def __init__(self,chain):
        self.chain = chain
        self.chainLength = len(chain)
        self.pos = -1
        self.currentChar = None
        self.advance()

    def throw_invalid_err(self):
        _char_ = self.currentChar
        _error = IllegalCharacterError(f"Illegal Character --> '{_char_}'")
        return [],_error

    def prevChar(self):
        _prevChar_ = None
        if self.pos-1 != -1:
            _prevChar_ = self.chain[self.pos-1]
        else:
            _prevChar_ = None
        return _prevChar_

    def nextChar(self):
        _nextChar_ = None                
        if self.pos+1 < len(self.chain):
            _nextChar_ = self.chain[self.pos+1]
        else:
            _nextChar_ = None
        return _nextChar_

    def getNextCharCheckIfIntReturnVal(self):
        nextIntVal = 1
        __ns = self.nextChar()

        if __ns and __ns.isnumeric():
            if int(__ns) == 0:
                return IllegalCompoundError("You cannot enumerate a ligand/element with 0.").stringify()
            if int(__ns) > 1:
                nextIntVal = int(__ns)
        return nextIntVal

    def advance(self):
        self.pos += 1

        if self.pos < len(self.chain):
            self.currentChar = self.chain[self.pos]
        else:
            self.currentChar = None

    def makeTokens(self):
        tokens = []
        while self.currentChar != None: #While we have a character value in a chain

            if self.currentChar in ' \t':
                self.advance()

            elif self.currentChar in [TknCloseSqrBr,TknOpenSqrBr]:
                tokens.append(Token(TknTypeSquareBracket,self.currentChar))
                self.advance()

                if self.prevChar() == TknCloseSqrBr and self.currentChar != None:
                    #num is set because we advanced
                    #[]num+ or []num-
                    __chrg_num = ""
                    if self.currentChar.isnumeric():
                        # n += str(self.currentChar)
                        if self.chain[self.chainLength-1] in ["+", "-"]:
                            __chrg = self.chain[self.chainLength-1]
                            __chrg_num = self.chain[self.pos:self.chainLength-1]
                            __chrg = int(__chrg+__chrg_num)
                            tokens.append(Token(TknTypeCharge,__chrg))
                            break #End of Loop
                        else:
                            print("ERR: Invalid Ending Number")

                    elif self.currentChar in ["+", "-"]:
                        tokens.append(Token(TknTypeCharge,int(self.currentChar+"1")))
                        self.advance()

            elif self.currentChar in TknElements:
                singleElComp = Component(self.currentChar,1)
                if not self.nextChar().isalpha():
                    singleElComp = Component(self.currentChar,self.getNextCharCheckIfIntReturnVal())
                    # print(f"The num of {self.currentChar} attached is {self.getNextCharCheckIfIntReturnVal()}")
                tokens.append(Token(TknTypeElement,singleElComp)) #changed this to component
                self.advance()
                
            #Compound Ligands here dummy 
            elif self.currentChar in [TknOpenParan]: 
                self.advance()
                __ligandBufStr = ""
                while self.currentChar != TknCloseParan:
                    __ligandBufStr += self.currentChar
                    self.advance()
                    if self.currentChar == None: 
                        return [], IllegalCompoundError(f" --> Expected '{TknCloseParan}' to close ");
                compLigand = __ligandBufStr

                compLigandComp = Component(compLigand,self.getNextCharCheckIfIntReturnVal())

                # print(f"The num of {compLigand} attached is {self.getNextCharCheckIfIntReturnVal()}")

                tokens.append(Token(TknTypeLigand,compLigandComp)) #changed this to component
                self.advance()

            elif self.currentChar.isnumeric() and int(self.currentChar != 0):
                # tokens.append(Token(TknTypeCount,self.currentChar))
                self.advance()                

            elif self.currentChar in [TknUnderscore]:
                tokens.append(Token(TknTypeUnderscore,self.currentChar))
                self.advance()

            # User defined Ligand starts Identification here 
            elif self.currentChar == TknOpenUserLigandDetect:
                __ligandBufStr = ""
                self.advance()

                # Two possible error cases, 
                # first embeded, 
                # second incomplete curly set or even complete curly but not able to identify ligand (parser will handle it )

                while self.currentChar != TknCloseUserLigandDetect:
                    # print(f"Self Current Char at point of open curl detect {self.currentChar}")
                    __ligandBufStr += self.currentChar
                    self.advance()
                    if self.currentChar == None: #reached end of string with no closing curly
                        return [], IllegalCompoundError(f" --> Expected {TknCloseUserLigandDetect} to close ");

                userDefinedLigand = __ligandBufStr

                userDefLigandComp = Component(userDefinedLigand,self.getNextCharCheckIfIntReturnVal())

                # print(f"The num of {userDefinedLigand} attached is {self.getNextCharCheckIfIntReturnVal()}")

                tokens.append(Token(TknTypeUserDefLigand,userDefLigandComp)) #changed this to component

                self.advance()

            #Two Letter Elements 
            elif self.currentChar not in TknElements and self.currentChar.isalpha():
                if self.currentChar.islower(): #NOTE: Of the Form X"y" where it is currently on y, we go back an index, pop and get value
                    if f"{self.chain[self.pos-1]}{self.currentChar}" in TknElements and self.pos>0:
                        element = f"{self.chain[self.pos-1]}{self.currentChar}"
                        tokens.pop()
                        
                        # print(f"The num of {element} attached is {self.getNextCharCheckIfIntReturnVal()}")

                        elComp = Component(element, self.getNextCharCheckIfIntReturnVal())
                        tokens.append(Token(TknTypeElement,elComp)) #changed this to component

                        self.advance()
                    else:
                        return self.throw_invalid_err()
                else:
                    if self.currentChar.isupper():#NOTE: Of the Form "X"y where it is currently on X, we go forward an index and get value then double advance to skip next value.
                        # print(len(self.chain),self.pos+1)
                        #if self.pos==0: #Why am I doing this?
                            # print("Hit 4")
                            # return self.throw_invalid_err()
                        
                        if len(self.chain) <= self.pos+1:
                            return self.throw_invalid_err()

                        if f"{self.currentChar}{self.chain[self.pos+1]}" in TknElements:
                            element = f"{self.currentChar}{self.chain[self.pos+1]}"

                            self.advance()

                            # print(f"The next value is {self.nextChar()}")
                            # print(f"The num of {element} attached is {self.getNextCharCheckIfIntReturnVal()}")

                            elComp = Component(element, self.getNextCharCheckIfIntReturnVal())
                            tokens.append(Token(TknTypeElement,elComp)) #changed this to component

                            self.advance()
                        else:
                            return self.throw_invalid_err()

            else:#throw invalid character error
                _char_ = self.currentChar
                self.advance()
                _error = IllegalCharacterError(f"Illegal Character --> '{_char_}'")
                return [],_error
    
    #CHANGE TO TYPE BASED
        if tokens == []:
            return "NULL_LINE",None #bro I cant even tf did I writye
        return tokens,None

##########################################################################################
#Coordinate Compound Class
##########################################################################################

class CoordinateCompound_Simple:
    global LigandsObject, IUPACmultipliers, IUPACmultipliers_COMP, mend, lexInstance
    #Simple Coordinate Compounds --> K3[CoF6], [Cr(CO)6], [Pt{en}2]CO3
    def __init__(self,parseObj):

        self.parseObj = parseObj
        self.OxState = 0
        self.name = None

    def searchLigandObject(self, lig2search):
        for ligSubObj in LigandsObject:
            # print(ligSubObj)
            if ligSubObj["Ligand"] == lig2search:
                return ligSubObj 

    def ligandObjectList(self):
        #This takes each (Ligand,count) in parseObject then makes it into an array sorted with ligandObject["IUPACname"] with (LigandObject, count)
        ligObjLst = []
        for i in self.parseObj["Ligands"]:
            __obj = self.searchLigandObject(i[0])
            ligObjLst.append(__obj)
        
        #incoming overkill sort method because screw clean code and time complexities (Im never going to fang am I?)
        names = []
        for lobj in ligObjLst:
            names.append(lobj["IUPACname"])
        names = sorted(names)

        bufList = [] #List of all sorted objs according to their IUPAC name
        for n in names:
            for x in ligObjLst:
                if x["IUPACname"] == n:    
                    bufList.append(x)

        nums = []
        for b in bufList:
            for k in self.parseObj["Ligands"]:
                if b["Ligand"] == k[0]:
                    nums.append(k[1])

        returnList = [] #finalList

        for BufligObj in bufList:
            ind = bufList.index(BufligObj)
            returnList.append((BufligObj,nums[ind]))

        return returnList


    def getOxState(self):
        ligs = self.parseObj["Ligands"]
        totalLigandCharge = 0
        for vex in ligs:
            name = vex[0]
            count = vex[1]
            charge = self.searchLigandObject(name)["Charge"]
            totalLigandCharge += count*charge
            #denticity = self.searchLigandObject(name).Denticity

        if self.parseObj["Anion"]:
            bing = self.parseObj["AnionCount"] * self.searchLigandObject(self.parseObj["Anion"])["Charge"]
            totalLigandCharge += bing
        if self.parseObj["Cation"]: #FIX Get data of all cations
            totalLigandCharge += self.parseObj["CationCount"] * 1 #temp value for all cations

        self.OxState = -totalLigandCharge

        if self.parseObj["IonCompVal"]:
            self.OxState = self.parseObj["IonCompVal"] - totalLigandCharge


        lexInstance.print(f"Predicted Ox State of Metal is: {self.OxState}")

    def verify(self):
        #this shoUld be done...somehow
        pass

    def name_mado(self):
        Compname = ""
        ligandObjectList = self.ligandObjectList()

        if self.parseObj["Cation"]:
            Compname += mend.element(self.parseObj["Cation"]).name

        lexInstance.print(f"LOL_Sorted: {ligandObjectList}")
        for l,n in ligandObjectList:
            ligNaname = l["IUPACname"]
            muliplier = IUPACmultipliers[n]
            if l["IsUserDefined"]:
                muliplier = IUPACmultipliers_COMP[n]
            Compname += f" {muliplier.capitalize()} {ligNaname}"

        Compname += " " + mend.element(self.parseObj["CentralMetal"]).name + f" ({self.OxState})"

        #Remove extra annoying space b/w start of name and screen
        if self.parseObj["Anion"]:
            Compname += " " + self.searchLigandObject(self.parseObj["Anion"])["Name"]
            Compname = Compname[1::]

        if self.parseObj["IonCompVal"]:
            Compname += " Ion"
            # Compname = Compname[1::]
        
        # lexInstance.activate()
        lexInstance.print(self.parseObj)

        if not self.parseObj["Cation"] and not self.parseObj["Anion"]:
            Compname = Compname[1::]

        self.name = Compname


##########################################################################################
#Parser
##########################################################################################
class Parser:
    def __init__(self,tokensArr):
        global TknTypeCharge

        self.rawTokens = tokensArr
        self.ligands = []
        self.centralMetal = None
        self.centralMetalCount=1
        self.parseObj = {}
        self.tokens = [tok.value for tok in tokensArr]

        self.Anion = None
        self.AnionCount = None
        self.Cation = None
        self.CationCount = None

        self.IonicCompensationValue = 0 
        self.isIon = False

        for __t in tokensArr:
            if __t.type == TknTypeCharge:
                self.isIon = True
                self.IonIndex = tokensArr.index(__t)
                self.IonicCompensationValue = self.tokens[self.IonIndex]

    def makeSphereObject(self):
        pass

    def parseThatshit(self):
        global Ligands, DblockElements

        #I know this is hardcoded here, I know. I just dont care.
        sqbrOpeningIndex = self.tokens.index("[") 
        sqbrClosingIndex = self.tokens.index("]")
        coordinateSphere = self.rawTokens[sqbrOpeningIndex+1:sqbrClosingIndex]

        self.parseObj["IonCompVal"] = None
        if self.isIon:
            self.parseObj["IonCompVal"] = self.IonicCompensationValue
        else:
            if  sqbrOpeningIndex != 0:
                cat = (self.tokens[:sqbrOpeningIndex])[0].component
                self.CationCount = (self.tokens[:sqbrOpeningIndex])[0].count
                self.Cation = cat            
            if  sqbrClosingIndex != len(self.tokens)-1:
                ann = (self.tokens[sqbrClosingIndex+1:])[0].component
                self.AnionCount = (self.tokens[sqbrClosingIndex+1:])[0].count
                self.Anion = ann

        self.parseObj["Cation"] = self.Cation
        self.parseObj["CationCount"] = self.CationCount
        self.parseObj["Anion"] = self.Anion
        self.parseObj["AnionCount"] = self.AnionCount

        #################### Coordinate Sphere Verification##################################

        csObj = {
            "CentralMetal":None,
            "CentralMetalCount":0,
            "Ligands":[] #Pair of Ligand, count of respective ligand -> [("H20",4),("CO",2)]
        }

        __lVals =  [i[0] for i in Ligands]
        # __lNames = [i[1] for i in Ligands] get ligand names 

        for p in coordinateSphere:

            if p.value.component in __lVals:
                __ligVal = p.value.component
                self.ligands.append((__ligVal,p.value.count))

            elif p.value.component in DblockElements:
                self.centralMetal = p.value.component
                self.centralMetalCount = p.value.count
            
            elif not p.value.component.isnumeric():
                return [],InvalidLigandError(f"The ligand {p.value} does not exist")
        
        csObj["CentralMetal"] = self.centralMetal
        csObj["CentralMetalCount"] = self.centralMetalCount
        csObj["Ligands"] = self.ligands

        for k in csObj:
            self.parseObj[k] = csObj[k]

        return self.parseObj, None

##########################################################################################
#Final Exported Methods to interface and internal run methods
##########################################################################################
def passTokens(inputChain):
    lxr = Lexer(inputChain)
    tkns,_err = lxr.makeTokens()
    lexInstance.deactivate()
    lexInstance.print(f"Tokens: {tkns}")
    if tkns != []:
        prsr = Parser(tkns)
        res, err = prsr.parseThatshit()

        if err: 
            return [], err
        else: 
            cordObj = CoordinateCompound_Simple(res)
            cordObj.getOxState()
            cordObj.name_mado()
            res = cordObj.name
            return res, None
            lexInstance.print(res)
    else: 
        return tkns,_err
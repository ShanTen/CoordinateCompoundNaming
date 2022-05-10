from lexer import runParser
from os import system
from os import name as OSName
import huepy as hp
from random import choice

##########################################################################################
#Declrations
##########################################################################################

NMSettings = {
    "EchoInput": True,
   	"CommentChar": "//",
}

HelpText = hp.cyan(
	"""Type a coordinate compound's formula to get it's name according to IUPAC's rules of nomenclature.\nEx: [Zn(OH)4]2- or [Co(H2O)4Cl2](Cl).\nUse cmds to see all commands.""")

commands = ['cmds', 'commands', 'clear', 'cls',
            'exit', 'quit', 'settings', 'config',
            'help', '?']


##########################################################################################
#Command Handling Method Definition
##########################################################################################

def handleNonPNomen(cmdString):
	global cacheDict, changedCache
	cmdString = cmdString.lower()
	if cmdString in ['clear', 'cls']:
		if OSName == 'nt':
			_ = system('cls')

	if cmdString in ['exit', 'quit']:
		exit(hp.purple("Bye."))

	if cmdString in ['help', '?']:
		print(HelpText)

	if cmdString in ['settings', 'config']:
		print(hp.lightred(NMSettings))

	if cmdString in ['cmds', 'commands']:
		print(f"The available commands are: {hp.lblue(commands)}")


def printIUPACResults(condensedFormula, comment, IUPACName):
	global NMSettings
	if(NMSettings["EchoInput"]):
		print(f"{hp.italic(hp.lgreen(condensedFormula))} => {hp.lgreen(IUPACName)} {hp.yellow(comment)}")
	else:
		print(f"{hp.lgreen(IUPACName)} {hp.yellow(comment)}")


def getExamples(fileLocation):
	with open(fileLocation, 'r') as f:
		comps = f.read().split("\n")
	return comps

##########################################################################################
#Main
##########################################################################################

examplesLocation = "./SampleSet.txt"  # Location for a file with examples
CompsExampleSet = getExamples(examplesLocation)
randomFlag = False

while 1:
    text = input("NM => ")

    if text.strip().lower() in commands:
        handleNonPNomen(text)

    elif '\n' in text:  # Handle Just Enter
        continue

    elif ' \n' in text:  # Handle Just Enter
        continue

    else:
        comment = ''
        commentChar = NMSettings["CommentChar"]
        condensedFormula = text

        if commentChar in text:  # Comment Handling
            comment = text[text.index(commentChar)::]
            condensedFormula = text[:text.index(commentChar)].strip()  # Remove trailing spaces

        if text in ["random", "rand"]:
            condensedFormula = choice(CompsExampleSet)
            print(condensedFormula)

        if condensedFormula != "" and not condensedFormula.isspace():
            res, err = runParser(condensedFormula)
            cIUPACNAME = res
            if err:
                print(hp.under(hp.red(err.stringify())))
            else:
                printIUPACResults(condensedFormula.strip(),comment, cIUPACNAME.strip())
        else:
            printIUPACResults("",comment,"")

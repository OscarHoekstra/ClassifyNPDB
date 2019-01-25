#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Description: A collection of my personal functions to use in other
scripts by importing or copy-pasting the code.
"""
# Importing various packages for use in the functions
from sys import argv
import time

def template(input):
	"""Does this, returns that

	Keyword Arguments:
		input -- type, what is inputted
	Returns:
		output -- type, what is outputted
	"""
	output = None
	print("Template function")
	return output

def JoinList(LIST):
	if type(LIST) == list:
		out = ', '.join(LIST)
	elif type(LIST) == str:
		out = LIST
	return out

def PrintTime():
	"""Print the current date and time on the screen."""
	CurTime = time.strftime("%d-%m-%Y %H:%M")
	print("It is currently: "+CurTime)

def interval(start,location = False, decimals = 2):
	Elapsed = time.time()-start
	if Elapsed < 600:
		IntervalTime = str(round(time.time()-start,decimals))+" Seconds"
	else:
		IntervalTime = str(round(time.time()-start)/60)+" Minutes"
	if location != False:
		print(IntervalTime+" at location "+str(number))
	newstart=time.time()
	return IntervalTime, newstart

def FileToString(FilePath):
	"""Parses a file into a single string

	Keyword Arguments:
		FilePath -- string, path to the file
	Returns:
		FileString -- string, string that contains text of input file
	"""
	with open(FilePath) as f:
		FileString = f.read()
	return FileString

def FileToList(FilePath):
	"""Parses a file with (space) seperated structure_id, smile and
inchi-key and put the structure_id and inchi-key in lists in lists

	Keyword Arguments:
		FilePath -- string, path to the inchi-key file
	Returns:
		List -- list, list of lists with necessary data
	"""
	List = []
	with open(FilePath) as f:
		for line in f:
			List.append(line.rstrip())
	return List

def CalcHamming(Line1, Line2):
	"""Calculates the Hamming distance of 2 sequences

	Keyword Arguments:
		Line1, Line2 -- string, Sequence of any kind
	Returns:
		Hamming -- int, Hamming distance between 2 input strings
	"""
	Hamming = 0
	Position = 0
	for Letter in Line1:
		if Letter != Line2[Position]:
			Hamming += 1
		Position += 1
	return Hamming

def CompareLength(String1, String2):
	"""Compares the length of 2 strings, returns True if same length

	Keyword Arguments:
		String1, String2 -- str, Strings of any type and length
	Returns:
		SameLength -- Boolean, True if 1 and 2 are same length
	"""
	if len(String1) == len(String2):
		print("Strings are of similar Length")
		SameLength = True
	else:
		print("Strings are NOT of similar Length")
		SameLength = False
	return SameLength

def DNAtoRNA(DNA):
	"""Returns the RNA sequence to a DNA Sequence

	Keyword Arguments:
		DNA -- string, A DNA sequence
	Returns:
		RNA -- string, A RNA sequence
	"""
	RNA = DNA.replace("T","U")
	return RNA

def FastaToList(InFileName):
	"""Parses a FASTA file and put data in lists in lists

	Keyword Arguments:
		InFileName -- string, name of the FASTA file
	Returns:
		List -- list, list of lists with fasta data
	"""
	List = []
	Sequence = ""
	with open(InFileName) as f:
		for line in f:
			if not line.strip():
				print("Empty Line Found")
			else:
				line = line.strip()
				if line.startswith(">"):
					if Sequence != "":
						List.append([Label,Sequence])
					Sequence = ""
					Label = line[1:]
				else:
					Sequence += line
	List.append([Label,Sequence])
	return List

def FASTQToList(InFileName):
	"""Parses a FASTQ file and put data in lists in lists

	Keyword Arguments:
		InFileName -- string, name of the FASTA file
	Returns:
		List -- list, list of lists with fasta data
	"""
	List = []
	with open(InFileName) as f:
		name = f.readline()
		while name.strip():
			name = name.strip()
			seq = f.readline().strip()
			plus = f.readline().strip()
			score = f.readline().strip()
			List.append([name,seq,score])
			name = f.readline()
	return List

def FindCharLoc(String, Character):
	"""Return a list with all locations of a character in a string

	Keyword Arguments:
		String -- string, string you want to find a certain character in
		Character -- string, singular character you want to find
	Returns:
		Positions -- list, locations of the character in the string
	"""
	Positions = [pos for pos, letter in enumerate(String) \
		if letter == Character]
	return Positions

def GCcontent(FastaList):
	"""Returns a list of list to which the GCcontent of the DNA seq was added

	Keyword Arguments:
		FastaList -- list, list of lists, 2nd value of lists is a DNA seq
	Returns:
		NewList -- list, list of lists with 3rd value as GCcontent
	"""
	NewList = []
	for Item in FastaList:
		Sequence = Item[1]
		GCCount = Sequence.count("G") + Sequence.count("C")
		GCValue = GCCount / len(Sequence) * 100
		Item.append(GCValue)
		NewList.append(Item)
	return NewList

def GetArgs(RemoveName = True):
	"""Return a list of the command line arguments without program name

	Keyword Arguments:
		RemoveName: Boolean. If True, removes script name from arguments
	Returns:
		Arguments: List with the arguments given by user
	"""
	if RemoveName == True:
		Arguments = argv[1:]
	else:
		Arguments = argv[0:]
		print ("Script name included in arguments")
	if len(Arguments) == 0:
		print ("No Arguments given!")
	return Arguments

def GetFileName(argv):
	"""Returns the name of the input file from argv

	Keyword arguments:
		argv -- list, command-line arguments
	Returns:
		file_name -- string, name of file provided as argument
	"""
	FileName = argv[1]
	return FileName

def GetFirstLine(InFileName):
	"""Returns the first line of the input file

	Keyword Arguments:
		InFileName -- string, name of the input file
	Returns:
		Line -- string, first line of the input file
	"""
	with open(InFileName) as f:
		Line = f.readline()
	return Line.strip()

def ReverseComplement(Input):
	"""Returns the reverse complement of a DNA string

	Keyword Arguments:
		Input -- string, DNA sequence
	Returns:
		RevComp -- string, Reverse Complement of a DNA string
	"""
	RevComp = ""
	CompDict = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
	for nuc in Input:
		RevComp = CompDict[nuc] + RevComp
	return RevComp

def RunTool(InFile, parameter=None):
	"""Runs the ... program from the command line and returns the output

	Keyword arguments:
		InFile -- string, name of input file
	Returns:
		OutFile -- string, name of the output file
	"""
	# check if output file already exists
	if os.path.exists(OutFile):
		return OutFile
	# if not, build the command and send it to the shell
	cmd = "tool {} {} -parameter1 {} -parameter2 {}" \
		.format(InFile, OutFile, setting1, setting2)
	subprocess.check_call(cmd, shell = True)
	return OutFile

def SeqToRF(Sequence):
	"""Return a list with all 3 forward reading frames

	Keyword Arguments:
		Sequence -- string, DNA or RNA Sequence
	Returns:
		RF -- list, List with all 3 forward reading frames of a Sequence

	Input the reverse complement of the sequence to find the reverse
	reading frames.
	"""
	RF = []
	for i in range(3):
		curSeq = Sequence[i:]
		StripAmount = len(curSeq) % 3
		if StripAmount == 0:
			RF.append(curSeq)
		else:
			RF.append(curSeq[:-StripAmount])
	return RF

def TranslateDNA(Seq):
	"""Return the corresponding protein sequence to a RNA or DNA string

	Keyword Arguments:
		Seq -- string, DNA or RNA sequence
	Returns:
		Prot -- string, Single letter notation Protein Sequence
	"""
	if "T" in Seq and "U" in Seq:
		print ("This is not a propper DNA or RNA string")
		return False
	elif "T" in Seq: TYPE = "DNA"
	elif "U" in Seq: TYPE = "RNA"
	else:
		print ("This is not a propper DNA or RNA string")
		return False

	if TYPE == "DNA":
		codontable = {
			'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
			'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
			'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
			'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
			'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
			'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
			'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
			'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
			'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
			'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
			'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
			'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
			'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
			'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
			'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
			'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
			}
	elif TYPE == "RNA":
		codontable = {
			'AUA':'I', 'AUC':'I', 'AUU':'I', 'AUG':'M',
			'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACU':'T',
			'AAC':'N', 'AAU':'N', 'AAA':'K', 'AAG':'K',
			'AGC':'S', 'AGU':'S', 'AGA':'R', 'AGG':'R',
			'CUA':'L', 'CUC':'L', 'CUG':'L', 'CUU':'L',
			'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCU':'P',
			'CAC':'H', 'CAU':'H', 'CAA':'Q', 'CAG':'Q',
			'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGU':'R',
			'GUA':'V', 'GUC':'V', 'GUG':'V', 'GUU':'V',
			'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCU':'A',
			'GAC':'D', 'GAU':'D', 'GAA':'E', 'GAG':'E',
			'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGU':'G',
			'UCA':'S', 'UCC':'S', 'UCG':'S', 'UCU':'S',
			'UUC':'F', 'UUU':'F', 'UUA':'L', 'UUG':'L',
			'UAC':'Y', 'UAU':'Y', 'UAA':'_', 'UAG':'_',
			'UGC':'C', 'UGU':'C', 'UGA':'_', 'UGG':'W',
			}
	n = 3
	Prot = ""
	Seq_List = [Seq[i:i+n] for i in range(0, len(Seq), n)]
	for codon in Seq_List:
		if codon != "\n":
			Prot += codontable[codon]
	return Prot

def Out(output, OutFileName = "Out_"+__file__[:-3]+".txt"):#[:-3] removes .py
	"""Return True if a file was written to.

	output: String that needs to be written to a file.

	Writes a string to a .txt file with the same name as this script,
	with Out- in front of it
	"""
	with open(OutFileName, 'w') as w:
		w.write(output)
		print("Output written to file")
	return True

if __name__ == "__main__":
	#This block is only for testing out new functions
	print("This line should not be printed in your script!")
	print("If this is printed, you might have done something wrong \
	with importing.")

	print (Output)
	print("Done")

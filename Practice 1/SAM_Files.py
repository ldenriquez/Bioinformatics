#!/usr/bin/env python
# coding: utf-8

# ## Bioinformatics Coding Practice 1
# By: Lauren Enriquez
# Task: Task: Given a SAM file and a reference fasta file, the goal is to implement a function that will create a pileup of mapped reads over a reference sequence. A function will also be written to identify potential sequencing errors in reads of equal length with the same mapping position.

# In[1]:


import sys


# In[2]:


#User Inputs: Reference fasta file & SAM read file
FASTA_file= sys.argv[1]
SAM_file = sys.argv[2]
print("Name of FASTA file: ", FASTA_file)
print("Name of SAM file: ", SAM_file)
print("\n")


# In[3]:


#Function to read reference FASTA seqs
def read_fasta(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line[1:], []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))


# In[4]:


#Function to read sam file
def read_sam(sam):
    #SAM read name, reference FASTA seq, SAM read seq
    name, ref, seq = None, None, []
    for line in sam:
        if line.startswith("@"):
            pass
        else:
            line = line.split('\t')
            if name: yield (name, ref, seq)
            name, ref, seq = line[0], line[2], line[9]
    if name: yield (name,ref,seq)


# In[5]:


#Scoring scale & parameters
class ScoreParams:
    def __init__(self, gap, mismatch):
        #Gap score
        self.gap = gap
        #Mismatch score
        self.mismatch = mismatch
    
    #Matching scores
    def match(self, chr):
        if chr == 'A':
            return 3
        elif chr == 'C' or chr == 'T':
            return 2
        else:
            return 1


# In[6]:


#Piecewise global alignment algorithm
def global_align(x, y, score=ScoreParams(-4, -3)):
   
    Scores = []
    for i in range(len(y) + 1):
        Scores.append([0] * (len(x) +1))
    for i in range(len(y)+1):
        Scores[i][0] = score.gap * i
    for i in range(len(x)+1):
        Scores[0][i] = score.gap * i
    for i in range(1, len(y) + 1):
        for j in range(1, len(x) + 1):
           
            Scores[i][j] = max(
            Scores[i][j-1] + score.gap,
            Scores[i-1][j] + score.gap,
            Scores[i-1][j-1] + (score.match(y[i-1]) if y[i-1] == x[j-1] else score.mismatch)
            )

    align_X = ""
    align_Y = ""
    i = len(x)
    j = len(y)

    while i > 0 or j > 0:
         
        current_score = Scores[j][i]

        if i > 0 and j > 0 and x[i - 1] == y[j - 1]:
            align_X = x[i - 1] + align_X
            align_Y = y[j - 1] + align_Y
            i = i - 1
            j = j - 1
         
        elif i > 0 and (current_score == Scores[j][i - 1] + score.mismatch or current_score == Scores[j][i - 1] + score.gap):
            align_X = x[i - 1] + align_X
            align_Y = "-" + align_Y
            i = i - 1
             
        else:
            align_X = "-" + align_X
            align_Y = y[j - 1] + align_Y
            j = j - 1
   
    return (" ".join(align_X), " ".join(align_Y))


# In[25]:


#Function to print out Pileup of mapped reads & store information in .txt files
def display(ref_seq,ref_name,align,names):
    f = open(ref_name + ".txt", "w+")
    
    #Determine the correct number of spaces
    pos_text = "Position: "
    y = len(pos_text)
    startpoint = ":"
    numberofspaces = y - len(ref_name) - 1
    for u in range(numberofspaces):
        startpoint = startpoint + " "
    reff = ref_name + startpoint
    x = len(reff)
    
    #Display to Terminal
    print("Position: " + str(list(range(1,len(ref_seq)+1))).replace(",","").replace("[", "").replace("]", ""))
    print(reff + " ".join(ref_seq))
    
    #Write in .txt
    f.write("Position: " + str(list(range(1,len(ref_seq)+1))).replace(",","").replace("[", "").replace("]", ""))
    f.write("\n")
    f.write(reff + " ".join(ref_seq))
    f.write("\n")
    
    for i in range(len(align)):
        sp = ":"
        spaces = x - len(names[i]) - 1
        for k in range(spaces):
            sp = sp + " "
            
        #Display to Terminal
        print(names[i] + sp + align[i])
        
        #Write in .txt
        f.write(names[i] + sp + align[i])
        f.write("\n")
    f.close()


# In[26]:


#Function to determine if there are duplicates in mapped reads
def checkIfDuplicates_2(listOfElems,listOfNames):  
    setOfElems = set()
    ErrorName = []
    check = False
    
    for i in range(len(listOfElems)):
        y = listOfElems[i]
        if y in setOfElems:
            check = True
            ErrorName.append(y)
        else:
            setOfElems.add(y)
            
    return (check,ErrorName)


# In[27]:


#Fuction to determine Hamming Distance
def hamming_dist(seq1, seq2):
    distance = 0
    l = len(seq1)
    for i in range(l):
        # Add 1 to the distance if these two characters are not equal
        if seq1[i] != seq2[i]:
            distance += 1
    
    return distance


# In[28]:


#Function to display Possible Errors
def error_function(sequences,listOfNames,OGsequences):
    z,y = checkIfDuplicates_2(sequences,listOfNames)
    if z == True:
        print("Error:")
        for i in range(len(y)):
            print(listOfNames[i], OGsequences[i])
        print("\n")


# In[29]:


#Function to produce a pileup of mapped reads over given genomic coordinates
def pileup_function(fastafile,samfile):
    # STARTING LISTS
    #List of containing all fasta references & sam sequences categorized
    REFERENCES = []
    
    #Fasta References Lists
    REF_NAME = []
    REF_SEQ = []
    
    #Upload and store reference fasta sequences
    with open(fastafile) as fp:
        for name, seq in read_fasta(fp):
            REF_NAME.append(name)
            REF_SEQ.append(seq)
        
        #Adding the correct number of layered lists within REFERENCES
        for i in range(len(REF_NAME)):
            REFERENCES.append([])
        for j in range(len(REFERENCES)):
            for k in range(4):
                REFERENCES[j].append([])
    
        #Add fasta reference information to REFERENCES
        for j in range(len(REFERENCES)):
            REFERENCES[j][0] = [REF_NAME[j]]
            REFERENCES[j][1] = [REF_SEQ[j]]
    
    with open(samfile) as sam:
        for name, ref, seq in read_sam(sam):
            for j in range(len(REFERENCES)):
                if str(ref) == str(REFERENCES[j][0][0]):
                
                    #Add sam reads information to REFERENCES
                    REFERENCES[j][2].append(name)
                    REFERENCES[j][3].append(seq)
    
    #Iterate through list of SAM seqs and conduct alignments,display, & error functions
    for j in REFERENCES:
        refname = ""
        samnames = []
        aligned = []
        samseq = []
        for i in range(len(j[2])):
        
            #Calls aligmnment algorithm
            t = global_align(j[1][0],j[3][i],score=ScoreParams(-4, -3))
            refname = j[0][0]
            samnames.append(j[2][i])
            aligned.append(t[1])
            samseq.append(j[3][i])
    
        #Calls display function
        display(j[1][0],refname,aligned,samnames)
        print("\n")
        
        #Calls error function
        error_function(aligned,samnames,samseq)


# In[30]:


pileup_function(FASTA_file,SAM_file)

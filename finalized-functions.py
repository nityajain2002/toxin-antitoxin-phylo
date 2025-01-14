import pandas as pd
import numpy as np
import seaborn as sns

def filteredDataframe(csv, hitName):
    '''
    Creates a filtered dataframe for a specific toxin and only includes pairs of two
    Input- Toxin name
    Output- Filtered dataframe
    '''
    df = pd.read_csv(csv)
    domain = df[df['Hit Name'] == hitName]
    contig_counts = domain['Contig'].value_counts()
    valid_contigs = contig_counts[contig_counts == 2].index
    filtered_df = df[(df['Hit Name'] == hitName) & (df['Contig'].isin(valid_contigs))]
    return filtered_df

def uniquePairs(df, g1, g2):
   '''
   Finds and counts the unique pairs or combinations between two columns
   Input- dataframe and two columns
   Output- dataframe with the unique pairs and their cgounts
   '''
   unique_pairs = df[[g1, g2]].drop_duplicates().reset_index(drop=True)
   pairs = [tuple(x) for x in unique_pairs.values]
   counts = []
   for pair in pairs:
      pair_count = len(df[(df[g1] == pair[0]) & (df[g2] == pair[1])])
      counts.append(pair_count)
   returnFrame = pd.DataFrame({
      g1: [x[0] for x in pairs],
      g2: [x[1] for x in pairs],
      'Counts': counts})
   return returnFrame

def randomizedDF(df, n, col):
   '''
   Randomizes the columns in a dataframe "n" times
   Input- dataframe, number of permutations, column to randomize
   Output- dataframe
   '''
   for _ in range(n):
      df[col] = np.random.permutation(df[col].values)
      print(f"After randomization\n", df[col])
   return df

def uniqueFastaFile(data="Toxins.csv"): # to streamline process, 14 TA familes
   '''
   Generates a filtered FASTA file for each Toxin-Antitoxin System, split by toxin and antitoxin 
   Input- csv file containing the unfiltered dataset
   Output- FASTA file for each TA system present in the dataset after filteration
   '''
   df = pd.read_csv(data)

   # filtering out duplicate contigs
   duplicates = df[df.duplicated(subset=['Contig','Hit Name'], keep=False)]

   # filter out the ones w/ two pairs (ie. both upstream & downstream)
   multipleAntitoxins = duplicates[(duplicates['Upstream'] != '-') & (duplicates['Downstream'] != '-')]
   removeDuplicates = ~duplicates.isin(multipleAntitoxins).all(axis=1)
   singleAntitoxins = duplicates[removeDuplicates]
   # prepare for MSA
   # split filtered data frame into TA families & create fasta file
   hitNames = singleAntitoxins['Hit Name'].unique() # my input list
   for hitName in hitNames:
      hitdf = singleAntitoxins[singleAntitoxins['Hit Name'] == hitName]
      inFile = hitName + '.fasta'
      with open(inFile, 'w') as file:
         for index, row in hitdf.iterrows():
            headerT = f">{hitName + '_' + str(index)}.toxin\n"
            headerA = f">{hitName + '_' + str(index)}.antitoxin\n"
            
            seqT = f"{row['Hit']}\n"
            seqA = ''
            if row['Upstream'] != '-':
                  seqA = f"{row['Upstream']}\n"
            else:
                  seqA = f"{row['Downstream']}\n"
            
            file.write(headerT)
            file.write(seqT)
            file.write(headerA)
            file.write(seqA)
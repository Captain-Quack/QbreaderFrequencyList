# _*_ coding: utf-8 _*_


from itertools import filterfalse
from sys import argv
from collections import Counter
from typing import Callable, Iterable
import regex
from titlecase import titlecase  #pyright ignore[reportMissingTypeStubs]


class bcolors:                                                 
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def remove_within(text: str, opening: str, closing: str) -> str:
    """
    Remove all text between start and end. Supports nesting.
    For example:
    (((blah blah))blah))) hello -> hello
    """
    re_open:  str = regex.escape(opening)
    re_close: str = regex.escape(closing)
    
    pattern: regex.Pattern[str] = regex.compile(fr"""(?x)
                             {re_open}   # opening character like '('
                             (?:         # stuff inside the grouping
                                [^{re_open}{re_close}]* # Match anything but the opening or closing char. 
                                |                       # or ...
                                (?R)+                   # match the whole pattern again. this is where the evil-black-magic-witchcraft happens.  
                             )*          # do this as many times as possible. (or don't, if the grouping is empty.)   
                             {re_close}  # close. 
                             """, regex.X) 
    return pattern.sub("", text, concurrent=True)

def remove_grouping(text: str) -> str:
    """
    Remove all text between parentheses, brackets, and braces.
    """
    for opening, closing in [("(", ")"), ("[", "]"), ("{", "}"),]:
        text = remove_within(text, opening, closing)
    
    return text


def remove_issues(assetion: Callable[[str], bool], text: Iterable[str]) -> Iterable[str]:
    """
    Prints/Removes all the words in the text that don't satisfy the predicate.
    """
    
    return filterfalse(assetion, text)
   
def main():
    """
    Read in a file of words, normalize them, and count the frequencies.
    """
      
    # used as a script. 
    if len(argv) == 2:
        filename = argv[1]
        print(bcolors.UNDERLINE, "Input file:", bcolors.ENDC, filename)
        assert filename.endswith(".txt"), "input should be a .txt file"
        x = input("Enter anything to continue, or 'SKIP', to skip")
        if x == 'SKIP': return
    # not used as a script, presumably for debugging. 
    else:
        print("script use: frequency_list.py <filename>")
        print("press any key to load example (or exit)...")
        input()      

        filename = r"C:\Users\mason\Downloads\Other Science.txt"  
    print(bcolors.OKBLUE, "\bReading File...", bcolors.ENDC)  

    
    with open(filename, encoding = "utf8") as file:        
        text: str = file.read()        
    print(bcolors.OKBLUE, "\bRemoving Unnecessary Stuff...", bcolors.ENDC)  

    # remove any grouping symbols:
    # - (That includes (Parentheses (Used for a lot of stuff)) )
    # - [That includes alternate answers (and even comments within those answes)]
    # - {And even stuff like pronounciation guides}
    group_strip: Iterable[str] = (remove_grouping(x) for x in text.splitlines())
    print(bcolors.OKBLUE, "\bPerforming some witchcraft...", bcolors.ENDC)  
    # the next line is more quality assurance then anything. 
    # content in which the editors couldn't bother to match ( with ) don't deserve to be counted. 
    group_strip_remove_issues = filterfalse(lambda x: any("()[]{}" in c for c in x), group_strip)
    # extract any html tags. only <b> (bold) and <u> (underline) are used. 
    html_extract = (regex.sub(r"<([bu])>([^<>]*)(?:<\\\1>)?", r"\g<1>", x, concurrent=True) for x in group_strip_remove_issues)
    # part one of trying to remove quotes
    # (this line was a part of a road bump that caused me many a headache)
    quote_extract = (regex.sub(r'"([^"]*)"', r"\g<1>", x, concurrent=True) for x in html_extract)
    # this removes any credit marks "<Name .Ed BlahBlah>". Also the html escape for < and >
    credit_extract = (regex.sub(r"(?:(&lt;)|(<)).*(?(1)&gt;|>)", "", x, concurrent=True) for x in quote_extract)
    # I forgot why I need this line, when the last line looks like it does the same thing...
    # but I'm also scared to remove it.
    credit_extract_sweep = (remove_within(x, r"<", r">") for x in credit_extract)
    # get only the first part of any "or" OR "OR" OR "Or" OR "oR" Statements
    # this assumes the most common respeonse comes first. 
    only_main_answers = (regex.split(r" +or +", x,flags=regex.IGNORECASE)[0] for x in credit_extract_sweep)
    # remove any extra spaces.
    sweep = (regex.sub(r" {2,}", r" ", titlecase(x.strip())) for x in only_main_answers) 
    
    

    # Two -> 2
    number_dict = {
        "1": "One",
        "2": "Two",
        "3": "Three",
        "4": "Four",
        "5": "Five",
        "6": "Six",
        "7": "Seven",
        "8": "Eight",
        "9": "Nine",
        "0": "Zero"
    }
    print(bcolors.OKBLUE, "\b%25 done filtering...", bcolors.ENDC)  
    
    number_pattern = regex.compile(f"\b({'|'.join(number_dict.keys())})\b")
    number_simplifier = (number_pattern.sub(lambda x: number_dict[x.group()], x) for x in sweep)
    bracket_sweep = (regex.sub(r"\[|;.*", "", x) for x in number_simplifier)
    # if a line has "ANSWER:" in it, get seccond half
    answer_sweep = (x.split("ANSWER: ")[1] for x in bracket_sweep)
    
    # this little line took soooooo long to do, because python can't parse utf_8 out of the box (see first line of code.)
    smart_quote_sweep_attempt = (regex.sub(r"(?:^|\W)(?:\u201c|\u2018)(.*)(?:\u201d|\u2019)(?:\W|$)", r"\g<1>", x) for x in answer_sweep)
    # also because, you know, I don't have a unicode keyboard. 
    the_quotes_left_behind = (regex.sub(r"\u201c|\u201d|\u2018|\u2019", "", x) for x in smart_quote_sweep_attempt)
    

    # This line takes the longest to process. 
    answerlines = list(the_quotes_left_behind)
   
    print(bcolors.OKBLUE, "\bDone filtering...", bcolors.ENDC)  
    print(bcolors.OKBLUE, "\bBeginning annoying part...", bcolors.ENDC)  
    
    # if the script tries to modify a file that is open, it will fail as a security error. 
    print(bcolors.WARNING, "\b> Remember to close any csv files if this is a repeat run. <", bcolors.ENDC)  
  
    new_filename = filename.replace(".txt", "_frequency_list.csv") 
    
    # We are now _forced_ to do manual labor, mostly b/c my IDE was refusing to run a program with smart quotes in it.
    bad_string: Callable[[str], bool] = lambda x: any(char in x for char in [
        '\u201c', 
        '\u201d', 
        '\u2018',
        '\u2019',
        "[", "]",
        "(", ")",
        "{", "}",
        "<", ">", 
        ])
    def handle_input() -> str:
        inp = input()
        match inp:
            case inp if not bad_string(inp) or (inp.isprintable()):
                return inp
            case inp if inp.endswith("ERROR"):
                return handle_input()
            case _:
                print("Invalid character. Please write it without grouping symbols or smart quotes")
                return handle_input()
            
            
    cached_errors: dict[str, str]= { "D\u201d": 'D"', "\uFFFDeptune's Rings": "Neptune's Rings" } 
   
    for i, x in enumerate(answerlines):
            

        x = answerlines[i] = titlecase(''.join(c for c in regex.sub(r"\[|\]|\{|\}|\(|\)|\<|\>|", "", x).replace("\u2018", "'").replace("\u2019", "'") if c.isprintable()))
        if '\uFFFD' in x or (not x.isprintable()):
            print(bcolors.FAIL, "\b--- Attention Required ----", bcolors.ENDC)  
            print(x, "has a weird character in it (you may not be able to see it though.) Correct it, please and thank you:")
            answerlines[i] = handle_input()
            print('=================')
        answerlines[i] = titlecase(answerlines[i].strip())
        
    print(bcolors.OKBLUE, "\bDone with annoying part!", bcolors.ENDC)  
    

    talley = Counter(answerlines)
    print(bcolors.OKBLUE, f"Writing to {new_filename} (check the folder of your input file.)\nInput is separated by semicolons.", bcolors.ENDC)
    
    
    
    with open(new_filename, "w", encoding = "utf_32") as file:
        file.write("Name, Frequency\n")
        
        for (entry, number) in talley.most_common():
            try:
                file.write(f'{entry};{number}\n')
            except Exception:
                print(bcolors.FAIL, "\b--- Attention Required ----", bcolors.ENDC)                  
                if entry in cached_errors:
                    file.write(f'"{cached_errors[entry]}";{number}\n')
                else: 
                    print(entry, "Cannot be written due to some wacky characters. Please retype it:")
                    corrected = cached_errors[entry] = entry
                    file.write(f'"{corrected}";{number}\n')
                
                print('=================')
                
        print(bcolors.OKBLUE, "\bDone!", bcolors.BOLD, "Go To Excel and and await the ~text formatting wizard~", bcolors.ENDC)
    
    # open file
    import os
    os.startfile(new_filename)
       
    print(bcolors.OKGREEN, "\bDone! Raw results:", bcolors.ENDC)  

    import pprint
    pprint.pprint(talley)
    
       
    
if __name__ == '__main__':
    print(bcolors.HEADER, "... Beggining Frequency List ... this might take a minute or two..", bcolors.ENDC)
    main()  
    print(bcolors.OKGREEN, "Talley complete.\n", bcolors.ENDC)
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re, sys



class to_xml:

    def __init__(self, name):
        self.program = ET.Element('program')
        self.program.set('name', name)
        self.call = 1
        self.header = """<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE program [\n\t<!ELEMENT program (tac+)>\n\t<!ELEMENT tac (dst?,src1?,src2?)>\n\t<!ELEMENT dst (#PCDATA)>\n\t<!ELEMENT src1 (#PCDATA)>\n\t<!ELEMENT src2 (#PCDATA)>\n\t<!ATTLIST program name CDATA #IMPLIED>\n\t<!ATTLIST tac opcode CDATA #REQUIRED>\n\t<!ATTLIST tac order CDATA #REQUIRED>\n\t<!ATTLIST dst type (integer|string|variable|label) #REQUIRED>\n\t<!ATTLIST src1 type (integer|string|variable)  #REQUIRED>\n\t<!ATTLIST src2 type (integer|string|variable)  #REQUIRED>\n\t<!ENTITY language "IPPeCode">\n\t<!ENTITY eol "&#xA;">\n\t<!ENTITY gt ">">\n\t<!ENTITY lt "<">\n]>"""


    def add_tac(self, opcode, dst_type, src1_type, src2_type, dst_val = None, src1_val = None, src2_val = None):
        self.tac = ET.SubElement(self.program, 'tac')
        self.tac.set('opcode', opcode)
        self.tac.set('order', str(self.call))
        self.call += 1

        if(dst_val is not None):
            self.dst = ET.SubElement(self.tac, 'dst')
            self.dst.set('type', dst_type)
            self.dst.text = dst_val
        if(src1_val is not None):
            self.src1 = ET.SubElement(self.tac, 'src1')
            self.src1.set('type', src1_type)
            self.src1.text = src1_val
        if(src2_val is not None):
            self.src2 = ET.SubElement(self.tac, 'src2')
            self.src2.set('type', src2_type)
            self.src2.text = src2_val

    def pretty_xml(self):
        # formating to a pretty sintax
        dom = xml.dom.minidom.parseString(ET.tostring(self.program))
        pretty_xml_as_string = dom.toprettyxml()

        return pretty_xml_as_string

        #return ET.tostring(self.program)
    
    def print_xml(self):
        print(self.header + re.sub('^<\?xml version.+ ?>', '', self.pretty_xml()), file=sys.stdout)

    def write_to_file(self, file):
        with open(f"{file}.xml", "w") as file:
            file.write(self.header + re.sub('^<\?xml version.+ ?>', '', self.pretty_xml()))




def main(code, program_name, output):
    
    global my_xml 
    my_xml = to_xml(program_name)

    for line in code:
        line = re.sub(' +', ' ', line) # Fixing more than one space separaton
        line = line.replace('\t', ' ') # Fixing tab separation
        split_line = string_grouping(line.rstrip())
        #print(split_line)
        try:
            strainer(split_line)
        except Exception as ex:
            print(f"Error code: {ex.args[0]} == {ex.args[1]}: {ex.args[2]}.", file=sys.stderr)
            return 1 # or the error code, didn't knew what was required
            #return ex.args[0]

    #my_xml.print_xml()
    if output == '-':
        my_xml.print_xml()
    else:
        my_xml.write_to_file(output)

    return 0

            
    



# My swich
def strainer(line):

    line[0] = str.upper(line[0]) #making operations case-insensitive

    if line[0] == "#":
        # this line is a comment
        pass
    elif line[0] == "MOV":
        operand_validator(line, {"dst":"z", "src1":"x", "src2":None})
    elif line[0] == "ADD":
        operand_validator(line, {"dst":"z", "src1":"x", "src2":"y"})
    elif line[0] == "SUB":
        operand_validator(line, {"dst":"z", "src1":"x", "src2":"y"})
    elif line[0] == "MUL":
        operand_validator(line, {"dst":"z", "src1":"x", "src2":"y"})
    elif line[0] == "DIV":
        operand_validator(line, {"dst":"z", "src1":"x", "src2":"y"})
    elif line[0] == "READINT":
        operand_validator(line, {"dst":"z", "src1":None, "src2":None})
    elif line[0] == "READSTR":
        operand_validator(line, {"dst":"z", "src1":None, "src2":None})
    elif line[0] == "PRINT":
        operand_validator(line, {"dst":None, "src1":"x", "src2":None})
    elif line[0] == "LABEL":
        operand_validator(line, {"dst":"l", "src1":None, "src2":None})
    elif line[0] == "JUMP":
        operand_validator(line, {"dst":"l", "src1":None, "src2":None})
    elif line[0] == "JUMPIFEQ":
        operand_validator(line, {"dst":"l", "src1":"x", "src2":"y"})
    elif line[0] == "JUMPIFLT":
        operand_validator(line, {"dst":"l", "src1":"x", "src2":"y"})
    elif line[0] == "CALL":
        operand_validator(line, {"dst":"l", "src1":None, "src2":None})
    elif line[0] == "RETURN":
        operand_validator(line, {"dst":None, "src1":None, "src2":None})
    elif line[0] == "PUSH":
        operand_validator(line, {"dst":None, "src1":"x", "src2":None})
    elif line[0] == "POP":
        operand_validator(line, {"dst":"z", "src1":None, "src2":None})
    else:
        # exception if the operation isn't recognised 
        raise Exception("11","Parsing Error","Unknown operation code of instruction")


    
# check for the right ammount of operands for each operation
def operand_validator(line, operands):

    opcode = line[0]
    last_type = None
    dst_type = None
    src1_type = None
    src2_type = None
    dst_val = None
    src1_val = None
    src2_val = None
    
    

    # comments cleaner
    for token in enumerate(line):
        if re.fullmatch("[%_$&a-zA-Z]*#.*$", token[1]) != None:
            line = line[:token[0]]
            

    # variables and labels validator 
    if len(line) == 1+len([i for i in operands.values() if i != None]): # checking for maching numbers of arguments
        for operand in zip([i for i in operands.items() if i[1] != None], line[1:]): # creating tuples with argument and its type
            last_type = None

            if operand[0][0] == 'dst':
                dst_val = operand[1]
            if operand[0][0] == 'src1':
                src1_val = operand[1]
            if operand[0][0] == 'src2':
                src2_val = operand[1]

            if operand[0][1] in ["x","y","z"]: 
                # ==================== variables validator ====================
                if re.fullmatch("^[%_$&a-zA-Z]{1}[%_$&a-zA-Z0-9]*", operand[1]) != None:
                    # variables
                    last_type = "variable"
                elif re.fullmatch("(^[-+1-9]{1}[0-9]*)|(0$)", operand[1]) != None:
                    # constants
                    last_type = "integer"
                elif  re.match("^\".*\"", operand[1]) != None:
                    # strings
                    last_type = "string"
                else:
                    if re.fullmatch('^[+,-]*0+.*', operand[1]) != None:
                        raise Exception("17", "Other lexical and syntax errors", "leadign zeros") # Fixing leading zeros problem
                    else:
                        raise Exception("14","Parsing Error","Bad kind of operand")
            elif operand[0][1] == "l": 
                # ==================== labels validator ====================
                if re.fullmatch("^@[%_$&a-zA-Z0-1]*", operand[1]) != None:
                    # labels 
                    last_type = "label" # fixing lable spell mistake
                else:
                    # exception in case labels or variables don't follow its structure
                    raise Exception("14","Parsing Error","Bad kind of operand")


            if dst_val is not None and operand[0][0] == 'dst':
                dst_type = last_type
            elif src1_val is not None and operand[0][0] == 'src1':
                src1_type = last_type
            elif src2_val is not None and operand[0][0] == 'src2':
                src2_type = last_type
        
     
        my_xml.add_tac(opcode, dst_type, src1_type, src2_type, dst_val, src1_val, src2_val)
        

    else:
        # exception in case argument doesn't much the requirements for the operation
        raise Exception("12","Parsing Error","Missing of excessing operand of instruction")

# reagroups the string in a single token
def string_grouping(line):
    double_space_line = ""
    leter_before = ""
    open = False
    for leter in line:
        if leter == '"':
            if leter_before != '\\':
                if open:
                    open = False
                else:
                    open = True
        if open == False and leter == " ":
            double_space_line += "  "
        else:
            double_space_line += leter
        leter_before = leter
        
    return double_space_line.split("  ")
    

# File dump into memory
def read_file(input_file):
    code = []
    with open(input_file) as file:
        code = file.readlines()
    return code

# Program entry point
if __name__ == "__main__":
    try:
        input_file = sys.argv[1]
    except IndexError:
        input_file = "test/IPPeCode.txt"

    try:
        out = sys.argv[2]
    except IndexError:
        out = "out"

    if input_file == "-":
        main(sys.stdin.readlines(), input_file, out)
    else:
        main(read_file(input_file), input_file, out)




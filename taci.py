import xml.etree.ElementTree as ET
import lxml.etree as DTD_check
import xml.dom.minidom
import re, sys, ast

class file_handling():

    def __init__(self):
        self.infile = None
        self.program = None
        self.output = None
        self.xml = None
        self.dtd = None
        self.inputs = []
        self.outputs = []

        self.line_arguments()
    
    # fuction that handles the line arguments of the script
    def line_arguments(self):

        # setting input for the program
        try:
            if re.match('--input',sys.argv[1]):
                self.infile = sys.argv[1]
                self.infile = self.infile.split('=')[1]    
            else:
                self.program = sys.argv[1]
                self.infile = None #sys.stdin.readlines()
                try:
                    self.output = sys.argv[2]
                except IndexError:
                    self.output = None
            #checking for second argument 
            try:
                if self.program == None:
                    self.program = sys.argv[2]
                    # checking for the existence of the third argument
                    try:
                        self.output = sys.argv[3]
                    except IndexError:
                        self.output = None

                else:
                    self.output = sys.argv[2]
            except IndexError:
                self.infile = None
        except IndexError:
            raise Exception("20","Parsing Error during the parsing of XML","invalid XML, file cannot be opened")
        #print(self.infile)
        #print(self.program)
        #print(self.output)

        '''
        xml_file = ''
        with open(self.program, 'r') as file:
            xml_file = file.read()
        xml_file = re.sub('\n|\t', '', xml_file)    
        dtd = re.search('<!DOCTYPE \w+ \[.*\]>', xml_file, re.DOTALL==True)
        xml = re.sub('<!DOCTYPE \w+ \[.*\]>', '', xml_file)
        
        print(dtd)
        print(xml)'''


    def get_inputs(self):
        if self.infile == None:
            self.inputs = sys.stdin.readlines()
        else:
            try:
                with open(self.infile, 'r') as file:
                    self.inputs = file.readlines()
            except:
                     raise Exception("30","Other run-time errors","could not open input file")
        for i in range(0, len(self.inputs)):
                self.inputs[i] = self.inputs[i].replace('\n', '')
        #print(self.inputs)

    # creates aoutput with each of the print statements in one line
    def push_outputs(self):
        for i in range(0, len(self.outputs)):
                self.outputs[i] = self.outputs[i]+'\n'
        if self.output == None:
            sys.stdout.writelines(self.outputs)
        else:
            try:
                with open(self.output, 'w') as file:
                    file.writelines(self.outputs)
            except:
                    raise Exception("30","Other run-time errors","could not open output file")
    
    def push_raw_outputs(self):
        print(self.outputs)
        aux = ''
        for i in range(0, len(self.outputs)):
            aux = aux+self.outputs[i].strip('"')
        if self.output == None:
            sys.stdout.write(aux)
        else:
            try:
                with open(self.output, 'w') as file:
                    file.writelines(aux)
            except:
                    raise Exception("30","Other run-time errors","could not open output file")
        print(aux)
        print('carlos\n peter\n proque no va')


    # chencking xml against DTD; uning of external library lxml version 4.6.3
    def check_dtd(self):
        try:
            parser = DTD_check.XMLParser(dtd_validation=True, no_network=False)
            DTD_check.parse(self.program, parser=parser)
        except Exception as e:
            raise Exception('30','other run-time errors', e.args)


class interpreter():
    def __init__(self, inputs, code):
        self.inputs = inputs
        self.inputs.reverse()
        self.code = ET.parse(code)
        self.root = self.code.getroot()
        self.outputs = []
        self.counter = 0
        self.stack = [] # using it as a stack with push and pop
        self.heap = {} # for storing variables
        self.heap_types = {}
        self.labels = {}

        self.main_loop()

    def main_loop(self):
        for child in self.root:
            if child.attrib['opcode'] == "LABEL":
                self.instruction_label(child)


        i = 0
        lines = len(list(self.root))
        while i <= lines-1:
        
            child = self.root[i]
            i += 1
            print(child.attrib)
            #self.counter = int(child.attrib['order'])
            
            if child.attrib['opcode'] == "MOV":
                self.instruction_mov(child)
            elif child.attrib['opcode'] == "ADD":
                self.instruction_add(child)
            elif child.attrib['opcode'] == "SUB":
                self.instruction_sub(child)
            elif child.attrib['opcode'] == "MUL":
                self.instruction_mul(child)
            elif child.attrib['opcode'] == "DIV":
                self.instruction_div(child)
            elif child.attrib['opcode'] == "READINT":
                self.instruction_readint(child)
            elif child.attrib['opcode'] == "READSTR":
                self.instruction_readstr(child)
            elif child.attrib['opcode'] == "PRINT":
                self.instruction_print(child)
            elif child.attrib['opcode'] == "LABEL":
                pass
            elif child.attrib['opcode'] == "JUMP":
                i = self.instruction_jump(child)
            elif child.attrib['opcode'] == "JUMPIFEQ":
                aux = self.instruction_jumpifeq(child)
                if type(aux) == type(i):
                    i = aux 
            elif child.attrib['opcode'] == "JUMPIFLT":
                aux = self.instruction_jumpiflt(child)
                if type(aux) == type(i):
                    i = aux
            elif child.attrib['opcode'] == "CALL":
                aux = self.instruction_call(child)
                if type(aux) == type(i):
                    self.counter = i
                    i = aux
            elif child.attrib['opcode'] == "RETURN":
                i = self.counter
            elif child.attrib['opcode'] == "PUSH":
                self.instruction_push(child)
            elif child.attrib['opcode'] == "POP":
                self.instruction_pop(child)

            print('\n')

    def instruction_mov(self, tac):
        if tac[1].attrib['type'] != 'variable':
            self.heap[tac[0].text] = tac[1].text
            self.heap_types[tac[0].text] = tac[1].attrib['type']
        else:
            self.heap[tac[0].text] = self.heap[tac[1].text]
            self.heap_types[tac[0].text] = self.heap_types[tac[1].text]
        print(self.heap)
        print(self.heap_types)

    def instruction_add(self, tac):
        try:
            if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                if self.heap_types[tac[1].text] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) + int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                if tac[1].attrib['type'] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(tac[1].text) + int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[2].attrib['type'] == self.heap_types[tac[1].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) + int(tac[2].text))
                    self.heap_types[tac[0].text] = self.heap_types[tac[1].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[1].attrib['type'] == tac[2].attrib['type']:
                    self.heap[tac[0].text] = str(int(tac[1].text) + int(tac[2].text))
                    self.heap_types[tac[0].text] = tac[1].attrib['type']
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
        except KeyError as ex:
            raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
            
        print(self.heap)
        print(self.heap_types)


    def instruction_sub(self, tac):
        try:
            if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                if self.heap_types[tac[1].text] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) - int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                if tac[1].attrib['type'] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(tac[1].text) - int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[2].attrib['type'] == self.heap_types[tac[1].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) - int(tac[2].text))
                    self.heap_types[tac[0].text] = self.heap_types[tac[1].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[1].attrib['type'] == tac[2].attrib['type']:
                    self.heap[tac[0].text] = str(int(tac[1].text) - int(tac[2].text))
                    self.heap_types[tac[0].text] = tac[1].attrib['type']
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
        except KeyError as ex:
            raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
        print(self.heap)
        print(self.heap_types)

    def instruction_mul(self, tac):
        try:
            if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                if self.heap_types[tac[1].text] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) * int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                if tac[1].attrib['type'] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(tac[1].text) * int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[2].attrib['type'] == self.heap_types[tac[1].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) * int(tac[2].text))
                    self.heap_types[tac[0].text] = self.heap_types[tac[1].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[1].attrib['type'] == tac[2].attrib['type']:
                    self.heap[tac[0].text] = str(int(tac[1].text) * int(tac[2].text))
                    self.heap_types[tac[0].text] = tac[1].attrib['type']
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
        except KeyError as ex:
            raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
        print(self.heap)
        print(self.heap_types)
    

    def instruction_div(self, tac):
        try:
            if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                if self.heap_types[tac[1].text] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) / int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                if tac[1].attrib['type'] == self.heap_types[tac[2].text]:
                    self.heap[tac[0].text] = str(int(tac[1].text) / int(self.heap[tac[2].text]))
                    self.heap_types[tac[0].text] = self.heap_types[tac[2].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[2].attrib['type'] == self.heap_types[tac[1].text]:
                    self.heap[tac[0].text] = str(int(self.heap[tac[1].text]) / int(tac[2].text))
                    self.heap_types[tac[0].text] = self.heap_types[tac[1].text]
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
            elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                if tac[1].attrib['type'] == tac[2].attrib['type']:
                    self.heap[tac[0].text] = str(int(tac[1].text) / int(tac[2].text))
                    self.heap_types[tac[0].text] = tac[1].attrib['type']
                else:
                    raise Exception("27", "Run-time Error", "Operands of incompatible type")
        except KeyError as ex:
            raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
        except ZeroDivisionError:
            raise Exception('25', 'Run-time Error', 'Division by zero using Div instruction')
        print(self.heap)
        print(self.heap_types)


    def instruction_readint(self, tac):
        try:
            self.heap[tac[0].text] = str(int(self.inputs.pop()))
            self.heap_types[tac[0].text] = 'integer'
        except ValueError:
            raise Exception('26', 'Run-time Error', 'READINT get invalid value (not an integer)')
        except IndexError:
            raise Exception('28', 'Run-time Error', 'Pop from the empty (data/call) stack is forbidden')
        print(self.heap)
        print(self.heap_types)

    def instruction_readstr(self, tac):
        try:
            self.heap[tac[0].text] = self.inputs.pop()
            self.heap_types[tac[0].text] = 'string'
        except ValueError:
            raise Exception('26', 'Run-time Error', 'READINT get invalid value (not an integer)')
        except IndexError:
            raise Exception('28', 'Run-time Error', 'Pop from the empty (data/call) stack is forbidden')
        print(self.heap)
        print(self.heap_types)

    def instruction_print(self, tac):
        if tac[0].attrib['type'] != 'variable':
            self.outputs.append(tac[0].text)
        else:
            self.outputs.append(self.heap[tac[0].text])

    def instruction_label(self, tac):
        if tac[0].text not in self.labels.keys():
            self.labels[tac[0].text] = int(tac.attrib['order'])
        else:
            raise Exception('21', 'Semantic Error', 'Labeloccurs several times')
        print(self.labels)

    def instruction_jump(self, tac):
        if tac[0].text in self.labels.keys():
            return int(self.labels[tac[0].text])-1
        else:
            raise Exception('23', 'Run-time Error', 'Jump/call to a non existing label')
        print(self.labels)

    def instruction_jumpifeq(self, tac):
        if tac[0].text in self.labels.keys():
            try:
                print('====================')
                if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                    if int(self.heap[tac[1].text]) == int(self.heap[tac[2].text]):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                    if int(tac[1].text) == int(self.heap[tac[2].text]):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                    if int(self.heap[tac[1].text]) == int(tac[2].text):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                    if int(tac[1].text) == int(tac[2].text):
                        return int(self.labels[tac[0].text])-1
            except KeyError as ex:
                raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
        else:
            raise Exception('23', 'Run-time Error', 'Jump/call to a non existing label')
        print(self.labels)


    def instruction_jumpiflt(self, tac):
        if tac[0].text in self.labels.keys():
            try:
                if tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] == 'variable':
                    if int(self.heap[tac[1].text]) < int(self.heap[tac[2].text]):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] == 'variable':
                    if int(tac[1].text) < int(self.heap[tac[2].text]):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] == 'variable' and tac[2].attrib['type'] != 'variable':
                    if int(self.heap[tac[1].text]) < int(tac[2].text):
                        return int(self.labels[tac[0].text])-1
                elif tac[1].attrib['type'] != 'variable' and tac[2].attrib['type'] != 'variable':
                    if int(tac[1].text) < int(tac[2].text):
                        return int(self.labels[tac[0].text])-1
            except KeyError as ex:
                raise Exception('24', 'Run-time Error', 'Read access to a non-defined variable {'+ex.args[0]+'}')
        else:
            raise Exception('23', 'Run-time Error', 'Jump/call to a non existing label')
        print(self.labels)

    def instruction_call(self, tac):
        try:
            return int(self.labels[tac[0].text])-1
        except:
            raise Exception('23', 'Run-time Error', 'Jump/call to a non existing label')

    def instruction_push(self, tac):
        if tac[0].attrib['type'] == 'variable':
            self.stack.append(self.heap[tac[0].text])
        else:
            self.stack.append(tac[0].text)
        print(self.stack)

    def instruction_pop(self, tac):
        if self.stack == []:
            raise Exception('28', 'Run-time Error', 'Pop from the empty (data/call) stack is forbidden')
        else:
            aux = self.stack.pop()
            self.heap[tac[0].text] = aux
            if type(aux) == type("palace_holder"):
                self.heap_types[tac[0].text] = "string"
            else:
                self.heap_types[tac[0].text] = "integer"
        print(self.stack)
        print(self.heap)


def main():

    try:
            # File handling
            files = file_handling()
            files.check_dtd()
            files.get_inputs()
            # Runing scrip interpretation
            vm = interpreter(files.inputs, files.program)

            files.outputs = vm.outputs
            files.push_outputs()
    except Exception as ex:
        try:
            print(f"Error code: {ex.args[0]} == {ex.args[1]}: {ex.args[2]}.", file=sys.stderr)
        except:
            ex = Exception('99', 'Internal errors', ex.args)
            print(f"Error code: {ex.args[0]} == {ex.args[1]}: {ex.args[2]}.", file=sys.stderr)
        return 1 # or the error code, didn't knew what was required
        #return ex.args[0]

   

# Program entry point
if __name__ == "__main__":
    main()



